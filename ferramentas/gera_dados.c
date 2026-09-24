/*
 * gera_dados - gera pares (destino, novos) de tamanho controlado para os
 * experimentos, a partir da base real do Inmetro.
 *
 * Cada linha sintética é a cópia de uma linha REAL sorteada da base, com a
 * coluna 0 (NumeroRegistro) substituída por uma chave no mesmo formato
 * "NNNNNN/AAAA". As chaves do destino são todas distintas e ficam fora de
 * ordem (permutação pseudoaleatória), como no arquivo original.
 *
 * Uso:
 *   gera_dados <base_utf8.csv> <n> <m> <%dup_destino> <%dup_lote> <semente>
 *              <saida_destino.csv> <saida_novos.csv>
 *
 *   n            linhas no destino
 *   m            linhas no arquivo de novos
 *   %dup_destino fração dos novos cuja chave já está no destino (0..100)
 *   %dup_lote    fração dos novos que repetem uma chave anterior do lote (0..100)
 *
 * O gerador é determinístico: mesma semente => mesmos arquivos em qualquer SO.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PRIMO 99999989ULL   /* primo < 10^8: x -> (A*x + B) mod P é injetora */

static unsigned long long estado;
static unsigned long long aleatorio(void)          /* xorshift64* */
{
    estado ^= estado >> 12;
    estado ^= estado << 25;
    estado ^= estado >> 27;
    return estado * 2685821657736338717ULL;
}
static double aleatorio01(void) { return (aleatorio() >> 11) * (1.0 / 9007199254740992.0); }

static unsigned long long A, B;
static void chave_sintetica(unsigned long long i, char *buf)
{
    unsigned long long x = (A * i + B) % PRIMO;
    sprintf(buf, "%06llu/%04llu", x % 1000000ULL, 1926ULL + x / 1000000ULL);
}

static char *le_linha(FILE *f)
{
    size_t cap = 1024, n = 0;
    char *s = malloc(cap);
    int c;
    while ((c = fgetc(f)) != EOF && c != '\n') {
        if (c == '\r' || c == '\0') continue;
        if (n + 1 >= cap) s = realloc(s, cap *= 2);
        s[n++] = (char)c;
    }
    if (c == EOF && n == 0) { free(s); return NULL; }
    s[n] = '\0';
    return s;
}

/* grava a linha trocando o 1º campo pela chave */
static void grava(FILE *o, const char *linha, const char *chave)
{
    const char *resto = strchr(linha, ';');
    fprintf(o, "%s%s\n", chave, resto ? resto : "");
}

int main(int argc, char **argv)
{
    if (argc != 9) {
        fprintf(stderr, "Uso: %s <base.csv> <n> <m> <%%dup_destino> <%%dup_lote> <semente> "
                        "<saida_destino.csv> <saida_novos.csv>\n", argv[0]);
        return 1;
    }
    long n = atol(argv[2]), m = atol(argv[3]);
    double pd = atof(argv[4]) / 100.0, pl = atof(argv[5]) / 100.0;
    estado = strtoull(argv[6], NULL, 10) * 0x9E3779B97F4A7C15ULL + 1;
    A = 1 + aleatorio() % (PRIMO - 1);
    B = aleatorio() % PRIMO;

    FILE *fb = fopen(argv[1], "rb");
    if (!fb) { perror(argv[1]); return 1; }
    char *cab = le_linha(fb);
    char **base = NULL;
    long nb = 0, cb = 0;
    char *l;
    while ((l = le_linha(fb)) != NULL) {
        if (!l[0]) { free(l); continue; }
        if (nb == cb) base = realloc(base, (size_t)(cb = cb ? cb * 2 : 128) * sizeof(char *));
        base[nb++] = l;
    }
    fclose(fb);
    if (!cab || nb == 0) { fprintf(stderr, "base vazia\n"); return 1; }

    char chave[32];

    FILE *fd = fopen(argv[7], "wb");
    if (!fd) { perror(argv[7]); return 1; }
    fprintf(fd, "%s\n", cab);
    for (long i = 0; i < n; i++) {
        chave_sintetica((unsigned long long)i, chave);
        grava(fd, base[aleatorio() % (unsigned long long)nb], chave);
    }
    fclose(fd);

    /* ids das chaves usadas no lote, para gerar repetições internas */
    unsigned long long *ids = malloc((size_t)(m ? m : 1) * sizeof *ids);
    unsigned long long proxima = (unsigned long long)n;   /* chaves inéditas */
    FILE *fn = fopen(argv[8], "wb");
    if (!fn) { perror(argv[8]); return 1; }
    fprintf(fn, "%s\n", cab);
    for (long j = 0; j < m; j++) {
        double r = aleatorio01();
        if (r < pd && n > 0)           ids[j] = aleatorio() % (unsigned long long)n;
        else if (r < pd + pl && j > 0) ids[j] = ids[aleatorio() % (unsigned long long)j];
        else                           ids[j] = proxima++;
        chave_sintetica(ids[j], chave);
        grava(fn, base[aleatorio() % (unsigned long long)nb], chave);
    }
    fclose(fn);
    return 0;
}
