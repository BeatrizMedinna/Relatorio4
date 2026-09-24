/*
 * ordenacao.h - MergeSort recursivo (top-down) e iterativo (bottom-up).
 * Ordem: chave crescente (strcmp); empates mantêm a ordem original (estável).
 */
#ifndef ORDENACAO_H
#define ORDENACAO_H

#include "csv.h"

/* Retornam 0 em caso de sucesso e -1 se faltar memória para o vetor auxiliar. */
int mergesort_recursivo(Item *v, long n);
int mergesort_iterativo(Item *v, long n);

#endif
