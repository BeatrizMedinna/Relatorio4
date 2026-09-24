#!/usr/bin/env bash
# Testes funcionais: os 6 métodos precisam produzir EXATAMENTE o mesmo arquivo
# de destino e os mesmos contadores. Uso: bash testes/testes_funcionais.sh
set -u
cd "$(dirname "$0")/.."
BIN=./bin/insere
TMP=$(mktemp -d)
METODOS="seq-iter seq-rec bin-iter-iter bin-iter-rec bin-rec-iter bin-rec-rec"
falhas=0

confere() {  # confere <descrição> <esperado> <obtido>
    if [ "$2" == "$3" ]; then echo "  ok   - $1"
    else echo "  FALHA - $1 (esperado: $2 | obtido: $3)"; falhas=$((falhas+1)); fi
}

echo "Teste 1: novos_exemplo.csv sobre base_andadores.csv (75 registros)"
ref=""
for m in $METODOS; do
    cp dados/base_andadores.csv "$TMP/d.csv"
    saida=$($BIN dados/novos_exemplo.csv "$TMP/d.csv" -m "$m")
    confere "$m: 6 inseridos"  "Inseridos: 6" "$(echo "$saida" | grep '^Inseridos')"
    confere "$m: 3 no destino, 2 no lote, 1 inválida" \
        "Rejeitados: 6 (já no destino: 3 | repetidos no lote: 2 | chave inválida: 1)" \
        "$(echo "$saida" | grep '^Rejeitados')"
    confere "$m: destino com 82 linhas (76 + 6)" "82" "$(wc -l < "$TMP/d.csv" | tr -d ' ')"
    h=$(cksum < "$TMP/d.csv")
    [ -z "$ref" ] && ref=$h
    confere "$m: arquivo idêntico ao dos outros métodos" "$ref" "$h"
    saida=$($BIN dados/novos_exemplo.csv "$TMP/d.csv" -m "$m")
    confere "$m: 2ª execução não insere nada" "Inseridos: 0" "$(echo "$saida" | grep '^Inseridos')"
done

echo "Teste 2: construção da base a partir do CSV real (destino inexistente)"
for m in $METODOS; do
    rm -f "$TMP/b.csv"
    $BIN dados/andadores_utf8.csv "$TMP/b.csv" -m "$m" > /dev/null
    confere "$m: base igual a dados/base_andadores.csv" \
        "$(cksum < dados/base_andadores.csv)" "$(cksum < "$TMP/b.csv")"
done

echo "Teste 3: chaves do destino são únicas após as inserções"
dups=$(cut -d';' -f1 "$TMP/d.csv" | tail -n +2 | sort | uniq -d | wc -l | tr -d ' ')
confere "nenhuma chave duplicada" "0" "$dups"

echo "Teste 4: dados sintéticos (n=5000, m=2000, 30% dup destino, 10% dup lote)"
./bin/gera_dados dados/andadores_utf8.csv 5000 2000 30 10 7 "$TMP/sd.csv" "$TMP/sn.csv"
ref=""; ref_resumo=""
for m in $METODOS; do
    cp "$TMP/sd.csv" "$TMP/x.csv"
    resumo=$($BIN "$TMP/sn.csv" "$TMP/x.csv" -m "$m" | grep '^Rejeitados')
    h=$(cksum < "$TMP/x.csv"); [ -z "$ref" ] && ref=$h && ref_resumo=$resumo
    confere "$m: resultado idêntico" "$ref" "$h"
    confere "$m: mesmos motivos de rejeição" "$ref_resumo" "$resumo"
done
dups=$(cut -d';' -f1 "$TMP/x.csv" | tail -n +2 | sort | uniq -d | wc -l | tr -d ' ')
confere "sintético: nenhuma chave duplicada no destino" "0" "$dups"

rm -rf "$TMP"
echo
if [ $falhas -eq 0 ]; then echo "TODOS OS TESTES PASSARAM"; else echo "$falhas FALHA(S)"; exit 1; fi
