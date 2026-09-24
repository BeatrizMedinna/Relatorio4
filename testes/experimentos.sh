#!/usr/bin/env bash
# Experimentos de desempenho. Uso: bash testes/experimentos.sh [repeticoes]
#
#  Exp. 1 - programa completo, m = 1000 novos fixos, destino n variando
#  Exp. 2 - programa completo, destino n = 50 000 fixo, m variando
#  Exp. 3 - algoritmos isolados em memória, n até 10^6 (bench_algoritmos)
#
# Os arquivos de entrada ficam em dados/experimentos/ (gerados com semente
# fixa, portanto reprodutíveis). Os resultados vão para resultados/*.csv.
set -eu
cd "$(dirname "$0")/.."
REPS=${1:-5}
# Linux aceita "unlimited"; no macOS o máximo é o limite "hard" (64 MB)
ulimit -s unlimited 2>/dev/null || ulimit -s hard 2>/dev/null || true

BASE=dados/andadores_utf8.csv
DIR=dados/experimentos
mkdir -p "$DIR" resultados
METODOS="seq-iter seq-rec bin-iter-iter bin-iter-rec bin-rec-iter bin-rec-rec"
SEMENTE=2026
PCT_DUP_DEST=50      # metade dos novos já existe no destino
PCT_DUP_LOTE=5       # 5% repetem uma chave anterior do próprio lote

cabecalho="metodo;n;m;t_carga;t_ordenacao;t_verificacao;t_gravacao;comp_ordenacao;comp_ordenacao_destino;comp_busca;prof_ordenacao;prof_busca"

mede() {  # mede <novos> <destino> <saida.csv>
    for m in $METODOS; do
        for r in $(seq "$REPS"); do
            ./bin/insere "$1" "$2" -m "$m" -s -t 2>&1 >/dev/null | grep '^METRICAS' | cut -d';' -f2- >> "$3"
        done
    done
}

echo "== Exp. 1: m = 1000, n variando =="
echo "$cabecalho" > resultados/exp1_bruto.csv
for n in 1000 2000 5000 10000 20000 50000; do
    d="$DIR/destino_n${n}.csv"; o="$DIR/novos_n${n}_m1000.csv"
    [ -f "$d" ] && [ -f "$o" ] || ./bin/gera_dados $BASE $n 1000 $PCT_DUP_DEST $PCT_DUP_LOTE $SEMENTE "$d" "$o"
    echo "  n=$n"; mede "$o" "$d" resultados/exp1_bruto.csv
done

echo "== Exp. 2: n = 50000, m variando =="
echo "$cabecalho" > resultados/exp2_bruto.csv
d="$DIR/destino_n50000.csv"
for m in 1 2 5 10 20 50 100 200 500 1000 2000 5000; do
    o="$DIR/novos_n50000_m${m}.csv"
    if [ ! -f "$o" ]; then
        # mesma semente e mesmo n => o destino gerado é idêntico ao do Exp. 1
        ./bin/gera_dados $BASE 50000 $m $PCT_DUP_DEST $PCT_DUP_LOTE $SEMENTE /tmp/_dest_descartavel.csv "$o"
        cmp -s /tmp/_dest_descartavel.csv "$d" || { echo "destino divergente!"; exit 1; }
        rm -f /tmp/_dest_descartavel.csv
    fi
    echo "  m=$m"; mede "$o" "$d" resultados/exp2_bruto.csv
done

echo "== Exp. 3: algoritmos isolados em memória =="
./bin/bench_algoritmos "$REPS" 200000 > resultados/exp3_algoritmos.csv

echo "Pronto. Resultados em resultados/"
