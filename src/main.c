/*
 * insere - insere registros de um CSV ao final de outro CSV sem duplicar
 *          a coluna usada como chave de unicidade.
 *
 * Uso:
 *   insere <novos.csv> <destino.csv> [opções]
 *
 * Opções:
 *   -m <metodo>   seq-iter      Solução 1, busca sequencial iterativa
 *                 seq-rec       Solução 1, busca sequencial recursiva
 *                 bin-iter-iter Solução 2, MergeSort iterativo + busca binária iterativa
 *                 bin-iter-rec  Solução 2, MergeSort iterativo + busca binária recursiva
 *                 bin-rec-iter  Solução 2, MergeSort recursivo + busca binária iterativa
 *                 bin-rec-rec   Solução 2, MergeSort recursivo + busca binária recursiva
 *                 (padrão: bin-rec-iter)
 *   -k <coluna>   índice (base 0) da coluna-chave (padrão: 0 = NumeroRegistro)
 *   -v            lista cada registro rejeitado e o motivo
 *   -s            simulação: faz toda a verificação mas NÃO grava o destino
 *   -t            imprime em stderr uma linha de métricas (usada nos testes)
 *
 * Regras:
 *   - A primeira linha de cada arquivo é o cabeçalho e nunca é inserida.
 *   - Se o destino não existir, ele é criado com o cabeçalho do arquivo de novos.
 *   - Rejeita-se o registro cuja chave (a) já existe no destino, (b) já apareceu
 *     antes no próprio arquivo de novos, ou (c) está vazia / coluna ausente.
 *   - Os registros aceitos são gravados ao final do destino, na ordem original.
 */
#include "csv.h"
#include "busca.h"
#include "ordenacao.h"
#include "metricas.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum Motivo { ACEITO = 0, DUP_DESTINO, DUP_LOTE, CHAVE_INVALIDA };
static const char *NOME_MOTIVO[] = {
    "aceito", "chave já existe no destino",
    "chave repetida no próprio arquivo de novos", "chave vazia ou coluna ausente"
};

typedef struct {
    Item  *itens;
    long   n, cap;
} Vetor;

static void falha(const char *msg, const char *detalhe)
{
    fprintf(stderr, "erro: %s%s%s\n", msg, detalhe ? ": " : "", detalhe ? detalhe : "");
    exit(EXIT_FAILURE);
}

static void vetor_adiciona(Vetor *v, char *chave, long idx)
{
    if (v->n == v->cap) {
        v->cap = v->cap ? v->cap * 2 : 1024;
        Item *novo = realloc(v->itens, (size_t)v->cap * sizeof(Item));
        if (!novo) falha("memória insuficiente", NULL);
        v->itens = novo;
    }
    v->itens[v->n].chave = chave;
    v->itens[v->n].idx = idx;
    v->n++;
}

static void uso(const char *prog)
{
    fprintf(stderr,
        "Uso: %s <novos.csv> <destino.csv> [-m metodo] [-k coluna] [-v] [-s] [-t]\n"
        "Métodos: seq-iter | seq-rec | bin-iter-iter | bin-iter-rec | bin-rec-iter | bin-rec-rec\n",
        prog);
    exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
    const char *arq_novos = NULL, *arq_destino = NULL, *metodo = "bin-rec-iter";
    int coluna = 0, verboso = 0, simular = 0, metricas = 0;

    /* ---------------- argumentos ---------------- */
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-m") && i + 1 < argc)      metodo = argv[++i];
        else if (!strcmp(argv[i], "-k") && i + 1 < argc) coluna = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-v")) verboso = 1;
        else if (!strcmp(argv[i], "-s")) simular = 1;
        else if (!strcmp(argv[i], "-t")) metricas = 1;
        else if (argv[i][0] == '-') uso(argv[0]);
        else if (!arq_novos)   arq_novos = argv[i];
        else if (!arq_destino) arq_destino = argv[i];
        else uso(argv[0]);
    }
    if (!arq_novos || !arq_destino || coluna < 0) uso(argv[0]);

    int sequencial = !strncmp(metodo, "seq-", 4);
    int seq_rec = !strcmp(metodo, "seq-rec");
    int ms_rec = 0, bb_rec = 0;
    if (!sequencial) {
        if      (!strcmp(metodo, "bin-iter-iter")) { ms_rec = 0; bb_rec = 0; }
        else if (!strcmp(metodo, "bin-iter-rec"))  { ms_rec = 0; bb_rec = 1; }
        else if (!strcmp(metodo, "bin-rec-iter"))  { ms_rec = 1; bb_rec = 0; }
        else if (!strcmp(metodo, "bin-rec-rec"))   { ms_rec = 1; bb_rec = 1; }
        else uso(argv[0]);
    } else if (strcmp(metodo, "seq-iter") && !seq_rec) {
        uso(argv[0]);
    }

    if (csv_eh_utf16(arq_novos) || csv_eh_utf16(arq_destino))
        falha("arquivo em UTF-16; converta antes com ferramentas/converte_utf16", NULL);

    double t0 = agora_segundos();

    /* ---------------- 1. carrega as chaves do destino ---------------- */
    Vetor dest = {0};
    int destino_existe = 0, destino_crlf = 0, destino_termina_nl = 1;
    FILE *fd = fopen(arq_destino, "rb");
    if (fd) {
        destino_existe = 1;
        int cr;
        char *linha = csv_le_linha(fd, &cr);        /* cabeçalho */
        if (linha) {
            destino_crlf = cr;
            free(linha);
            long num = 1;
            while ((linha = csv_le_linha(fd, NULL)) != NULL) {
                num++;
                char *chave = csv_extrai_campo(linha, coluna);
                if (chave && chave[0]) vetor_adiciona(&dest, chave, -num);
                else free(chave);
                free(linha);
            }
            /* o arquivo termina com quebra de linha? (para não "colar" linhas) */
            if (fseek(fd, -1, SEEK_END) == 0) destino_termina_nl = (fgetc(fd) == '\n');
        } else {
            destino_existe = 0;                     /* arquivo vazio */
        }
        fclose(fd);
    }
    long n = dest.n;

    /* ---------------- 2. carrega os registros novos ---------------- */
    FILE *fn = fopen(arq_novos, "rb");
    if (!fn) falha("não foi possível abrir", arq_novos);
    char *cabecalho = csv_le_linha(fn, NULL);
    if (!cabecalho) falha("arquivo de novos vazio", arq_novos);
    csv_remove_bom(cabecalho);

    char **linhas = NULL;
    char **chaves = NULL;
    long m = 0, cap = 0;
    char *linha;
    while ((linha = csv_le_linha(fn, NULL)) != NULL) {
        if (linha[0] == '\0') { free(linha); continue; }   /* ignora linhas em branco */
        if (m == cap) {
            cap = cap ? cap * 2 : 1024;
            linhas = realloc(linhas, (size_t)cap * sizeof(char *));
            chaves = realloc(chaves, (size_t)cap * sizeof(char *));
            if (!linhas || !chaves) falha("memória insuficiente", NULL);
        }
        linhas[m] = linha;
        chaves[m] = csv_extrai_campo(linha, coluna);
        m++;
    }
    fclose(fn);

    int *motivo = calloc((size_t)(m ? m : 1), sizeof(int));
    if (!motivo) falha("memória insuficiente", NULL);
    for (long i = 0; i < m; i++)
        if (!chaves[i] || !chaves[i][0]) motivo[i] = CHAVE_INVALIDA;

    double t1 = agora_segundos();
    double t_ord = 0.0;
    unsigned long long comp_ord = 0, comp_ord_dest = 0, comp_busca = 0;
    long prof_ord = 0, prof_busca = 0;

    /* ---------------- 3. verificação de duplicidade ---------------- */
    if (sequencial) {
        /* SOLUÇÃO 1: o vetor fica na ordem do arquivo. Cada chave aceita é
         * acrescentada ao final, para que repetições dentro do próprio
         * arquivo de novos também sejam detectadas. */
        metricas_zera();
        for (long i = 0; i < m; i++) {
            if (motivo[i]) continue;
            long pos = seq_rec ? busca_sequencial_recursiva(dest.itens, dest.n, chaves[i])
                               : busca_sequencial_iterativa(dest.itens, dest.n, chaves[i]);
            if (pos < 0) {
                motivo[i] = ACEITO;
                vetor_adiciona(&dest, chaves[i], i);
            } else {
                motivo[i] = (dest.itens[pos].idx >= 0) ? DUP_LOTE : DUP_DESTINO;
            }
        }
        comp_busca = g_comparacoes;
        prof_busca = g_prof_max;
    } else {
        /* SOLUÇÃO 2:
         *  (a) ordena as n chaves do destino com MergeSort;
         *  (b) ordena as chaves válidas do lote com o mesmo MergeSort (estável):
         *      chaves iguais ficam vizinhas e a 1ª ocorrência (menor idx) vem
         *      primeiro, então repetições no lote saem de uma varredura linear;
         *  (c) busca binária de cada chave do lote no vetor do destino. */
        Vetor lote = {0};
        for (long i = 0; i < m; i++)
            if (!motivo[i]) vetor_adiciona(&lote, chaves[i], i);

        metricas_zera();
        double ta = agora_segundos();
        int erro = ms_rec ? mergesort_recursivo(dest.itens, dest.n)
                          : mergesort_iterativo(dest.itens, dest.n);
        comp_ord_dest = g_comparacoes;          /* só a ordenação do destino */
        if (!erro) erro = ms_rec ? mergesort_recursivo(lote.itens, lote.n)
                                 : mergesort_iterativo(lote.itens, lote.n);
        if (erro) falha("memória insuficiente para o MergeSort", NULL);
        t_ord = agora_segundos() - ta;
        comp_ord = g_comparacoes;
        prof_ord = g_prof_max;

        metricas_zera();
        char *repetida_no_lote = calloc((size_t)(m ? m : 1), 1);
        if (!repetida_no_lote) falha("memória insuficiente", NULL);
        for (long j = 1; j < lote.n; j++) {
            g_comparacoes++;
            if (strcmp(lote.itens[j].chave, lote.itens[j - 1].chave) == 0)
                repetida_no_lote[lote.itens[j].idx] = 1;
        }
        /* O destino é consultado primeiro: uma chave que já existe no destino é
         * classificada assim mesmo que também se repita no lote (mesma regra da
         * Solução 1, para que os dois métodos relatem os mesmos motivos). */
        for (long i = 0; i < m; i++) {
            if (motivo[i]) continue;
            long pos = bb_rec ? busca_binaria_recursiva(dest.itens, dest.n, chaves[i])
                              : busca_binaria_iterativa(dest.itens, dest.n, chaves[i]);
            if (pos >= 0)                 motivo[i] = DUP_DESTINO;
            else if (repetida_no_lote[i]) motivo[i] = DUP_LOTE;
            else                          motivo[i] = ACEITO;
        }
        free(repetida_no_lote);
        comp_busca = g_comparacoes;
        prof_busca = g_prof_max;
        free(lote.itens);
    }

    double t2 = agora_segundos();

    /* ---------------- 4. grava os aceitos ao final do destino ---------------- */
    long aceitos = 0, rej[4] = {0, 0, 0, 0};
    for (long i = 0; i < m; i++) {
        if (motivo[i] == ACEITO) aceitos++;
        else rej[motivo[i]]++;
    }

    if (!simular && aceitos > 0) {
        FILE *fo = fopen(arq_destino, "ab");
        if (!fo) falha("não foi possível gravar", arq_destino);
        const char *nl = destino_crlf ? "\r\n" : "\n";
        if (!destino_existe) fprintf(fo, "%s%s", cabecalho, nl);
        else if (!destino_termina_nl) fputs(nl, fo);
        for (long i = 0; i < m; i++)
            if (motivo[i] == ACEITO) fprintf(fo, "%s%s", linhas[i], nl);
        if (fclose(fo) != 0) falha("erro ao fechar", arq_destino);
    }
    double t3 = agora_segundos();

    /* ---------------- 5. relatório ---------------- */
    if (verboso)
        for (long i = 0; i < m; i++)
            if (motivo[i] != ACEITO)
                printf("REJEITADO linha %ld [%s]: %s\n", i + 2,
                       chaves[i] ? chaves[i] : "", NOME_MOTIVO[motivo[i]]);

    printf("Método: %s | coluna-chave: %d\n", metodo, coluna);
    printf("Registros no destino: %ld | registros lidos: %ld\n", n, m);
    printf("Inseridos: %ld%s\n", aceitos, simular ? " (simulação: nada gravado)" : "");
    printf("Rejeitados: %ld (já no destino: %ld | repetidos no lote: %ld | chave inválida: %ld)\n",
           m - aceitos, rej[DUP_DESTINO], rej[DUP_LOTE], rej[CHAVE_INVALIDA]);

    if (metricas)
        /* metodo;n;m;t_carga;t_ordenacao;t_verificacao_total;t_gravacao;
           comp_ordenacao;comp_ordenacao_destino;comp_busca;prof_ordenacao;prof_busca
           (t_verificacao_total inclui a ordenação; comp_busca inclui a
            varredura de vizinhos do lote ordenado na Solução 2) */
        fprintf(stderr, "METRICAS;%s;%ld;%ld;%.9f;%.9f;%.9f;%.9f;%llu;%llu;%llu;%ld;%ld\n",
                metodo, n, m, t1 - t0, t_ord, t2 - t1, t3 - t2,
                comp_ord, comp_ord_dest, comp_busca, prof_ord, prof_busca);

    /* ---------------- limpeza ---------------- */
    for (long i = 0; i < m; i++) { free(linhas[i]); free(chaves[i]); }
    for (long i = 0; i < n; i++) {
        /* em seq, dest.itens[n..] apontam para chaves[] (já liberadas) */
        free(dest.itens[i].chave);
    }
    free(dest.itens);
    free(linhas);
    free(chaves);
    free(motivo);
    free(cabecalho);
    return EXIT_SUCCESS;
}
