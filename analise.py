"""
Trabalho Final - Métodos de Computação Experimental e Quantitativa (PUC-Campinas, 2026)

Pergunta: em bezerros leiteiros alojados em grupo em baias de 60 m², a disponibilidade de
4,29 m²/bezerro (coortes de 14 animais), comparada a 3,75 m²/bezerro (coortes de 16 animais),
está associada a diferença na porcentagem da baia utilizada por cada bezerro?

H0: mu_A = mu_B    H1: mu_A != mu_B (bilateral), alfa = 0,05
A = 3,75 m²/bezerro (coortes 3 e 4) | B = 4,29 m²/bezerro (coortes 1 e 2)

Dados: Occhiuto et al. (2022), Dryad, DOI 10.5061/dryad.4qrfj6qbq (versão 5, 04/05/2022),
licença CC0 1.0. Cópia idêntica no Zenodo (registro 6518187), usada para o download.

Uso: python analise.py
O script baixa os dados brutos (se ainda não existirem), gera os dados limpos,
os números do Marco 3 / artigo e a Figura 1.
"""
from pathlib import Path
import hashlib
import urllib.request

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import brentq
import matplotlib

matplotlib.use("Agg")  # gera a figura em arquivo, sem abrir janela
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
try:
    RAIZ = Path(__file__).resolve().parent
except NameError:  # executado colando o código numa célula do Colab
    RAIZ = Path.cwd()

BRUTOS = RAIZ / "dados" / "brutos"
LIMPOS = RAIZ / "dados" / "limpos"
RESULTADOS = RAIZ / "resultados"

URL_CSV = "https://zenodo.org/api/records/6518187/files/Calves_movement_space_use.csv/content"
MD5_CSV = "60be3826e19729e4744eab679bc79cc2"  # checksum publicado no Zenodo
ARQ_BRUTO = BRUTOS / "Calves_movement_space_use.csv"

AREA_BAIA = 60.0  # m² (baias de 6 m x 10 m, Occhiuto et al., 2022)
ALFA = 0.05
SEMENTE = 2026  # usada só no espalhamento horizontal dos pontos da figura

# Coortes 1 e 2: 14 bezerros -> 60/14 = 4,29 m²/bezerro (grupo B)
# Coortes 3 e 4: 16 bezerros -> 60/16 = 3,75 m²/bezerro (grupo A)
GRUPO_POR_COORTE = {1: "B", 2: "B", 3: "A", 4: "A"}

saida = []  # linhas do relatório de resultados


def relata(texto=""):
    print(texto)
    saida.append(texto)


# ---------------------------------------------------------------------------
# 1. Dados brutos: download e conferência de integridade
# ---------------------------------------------------------------------------
BRUTOS.mkdir(parents=True, exist_ok=True)
LIMPOS.mkdir(parents=True, exist_ok=True)
RESULTADOS.mkdir(parents=True, exist_ok=True)

if not ARQ_BRUTO.exists():
    print("Baixando os dados brutos do Zenodo...")
    urllib.request.urlretrieve(URL_CSV, ARQ_BRUTO)

md5 = hashlib.md5(ARQ_BRUTO.read_bytes()).hexdigest()
assert md5 == MD5_CSV, f"Arquivo bruto diferente do publicado (md5 {md5})"

bruto = pd.read_csv(ARQ_BRUTO)

relata("1. VERIFICAÇÃO DOS DADOS BRUTOS")
relata(f"Linhas x colunas: {bruto.shape[0]} x {bruto.shape[1]}")
relata(f"Valores ausentes: {int(bruto.isna().sum().sum())}")
relata(f"Linhas duplicadas: {int(bruto.duplicated().sum())}")
relata(f"Bezerro + janela repetidos: {int(bruto.duplicated(['Calf_ID', 'Observation']).sum())}")
relata(f"Bezerros por coorte: {bruto.groupby('Cohort').Calf_ID.nunique().to_dict()}")
relata(f"AllDayArea_95 (m²): mín. {bruto.AllDayArea_95.min()} | máx. {bruto.AllDayArea_95.max()}")
fora_da_baia = int(((bruto.AllDayArea_95 <= 0) | (bruto.AllDayArea_95 > AREA_BAIA)).sum())
relata(f"Áreas fora do intervalo (0, 60] m²: {fora_da_baia}")
# O README da base inverte os rótulos (chama a área de 95% de "core"); o artigo define
# core = 50% e total = 95%. Conferência: a área de 95% deve ser sempre maior que a de 50%.
relata(f"AllDayArea_95 > AllDayArea_50 em todas as linhas: {bool((bruto.AllDayArea_95 > bruto.AllDayArea_50).all())}")

# ---------------------------------------------------------------------------
# 2. Dados limpos: VD em %, média por bezerro (unidade de análise)
# ---------------------------------------------------------------------------
dados = bruto.copy()
dados["vd_pct"] = 100 * dados["AllDayArea_95"] / AREA_BAIA

# Uma média por bezerro, para não tratar as janelas repetidas do mesmo animal
# como observações independentes (pseudorreplicação).
por_bezerro = (
    dados.groupby(["Calf_ID", "Cohort"], as_index=False)
    .agg(n_janelas=("vd_pct", "size"), vd_pct=("vd_pct", "mean"))
)
por_bezerro["grupo"] = por_bezerro["Cohort"].map(GRUPO_POR_COORTE)
por_bezerro["espaco_m2_bezerro"] = por_bezerro["grupo"].map({"A": 60 / 16, "B": 60 / 14}).round(2)
por_bezerro.to_csv(LIMPOS / "medias_por_bezerro.csv", index=False)

A = por_bezerro.loc[por_bezerro.grupo == "A", "vd_pct"].to_numpy()
B = por_bezerro.loc[por_bezerro.grupo == "B", "vd_pct"].to_numpy()
nA, nB = len(A), len(B)

# ---------------------------------------------------------------------------
# 3. Estatística descritiva
# ---------------------------------------------------------------------------
relata()
relata("2. ESTATÍSTICA DESCRITIVA (média por bezerro, % da baia)")
for nome, x in (("A (3,75 m²/bezerro)", A), ("B (4,29 m²/bezerro)", B)):
    relata(f"Grupo {nome}: n = {len(x)} | média = {x.mean():.2f}% | DP = {x.std(ddof=1):.2f} p.p. "
           f"| mediana = {np.median(x):.2f}%")

# ---------------------------------------------------------------------------
# 4. Pressupostos
# ---------------------------------------------------------------------------
relata()
relata("3. PRESSUPOSTOS")
shA, shB = stats.shapiro(A), stats.shapiro(B)
relata(f"Shapiro-Wilk: A p = {shA.pvalue:.2f} | B p = {shB.pvalue:.2f}")
lev = stats.levene(A, B)  # só descritivo: o Welch não supõe variâncias iguais
relata(f"Levene (descritivo): p = {lev.pvalue:.2f}")

# ---------------------------------------------------------------------------
# 5. Teste principal (confirmatório): t de Welch bilateral + IC 95%
# ---------------------------------------------------------------------------
welch = stats.ttest_ind(A, B, equal_var=False)
dif = A.mean() - B.mean()
ep = np.sqrt(A.var(ddof=1) / nA + B.var(ddof=1) / nB)
t_crit = stats.t.ppf(1 - ALFA / 2, welch.df)
ic = (dif - t_crit * ep, dif + t_crit * ep)

relata()
relata("4. TESTE PRINCIPAL (confirmatório, previsto no protocolo)")
relata(f"Welch: t = {welch.statistic:.4f} | gl = {welch.df:.2f} | p = {welch.pvalue:.4f}")
relata(f"Decisão (alfa = {ALFA}): {'rejeitar H0' if welch.pvalue < ALFA else 'não rejeitar H0'}")
relata(f"Diferença A - B = {dif:.3f} p.p. | IC 95% = [{ic[0]:.3f}; {ic[1]:.3f}] p.p.")

# ---------------------------------------------------------------------------
# 6. Tamanho de efeito: d de Cohen (DP combinado)
# ---------------------------------------------------------------------------
sp = np.sqrt(((nA - 1) * A.var(ddof=1) + (nB - 1) * B.var(ddof=1)) / (nA + nB - 2))
d = dif / sp
relata(f"d de Cohen = {d:.3f}")

# ---------------------------------------------------------------------------
# 7. Análise de sensibilidade: Mann-Whitney bilateral
# ---------------------------------------------------------------------------
mw = stats.mannwhitneyu(A, B, alternative="two-sided")
relata()
relata("5. SENSIBILIDADE (Mann-Whitney bilateral)")
relata(f"U (grupo A) = {mw.statistic:.0f} | p = {mw.pvalue:.4f}")

# ---------------------------------------------------------------------------
# 8. Relevância prática (em m²) e poder
# ---------------------------------------------------------------------------
m2 = AREA_BAIA / 100  # converte p.p. da baia em m²


def poder(d_alvo, alfa=ALFA):
    """Poder do teste t bilateral para dois grupos (aproximação pela t não central)."""
    gl = nA + nB - 2
    nc = d_alvo * np.sqrt(nA * nB / (nA + nB))
    tc = stats.t.ppf(1 - alfa / 2, gl)
    return 1 - stats.nct.cdf(tc, gl, nc) + stats.nct.cdf(-tc, gl, nc)


d_min_80 = brentq(lambda x: poder(x) - 0.80, 0.05, 1.5)

relata()
relata("6. RELEVÂNCIA PRÁTICA E PODER")
relata(f"Médias em área: A = {A.mean() * m2:.2f} m² | B = {B.mean() * m2:.2f} m²")
relata(f"Diferença = {dif * m2:.2f} m² | IC 95% = [{ic[0] * m2:.2f}; {ic[1] * m2:.2f}] m²")
relata(f"Menor efeito detectável com poder de 80%: d = {d_min_80:.2f} "
       f"(= {d_min_80 * sp:.2f} p.p. = {d_min_80 * sp * m2:.2f} m²)")
relata(f"Poder para o efeito observado (d = {d:.2f}): {poder(d):.0%}")

(RESULTADOS / "resultados.txt").write_text("\n".join(saida) + "\n", encoding="utf-8")

# ---------------------------------------------------------------------------
# 9. Figura 1: pontos individuais, mediana e média com IC 95%
# ---------------------------------------------------------------------------
rng = np.random.default_rng(SEMENTE)
fig, ax = plt.subplots(figsize=(6, 3.6))
for pos, (x, cor) in enumerate(((A, "tab:blue"), (B, "tab:orange"))):
    ax.scatter(pos + rng.uniform(-0.12, 0.12, len(x)), x, s=14, alpha=0.6, color=cor)
    ax.hlines(np.median(x), pos - 0.25, pos + 0.25, color="tab:blue", lw=1.5)
    meia = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    ax.errorbar(pos, x.mean(), yerr=meia, fmt="D", color=cor, markersize=5, capsize=3)
ax.set_xticks([0, 1], [f"Grupo A\n3,75 m²/bezerro (n={nA})", f"Grupo B\n4,29 m²/bezerro (n={nB})"])
ax.set_xlim(-0.6, 1.6)
ax.set_ylabel("Porcentagem da baia utilizada (%)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(RESULTADOS / "figura1.png", dpi=200)

print(f"\nArquivos gerados em: {LIMPOS} e {RESULTADOS}")
