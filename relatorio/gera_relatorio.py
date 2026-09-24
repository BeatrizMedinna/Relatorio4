"""
gera_relatorio.py - monta o relatório em PDF a partir dos resultados.
Uso (na raiz do repositório):  python3 relatorio/analise.py && python3 relatorio/gera_relatorio.py
Requer: pandas, reportlab
"""
import math
import os

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

# ------------------------------------------------------------------ dados do trabalho
DISCIPLINA = "Análise de Algoritmos"
INTEGRANTES = ("Caroline Zaiatz – UC24101689<br/>Beatriz Nascimento Costa Medina – UC24101412<br/>"
               "Eloisa Sousa de Jesus – UC23100484")
PROFESSOR = "Zoe Roberto Magalhães Junior"
REPOSITORIO = "https://github.com/BeatrizMedinna/Relatorio4"
LINK_DADOS = "https://dados.gov.br/dados/conjuntos-dados/registro-de-objetos"

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
FIG = os.path.join(RAIZ, "relatorio", "figuras")
SAIDA = os.path.join(RAIZ, "relatorio", "relatorio.pdf")

# Fontes DejaVu: usa as do sistema (Linux) ou, se não existirem (macOS/Windows),
# as que já vêm dentro do matplotlib.
FD = "/usr/share/fonts/truetype/dejavu/"
if not os.path.exists(FD + "DejaVuSerif.ttf"):
    import matplotlib
    FD = os.path.join(matplotlib.get_data_path(), "fonts", "ttf") + os.sep
pdfmetrics.registerFont(TTFont("Serif", FD + "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", FD + "DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I", FD + "DejaVuSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BI", FD + "DejaVuSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Sans", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-B", italic="Serif-I", boldItalic="Serif-BI")

AZUL = colors.HexColor("#1f3b63")
st_corpo = ParagraphStyle("corpo", fontName="Serif", fontSize=10, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=6)
st_h1 = ParagraphStyle("h1", fontName="Sans-B", fontSize=14, leading=18, textColor=AZUL, spaceBefore=10, spaceAfter=6)
st_h2 = ParagraphStyle("h2", fontName="Sans-B", fontSize=11.5, leading=15, textColor=AZUL, spaceBefore=8, spaceAfter=4)
st_eq = ParagraphStyle("eq", fontName="Serif", fontSize=10.5, leading=15, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
st_leg = ParagraphStyle("leg", fontName="Serif-I", fontSize=8.8, leading=11, alignment=TA_CENTER, spaceAfter=10)
st_cod = ParagraphStyle("cod", fontName="Mono", fontSize=7.8, leading=9.6, backColor=colors.HexColor("#f4f6f9"),
                        borderPadding=5, leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=10)
st_cel = ParagraphStyle("cel", fontName="Serif", fontSize=8.3, leading=10.4)
st_celb = ParagraphStyle("celb", fontName="Sans-B", fontSize=8.3, leading=10.4, textColor=colors.white)
st_marc = ParagraphStyle("marc", parent=st_corpo, leftIndent=14, bulletIndent=4, spaceAfter=3)

H = []  # "história" do documento


def p(t): H.append(Paragraph(t, st_corpo))
def h1(t): H.append(Paragraph(t, st_h1))
def h2(t): H.append(Paragraph(t, st_h2))
def eq(t): H.append(Paragraph(t, st_eq))
def cod(t): H.append(Preformatted(t.strip("\n"), st_cod))
def item(t): H.append(Paragraph(t, st_marc, bulletText="•"))


def fig(nome, largura, legenda):
    caminho = os.path.join(FIG, nome)
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(caminho).getSize()
    H.append(KeepTogether([Image(caminho, width=largura, height=largura * h / w),
                           Paragraph(legenda, st_leg)]))


st_cel_p = ParagraphStyle("celp", parent=st_cel, fontSize=7.2, leading=9)
st_celb_p = ParagraphStyle("celbp", parent=st_celb, fontSize=7.2, leading=9)


def tab(linhas, larguras, legenda, pequeno=False):
    cb, cc = (st_celb_p, st_cel_p) if pequeno else (st_celb, st_cel)
    dados = [[Paragraph(str(c), cb) for c in linhas[0]]] + \
            [[Paragraph(str(c), cc) for c in l] for l in linhas[1:]]
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2f7")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c2cf")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 if pequeno else 6), ("RIGHTPADDING", (0, 0), (-1, -1), 3 if pequeno else 6),
    ]))
    H.append(KeepTogether([t, Paragraph(legenda, st_leg)]))


def fmt(x, casas=0):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def ms(x): return fmt(x * 1000, 2)


# ------------------------------------------------------------------ carrega resultados
e1 = pd.read_csv(os.path.join(RES, "exp1_resumo.csv"), sep=";")
e2 = pd.read_csv(os.path.join(RES, "exp2_resumo.csv"), sep=";")
cs = pd.read_csv(os.path.join(RES, "resumo_comparacoes_seq.csv"), sep=";")
rm = pd.read_csv(os.path.join(RES, "resumo_mergesort.csv"), sep=";")
rb = pd.read_csv(os.path.join(RES, "resumo_buscas.csv"), sep=";")


def v1(met, n, col): return float(e1[(e1.metodo == met) & (e1.n == n)][col].iloc[0])
def v2(met, m, col): return float(e2[(e2.metodo == met) & (e2.m == m)][col].iloc[0])
def vb(alg, n, col): return float(rb[(rb.algoritmo == alg) & (rb.n == n)][col].iloc[0])


def memoria_gb():
    """RAM da máquina em GB (macOS via sysctl; Linux via sysconf)."""
    try:
        import subprocess
        b = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True, stderr=subprocess.DEVNULL).strip())
        return round(b / 1024 ** 3)
    except Exception:
        try:
            return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024 ** 3)
        except Exception:
            return None


RAM = memoria_gb()
AMBIENTE = ("MacBook Air com processador Apple M2" + (f", {RAM} GB de RAM" if RAM else "") +
            ", macOS 15.6.1, Apple Clang 16.0.0")

NMAX = int(e1.n.max())
NMIN = int(e1.n.min())
BIN = ["bin-iter-iter", "bin-iter-rec", "bin-rec-iter", "bin-rec-rec"]


def inclinacao(met, col="t_verificacao"):
    a, b = v1(met, NMIN, col), v1(met, NMAX, col)
    return math.log(b / a) / math.log(NMAX / NMIN)


# ================================================================== CAPA
H.append(Spacer(1, 3.2 * cm))
H.append(Paragraph(DISCIPLINA, ParagraphStyle("c0", fontName="Sans", fontSize=11, alignment=TA_CENTER, textColor=colors.grey)))
H.append(Spacer(1, 1.2 * cm))
H.append(Paragraph("Inserção sem duplicidade em arquivos CSV",
                   ParagraphStyle("c1", fontName="Sans-B", fontSize=21, leading=26, alignment=TA_CENTER, textColor=AZUL)))
H.append(Spacer(1, 0.4 * cm))
H.append(Paragraph("Busca sequencial × MergeSort com busca binária — versões iterativas e recursivas: "
                   "análise de complexidade e verificação experimental",
                   ParagraphStyle("c2", fontName="Serif", fontSize=12.5, leading=17, alignment=TA_CENTER)))
H.append(Spacer(1, 1.6 * cm))
H.append(Paragraph(f"Base de dados: registros de objeto do Inmetro — <i>Andadores Infantis</i> "
                   f"(Portal de Dados Abertos, dados.gov.br)",
                   ParagraphStyle("c3", fontName="Serif", fontSize=10.5, alignment=TA_CENTER)))
H.append(Spacer(1, 2.6 * cm))
for t in [f"<b>Integrantes</b><br/>{INTEGRANTES}", "", f"<b>Professor:</b> {PROFESSOR}", f"<b>Repositório:</b> {REPOSITORIO}", "2026"]:
    H.append(Paragraph(t, ParagraphStyle("c4", fontName="Serif", fontSize=10.5, leading=16, alignment=TA_CENTER)))
H.append(PageBreak())

# ================================================================== 1. INTRODUÇÃO
h1("1. Objetivo")
p("Este trabalho implementa, em linguagem C, um programa que acrescenta ao final de um arquivo CSV de destino os "
  "registros contidos em outro arquivo CSV, recusando todo registro cujo valor na coluna-chave já exista. "
  "A verificação de duplicidade é resolvida de duas maneiras: <b>Solução 1</b>, com busca sequencial (iterativa "
  "e recursiva), e <b>Solução 2</b>, carregando as chaves em um vetor na memória principal, ordenando-o com "
  "MergeSort (iterativo e recursivo) e consultando-o com busca binária (iterativa e recursiva). Para cada "
  "algoritmo são demonstradas as complexidades de tempo e de espaço, e as previsões teóricas são confrontadas "
  "com medições de tempo, contagens de comparações e profundidades de pilha obtidas experimentalmente.")
p("Notação usada em todo o texto: <i>n</i> é o número de registros já existentes no destino, <i>m</i> o número de "
  "registros no arquivo de novos, lg <i>x</i> = log<sub>2</sub> <i>x</i>, e <i>L</i> o tamanho médio de uma chave "
  "(aqui, 11 caracteres). Como <i>L</i> é constante, uma comparação de chaves (<font name='Mono'>strcmp</font>) "
  "custa O(1) e é a <b>operação dominante</b> contada na análise.")

# ================================================================== 2. BASE DE DADOS
h1("2. Base de dados")
p(f"Foi usado o conjunto de dados do Inmetro com os <b>registros de objeto</b> do programa de avaliação da "
  f"conformidade <i>Andadores Infantis</i>, publicado no Portal de Dados Abertos ({LINK_DADOS}). Cada linha "
  "descreve um item vinculado a um registro concedido pelo Inmetro: situação do registro, datas, dados do "
  "fornecedor (razão social, CNPJ, endereço, e-mail), fabricante, portaria aplicável, certificado, país de "
  "origem e a descrição do item (marca, modelo, descrição, códigos de barras e situação do item).")
tab([["Característica", "Valor"],
     ["Arquivo", "ANDADORES_INFANTIS.csv (guardado sem alterações em dados/original/)"],
     ["Registros / colunas", "93 linhas de dados + cabeçalho / 32 colunas"],
     ["Separador / quebra de linha", "ponto e vírgula (;) / CRLF"],
     ["Codificação", "UTF-16 LE com BOM (FF FE); campos vazios preenchidos com o caractere NUL (U+0000)"],
     ["Período", "registros concedidos de 2019 a 2026"],
     ["Colunas principais", "NumeroRegistro, Status, DataConcessao, RazaoSocial, CnpjCpf, Municipio, Uf, Fabricante, "
                            "Certificado, PaisOrigem, ItemMarca, ItemModelo, ItemDescricao, ItemCodigodeBarra, ItemStatus"]],
    [4.2 * cm, 12.3 * cm], "Tabela 1 – Características do arquivo original.")
p("Duas particularidades do arquivo exigiram tratamento. Primeiro, a codificação UTF-16 faz cada caractere ASCII "
  "ocupar dois bytes (um deles nulo), o que quebra qualquer leitura com funções de string de C. Por isso o "
  "repositório inclui <font name='Mono'>ferramentas/converte_utf16.c</font>, que converte o arquivo para UTF-8, "
  "troca CRLF por LF e elimina os caracteres NUL dos campos vazios, gerando "
  "<font name='Mono'>dados/andadores_utf8.csv</font>. O programa principal detecta arquivos UTF-16 e pede a "
  "conversão em vez de produzir resultados errados. Segundo, algumas descrições contêm vírgulas, mas nenhuma "
  "contém ponto e vírgula nem aspas; ainda assim, o leitor de campos respeita campos entre aspas.")

# ================================================================== 3. CHAVE
h1("3. Coluna usada como chave de unicidade")
p("A chave escolhida é <b>NumeroRegistro</b> (coluna 0), no formato <font name='Mono'>NNNNNN/AAAA</font> "
  "(número sequencial do registro / ano de concessão). É o identificador que o Inmetro atribui a cada registro "
  "de objeto: dois registros distintos não podem ter o mesmo número, portanto é uma coluna cujos valores "
  "<i>devem</i> ser únicos. Os valores <b>não estão ordenados</b> no arquivo: as primeiras linhas são "
  "010691/2026, 010280/2026, 010693/2026, 010522/2026, 010524/2026, 007770/2026... — a sequência sobe e desce, "
  "e comparar a coluna com sua versão ordenada confirma que ela está fora de ordem.")
p("Ao analisar o arquivo, verificou-se que ele tem <b>93 linhas mas apenas 75 números de registro distintos</b>: "
  "8 registros aparecem em mais de uma linha (18 linhas excedentes), porque o Inmetro publica uma linha por "
  "<i>item</i> do registro, incluindo versões anteriores de itens já marcados como “Excluido” (Tabela 2). "
  "Ou seja, o arquivo bruto não é uma tabela de registros, e sim de itens. Para obter uma base de destino "
  "na qual a chave é de fato única — pré-requisito do problema — a base foi construída pelo próprio programa: "
  "partindo de um destino inexistente, os 93 registros foram inseridos; o programa aceitou 75 e rejeitou as "
  "18 repetições (mantendo a primeira ocorrência de cada número). O resultado é "
  "<font name='Mono'>dados/base_andadores.csv</font>, que serve de destino nos testes com dados reais "
  "(comando <font name='Mono'>make base</font>).")
tab([["NumeroRegistro", "Linhas no arquivo", "Motivo da repetição"],
     ["001472/2022", "7", "6 versões excluídas + 1 item vigente"],
     ["001803/2023", "4", "3 versões excluídas + 1 item vigente"],
     ["005052/2021", "4", "3 versões excluídas + 1 item vigente"],
     ["009477/2019", "3", "2 versões excluídas + 1 item vigente"],
     ["001185/2024, 001636/2023, 006227/2019", "2 cada", "1 versão excluída + 1 item vigente"],
     ["005630/2021", "2", "dois itens vigentes (Ref. 914 e Ref. 915)"]],
    [5.6 * cm, 3.0 * cm, 7.9 * cm], "Tabela 2 – Números de registro repetidos no arquivo original.")

# ================================================================== 4. IMPLEMENTAÇÃO
h1("4. Implementação")
p("O programa <font name='Mono'>insere</font> recebe na linha de comando o arquivo de novos registros e o "
  "arquivo de destino, nessa ordem (<font name='Mono'>./bin/insere novos.csv destino.csv</font>). A opção "
  "<font name='Mono'>-m</font> escolhe um dos seis métodos: <font name='Mono'>seq-iter</font>, "
  "<font name='Mono'>seq-rec</font> (Solução 1) e <font name='Mono'>bin-X-Y</font> (Solução 2), em que X é a "
  "versão do MergeSort e Y a da busca binária (<font name='Mono'>iter</font> ou <font name='Mono'>rec</font>). "
  "Há ainda <font name='Mono'>-k</font> (coluna-chave), <font name='Mono'>-v</font> (lista os rejeitados), "
  "<font name='Mono'>-s</font> (simulação, sem gravar) e <font name='Mono'>-t</font> (métricas). O fluxo é:")
item("<b>Carga:</b> lê o destino linha a linha e guarda apenas as chaves em um vetor de "
     "<font name='Mono'>Item {char *chave; long idx;}</font>; lê o arquivo de novos guardando as linhas "
     "completas (precisam ser gravadas depois) e suas chaves. As chaves são comparadas sem espaços nas pontas.")
item("<b>Verificação:</b> cada registro novo é classificado como aceito, duplicado no destino, duplicado "
     "dentro do próprio lote ou inválido (chave vazia/coluna ausente). A verificação dentro do lote é "
     "indispensável: sem ela, um arquivo de novos com duas linhas de mesma chave inédita introduziria uma "
     "duplicata no destino.")
item("<b>Gravação:</b> os aceitos são acrescentados ao final do destino (modo <i>append</i>), na ordem original, "
     "com o mesmo tipo de quebra de linha do destino; se o destino não existe, é criado com o cabeçalho.")
p("<b>Premissa comum às duas soluções.</b> Nas duas soluções as chaves do destino são lidas do disco uma única "
  "vez e mantidas em RAM; o que as diferencia é o algoritmo de verificação. Uma busca sequencial que relesse o "
  "arquivo de destino para cada registro novo teria o mesmo Θ(<i>m·n</i>) comparações, porém multiplicaria "
  "também a leitura de disco por <i>m</i>, o que misturaria custo de E/S com custo de algoritmo e inviabilizaria "
  "a comparação. A leitura dos arquivos, Θ(<i>n + m</i>) linhas, é idêntica nos seis métodos e é medida à parte.")
p("<b>Instrumentação.</b> Toda comparação de chaves incrementa um contador global, e toda chamada recursiva "
  "atualiza a profundidade atual e a máxima da pilha. Esse custo O(1) é o mesmo em todas as versões. Nas "
  "funções recursivas o decremento da profundidade ocorre depois da chamada, de modo que ela não é a última "
  "instrução: o compilador não pode convertê-la em laço (<i>tail call</i>), e a recursão medida é real.")
p("<b>Validação.</b> O script <font name='Mono'>testes/testes_funcionais.sh</font> executa os seis métodos "
  "sobre os mesmos dados (base real + <font name='Mono'>novos_exemplo.csv</font>, com 12 casos: inéditos, "
  "já existentes, chave com espaços, repetição no lote e chave vazia; construção da base a partir do CSV real; "
  "e um conjunto sintético com 5 000 + 2 000 linhas) e confere que os arquivos resultantes são idênticos byte "
  "a byte, que uma segunda execução não insere nada e que o destino final não tem chaves repetidas. Todos os "
  "testes passaram, e a execução com AddressSanitizer não acusou erros de memória.")

# ================================================================== 5. SOLUÇÃO 1
h1("5. Solução 1 — busca sequencial")
cod("""
long busca_sequencial_iterativa(const Item *v, long n, const char *chave) {
    for (long i = 0; i < n; i++)
        if (compara(v[i].chave, chave) == 0) return i;
    return -1;
}
static long seq_rec(const Item *v, long n, const char *chave, long i) {
    long r;
    ENTRA_RECURSAO();
    if (i >= n)                                  r = -1;                 /* caso base */
    else if (compara(v[i].chave, chave) == 0)    r = i;                  /* caso base */
    else                                         r = seq_rec(v, n, chave, i + 1);
    SAI_RECURSAO();
    return r;
}""")
h2("5.1 Busca sequencial iterativa")
p("<b>Tempo.</b> O laço executa uma comparação por iteração. Se a chave está na posição <i>i</i> (base 0), são "
  "feitas <i>i</i> + 1 comparações; se não está, são <i>n</i>. Logo: melhor caso 1 comparação, Θ(1); pior caso "
  "(ausente ou na última posição) <i>n</i> comparações, Θ(<i>n</i>). Supondo a chave presente em posição "
  "uniformemente distribuída, o caso médio de sucesso é")
eq("C<sub>suc</sub>(<i>n</i>) = (1/<i>n</i>) · Σ<sub><i>i</i>=1..<i>n</i></sub> <i>i</i> = (<i>n</i> + 1)/2 = Θ(<i>n</i>),  "
   "C<sub>insuc</sub>(<i>n</i>) = <i>n</i> = Θ(<i>n</i>).")
p("<b>Espaço.</b> Além do vetor recebido (que pertence ao chamador), usa só as variáveis <i>i</i>, <i>n</i> e dois "
  "ponteiros: espaço extra O(1).")
h2("5.2 Busca sequencial recursiva")
p("<b>Tempo.</b> Seja T(<i>k</i>) o custo quando restam <i>k</i> = <i>n</i> − <i>i</i> elementos. Cada chamada faz "
  "trabalho constante <i>c</i> e, no pior caso, uma chamada com <i>k</i> − 1 elementos:")
eq("T(0) = <i>c</i><sub>0</sub>;   T(<i>k</i>) = T(<i>k</i> − 1) + <i>c</i>  ⇒  "
   "T(<i>k</i>) = T(<i>k</i> − <i>j</i>) + <i>j·c</i>  ⇒  (<i>j</i> = <i>k</i>)  T(<i>n</i>) = <i>c</i><sub>0</sub> + <i>n·c</i> = Θ(<i>n</i>).")
p("O número de comparações é exatamente o mesmo da versão iterativa (melhor 1, pior <i>n</i>, média (<i>n</i>+1)/2).")
p("<b>Espaço.</b> Cada chamada empilha um quadro de ativação que só é liberado quando a busca termina. No pior "
  "caso há <i>n</i> + 1 quadros simultâneos: S(<i>n</i>) = (<i>n</i> + 1)·<i>s</i> = Θ(<i>n</i>), em que <i>s</i> é o "
  "tamanho do quadro. Em um binário gerado com GCC 13 (-O2, x86-64, Linux), cada quadro ocupa <b>48 bytes</b> "
  "(cinco registradores salvos + endereço de retorno); com a pilha padrão de 8 MiB, o limite teórico é "
  "8 388 608 / 48 ≈ <b>174 762</b> chamadas, e a busca funcionou com 174 000 elementos e terminou com "
  "<i>segmentation fault</i> com 176 000. No MacBook (Apple M2, Clang) o efeito foi reproduzido limitando a "
  "pilha a 1 MiB (<font name='Mono'>ulimit -s 1024</font>): com <i>n</i> = 50 000, a busca sequencial recursiva "
  "terminou com <i>segmentation fault</i>, enquanto a Solução 2 recursiva (17 quadros) executou normalmente. "
  "Esse é o efeito prático do espaço Θ(<i>n</i>): a versão "
  "recursiva não é apenas mais lenta, ela tem um limite de tamanho que a iterativa não tem (no Windows, "
  "com 1 MB de pilha, o limite cai para a ordem de 20 mil elementos; por isso o Makefile aumenta a pilha).")
h2("5.3 Custo do programa completo (Solução 1)")
p("Para detectar repetições dentro do lote, cada chave aceita é acrescentada ao fim do vetor, que cresce de "
  "<i>n</i> até <i>n</i> + <i>A</i> (<i>A</i> = aceitos). A <i>i</i>-ésima busca examina no máximo <i>n</i> + <i>i</i> chaves:")
eq("C<sub>1</sub>(<i>n</i>, <i>m</i>) ≤ Σ<sub><i>i</i>=0..<i>m</i>−1</sub> (<i>n</i> + <i>i</i>) = <i>m·n</i> + <i>m</i>(<i>m</i> − 1)/2 "
   "= O(<i>m·n</i> + <i>m</i><sup>2</sup>)   (= O(<i>m·n</i>) quando <i>m</i> ≤ <i>n</i>).")
p("Se uma fração <i>p</i> dos novos já existe no destino (custo médio (<i>n</i>+1)/2) e o restante precisa percorrer "
  "o vetor inteiro, o valor esperado é aproximadamente <i>D</i>(<i>n</i>+1)/2 + (<i>A</i>+<i>L</i>)(<i>n</i> + <i>A</i>/2), "
  "com <i>D</i>, <i>L</i> e <i>A</i> = quantidades de duplicados no destino, repetidos no lote e aceitos. "
  "Espaço total: vetor de <i>n</i> + <i>m</i> ponteiros + as chaves = Θ(<i>n</i> + <i>m</i>); a versão recursiva "
  "acrescenta até <i>n</i> + <i>m</i> quadros de pilha, também Θ(<i>n</i> + <i>m</i>).")

# ================================================================== 6. SOLUÇÃO 2
h1("6. Solução 2 — MergeSort e busca binária")
p("As <i>n</i> chaves do destino são carregadas em um vetor em RAM e ordenadas. As chaves válidas do lote "
  "também são ordenadas com o mesmo MergeSort: como ele é <b>estável</b>, chaves iguais ficam vizinhas e a "
  "primeira ocorrência (menor posição original) vem antes, de modo que as repetições internas do lote são "
  "detectadas por uma única varredura de vizinhos (<i>m</i> − 1 comparações). Por fim, cada chave do lote é "
  "procurada no vetor do destino por busca binária.")
cod("""
static void intercala(Item *v, Item *aux, long ini, long meio, long fim) {   /* Θ(fim-ini+1) */
    long i = ini, j = meio + 1, k = ini;
    while (i <= meio && j <= fim)
        aux[k++] = (compara(v[i].chave, v[j].chave) <= 0) ? v[i++] : v[j++];   /* <= : estável */
    while (i <= meio) aux[k++] = v[i++];
    while (j <= fim)  aux[k++] = v[j++];
    memcpy(v + ini, aux + ini, (fim - ini + 1) * sizeof(Item));
}
static void ms_rec(Item *v, Item *aux, long ini, long fim) {               /* top-down  */
    if (ini < fim) { long meio = ini + (fim - ini) / 2;
        ms_rec(v, aux, ini, meio); ms_rec(v, aux, meio + 1, fim); intercala(v, aux, ini, meio, fim); }
}
int mergesort_iterativo(Item *v, long n) {                                  /* bottom-up */
    Item *aux = malloc(n * sizeof(Item));
    for (long larg = 1; larg < n; larg *= 2)
        for (long ini = 0; ini < n - larg; ini += 2 * larg) {
            long fim = min(ini + 2 * larg - 1, n - 1);
            intercala(v, aux, ini, ini + larg - 1, fim);
        }
    free(aux); return 0;
}""")
h2("6.1 MergeSort recursivo (top-down)")
p("<b>Tempo.</b> A intercalação de dois blocos que somam <i>k</i> elementos faz no máximo <i>k</i> − 1 comparações e "
  "2<i>k</i> movimentos: Θ(<i>k</i>). Dividir custa O(1). Assim,")
eq("T(1) = <i>c</i>;   T(<i>n</i>) = T(⌈<i>n</i>/2⌉) + T(⌊<i>n</i>/2⌋) + Θ(<i>n</i>).")
p("Pela árvore de recursão: o nível <i>j</i> tem 2<sup><i>j</i></sup> subproblemas de tamanho <i>n</i>/2<sup><i>j</i></sup>, "
  "somando <i>c·n</i> por nível; há ⌈lg <i>n</i>⌉ níveis de intercalação, logo T(<i>n</i>) = <i>c·n</i>⌈lg <i>n</i>⌉ + Θ(<i>n</i>) "
  "= Θ(<i>n</i> log <i>n</i>). O mesmo resultado sai do Teorema Mestre (<i>a</i> = 2, <i>b</i> = 2, "
  "<i>f</i>(<i>n</i>) = Θ(<i>n</i>) = Θ(<i>n</i><sup>log<sub>b</sub> a</sup>), caso 2). O custo não depende da ordem da "
  "entrada: melhor, médio e pior caso são Θ(<i>n</i> log <i>n</i>). Em comparações, o pior caso é exatamente "
  "<i>n</i>⌈lg <i>n</i>⌉ − 2<sup>⌈lg <i>n</i>⌉</sup> + 1 e o caso médio vale aproximadamente <i>n</i> lg <i>n</i> − 1,26<i>n</i> (Knuth).")
p("<b>Espaço.</b> O vetor auxiliar tem <i>n</i> posições (16 bytes cada: ponteiro + índice), Θ(<i>n</i>). A pilha "
  "tem profundidade máxima ⌈lg <i>n</i>⌉ + 1, Θ(log <i>n</i>). Total: Θ(<i>n</i>) + Θ(log <i>n</i>) = Θ(<i>n</i>).")
h2("6.2 MergeSort iterativo (bottom-up)")
p("<b>Tempo.</b> O laço externo percorre larguras 1, 2, 4, …, enquanto largura &lt; <i>n</i>: são ⌈lg <i>n</i>⌉ passadas. "
  "Em cada passada, os blocos intercalados são disjuntos e cobrem o vetor, então a passada custa Θ(<i>n</i>). "
  "Total: ⌈lg <i>n</i>⌉ · Θ(<i>n</i>) = Θ(<i>n</i> log <i>n</i>), também independente da entrada. A diferença em relação à "
  "versão recursiva está na forma da árvore de intercalações: quando <i>n</i> não é potência de 2, o bottom-up "
  "intercala blocos de tamanhos mais desiguais no final (por exemplo, 32 768 com 17 232 para <i>n</i> = 50 000), "
  "o que muda ligeiramente o número de comparações, mas não a ordem de grandeza.")
p("<b>Espaço.</b> Mesmo vetor auxiliar Θ(<i>n</i>) e apenas variáveis de laço, O(1): total Θ(<i>n</i>), <b>sem pilha</b>. "
  "As duas versões têm portanto a mesma complexidade assintótica de tempo e de espaço; a recursiva paga "
  "Θ(log <i>n</i>) de pilha (21 quadros para <i>n</i> = 10<sup>6</sup>, desprezível) e o custo das chamadas de função.")
h2("6.3 Busca binária iterativa")
cod("""
long busca_binaria_iterativa(const Item *v, long n, const char *chave) {
    long ini = 0, fim = n - 1;
    while (ini <= fim) {
        long meio = ini + (fim - ini) / 2;              /* evita overflow de ini+fim */
        int c = compara(v[meio].chave, chave);
        if (c == 0) return meio;
        if (c < 0) ini = meio + 1; else fim = meio - 1;
    }
    return -1;
}""")
p("<b>Tempo.</b> Se o intervalo tem <i>k</i> elementos, após uma iteração sem sucesso restam no máximo ⌊<i>k</i>/2⌋. "
  "Depois de <i>t</i> iterações restam no máximo ⌊<i>n</i>/2<sup><i>t</i></sup>⌋ elementos, e o laço termina quando o "
  "intervalo fica vazio; logo <i>t</i> ≤ ⌊lg <i>n</i>⌋ + 1. Melhor caso: 1 comparação, Θ(1); pior caso e busca sem "
  "sucesso: ⌊lg <i>n</i>⌋ + 1 comparações, Θ(log <i>n</i>); média de sucesso ≈ lg <i>n</i> − 1.")
p("<b>Espaço.</b> Apenas <i>ini</i>, <i>fim</i>, <i>meio</i> e <i>c</i>: O(1).")
h2("6.4 Busca binária recursiva")
p("<b>Tempo.</b> Cada chamada faz trabalho constante e, se não encontra, chama a si mesma sobre metade do intervalo:")
eq("T(0) = <i>c</i>;   T(<i>n</i>) = T(⌊<i>n</i>/2⌋) + <i>c</i>  ⇒  T(<i>n</i>) = <i>c</i>(⌊lg <i>n</i>⌋ + 2) = Θ(log <i>n</i>)")
p("(Teorema Mestre com <i>a</i> = 1, <i>b</i> = 2, <i>f</i>(<i>n</i>) = Θ(1) = Θ(<i>n</i><sup>0</sup>): caso 2). O número "
  "de comparações é idêntico ao da versão iterativa.")
p("<b>Espaço.</b> Até ⌊lg <i>n</i>⌋ + 2 quadros simultâneos na pilha (o último é o caso base com intervalo vazio): "
  "Θ(log <i>n</i>), contra O(1) da iterativa.")
h2("6.5 Custo do programa completo (Solução 2)")
eq("T<sub>2</sub>(<i>n</i>, <i>m</i>) = Θ(<i>n</i> log <i>n</i>) [ordena destino] + Θ(<i>m</i> log <i>m</i>) [ordena lote] "
   "+ Θ(<i>m</i>) [vizinhos] + <i>m</i>·Θ(log <i>n</i>) [buscas] = Θ(<i>n</i> log <i>n</i> + <i>m</i> log <i>m</i> + <i>m</i> log <i>n</i>)")
p("Espaço: vetores de <i>n</i> e <i>m</i> itens mais o auxiliar do MergeSort (liberado ao fim de cada ordenação), "
  "Θ(<i>n</i> + <i>m</i>), mais O(log <i>n</i>) de pilha nas versões recursivas.")

# ================================================================== 7. COMPARAÇÃO TEÓRICA
h1("7. Comparação teórica entre as soluções")
tab([["Algoritmo / programa", "Tempo (melhor)", "Tempo (pior)", "Espaço extra"],
     ["Busca sequencial iterativa", "Θ(1)", "Θ(n)", "O(1)"],
     ["Busca sequencial recursiva", "Θ(1)", "Θ(n)", "Θ(n) – pilha"],
     ["MergeSort recursivo", "Θ(n log n)", "Θ(n log n)", "Θ(n) aux + Θ(log n) pilha"],
     ["MergeSort iterativo", "Θ(n log n)", "Θ(n log n)", "Θ(n) aux"],
     ["Busca binária iterativa", "Θ(1)", "Θ(log n)", "O(1)"],
     ["Busca binária recursiva", "Θ(1)", "Θ(log n)", "Θ(log n) – pilha"],
     ["<b>Solução 1</b> (m inserções)", "Θ(m)", "Θ(m·n + m²)", "Θ(n+m); rec.: + Θ(n+m) pilha"],
     ["<b>Solução 2</b> (m inserções)", "Θ(n log n + m log m)", "Θ(n log n + m log m + m log n)", "Θ(n+m); rec.: + Θ(log n) pilha"]],
    [5.0 * cm, 3.3 * cm, 4.6 * cm, 3.6 * cm], "Tabela 3 – Resumo das complexidades (n = destino, m = novos).")
p("Para <i>m</i> proporcional a <i>n</i>, a Solução 1 é quadrática, Θ(<i>n</i><sup>2</sup>), e a Solução 2 é "
  "Θ(<i>n</i> log <i>n</i>): a vantagem da Solução 2 cresce sem limite. Mas a Solução 2 paga o custo fixo de ordenar o "
  "destino mesmo quando há poucos registros novos. Igualando os custos esperados em comparações (com metade dos "
  "novos já presentes, a Solução 1 gasta cerca de 0,75·<i>n</i> por registro) obtém-se o ponto de equilíbrio")
eq("0,75·<i>m·n</i> ≈ <i>n</i> lg <i>n</i> − 1,26<i>n</i>   ⇒   <i>m</i>* ≈ (lg <i>n</i> − 1,26) / 0,75 ≈ 19  para <i>n</i> = 50 000.")
p("Abaixo de algumas dezenas de registros novos, a busca sequencial deve ser mais barata; acima disso, "
  "a ordenação se paga. Quanto ao espaço, as duas soluções são Θ(<i>n</i> + <i>m</i>); a diferença está nas versões "
  "recursivas: a busca sequencial recursiva usa pilha linear, enquanto as recursões da Solução 2 são logarítmicas.")

# ================================================================== 8. EXPERIMENTOS
h1("8. Resultados experimentais")
h2("8.1 Metodologia")
p(f"Ambiente: {AMBIENTE}, com "
  "<font name='Mono'>-std=c11 -O2</font> (o programa usa um único núcleo). Os tempos foram medidos com relógio monotônico "
  "(<font name='Mono'>clock_gettime</font>) dentro do programa, separando leitura dos arquivos, ordenação, buscas e "
  "gravação; cada ponto é a <b>mediana de 5 execuções</b>, com a opção <font name='Mono'>-s</font> (sem gravar) para que "
  "todas as execuções usem o mesmo destino. Também foram registrados o número de comparações e a profundidade "
  "máxima de recursão, que não dependem da máquina.")
p("Como a base real tem só 75 registros (tempos de microssegundos, dominados por ruído), os experimentos usaram "
  "arquivos gerados por <font name='Mono'>ferramentas/gera_dados.c</font>: cada linha é a cópia de uma linha "
  "<b>real</b> da base, sorteada, com o NumeroRegistro trocado por uma chave única no mesmo formato "
  "<font name='Mono'>NNNNNN/AAAA</font>, em ordem pseudoaleatória. Nos arquivos de novos, 50% das chaves já existem "
  "no destino, 5% repetem uma chave anterior do próprio lote e o restante é inédito. Com semente fixa, os arquivos "
  "são reprodutíveis e estão no repositório (<font name='Mono'>dados/experimentos/</font>, até 34 MB).")
item("<b>Exp. 1</b> – programa completo, <i>m</i> = 1 000 fixo, <i>n</i> ∈ {1 000, 2 000, 5 000, 10 000, 20 000, 50 000}.")
item("<b>Exp. 2</b> – programa completo, <i>n</i> = 50 000 fixo, <i>m</i> de 1 a 5 000.")
item("<b>Exp. 3</b> – algoritmos isolados em memória (<font name='Mono'>ferramentas/bench_algoritmos.c</font>, mesmas funções "
     "de <font name='Mono'>src/</font>), <i>n</i> até 10<sup>6</sup>; 1 000 consultas por tamanho, metade presentes.")

h2("8.2 Experimento 1 — tempo em função de n")
fig("fig1_exp1_tempo.png", 13.5 * cm, "Figura 1 – Tempo de verificação (ordenação + buscas) com m = 1000, escala log-log.")
linhas = [["Método"] + [fmt(n) for n in sorted(e1.n.unique())] + ["inclinação"]]
for met in ["seq-iter", "seq-rec"] + BIN:
    linhas.append([met] + [ms(v1(met, n, "t_verificacao")) for n in sorted(e1.n.unique())]
                  + [fmt(inclinacao(met), 2)])
tab(linhas, [2.6 * cm] + [1.85 * cm] * 6 + [1.8 * cm], pequeno=True, legenda=
    "Tabela 4 – Tempo de verificação (ms), m = 1000. Inclinação = expoente empírico k em t ∝ n<sup>k</sup> entre n = 1000 e 50 000.")
s_it, s_rec = v1("seq-iter", NMAX, "t_verificacao"), v1("seq-rec", NMAX, "t_verificacao")
b_min = min(v1(m, NMAX, "t_verificacao") for m in BIN)
b_max = max(v1(m, NMAX, "t_verificacao") for m in BIN)
def compara_com_1(x):
    return "abaixo de 1" if x < 0.95 else ("acima de 1" if x > 1.05 else "próxima de 1")


incl_bin_min = min(inclinacao(m) for m in BIN)
incl_bin_max = max(inclinacao(m) for m in BIN)
if incl_bin_max < 0.95:
    frase_incl_bin = ("ficou abaixo de 1 porque, com <i>n</i> pequeno, pesam as parcelas que não dependem de "
                      "<i>n</i> (ordenar o lote de 1 000 chaves e as buscas)")
else:
    frase_incl_bin = f"ficou {compara_com_1((incl_bin_min + incl_bin_max) / 2)}"


def incl_ord(met, n0=5000):
    a, b = v1(met, n0, "t_ordenacao"), v1(met, NMAX, "t_ordenacao")
    return math.log(b / a) / math.log(NMAX / n0)


p(f"Com <i>m</i> fixo, a teoria prevê para a Solução 1 tempo linear em <i>n</i> (Θ(<i>m·n</i>)), e a inclinação medida "
  f"foi {fmt(inclinacao('seq-iter'), 2)} (iterativa) e {fmt(inclinacao('seq-rec'), 2)} (recursiva) — praticamente 1. "
  f"Na Solução 2 a inclinação do tempo total ({fmt(incl_bin_min, 2)} a {fmt(incl_bin_max, 2)}) {frase_incl_bin}. "
  "Isolando apenas a "
  "ordenação, que é o termo dominante Θ(<i>n</i> log <i>n</i>), a inclinação entre <i>n</i> = 5 000 e 50 000 foi "
  f"{fmt(min(incl_ord(m) for m in BIN), 2)} a {fmt(max(incl_ord(m) for m in BIN), 2)}, "
  f"compatível com <i>n</i> log <i>n</i> (a previsão teórica nessa faixa é "
  f"{fmt(math.log((NMAX*math.log2(NMAX))/(5000*math.log2(5000)))/math.log(NMAX/5000), 2)}). "
  f"Em <i>n</i> = {fmt(NMAX)}, a Solução 2 levou {ms(b_min)}–{ms(b_max)} ms, contra {ms(s_it)} ms da busca sequencial "
  f"iterativa (<b>{fmt(s_it / b_max, 1)}× a {fmt(s_it / b_min, 1)}× mais rápida</b>) e {ms(s_rec)} ms da recursiva.")
tab([["n", "Duplic. destino (D)", "Repet. lote (L)", "Aceitos (A)", "Comparações medidas", "Modelo teórico", "Diferença"]] +
    [[fmt(r.n), fmt(r.D), fmt(r.L), fmt(r.A), fmt(r.observado), fmt(r.modelo), fmt(r.erro_pct, 2) + "%"] for r in cs.itertuples()],
    [1.6 * cm, 2.5 * cm, 2.2 * cm, 2.0 * cm, 3.0 * cm, 2.8 * cm, 2.0 * cm],
    "Tabela 5 – Solução 1: comparações medidas × modelo D(n+1)/2 + (A+L)(n + A/2) da seção 5.3.")
p("A contagem de comparações da Solução 1 coincide com o modelo teórico com diferença de no máximo "
  f"{fmt(cs.erro_pct.abs().max(), 1)}% (Tabela 5); o resíduo vem de as posições das chaves duplicadas serem "
  "sorteadas, e não exatamente centradas em <i>n</i>/2.")
fig("fig2_exp1_composicao.png", 13.5 * cm,
    f"Figura 2 – Composição do tempo total para n = {fmt(NMAX)} e m = 1000.")
p(f"A Figura 2 mostra um fato prático importante: na Solução 2 a leitura dos arquivos "
  f"(≈ {ms(v1('bin-iter-iter', NMAX, 't_carga'))} ms para {fmt(NMAX)} linhas, ≈ 34 MB) custa cerca de "
  f"{fmt(v1('bin-iter-iter', NMAX, 't_carga') / v1('bin-iter-iter', NMAX, 't_verificacao'), 0)} vezes mais do que "
  "ordenar e buscar. A leitura é Θ(<i>n</i>·tamanho da linha) e é inevitável; depois da ordenação, o gargalo "
  f"deixa de ser o algoritmo. Na Solução 1, a verificação levou {ms(v1('seq-iter', NMAX, 't_verificacao'))} ms "
  f"(iterativa) e {ms(v1('seq-rec', NMAX, 't_verificacao'))} ms (recursiva), contra "
  f"{ms(v1('bin-iter-iter', NMAX, 't_verificacao'))} ms da Solução 2.")

h2("8.3 Experimento 2 — ponto de equilíbrio em função de m")
fig("fig3_exp2_cruzamento.png", 16 * cm,
    "Figura 3 – n = 50 000 fixo. Esquerda: tempo de verificação; direita: total de comparações (ordenação + buscas).")
ms_ = sorted(e2.m.unique())
linhas = [["m"] + [fmt(m) for m in ms_ if m in (1, 5, 10, 20, 50, 100, 1000, 5000)]]
sel = [m for m in ms_ if m in (1, 5, 10, 20, 50, 100, 1000, 5000)]
for met in ["seq-iter", "seq-rec", "bin-iter-iter", "bin-rec-iter"]:
    linhas.append([met] + [ms(v2(met, m, "t_verificacao")) for m in sel])
linhas.append(["comp. seq"] + [fmt(v2("seq-iter", m, "comp_busca")) for m in sel])
linhas.append(["comp. bin"] + [fmt(v2("bin-iter-iter", m, "comp_ordenacao") + v2("bin-iter-iter", m, "comp_busca")) for m in sel])
tab(linhas, [1.9 * cm] + [1.84 * cm] * 8, pequeno=True, legenda="Tabela 6 – Exp. 2: tempo de verificação (ms) e comparações, n = 50 000.")


def cruzamento(col_seq, col_bin):
    """Retorna (m anterior, m posterior, m interpolado) do ponto em que seq passa bin."""
    for a, b in zip(ms_, ms_[1:]):
        if col_seq(a) <= col_bin(a) and col_seq(b) > col_bin(b):
            da, db = col_seq(a) - col_bin(a), col_seq(b) - col_bin(b)
            return a, b, a + (b - a) * (-da) / (db - da)
    return None, None, None


fc_s = lambda m: v2("seq-iter", m, "comp_busca")
fc_b = lambda m: v2("bin-iter-iter", m, "comp_ordenacao") + v2("bin-iter-iter", m, "comp_busca")
ft_s = lambda m: v2("seq-iter", m, "t_verificacao")
ft_b = lambda m: min(v2(b, m, "t_verificacao") for b in BIN)
c_a, c_b, c_x = cruzamento(fc_s, fc_b)
t_a, t_b, t_x = cruzamento(ft_s, ft_b)
m_tempo = round(t_x, -1) if t_x is not None else None
if c_x is not None:
    frase_comp = (f"Em comparações, as curvas se cruzam entre <i>m</i> = {c_a} e <i>m</i> = {c_b} (interpolando, "
                  f"<i>m</i> ≈ {fmt(c_x)}) — em acordo com a estimativa teórica <i>m</i>* ≈ 19 da seção 7. ")
else:
    frase_comp = "Em comparações, não houve cruzamento na faixa medida. "
if t_x is None:
    frase_tempo = "Em tempo, não houve cruzamento na faixa de <i>m</i> medida. "
elif c_x is not None and t_x > c_x * 1.2:
    frase_tempo = (f"Em tempo, o cruzamento ocorre mais tarde, entre <i>m</i> = {t_a} e {t_b} (≈ {fmt(t_x)}): a "
                   "comparação na busca sequencial é mais barata que a do MergeSort, porque percorre a memória em "
                   "ordem (bom uso de cache e de pré-busca do processador), enquanto a intercalação também move "
                   "2<i>n</i> itens por nível. ")
elif c_x is not None and t_x < c_x / 1.2:
    frase_tempo = (f"Em tempo, o cruzamento ocorre mais cedo, entre <i>m</i> = {t_a} e {t_b} (≈ {fmt(t_x)}): nesta "
                   "máquina, cada comparação da busca sequencial saiu relativamente mais cara que as operações do "
                   "MergeSort. ")
else:
    frase_tempo = (f"Em tempo, o cruzamento ocorre praticamente no mesmo ponto, entre <i>m</i> = {t_a} e {t_b} "
                   f"(≈ {fmt(t_x)}). ")
p(f"A curva da Solução 1 cresce linearmente com <i>m</i>, enquanto a da Solução 2 é praticamente plana: o custo "
  f"está quase todo na ordenação do destino (≈ {fmt(v2('bin-iter-iter', 1, 'comp_ordenacao'))} comparações), e cada "
  f"registro novo acrescenta só ≈ lg 50 000 ≈ 16 comparações. " + frase_comp + frase_tempo +
  "A análise assintótica prevê corretamente o formato das curvas e a ordem de "
  "grandeza do cruzamento; a posição exata depende das constantes escondidas no Θ.")

h2("8.4 Experimento 3 — MergeSort iterativo × recursivo")
fig("fig4_exp3_mergesort.png", 16 * cm,
    "Figura 4 – Esquerda: tempo de ordenação. Direita: tempo dividido por n·lg n (constante ⇒ comportamento Θ(n log n)).")
linhas = [["n", "Comp. iterativo", "Comp. recursivo", "Pior caso top-down", "Média aprox.", "Tempo it. (ms)", "Tempo rec. (ms)", "rec/it"]]
for r in rm.itertuples():
    linhas.append([fmt(r.n), fmt(r.comparacoes_mergesort_iter), fmt(r.comparacoes_mergesort_rec), fmt(r.pior_top_down),
                   fmt(r.medio_aprox), ms(r.tempo_mediano_s_mergesort_iter), ms(r.tempo_mediano_s_mergesort_rec),
                   fmt(r.razao_tempo_rec_iter, 2)])
tab(linhas, [1.9 * cm, 2.2 * cm, 2.2 * cm, 2.3 * cm, 2.1 * cm, 2.0 * cm, 2.0 * cm, 1.3 * cm], pequeno=True, legenda=
    "Tabela 7 – MergeSort: comparações medidas × fórmulas teóricas, e tempos (Exp. 3).")
p("As comparações do MergeSort recursivo ficaram sempre abaixo do pior caso exato "
  "<i>n</i>⌈lg <i>n</i>⌉ − 2<sup>⌈lg <i>n</i>⌉</sup> + 1 e próximas da aproximação de caso médio "
  f"<i>n</i> lg <i>n</i> − 1,26<i>n</i> (diferença máxima de "
  f"{fmt(100 * ((rm.comparacoes_mergesort_rec - rm.medio_aprox) / rm.medio_aprox).abs().max(), 1)}%). "
  "O bottom-up faz um pouco mais de comparações quando <i>n</i> não é potência de 2 (em alguns tamanhos chega "
  "a ultrapassar a fórmula do top-down, que não se aplica a ele), pelas intercalações desbalanceadas descritas na "
  "seção 6.2. O tempo dividido por <i>n</i> lg <i>n</i> fica aproximadamente constante (Figura 4, direita); "
  "variações para <i>n</i> grande refletem efeitos de cache (o vetor deixa de caber nela), e não uma mudança de "
  "ordem de complexidade. " + (
      f"A versão recursiva foi em média {fmt(rm.razao_tempo_rec_iter.mean(), 2)}× mais lenta que a iterativa: "
      "mesma complexidade, mas com o custo de ~2<i>n</i> chamadas de função."
      if rm.razao_tempo_rec_iter.mean() > 1.02 else
      f"As duas versões tiveram tempos muito próximos (razão média recursiva/iterativa de "
      f"{fmt(rm.razao_tempo_rec_iter.mean(), 2)}), o que é coerente com a mesma complexidade Θ(<i>n</i> log <i>n</i>)."))

h2("8.5 Experimento 3 — buscas e espaço de pilha")
fig("fig5_exp3_buscas.png", 16 * cm, "Figura 5 – Tempo e comparações por consulta (1000 consultas, metade presentes).")
linhas = [["n", "seq. it. (µs)", "seq. rec. (µs)", "rec/it", "comp. seq (med./teor.)", "bin. it. (µs)", "bin. rec. (µs)", "comp. bin (med./teor.)"]]
for n in sorted(rb.n.unique()):
    tem_seq = n in set(rb[rb.algoritmo == "seq_iter"].n)
    linhas.append([fmt(n),
                   fmt(vb("seq_iter", n, "us_por_consulta"), 1) if tem_seq else "–",
                   fmt(vb("seq_rec", n, "us_por_consulta"), 1) if tem_seq else "–",
                   fmt(vb("seq_rec", n, "us_por_consulta") / vb("seq_iter", n, "us_por_consulta"), 1) if tem_seq else "–",
                   (fmt(vb("seq_iter", n, "comp_por_consulta")) + " / " + fmt(vb("seq_iter", n, "teorico_por_consulta"))) if tem_seq else "–",
                   fmt(vb("bin_iter", n, "us_por_consulta"), 3), fmt(vb("bin_rec", n, "us_por_consulta"), 3),
                   fmt(vb("bin_iter", n, "comp_por_consulta"), 2) + " / " + fmt(vb("bin_iter", n, "teorico_por_consulta"), 2)])
tab(linhas, [1.9 * cm, 1.7 * cm, 1.8 * cm, 1.1 * cm, 3.1 * cm, 1.7 * cm, 1.8 * cm, 2.9 * cm], pequeno=True, legenda=
    "Tabela 8 – Custo por consulta. Teórico sequencial: ½(n+1)/2 + ½n; binária: ½(⌊lg n⌋+1) + ½(lg n − 1). "
    "Sequenciais medidas até n = 200 000.")
seq_ratio = (rb[rb.algoritmo == "seq_rec"].set_index("n").us_por_consulta /
             rb[rb.algoritmo == "seq_iter"].set_index("n").us_por_consulta)
bin_ratio = (rb[rb.algoritmo == "bin_rec"].set_index("n").us_por_consulta /
             rb[rb.algoritmo == "bin_iter"].set_index("n").us_por_consulta)
p("As comparações por consulta confirmam a teoria: a busca sequencial cresce linearmente (≈ 0,75<i>n</i>), a binária "
  f"cresce uma unidade cada vez que <i>n</i> dobra (de {fmt(vb('bin_iter', 1000, 'comp_por_consulta'), 1)} em <i>n</i> = 1 000 para "
  f"{fmt(vb('bin_iter', 1000000, 'comp_por_consulta'), 1)} em <i>n</i> = 10<sup>6</sup>, exatamente como lg <i>n</i>). "
  f"Em <i>n</i> = 200 000, uma busca binária custa {fmt(vb('bin_iter', 200000, 'us_por_consulta'), 2)} µs contra "
  f"{fmt(vb('seq_iter', 200000, 'us_por_consulta'), 0)} µs da sequencial — cerca de "
  f"{fmt(vb('seq_iter', 200000, 'us_por_consulta') / vb('bin_iter', 200000, 'us_por_consulta'), 0)} vezes menos. "
  f"A recursão custou caro na busca sequencial ({fmt(seq_ratio.min(), 1)}× a {fmt(seq_ratio.max(), 1)}× mais lenta que a "
  "iterativa), porque há uma chamada de função — com empilhamento de registradores — para cada elemento examinado; "
  f"na binária a razão ficou entre {fmt(bin_ratio.min(), 2)}× e {fmt(bin_ratio.max(), 2)}×, pois são só ~20 chamadas.")
fig("fig6_profundidade.png", 12.5 * cm, "Figura 6 – Profundidade máxima de pilha medida × previsão teórica.")
p("A profundidade de pilha medida coincidiu exatamente com a teoria em todos os tamanhos: <i>n</i> + 1 na busca "
  "sequencial recursiva, ⌈lg <i>n</i>⌉ + 1 no MergeSort recursivo e ⌊lg <i>n</i>⌋ + 2 na busca binária recursiva "
  "(por exemplo, 200 001, 19 e 19 para <i>n</i> = 200 000; nos experimentos 1 e 2, a busca sequencial recursiva "
  "chegou a <i>n</i> + <i>A</i> + 1, incluindo as chaves aceitas do lote). A busca sequencial recursiva com "
  "<i>n</i> = 200 000 só pôde ser executada com a pilha ampliada (no macOS, <font name='Mono'>ulimit -s hard</font>, 64 MiB); com a pilha "
  "padrão ela falha, como previsto na seção 5.2. Essa é a confirmação experimental de que o espaço Θ(<i>n</i>) "
  "da recursão linear é um problema real, enquanto o Θ(log <i>n</i>) das recursões da Solução 2 é inofensivo.")

# ================================================================== 9. CONCLUSÕES
h1("9. Conclusões")
item("<b>Correção.</b> Os seis métodos produzem arquivos idênticos e nunca introduzem chaves repetidas no destino, "
     "inclusive quando a repetição está dentro do próprio arquivo de novos — caso que precisa ser tratado "
     "explicitamente.")
item(f"<b>Teoria × prática.</b> As contagens de comparações da Solução 1 ficaram a no máximo "
     f"{fmt(cs.erro_pct.abs().max(), 1)}% do modelo teórico, as "
     "profundidades de pilha coincidiram exatamente com as fórmulas, e as inclinações log-log dos tempos "
     "confirmaram o crescimento linear da Solução 1 (com <i>m</i> fixo) e Θ(<i>n</i> log <i>n</i>) da ordenação.")
item(f"<b>Solução 1 × Solução 2.</b> A Solução 2 é assintoticamente superior — Θ((<i>n</i> + <i>m</i>) log(<i>n</i> + <i>m</i>)) "
     f"contra Θ(<i>m·n</i>) — e foi cerca de {fmt(s_it / ((b_max + b_min) / 2), 0)}× mais rápida com <i>n</i> = 50 000 e "
     f"<i>m</i> = 1 000. Porém ela tem um custo fixo de ordenação: para poucos registros novos"
     + (f" (menos de ~{fmt(m_tempo)} com <i>n</i> = 50 000)" if m_tempo else "") +
     ", a busca sequencial é mais rápida. A notação assintótica indica qual solução escala; as "
     "constantes decidem qual vence em entradas pequenas.")
todas_iter_mais_rapidas = (rm.razao_tempo_rec_iter.mean() > 1 and seq_ratio.mean() > 1 and bin_ratio.mean() > 1)
item("<b>Iterativo × recursivo.</b> Em todos os pares a complexidade de tempo é a mesma"
     + (" e a versão iterativa foi mais rápida." if todas_iter_mais_rapidas else
        "; a versão iterativa foi mais rápida na maioria dos casos, com destaque para a busca sequencial.") +
     " No espaço, a diferença importa quando a recursão é linear: a busca sequencial recursiva é "
     "limitada pelo tamanho da pilha (≈ 175 mil elementos com a pilha padrão de 8 MiB no Linux x86-64), enquanto MergeSort e busca binária "
     "recursivos usam poucas dezenas de quadros mesmo com um milhão de chaves.")
item("<b>Gargalo real.</b> Com a Solução 2, o tempo total passa a ser dominado pela leitura dos arquivos. Se as "
     "inserções forem frequentes, vale manter o índice de chaves já ordenado entre execuções (evitando reordenar "
     "o destino a cada vez) ou usar uma estrutura como tabela hash ou árvore balanceada.")
item("<b>Qualidade da base.</b> A coluna candidata natural a chave (NumeroRegistro) estava repetida no arquivo "
     "publicado, porque cada linha representa um item, e não um registro. Verificar essa premissa antes de "
     "implementar foi essencial para definir corretamente o que significa “não duplicar”.")

# ================================================================== 10. REPOSITÓRIO
h1("10. Repositório e instruções")
p(f"Código-fonte, arquivos de teste, resultados brutos e scripts: <b>{REPOSITORIO}</b>. Compilação e execução:")
cod("""
make                                   # compila bin/insere e as ferramentas (GCC ou Clang, C11)
./bin/insere <novos.csv> <destino.csv> [-m metodo] [-k coluna] [-v] [-s] [-t]
#   metodo: seq-iter | seq-rec | bin-iter-iter | bin-iter-rec | bin-rec-iter | bin-rec-rec
make base                              # converte o CSV do Inmetro e recria dados/base_andadores.csv
make testes                            # testes funcionais
make experimentos                      # experimentos 1, 2 e 3 -> resultados/
python3 relatorio/analise.py           # resumos e gráficos
python3 relatorio/gera_relatorio.py    # este relatório""")

h1("Referências")
for r in ["CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. <i>Algoritmos: teoria e prática</i>. 3. ed. Rio de Janeiro: Elsevier, 2012.",
          "KNUTH, D. E. <i>The Art of Computer Programming, vol. 3: Sorting and Searching</i>. 2. ed. Addison-Wesley, 1998.",
          "ZIVIANI, N. <i>Projeto de algoritmos com implementações em Pascal e C</i>. 3. ed. São Paulo: Cengage Learning, 2011.",
          "BRASIL. Portal de Dados Abertos. <i>Registro de Objetos</i> (Inmetro). Disponível em: https://dados.gov.br/dados/conjuntos-dados/registro-de-objetos. Arquivo: ANDADORES_INFANTIS.csv."]:
    H.append(Paragraph(r, ParagraphStyle("ref", parent=st_corpo, alignment=0, leftIndent=12, firstLineIndent=-12)))


def rodape(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Sans", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2.2 * cm, 1.3 * cm, "Inserção sem duplicidade em CSV — Soluções 1 e 2")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.3 * cm, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate(SAIDA, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="Inserção sem duplicidade em arquivos CSV",
                        author="Caroline Zaiatz, Beatriz Nascimento Costa Medina, Eloisa Sousa de Jesus")
doc.build(H, onFirstPage=rodape, onLaterPages=rodape)
print("Relatório gerado em", SAIDA)
