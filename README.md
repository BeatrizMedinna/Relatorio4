# Inserção sem duplicidade em CSV — busca sequencial × MergeSort + busca binária

**Análise de Algoritmos** — Prof. Zoe Roberto Magalhães Junior

Integrantes: Caroline Zaiatz (UC24101689), Beatriz Nascimento Costa Medina (UC24101412),
Eloisa Sousa de Jesus (UC23100484)

Programa em C que insere, ao final de um arquivo CSV de destino, os registros de
outro CSV, **sem permitir valores repetidos na coluna-chave**. A verificação de
duplicidade é feita de duas formas, cada uma em versão iterativa e recursiva:

| Solução | Verificação | Complexidade de tempo | Espaço extra do algoritmo |
|---|---|---|---|
| 1 | busca sequencial iterativa | Θ(m·n + m²) | O(1) |
| 1 | busca sequencial recursiva | Θ(m·n + m²) | Θ(n + m) (pilha) |
| 2 | MergeSort iterativo/recursivo + busca binária iterativa/recursiva | Θ(n log n + m log m + m log n) | Θ(n + m) (vetor auxiliar) + O(log n) de pilha nas recursivas |

*n* = registros já existentes no destino, *m* = registros novos.

## Base de dados

- **Fonte:** Portal de Dados Abertos — conjunto *Registro de Objetos* (Inmetro),
  <https://dados.gov.br/dados/conjuntos-dados/registro-de-objetos>, arquivo do
  programa de avaliação da conformidade *Andadores Infantis*.
- **Arquivo original:** `dados/original/ANDADORES_INFANTIS.csv`
  (UTF-16 LE com BOM, separador `;`, quebras CRLF, 93 linhas, 32 colunas).
- **Coluna-chave:** `NumeroRegistro` (coluna 0), no formato `NNNNNN/AAAA`,
  fora de ordem no arquivo.
- O arquivo publicado repete o `NumeroRegistro` em 18 linhas (histórico de itens
  do mesmo registro). A base de destino `dados/base_andadores.csv` (75 registros,
  chave única) foi construída **pelo próprio programa** — veja `make base`.

## Estrutura

```
src/                  código do programa principal (insere)
  main.c              leitura dos argumentos, fluxo das duas soluções, gravação
  csv.c / csv.h       leitura de linhas e extração de campos (aspas, BOM, CRLF)
  busca.c / busca.h   busca sequencial e binária, iterativas e recursivas
  ordenacao.c / .h    MergeSort recursivo (top-down) e iterativo (bottom-up)
  metricas.c / .h     contadores de comparações/profundidade e relógio
ferramentas/
  converte_utf16.c    converte o CSV original (UTF-16) para UTF-8
  gera_dados.c        gera arquivos sintéticos (destino/novos) para os experimentos
  bench_algoritmos.c  mede os algoritmos isolados em memória (n até 10^6)
dados/
  original/           arquivo baixado do portal, sem alterações
  andadores_utf8.csv  o mesmo arquivo convertido para UTF-8
  base_andadores.csv  destino com chave única (75 registros)
  novos_exemplo.csv   12 registros de teste (inéditos, repetidos, chave vazia...)
  experimentos/       arquivos usados nos experimentos 1 e 2
testes/
  testes_funcionais.sh  confere se os 6 métodos produzem o mesmo resultado
  experimentos.sh       mede os tempos (gera resultados/*.csv)
resultados/           medições brutas e resumos
relatorio/            scripts de análise/gráficos e o relatório em PDF
```

## Compilação

Requisitos: GCC (ou Clang) com suporte a C11 e `make`.

```bash
make            # gera bin/insere, bin/converte_utf16, bin/gera_dados, bin/bench_algoritmos
```

Sem `make`:

```bash
gcc -std=c11 -O2 -Wall -o insere src/main.c src/csv.c src/busca.c src/ordenacao.c src/metricas.c
```

No **Windows (MinGW)**, acrescente `-Wl,--stack,268435456` — a busca sequencial
recursiva usa uma chamada por registro e a pilha padrão do Windows é de só 1 MB
(o Makefile já faz isso automaticamente).

## Execução

```bash
./bin/insere <novos.csv> <destino.csv> [-m metodo] [-k coluna] [-v] [-s] [-t]
```

| Opção | Significado |
|---|---|
| `-m seq-iter` | Solução 1, busca sequencial iterativa |
| `-m seq-rec` | Solução 1, busca sequencial recursiva |
| `-m bin-iter-iter` | Solução 2, MergeSort iterativo + busca binária iterativa |
| `-m bin-iter-rec` | Solução 2, MergeSort iterativo + busca binária recursiva |
| `-m bin-rec-iter` | Solução 2, MergeSort recursivo + busca binária iterativa (**padrão**) |
| `-m bin-rec-rec` | Solução 2, MergeSort recursivo + busca binária recursiva |
| `-k N` | coluna-chave (base 0). Padrão: 0 (`NumeroRegistro`) |
| `-v` | lista cada registro rejeitado e o motivo |
| `-s` | simulação: verifica tudo, mas não grava |
| `-t` | imprime métricas (tempos, comparações, profundidade) em stderr |

Exemplo:

```bash
cp dados/base_andadores.csv /tmp/destino.csv
./bin/insere dados/novos_exemplo.csv /tmp/destino.csv -m seq-iter -v
```

Saída:

```
REJEITADO linha 6 [010693/2026]: chave já existe no destino
REJEITADO linha 7 [004675/2023]: chave já existe no destino
REJEITADO linha 8 [010691/2026]: chave já existe no destino
REJEITADO linha 9 [012001/2026]: chave repetida no próprio arquivo de novos
REJEITADO linha 10 []: chave vazia ou coluna ausente
REJEITADO linha 12 [007777/2025]: chave repetida no próprio arquivo de novos
Método: seq-iter | coluna-chave: 0
Registros no destino: 75 | registros lidos: 12
Inseridos: 6
Rejeitados: 6 (já no destino: 3 | repetidos no lote: 2 | chave inválida: 1)
```

Regras adotadas:

- a primeira linha de cada arquivo é o cabeçalho e nunca é inserida;
- se o destino não existir, ele é criado com o cabeçalho do arquivo de novos;
- a chave é comparada sem espaços nas pontas (`" 010691/2026 "` = `"010691/2026"`);
- também é rejeitado o registro que repete uma chave **já aceita do mesmo lote**
  (sem isso, o próprio lote poderia introduzir duplicatas);
- os aceitos são gravados ao final do destino, na ordem original, preservando o
  tipo de quebra de linha do destino (LF ou CRLF).

## Reproduzindo tudo

```bash
make base           # converte o CSV do Inmetro e recria dados/base_andadores.csv
make testes         # testes funcionais (os 6 métodos devem concordar)
make experimentos   # ~3 min; grava resultados/exp1_bruto.csv, exp2_bruto.csv, exp3_algoritmos.csv
python3 relatorio/analise.py         # resumos + gráficos (pandas, matplotlib)
python3 relatorio/gera_relatorio.py  # relatório PDF (reportlab)
```

Os tempos dependem da máquina; comparações e profundidades de recursão são
determinísticas (os geradores usam semente fixa).
