/*
 * converte_utf16 - converte o CSV original do Inmetro (UTF-16 LE com BOM,
 * quebras CRLF e campos vazios preenchidos com o caractere NUL) para
 * UTF-8 com quebras LF e campos vazios de verdade.
 *
 * Uso: converte_utf16 <entrada_utf16.csv> <saida_utf8.csv>
 */
#include <stdio.h>
#include <stdlib.h>

static void grava_utf8(FILE *o, unsigned long cp)
{
    if (cp < 0x80) fputc((int)cp, o);
    else if (cp < 0x800) {
        fputc(0xC0 | (int)(cp >> 6), o);
        fputc(0x80 | (int)(cp & 0x3F), o);
    } else if (cp < 0x10000) {
        fputc(0xE0 | (int)(cp >> 12), o);
        fputc(0x80 | (int)((cp >> 6) & 0x3F), o);
        fputc(0x80 | (int)(cp & 0x3F), o);
    } else {
        fputc(0xF0 | (int)(cp >> 18), o);
        fputc(0x80 | (int)((cp >> 12) & 0x3F), o);
        fputc(0x80 | (int)((cp >> 6) & 0x3F), o);
        fputc(0x80 | (int)(cp & 0x3F), o);
    }
}

static int le_u16(FILE *f, int big_endian, unsigned *u)
{
    int a = fgetc(f), b = fgetc(f);
    if (a == EOF || b == EOF) return 0;
    *u = big_endian ? (unsigned)((a << 8) | b) : (unsigned)((b << 8) | a);
    return 1;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "Uso: %s <entrada_utf16.csv> <saida_utf8.csv>\n", argv[0]);
        return 1;
    }
    FILE *f = fopen(argv[1], "rb"), *o = fopen(argv[2], "wb");
    if (!f || !o) { perror("fopen"); return 1; }

    int a = fgetc(f), b = fgetc(f), be;
    if (a == 0xFF && b == 0xFE) be = 0;
    else if (a == 0xFE && b == 0xFF) be = 1;
    else { fprintf(stderr, "erro: o arquivo não começa com BOM UTF-16\n"); return 1; }

    unsigned u, u2;
    while (le_u16(f, be, &u)) {
        unsigned long cp = u;
        if (u >= 0xD800 && u <= 0xDBFF && le_u16(f, be, &u2))   /* par substituto */
            cp = 0x10000 + (((unsigned long)u - 0xD800) << 10) + (u2 - 0xDC00);
        if (cp == 0 || cp == '\r') continue;                    /* NUL e CR */
        grava_utf8(o, cp);
    }
    fclose(f);
    fclose(o);
    return 0;
}
