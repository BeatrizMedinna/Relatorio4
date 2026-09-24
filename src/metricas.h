/*
 * metricas.h - Contadores usados para comparar a teoria com a prática.
 *
 *  g_comparacoes : número de comparações entre chaves (chamadas a strcmp)
 *  g_prof_atual  : profundidade atual da pilha de recursão
 *  g_prof_max    : maior profundidade de recursão atingida
 *
 * Os contadores têm custo O(1) por uso e são aplicados igualmente em todas
 * as versões, portanto não distorcem a comparação entre elas.
 */
#ifndef METRICAS_H
#define METRICAS_H

extern unsigned long long g_comparacoes;
extern long g_prof_atual;
extern long g_prof_max;

#define ENTRA_RECURSAO() \
    do { if (++g_prof_atual > g_prof_max) g_prof_max = g_prof_atual; } while (0)
#define SAI_RECURSAO() (g_prof_atual--)

void   metricas_zera(void);
double agora_segundos(void); /* relógio monotônico de alta resolução */

#endif
