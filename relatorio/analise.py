"""
analise.py - resume os resultados brutos (mediana das repetições), calcula os
valores teóricos e gera os gráficos usados no relatório.

Uso (na raiz do repositório):  python3 relatorio/analise.py
Requer: pandas, matplotlib
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
FIG = os.path.join(RAIZ, "relatorio", "figuras")
DADOS = os.path.join(RAIZ, "dados", "experimentos")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight"})

ROTULO = {
    "seq-iter": "Sol. 1 – seq. iterativa", "seq-rec": "Sol. 1 – seq. recursiva",
    "bin-iter-iter": "Sol. 2 – MS iter + BB iter", "bin-iter-rec": "Sol. 2 – MS iter + BB rec",
    "bin-rec-iter": "Sol. 2 – MS rec + BB iter", "bin-rec-rec": "Sol. 2 – MS rec + BB rec",
}
ESTILO = {
    "seq-iter": ("tab:red", "o", "-"), "seq-rec": ("tab:orange", "s", "--"),
    "bin-iter-iter": ("tab:blue", "^", "-"), "bin-iter-rec": ("tab:cyan", "v", "--"),
    "bin-rec-iter": ("tab:green", "D", "-"), "bin-rec-rec": ("olive", "x", "--"),
}


def resume(arquivo):
    d = pd.read_csv(os.path.join(RES, arquivo), sep=";")
    d["t_busca"] = d.t_verificacao - d.t_ordenacao
    return d.groupby(["metodo", "n", "m"]).median(numeric_only=True).reset_index()


def categorias(novos, destino):
    """Conta, no arquivo de novos, quantos registros caem em cada categoria."""
    chaves_dest = set()
    with open(destino, encoding="utf-8") as f:
        next(f)
        for linha in f:
            chaves_dest.add(linha.split(";", 1)[0].strip())
    vistos, D, L, A = set(), 0, 0, 0
    with open(novos, encoding="utf-8") as f:
        next(f)
        for linha in f:
            k = linha.split(";", 1)[0].strip()
            if k in chaves_dest: D += 1
            elif k in vistos:    L += 1
            else:                A += 1; vistos.add(k)
    return D, L, A


def modelo_seq(n, D, L, A):
    """Comparações esperadas da Solução 1:
       duplicado no destino -> em média (n+1)/2;
       inédito -> n + k (k = aceitos até então; em média A/2);
       repetido no lote -> em média n + A/2."""
    return D * (n + 1) / 2 + (A + L) * (n + A / 2)


def ms_pior(n):          # pior caso do MergeSort top-down
    c = math.ceil(math.log2(n))
    return n * c - 2 ** c + 1


def ms_medio(n):         # aproximação do caso médio (Knuth): n lg n - 1,26 n
    return n * math.log2(n) - 1.2645 * n


def main():
    e1, e2 = resume("exp1_bruto.csv"), resume("exp2_bruto.csv")
    e3 = pd.read_csv(os.path.join(RES, "exp3_algoritmos.csv"), sep=";")

    # ---------- Tabela: comparações da Sol. 1 (teoria x prática) ----------
    linhas = []
    for n in sorted(e1.n.unique()):
        D, L, A = categorias(os.path.join(DADOS, f"novos_n{n}_m1000.csv"),
                             os.path.join(DADOS, f"destino_n{n}.csv"))
        obs = int(e1[(e1.metodo == "seq-iter") & (e1.n == n)].comp_busca.iloc[0])
        mod = modelo_seq(n, D, L, A)
        linhas.append(dict(n=n, D=D, L=L, A=A, observado=obs, modelo=round(mod),
                           erro_pct=100 * (obs - mod) / mod))
    pd.DataFrame(linhas).to_csv(os.path.join(RES, "resumo_comparacoes_seq.csv"), sep=";", index=False)

    # ---------- Tabela: MergeSort teoria x prática ----------
    ms = e3[e3.algoritmo.str.startswith("mergesort")].pivot(index="n", columns="algoritmo",
                                                              values=["comparacoes", "tempo_mediano_s", "profundidade_max"])
    ms.columns = [f"{a}_{b}" for a, b in ms.columns]
    ms = ms.reset_index()
    ms["pior_top_down"] = ms.n.apply(ms_pior)
    ms["medio_aprox"] = ms.n.apply(ms_medio).round()
    ms["prof_teorica"] = ms.n.apply(lambda n: math.ceil(math.log2(n)) + 1)
    ms["razao_tempo_rec_iter"] = ms.tempo_mediano_s_mergesort_rec / ms.tempo_mediano_s_mergesort_iter
    ms["ns_por_nlgn_iter"] = 1e9 * ms.tempo_mediano_s_mergesort_iter / (ms.n * ms.n.apply(math.log2))
    ms["ns_por_nlgn_rec"] = 1e9 * ms.tempo_mediano_s_mergesort_rec / (ms.n * ms.n.apply(math.log2))
    ms.to_csv(os.path.join(RES, "resumo_mergesort.csv"), sep=";", index=False)

    # ---------- Tabela: buscas teoria x prática ----------
    bs = e3[~e3.algoritmo.str.startswith("mergesort")].copy()
    bs["comp_por_consulta"] = bs.comparacoes / bs.m
    bs["teorico_por_consulta"] = bs.apply(
        lambda r: (0.5 * (r.n + 1) / 2 + 0.5 * r.n) if r.algoritmo.startswith("seq")
        else 0.5 * (math.floor(math.log2(r.n)) + 1) + 0.5 * (math.log2(r.n) - 1), axis=1)
    bs["us_por_consulta"] = 1e6 * bs.tempo_mediano_s / bs.m
    bs.to_csv(os.path.join(RES, "resumo_buscas.csv"), sep=";", index=False)

    e1.to_csv(os.path.join(RES, "exp1_resumo.csv"), sep=";", index=False)
    e2.to_csv(os.path.join(RES, "exp2_resumo.csv"), sep=";", index=False)

    # ======================= GRÁFICOS =======================
    # Fig 1 - Exp1: tempo de verificação x n
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for met in ROTULO:
        d = e1[e1.metodo == met]
        c, mk, ls = ESTILO[met]
        ax.plot(d.n, d.t_verificacao * 1000, marker=mk, ls=ls, color=c, label=ROTULO[met], ms=5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("n (registros no destino)"); ax.set_ylabel("tempo de verificação (ms)")
    ax.set_title("Exp. 1 – verificação de duplicidade, m = 1000 novos")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig1_exp1_tempo.png")); plt.close(fig)

    # Fig 2 - Exp1: decomposição do tempo total (carga, verificação) para n = 50000
    fig, ax = plt.subplots(figsize=(7, 3.6))
    d = e1[e1.n == e1.n.max()].set_index("metodo").loc[list(ROTULO)]
    y = range(len(d))
    ax.barh(y, d.t_carga * 1000, color="lightgray", label="leitura dos CSV (comum)")
    ax.barh(y, d.t_ordenacao * 1000, left=d.t_carga * 1000, color="tab:blue", label="ordenação (MergeSort)")
    ax.barh(y, d.t_busca * 1000, left=(d.t_carga + d.t_ordenacao) * 1000, color="tab:red", label="buscas")
    ax.set_yticks(list(y)); ax.set_yticklabels([ROTULO[m] for m in d.index], fontsize=8)
    ax.invert_yaxis(); ax.set_xlabel("tempo (ms)")
    ax.set_title(f"Exp. 1 – composição do tempo, n = {int(e1.n.max())}, m = 1000")
    ax.legend(fontsize=8, loc="lower right")
    fig.savefig(os.path.join(FIG, "fig2_exp1_composicao.png")); plt.close(fig)

    # Fig 3 - Exp2: tempo x m, n = 50000
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    for met in ["seq-iter", "seq-rec", "bin-iter-iter", "bin-rec-iter"]:
        d = e2[e2.metodo == met]
        c, mk, ls = ESTILO[met]
        ax1.plot(d.m, d.t_verificacao * 1000, marker=mk, ls=ls, color=c, label=ROTULO[met], ms=5)
        comp = d.comp_ordenacao + d.comp_busca
        ax2.plot(d.m, comp, marker=mk, ls=ls, color=c, label=ROTULO[met], ms=5)
    for ax in (ax1, ax2):
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("m (registros novos)")
    ax1.set_ylabel("tempo de verificação (ms)"); ax1.set_title("Exp. 2 – tempo, n = 50 000")
    ax2.set_ylabel("comparações de chaves"); ax2.set_title("Exp. 2 – comparações, n = 50 000")
    ax1.legend(fontsize=7)
    fig.savefig(os.path.join(FIG, "fig3_exp2_cruzamento.png")); plt.close(fig)

    # Fig 4 - Exp3: MergeSort iter x rec
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(ms.n, ms.tempo_mediano_s_mergesort_iter * 1000, "o-", color="tab:blue", label="MergeSort iterativo")
    ax1.plot(ms.n, ms.tempo_mediano_s_mergesort_rec * 1000, "D--", color="tab:green", label="MergeSort recursivo")
    ax1.set_xscale("log"); ax1.set_yscale("log"); ax1.set_xlabel("n"); ax1.set_ylabel("tempo (ms)")
    ax1.set_title("Exp. 3 – tempo de ordenação"); ax1.legend(fontsize=8)
    ax2.plot(ms.n, ms.ns_por_nlgn_iter, "o-", color="tab:blue", label="iterativo")
    ax2.plot(ms.n, ms.ns_por_nlgn_rec, "D--", color="tab:green", label="recursivo")
    ax2.set_xscale("log"); ax2.set_xlabel("n"); ax2.set_ylabel("tempo / (n·log₂ n)  [ns]")
    ax2.set_ylim(bottom=0); ax2.set_title("Tempo normalizado por n·log₂ n"); ax2.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig4_exp3_mergesort.png")); plt.close(fig)

    # Fig 5 - Exp3: buscas
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    cores = {"seq_iter": ("tab:red", "o-"), "seq_rec": ("tab:orange", "s--"),
             "bin_iter": ("tab:blue", "^-"), "bin_rec": ("tab:cyan", "v--")}
    nomes = {"seq_iter": "sequencial iterativa", "seq_rec": "sequencial recursiva",
             "bin_iter": "binária iterativa", "bin_rec": "binária recursiva"}
    for alg, (c, st) in cores.items():
        d = bs[bs.algoritmo == alg]
        ax1.plot(d.n, d.us_por_consulta, st, color=c, label=nomes[alg], ms=5)
        ax2.plot(d.n, d.comp_por_consulta, st, color=c, label=nomes[alg], ms=5)
    for ax in (ax1, ax2):
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("n")
    ax1.set_ylabel("tempo por consulta (µs)"); ax1.set_title("Exp. 3 – tempo por busca")
    ax2.set_ylabel("comparações por consulta"); ax2.set_title("Exp. 3 – comparações por busca")
    ax1.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig5_exp3_buscas.png")); plt.close(fig)

    # Fig 6 - profundidade de recursão
    fig, ax = plt.subplots(figsize=(7, 4))
    d = bs[bs.algoritmo == "seq_rec"]
    ax.plot(d.n, d.profundidade_max, "s--", color="tab:orange", label="busca sequencial recursiva (≈ n)")
    ax.plot(ms.n, ms.profundidade_max_mergesort_rec, "D--", color="tab:green", label="MergeSort recursivo (⌈log₂ n⌉ + 1)")
    d = bs[bs.algoritmo == "bin_rec"]
    ax.plot(d.n, d.profundidade_max, "v--", color="tab:cyan", label="busca binária recursiva (⌊log₂ n⌋ + 2)")
    ax.axhline(174762, color="k", lw=0.8, ls=":")
    ax.text(1100, 200000, "limite de 8 MiB com 48 B/chamada (Linux x86-64) ≈ 174 762", fontsize=8)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("n"); ax.set_ylabel("profundidade máxima da pilha")
    ax.set_title("Espaço de pilha medido (Exp. 3)"); ax.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig6_profundidade.png")); plt.close(fig)

    print("Resumos em resultados/ e figuras em relatorio/figuras/")


if __name__ == "__main__":
    main()
    