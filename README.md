# Disponibilidade de espaço e uso da baia por bezerros leiteiros

Trabalho Final de Métodos de Computação Experimental e Quantitativa (PUC-Campinas, 2026).

Equipe: Geovana da Silva Barbosa, Mariana Costa Gonçalves da Silva e Sofia de Abreu Guimarães.

## Pergunta

Em bezerros leiteiros alojados em grupo em baias de 60 m², a disponibilidade de 4,29 m²/bezerro
(coortes de 14 animais), comparada a 3,75 m²/bezerro (coortes de 16 animais), está associada a
diferença na porcentagem da baia utilizada por cada bezerro?

- H0: μA = μB; H1: μA ≠ μB (bilateral), α = 0,05.
- A = 3,75 m²/bezerro (coortes 3 e 4, 32 bezerros); B = 4,29 m²/bezerro (coortes 1 e 2, 28 bezerros).
- VD: porcentagem da baia utilizada = 100 × `AllDayArea_95` ÷ 60, média por bezerro.
- Estudo observacional: as condições não foram sorteadas.

## Dados

- Fonte: Occhiuto, F.; Vázquez-Diosdado, J. A.; Carslake, C.; Kaler, J. (2022), conjunto de dados
  do artigo publicado na *Royal Society Open Science* 9: 212019.
- Dryad, DOI [10.5061/dryad.4qrfj6qbq](https://doi.org/10.5061/dryad.4qrfj6qbq), versão 5 (04/05/2022).
  Cópia idêntica no Zenodo (registro 6518187), usada pelo script para o download.
- Licença: CC0 1.0 (domínio público). Acesso em: 2 nov. 2026.
- Arquivo: `Calves_movement_space_use.csv` (685 linhas, 14 colunas). O script confere o MD5
  publicado no Zenodo.
- Observação: o README original da base inverte os rótulos das áreas. Seguimos o artigo:
  `AllDayArea_50` = área *core* (50%) e `AllDayArea_95` = área total (95%).

## Como reexecutar

Com Python 3.10 ou mais recente:

```
pip install -r requirements.txt
python analise.py
```

No Google Colab: envie `analise.py` e `requirements.txt` para a sessão e rode
`!python analise.py` numa célula.

O script baixa os dados brutos (se ainda não estiverem em `dados/brutos/`), gera os dados limpos,
os números e a figura. Os dados brutos nunca são editados à mão.

## Estrutura

```
analise.py                          script único: dados brutos -> números e figura
requirements.txt                    bibliotecas usadas
dados/brutos/                       CSV original, baixado pelo script
dados/limpos/medias_por_bezerro.csv uma linha por bezerro (unidade de análise)
resultados/resultados.txt           todos os números do relatório
resultados/figura1.png              Figura 1
```

## Resultados esperados

| Item | Valor |
|---|---|
| Médias (DP) | A: 66,41% (4,06); B: 65,62% (4,20) |
| Welch | t = 0,7345; gl = 56,38; p = 0,4657 |
| Diferença A − B e IC 95% | 0,785 p.p.; [−1,356; 2,927] |
| d de Cohen | 0,191 |
| Mann-Whitney (sensibilidade) | U (grupo A) = 494; p = 0,5002 |

Testado com numpy 2.4.6, pandas 3.1.1, scipy 1.17.1 e matplotlib 3.11.2.
