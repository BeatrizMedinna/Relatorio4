#include "busca.h"
#include "metricas.h"

#include <string.h>

/* Comparação instrumentada: toda comparação de chaves passa por aqui. */
static int compara(const char *a, const char *b)
{
    g_comparacoes++;
    return strcmp(a, b);
}

/* ------------------------------------------------------------------ */
/* SOLUÇÃO 1 - BUSCA SEQUENCIAL                                        */
/* ------------------------------------------------------------------ */

/* Iterativa: percorre v[0..n-1].
 * Tempo: melhor O(1), pior/ausente n comparações -> O(n).
 * Espaço extra: O(1) (apenas a variável i). */
long busca_sequencial_iterativa(const Item *v, long n, const char *chave)
{
    for (long i = 0; i < n; i++)
        if (compara(v[i].chave, chave) == 0)
            return i;
    return -1;
}

/* Recursiva: T(k) = T(k-1) + c, onde k = n - i elementos restantes.
 * Tempo: O(n). Espaço extra: um quadro de pilha por elemento -> O(n).
 * Observação: a chamada recursiva NÃO é a última instrução (SAI_RECURSAO
 * vem depois), então o compilador não consegue transformá-la em laço
 * (tail call). Isso mantém a recursão "de verdade" para a análise. */
static long seq_rec(const Item *v, long n, const char *chave, long i)
{
    long r;
    ENTRA_RECURSAO();
    if (i >= n)
        r = -1;                                   /* caso base: não achou */
    else if (compara(v[i].chave, chave) == 0)
        r = i;                                    /* caso base: achou */
    else
        r = seq_rec(v, n, chave, i + 1);          /* passo recursivo */
    SAI_RECURSAO();
    return r;
}

long busca_sequencial_recursiva(const Item *v, long n, const char *chave)
{
    return seq_rec(v, n, chave, 0);
}

/* ------------------------------------------------------------------ */
/* SOLUÇÃO 2 - BUSCA BINÁRIA                                           */
/* ------------------------------------------------------------------ */

/* Iterativa: a cada passo o intervalo [ini, fim] cai pela metade.
 * Tempo: no máximo floor(log2 n) + 1 iterações -> O(log n).
 * Espaço extra: O(1) (ini, fim, meio). */
long busca_binaria_iterativa(const Item *v, long n, const char *chave)
{
    long ini = 0, fim = n - 1;
    while (ini <= fim) {
        long meio = ini + (fim - ini) / 2;       /* evita overflow de ini+fim */
        int c = compara(v[meio].chave, chave);
        if (c == 0) return meio;
        if (c < 0) ini = meio + 1;
        else       fim = meio - 1;
    }
    return -1;
}

/* Recursiva: T(n) = T(n/2) + c  =>  O(log n) pelo Teorema Mestre (caso 2).
 * Espaço extra: um quadro de pilha por nível -> O(log n). */
static long bin_rec(const Item *v, long ini, long fim, const char *chave)
{
    long r;
    ENTRA_RECURSAO();
    if (ini > fim) {
        r = -1;
    } else {
        long meio = ini + (fim - ini) / 2;
        int c = compara(v[meio].chave, chave);
        if (c == 0)     r = meio;
        else if (c < 0) r = bin_rec(v, meio + 1, fim, chave);
        else            r = bin_rec(v, ini, meio - 1, chave);
    }
    SAI_RECURSAO();
    return r;
}

long busca_binaria_recursiva(const Item *v, long n, const char *chave)
{
    return bin_rec(v, 0, n - 1, chave);
}
