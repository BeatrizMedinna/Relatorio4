/*
 * busca.h - Buscas sequenciais (Solução 1) e binárias (Solução 2).
 * Todas retornam o índice onde a chave foi encontrada ou -1.
 */
#ifndef BUSCA_H
#define BUSCA_H

#include "csv.h"

/* Solução 1: vetor em qualquer ordem. */
long busca_sequencial_iterativa(const Item *v, long n, const char *chave);
long busca_sequencial_recursiva(const Item *v, long n, const char *chave);

/* Solução 2: vetor obrigatoriamente ordenado (strcmp crescente). */
long busca_binaria_iterativa(const Item *v, long n, const char *chave);
long busca_binaria_recursiva(const Item *v, long n, const char *chave);

#endif
