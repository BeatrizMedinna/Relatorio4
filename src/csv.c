#include "csv.h"

#include <stdlib.h>
#include <string.h>

char *csv_le_linha(FILE *f, int *teve_cr)
{
    size_t cap = 256, n = 0;
    char *buf = malloc(cap);
    int c, leu_algo = 0;

    if (!buf) return NULL;
    if (teve_cr) *teve_cr = 0;

    while ((c = fgetc(f)) != EOF) {
        leu_algo = 1;
        if (c == '\n') break;
        if (c == '\0') continue;           /* campos vazios em UTF-16 mal convertidos */
        if (n + 1 >= cap) {
            char *novo = realloc(buf, cap *= 2);
            if (!novo) { free(buf); return NULL; }
            buf = novo;
        }
        buf[n++] = (char)c;
    }
    if (!leu_algo) { free(buf); return NULL; }

    if (n > 0 && buf[n - 1] == '\r') {
        n--;
        if (teve_cr) *teve_cr = 1;
    }
    buf[n] = '\0';
    return buf;
}

void csv_remove_bom(char *linha)
{
    unsigned char *u = (unsigned char *)linha;
    if (u[0] == 0xEF && u[1] == 0xBB && u[2] == 0xBF)
        memmove(linha, linha + 3, strlen(linha + 3) + 1);
}

int csv_eh_utf16(const char *caminho)
{
    unsigned char b[2] = {0, 0};
    FILE *f = fopen(caminho, "rb");
    if (!f) return 0;
    size_t lidos = fread(b, 1, 2, f);
    fclose(f);
    return lidos == 2 && ((b[0] == 0xFF && b[1] == 0xFE) || (b[0] == 0xFE && b[1] == 0xFF));
}

int csv_conta_campos(const char *linha)
{
    int campos = 1, entre_aspas = 0;
    for (const char *p = linha; *p; p++) {
        if (*p == '"') entre_aspas = !entre_aspas;
        else if (*p == CSV_SEPARADOR && !entre_aspas) campos++;
    }
    return campos;
}

char *csv_extrai_campo(const char *linha, int coluna)
{
    const char *p = linha;
    int atual = 0;

    /* Avança até o início da coluna desejada, respeitando aspas. */
    while (atual < coluna) {
        int entre_aspas = 0;
        while (*p && (entre_aspas || *p != CSV_SEPARADOR)) {
            if (*p == '"') entre_aspas = !entre_aspas;
            p++;
        }
        if (!*p) return NULL;              /* a linha tem menos colunas */
        p++;                               /* pula o ';' */
        atual++;
    }

    size_t cap = strlen(p) + 1, n = 0;
    char *campo = malloc(cap);
    if (!campo) return NULL;

    if (*p == '"') {                       /* campo entre aspas: "" vira " */
        p++;
        while (*p) {
            if (*p == '"') {
                if (p[1] == '"') { campo[n++] = '"'; p += 2; continue; }
                break;
            }
            campo[n++] = *p++;
        }
    } else {
        while (*p && *p != CSV_SEPARADOR) campo[n++] = *p++;
    }
    campo[n] = '\0';

    /* Remove espaços nas pontas: " 010691/2026 " == "010691/2026". */
    size_t ini = 0;
    while (campo[ini] == ' ' || campo[ini] == '\t') ini++;
    while (n > ini && (campo[n - 1] == ' ' || campo[n - 1] == '\t')) n--;
    campo[n] = '\0';
    if (ini) memmove(campo, campo + ini, n - ini + 1);
    return campo;
}
