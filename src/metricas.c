#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include "metricas.h"

unsigned long long g_comparacoes = 0;
long g_prof_atual = 0;
long g_prof_max = 0;

void metricas_zera(void)
{
    g_comparacoes = 0;
    g_prof_atual = 0;
    g_prof_max = 0;
}

#ifdef _WIN32
#include <windows.h>
double agora_segundos(void)
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart / (double)f.QuadPart;
}
#else
#include <time.h>
double agora_segundos(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}
#endif
