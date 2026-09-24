/*
 * csv.h - Leitura de linhas e extração de campos de arquivos CSV
 *         separados por ';' (padrão do Portal de Dados Abertos / Inmetro).
 */
#ifndef CSV_H
#define CSV_H

#include <stdio.h>
#include <stddef.h>

#define CSV_SEPARADOR ';'

/* Um elemento do vetor de chaves. 'idx' guarda a posição original do
 * registro (usado para desempate estável e para relatar a linha). */
typedef struct {
    char *chave;
    long  idx;
} Item;

/* Lê uma linha inteira (qualquer tamanho). Remove '\n' e '\r' do final e
 * descarta bytes nulos. Retorna string alocada com malloc ou NULL no EOF.
 * Se 'teve_cr' não for NULL, informa se a linha terminava em "\r\n". */
char *csv_le_linha(FILE *f, int *teve_cr);

/* Retorna uma cópia (malloc) do campo de índice 'coluna' da linha,
 * sem aspas e sem espaços nas pontas. Retorna NULL se a coluna não existir. */
char *csv_extrai_campo(const char *linha, int coluna);

/* Conta quantos campos a linha possui. */
int csv_conta_campos(const char *linha);

/* Remove o BOM UTF-8 (EF BB BF) do início da string, se existir. */
void csv_remove_bom(char *linha);

/* Detecta arquivo UTF-16 (BOM FF FE ou FE FF). Retorna 1 se for UTF-16. */
int csv_eh_utf16(const char *caminho);

#endif
