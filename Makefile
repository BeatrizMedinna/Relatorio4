# Compilação:   make            (gera bin/insere e as ferramentas auxiliares)
# Base real:    make base       (converte o CSV do Inmetro e monta dados/base_andadores.csv)
# Testes:       make testes     (testes funcionais: os 6 métodos devem concordar)
# Experimentos: make experimentos (gera os dados sintéticos e mede os tempos)

CC      ?= gcc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -pedantic
SRC     = src/main.c src/csv.c src/busca.c src/ordenacao.c src/metricas.c
HDR     = src/csv.h src/busca.h src/ordenacao.h src/metricas.h

# A busca sequencial recursiva usa uma chamada por elemento (espaço O(n)).
# No Windows a pilha padrão é de só 1 MB, então pedimos 256 MB ao linker.
ifeq ($(OS),Windows_NT)
  LDFLAGS += -Wl,--stack,268435456
  EXE = .exe
endif

all: bin/insere$(EXE) bin/gera_dados$(EXE) bin/converte_utf16$(EXE) bin/bench_algoritmos$(EXE)

bin:
	mkdir -p bin

bin/insere$(EXE): $(SRC) $(HDR) | bin
	$(CC) $(CFLAGS) -o $@ $(SRC) $(LDFLAGS)

bin/gera_dados$(EXE): ferramentas/gera_dados.c | bin
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

bin/converte_utf16$(EXE): ferramentas/converte_utf16.c | bin
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

bin/bench_algoritmos$(EXE): ferramentas/bench_algoritmos.c src/busca.c src/ordenacao.c src/metricas.c $(HDR) | bin
	$(CC) $(CFLAGS) -o $@ ferramentas/bench_algoritmos.c src/busca.c src/ordenacao.c src/metricas.c $(LDFLAGS)

base: all
	./bin/converte_utf16 dados/original/ANDADORES_INFANTIS.csv dados/andadores_utf8.csv
	rm -f dados/base_andadores.csv
	./bin/insere dados/andadores_utf8.csv dados/base_andadores.csv -m seq-iter -v

testes: all
	bash testes/testes_funcionais.sh

experimentos: all
	bash testes/experimentos.sh

clean:
	rm -rf bin

.PHONY: all base testes experimentos clean
