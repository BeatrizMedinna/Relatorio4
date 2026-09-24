#include "ordenacao.h"
#include "metricas.h"

#include <stdlib.h>
#include <string.h>

/* Intercala v[ini..meio] e v[meio+1..fim] (ambos já ordenados) usando aux.
 * Custo: no máximo (fim - ini) comparações e (fim - ini + 1) movimentos,
 * ou seja, Theta(k) para k elementos. É a MESMA rotina nas duas versões,
 * então qualquer diferença entre elas vem só da forma de dividir o vetor. */
static void intercala(Item *v, Item *aux, long ini, long meio, long fim)
{
    long i = ini, j = meio + 1, k = ini;

    while (i <= meio && j <= fim) {
        g_comparacoes++;
        /* "<=" garante estabilidade: em empate, o da esquerda vem primeiro */
        if (strcmp(v[i].chave, v[j].chave) <= 0) aux[k++] = v[i++];
        else                                      aux[k++] = v[j++];
    }
    while (i <= meio) aux[k++] = v[i++];
    while (j <= fim)  aux[k++] = v[j++];

    memcpy(v + ini, aux + ini, (size_t)(fim - ini + 1) * sizeof(Item));
}

/* ------------------------------------------------------------------ */
/* RECURSIVO (top-down)                                                */
/* T(n) = 2T(n/2) + Theta(n)  =>  Theta(n log n)                       */
/* Espaço: aux de n posições + pilha de profundidade ceil(log2 n) + 1  */
/* ------------------------------------------------------------------ */
static void ms_rec(Item *v, Item *aux, long ini, long fim)
{
    ENTRA_RECURSAO();
    if (ini < fim) {
        long meio = ini + (fim - ini) / 2;
        ms_rec(v, aux, ini, meio);          /* ordena a metade esquerda */
        ms_rec(v, aux, meio + 1, fim);      /* ordena a metade direita  */
        intercala(v, aux, ini, meio, fim);  /* junta as duas metades    */
    }
    SAI_RECURSAO();
}

int mergesort_recursivo(Item *v, long n)
{
    if (n < 2) return 0;
    Item *aux = malloc((size_t)n * sizeof(Item));
    if (!aux) return -1;
    ms_rec(v, aux, 0, n - 1);
    free(aux);
    return 0;
}

/* ------------------------------------------------------------------ */
/* ITERATIVO (bottom-up)                                               */
/* Intercala blocos de tamanho 1, 2, 4, ... até cobrir o vetor.         */
/* Laço externo: ceil(log2 n) passadas; cada passada: Theta(n)          */
/*   =>  Theta(n log n).                                               */
/* Espaço: aux de n posições + O(1) variáveis; sem pilha de recursão.   */
/* ------------------------------------------------------------------ */
int mergesort_iterativo(Item *v, long n)
{
    if (n < 2) return 0;
    Item *aux = malloc((size_t)n * sizeof(Item));
    if (!aux) return -1;

    for (long largura = 1; largura < n; largura *= 2) {
        for (long ini = 0; ini < n - largura; ini += 2 * largura) {
            long meio = ini + largura - 1;
            long fim  = ini + 2 * largura - 1;
            if (fim > n - 1) fim = n - 1;
            intercala(v, aux, ini, meio, fim);
        }
    }
    free(aux);
    return 0;
}
