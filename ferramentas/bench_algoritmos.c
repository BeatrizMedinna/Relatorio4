/*
 * bench_algoritmos - mede os algoritmos isoladamente, em memória, para
 * tamanhos maiores do que os arquivos CSV do repositório comportariam
 * (até 10^6 chaves). Usa exatamente as mesmas funções de src/.
 *
 * Saída (stdout, CSV com ';'):
 *   algoritmo;n;m;tempo_mediano_s;comparacoes;profundidade_max
 *
 * Uso: bench_algoritmos [repeticoes] [n_max_sequencial]
 *   (no Linux/macOS rode com "ulimit -s unlimited" por causa da busca
 *    sequencial recursiva, que usa uma chamada de função por elemento)
 */
#include "../src/csv.h"
#include "../src/busca.h"
#include "../src/ordenacao.h"
#include "../src/metricas.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned long long estado = 88172645463325252ULL;
static unsigned long long aleatorio(void)
{
    estado ^= estado >> 12; estado ^= estado << 25; estado ^= estado >> 27;
    return estado * 2685821657736338717ULL;
}

#define PRIMO 99999989ULL
static char *chave(unsigned long long i, unsigned long long A, unsigned long long B)
{
    char buf[32];
    unsigned long long x = (A * i + B) % PRIMO;
    sprintf(buf, "%06llu/%04llu", x % 1000000ULL, 1926ULL + x / 1000000ULL);
    char *s = malloc(strlen(buf) + 1);
    strcpy(s, buf);
    return s;
}

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static double mediana(double *t, int r)
{
    qsort(t, (size_t)r, sizeof(double), cmp_double);
    return (r % 2) ? t[r / 2] : (t[r / 2 - 1] + t[r / 2]) / 2.0;
}

int main(int argc, char **argv)
{
    int reps = argc > 1 ? atoi(argv[1]) : 5;
    long n_max_seq = argc > 2 ? atol(argv[2]) : 200000;
    const long tamanhos[] = {1000, 2000, 5000, 10000, 20000, 50000,
                             100000, 200000, 500000, 1000000};
    const int nt = (int)(sizeof tamanhos / sizeof tamanhos[0]);
    const long M = 1000;                     /* consultas por tamanho */
    double *t = malloc((size_t)reps * sizeof(double));

    printf("algoritmo;n;m;tempo_mediano_s;comparacoes;profundidade_max\n");

    for (int a = 0; a < nt; a++) {
        long n = tamanhos[a];
        unsigned long long A = 1 + aleatorio() % (PRIMO - 1), B = aleatorio() % PRIMO;

        Item *orig = malloc((size_t)n * sizeof(Item));
        Item *v = malloc((size_t)n * sizeof(Item));
        for (long i = 0; i < n; i++) { orig[i].chave = chave((unsigned long long)i, A, B); orig[i].idx = i; }

        /* ---- MergeSort ---- */
        for (int rec = 0; rec <= 1; rec++) {
            unsigned long long comp = 0; long prof = 0;
            for (int r = 0; r < reps; r++) {
                memcpy(v, orig, (size_t)n * sizeof(Item));
                metricas_zera();
                double t0 = agora_segundos();
                if (rec) mergesort_recursivo(v, n); else mergesort_iterativo(v, n);
                t[r] = agora_segundos() - t0;
                comp = g_comparacoes; prof = g_prof_max;
            }
            printf("%s;%ld;%d;%.9f;%llu;%ld\n", rec ? "mergesort_rec" : "mergesort_iter",
                   n, 0, mediana(t, reps), comp, prof);
            fflush(stdout);
        }

        /* ---- consultas: metade presentes, metade ausentes ---- */
        char **q = malloc((size_t)M * sizeof(char *));
        for (long j = 0; j < M; j++)
            q[j] = (j % 2 == 0) ? chave(aleatorio() % (unsigned long long)n, A, B)
                                : chave((unsigned long long)n + (unsigned long long)j, A, B);

        memcpy(v, orig, (size_t)n * sizeof(Item));
        mergesort_iterativo(v, n);             /* vetor ordenado p/ binária */

        const char *nomes[] = {"seq_iter", "seq_rec", "bin_iter", "bin_rec"};
        for (int alg = 0; alg < 4; alg++) {
            if (alg < 2 && n > n_max_seq) continue;
            const Item *base = (alg < 2) ? orig : v;
            unsigned long long comp = 0; long prof = 0; long achados = 0;
            for (int r = 0; r < reps; r++) {
                metricas_zera(); achados = 0;
                double t0 = agora_segundos();
                for (long j = 0; j < M; j++) {
                    long p;
                    switch (alg) {
                        case 0:  p = busca_sequencial_iterativa(base, n, q[j]); break;
                        case 1:  p = busca_sequencial_recursiva(base, n, q[j]); break;
                        case 2:  p = busca_binaria_iterativa(base, n, q[j]);    break;
                        default: p = busca_binaria_recursiva(base, n, q[j]);    break;
                    }
                    achados += (p >= 0);
                }
                t[r] = agora_segundos() - t0;
                comp = g_comparacoes; prof = g_prof_max;
            }
            if (achados != M / 2) fprintf(stderr, "ERRO: %s achou %ld de %ld\n", nomes[alg], achados, M / 2);
            printf("%s;%ld;%ld;%.9f;%llu;%ld\n", nomes[alg], n, M, mediana(t, reps), comp, prof);
            fflush(stdout);
        }

        for (long j = 0; j < M; j++) free(q[j]);
        free(q);
        for (long i = 0; i < n; i++) free(orig[i].chave);
        free(orig); free(v);
    }
    free(t);
    return 0;
}
