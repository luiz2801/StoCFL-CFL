# Relatório: relação entre `m`, `k` e `τ` na clusterização do StoCFL

Fonte dos dados: saídas do notebook [teste-fracao-clientes.ipynb](../projetos/StoCFL/teste-fracao-clientes.ipynb), executado em 2026-11-06 (Rotated MNIST, `n = 240` clientes, 50 rodadas, seed 0, só clusterização com `--train 0`, GPU). Os números são de **uma seed e uma execução por célula**; as bordas de `τ` só são conhecidas até o vizinho avaliado (intervalos de ~0.03). Fatos medidos estão separados de hipóteses no texto. Os logs dessas execuções foram apagados em 2026-11-10 e os dados estão em `projetos/StoCFL/logs/resultados-fracao-clientes.json` (não versionado; [D-040](decisoes.md)).

## 1. Os três parâmetros

| Símbolo | O que é | Onde atua |
|---|---|---|
| `k` | nº de grupos reais (rotações igualmente espaçadas: 90°, 45° ou 22,5° entre grupos vizinhos). É a propriedade **dos dados**, não do algoritmo. | Define o gabarito e quão parecidos são os grupos vizinhos. |
| `τ` | limiar de cosseno: dois clusters se fundem se `cos > τ` (guia 4.1, 4.9). | Decide **o que** se funde. |
| `m` | fração dos `n` clientes sorteada por rodada (`num_per_round = m·n`). | Decide **quando** (e se) as fusões acontecem. |

A ideia central: `τ` e `k` decidem se a partição **correta é alcançável**; `m` decide se ela é **alcançada** em 50 rodadas. Os dois efeitos são quase independentes, com uma interação entre `m` e `k` (seção 4).

## 2. `k` × `τ`: a janela de `τ` que recupera os grupos

Intervalo de `τ` com ARI máximo (maior `τ` ótimo avaliado, `m` = 100% e 25%, que coincidem):

| `k` | Ângulo entre grupos | `τ` mínimo que funciona (borda inferior em) | `τ` máximo que funciona (borda superior em) | Largura | `τ` sugerido (centro) |
|---|---|---|---|---|---|
| 4 | 90° | (0.3125, 0.3438] | [0.9062, 0.9375) | ~0.56 | 0.63 |
| 8 | 45° | (0.4375, 0.4688] | [0.9375, 0.9688) | ~0.47 | 0.70 |
| 16 | 22,5° | (0.7188, 0.75] | [0.9688, 1.0) | ~0.22 | 0.86 |

Leitura:

- **A borda inferior sobe com `k`** (≈0.34 → 0.47 → 0.75). Hipótese (compatível com os dados, e sustentada pela medição do cosseno na seção seguinte, que os dados originais não traziam): grupos vizinhos ficam mais parecidos quanto menor o ângulo, então o cosseno entre eles é mais alto e `τ` precisa ser maior para não os fundir.
- **A borda superior quase não muda** (0.91 → 0.97, subindo pouco). Acima dela, o cosseno entre clientes do **mesmo** grupo (que têm dados diferentes) já não passa de `τ`, e o grupo se fragmenta. O motivo da pequena subida com `k` não é explicado por estes dados.
- **A janela estreita com `k`**: de ~0.56 para ~0.22. Quanto mais grupos próximos, mais fino precisa ser o ajuste de `τ`.
- **O `τ = 0.5` do artigo** (padrão dos scripts) funciona para `k = 4` e `k = 8`, mas **falha para `k = 16`**: em `τ = 0.5`, `m` = 100% e 25% dão 1 cluster e `m` = 10% dá 3 (1 gigante e ~2 clientes não sorteados), todos com ARI 0. Já o `τ = 0.9` do notebook está dentro da janela para os três `k`, mas **perto da borda superior para `k = 4`** (0.9062 funciona, 0.9375 não): margem pequena.

### Medição dos cossenos (adicionada em 2026-11-10)

A saída dos scripts tinha a lista de cossenos entre os clientes na rodada 0. Com `m` = 100% (seed 0), a partição depois da rodada 0 é exatamente o conjunto de componentes conexas do grafo "cosseno > `τ`" sobre essa matriz (conferido nas 48 execuções com `m` = `n`), então a janela de `τ` pode ser **calculada** dela: a borda inferior é o peso da primeira aresta, em ordem decrescente de cosseno, que junta grupos diferentes, e a superior é o peso em que o último grupo fica conexo. As seis bordas previstas caem dentro dos intervalos medidos:

| `k` | Borda inferior prevista | Intervalo medido | Borda superior prevista | Intervalo medido | Maior cosseno entre os `k` clusters corretos |
|---|---|---|---|---|---|
| 4 | 0.3389 | (0.3125, 0.3438] | 0.9264 | [0.9062, 0.9375) | 0.262 |
| 8 | 0.4549 | (0.4375, 0.4688] | 0.9560 | [0.9375, 0.9688) | 0.382 |
| 16 | 0.7397 | (0.7188, 0.75] | 0.9715 | [0.9688, 1.0) | 0.729 |

- A borda inferior sobe com `k` e o cosseno entre os grupos vizinhos também (0.262 → 0.382 → 0.729), como a hipótese acima previa.
- A borda inferior fica **acima** do maior cosseno entre os clusters finais nos três `k`: quem decide a fusão errada são os cossenos entre **clientes** (cadeia de vizinhos, *single linkage*), e não os entre as médias dos clusters.
- Para `k = 16`, `τ = 0.75` fica só **0.010** acima da borda inferior prevista (0.7397), na seed 0. É uma margem muito menor do que os intervalos de ~0.03 da tabela da seção 2 sugerem.
- Vale para uma seed e `n = 240`. A matriz está em `cossenos_clientes_rodada_0` do JSON.

### Como as falhas aparecem

- **`τ` abaixo da borda inferior:** fusão de grupos diferentes, **irreversível** (guia 4.12 #9). Como a fusão é *single linkage* e transitiva (4.1), basta uma cadeia de vizinhos: com `k = 16`, `m` = 100%, `τ = 0.719` dá **1 cluster** e `τ = 0.75` dá 16 (transição abrupta). A pureza cai (`1/k` quando tudo se funde).
- **`τ` acima da borda superior:** clusters demais, mas **sem misturar grupos** (pureza 1.0). Em `τ = 0.9375` com `k = 4`, `m` = 100%: 12 clusters (ARI 0.955). Em `τ = 1.0` ninguém se funde: 240 clusters, ARI 0, pureza 1.
- Por isso a **pureza sozinha engana** (singletons têm pureza 1): leia sempre junto com ARI e nº de clusters.

## 3. `m` × `τ`: `m` não desloca a janela (para `m` ≥ 25%)

- Para `m` = 100% e 25%, as janelas de `τ` são **idênticas** nos três `k`, com o mesmo ARI em cada `τ`. Para `m` = 10% a janela é a mesma ou ligeiramente mais larga embaixo (`k = 8`: borda inferior em 0.4375 em vez de 0.4688), e o ARI máximo cai (seção 4).
- Em `τ` = 0.438 com `k = 8`, `m` = 100% funde dois grupos vizinhos (7 clusters, ARI 0.868) e `m` = 10% não (10 clusters, ARI 0.990). Hipótese: com poucos clientes por rodada, a fusão errada leva mais tempo para ocorrer. **Isso não é proteção**: o que a salva aqui é a amostragem, e em `τ` menores o `m` = 10% também se funde (3 clusters, ARI 0).
- Na prática: **escolha `τ` olhando `k` e os dados; `m` não precisa entrar nessa escolha**, desde que seja alto o bastante para o item seguinte.

## 4. `m` × `k`: quando a partição correta é alcançada

Com `τ` dentro da janela (o ARI fica constante em `τ` dentro dela), o resultado final depende só de `m` e `k`:

| `m` | Clientes/rodada | Clientes/grupo/rodada (`m·n/k`) para `k` = 4 / 8 / 16 | Rodada estável | Clusters finais `k` = 4 / 8 / 16 | ARI `k` = 4 / 8 / 16 |
|---|---|---|---|---|---|
| 100% | 240 | 60 / 30 / 15 | 1 | 4 / 8 / 16 | 1.00 / 1.00 / 1.00 |
| 50% | 120 | 30 / 15 / 7,5 | 10 | 4 / 8 / 16 | 1.00 / 1.00 / 1.00 |
| 25% | 60 | 15 / 7,5 / 3,75 | 20 | 4 / 8 / 16 | 1.00 / 1.00 / 1.00 |
| 10% | 24 | 6 / 3 / 1,5 | 49–50 | 6 / 10 / 22 | 0.989 / 0.990 / 0.965 |
| 5% | 12 | 3 / 1,5 / 0,75 | 49–50 | 35 / 56 / 106 | 0.820 / 0.737 / 0.480 |

Pureza final 1.0 e nenhum cluster misto em todas as 15 células: **`m` baixo nunca misturou grupos, só deixou clusters sobrando**.

### Dois mecanismos distintos

1. **Cobertura (só depende de `m`).** Um cliente só entra na fusão depois de ser sorteado (guia 4.1, 4.5), e sem ser sorteado continua um cluster unitário. A cobertura final foi **a mesma para os três `k`** (0.99 com `m` = 10%, 0.89 com `m` = 5%), porque a seed e a amostragem são as mesmas. Os clientes não observados explicam quase todo o excesso de clusters com `m` = 10%: `k` = 4 → 6 clusters (4 + ~2 não observados) e `k` = 8 → 10 (8 + ~2). Também explica por que `m` = 10% dá **3 clusters** (e não 1) em `τ` ≤ 0.25: 1 cluster gigante mais ~2 clientes nunca sorteados. A cobertura esperada é `1 − (1 − m)^50`: 99,5% para `m` = 10% e 92% para `m` = 5%.
2. **Oportunidades de fusão (depende de `m` **e** `k`).** Dois clusters do mesmo grupo só se fundem se ambos forem sorteados **na mesma rodada**. Com poucos clientes por grupo por rodada, esse encontro é raro. Isto aparece só quando `m·n/k` é pequeno: com `m` = 10% e `k` = 16 (1,5 por grupo) sobram **6** clusters além de `k`, dos quais ~2 não observados e **~4 fragmentos de clientes observados que não se encontraram**; com `k` = 4 e 8 não sobra nenhum além dos não observados. Com `m` = 5%, o excesso é 31, 48 e 90 clusters para `k` = 4, 8 e 16, com ~26 não observados em todos: o restante (~5, ~22 e ~64) são fragmentos, e **cresce com `k`**.

Consequência: **o mesmo `m` fica pior à medida que `k` cresce.** Com `m` = 5%, o ARI cai de 0.82 (`k` = 4) para 0.48 (`k` = 16). Pelos dados, `m·n/k ≥ ~3,75` foi suficiente (ARI 1.0 com `m` = 25%, `k` = 16), e `≤ 1,5` já deixou resíduo; entre esses pontos não há medida. É uma regra empírica de um cenário, não um limite teórico.

### Velocidade (rodada estável)

A rodada em que a partição para de mudar foi 1, 10 e 20 para `m` = 100%, 50% e 25%, **igual para os três `k`**. Isso equivale a ~5·n sorteios (120·10 = 60·20 = 1200 = 5·240) e é ≈ `5/m` rodadas. Com `m` ≤ 10%, a partição ainda mudava perto da rodada 50. Com poucos pontos e uma seed, a "constante 5" é uma **observação**, não uma lei; ela não depende de `k` aqui, o que sugere que, com `τ` na janela, o tempo é dominado por quando os clientes são observados e encontrados, e não pelo `k`.

## 5. Resumo operacional

1. Escolha `τ` pelo **`k`** (e pelos dados): janela estreita para `k` grande. Se `k` for desconhecido, rode a busca de `τ` (seção 5 do notebook) com `--train 0`, como sugere o guia 4.9; prefira o **centro** da janela, que fica longe das duas bordas.
2. Escolha `m` pela **cobertura e pelas oportunidades de fusão**: `m·n/k` de alguns clientes por grupo por rodada, e `m` alto o bastante para cobrir quase todos os clientes em `com_round` rodadas (`1 − (1 − m)^rodadas`).
3. Não compense `m` baixo mexendo em `τ`: com `m` ≤ 10%, o ARI é constante em toda a janela. O limite é de amostragem, não de limiar.
4. Valores mal calibrados falham de formas diferentes: `τ` baixo **mistura grupos (irreversível)**; `τ` alto ou `m` baixo **fragmentam** grupos (sem mistura, e o `m` baixo se recupera com mais rodadas).

## 6. Limites deste relatório

- Uma seed e uma execução por célula: o `τ` mínimo/máximo e a "constante 5" podem mudar com outra partição dos dados; as bordas valem só até o vizinho avaliado.
- A busca de `τ` rodou só com `m` = 100%, 25% e 10% (não 50% nem 5%). As conclusões sobre `τ` com `m` = 5% e 50% vêm da tabela da seção 2 do notebook (`τ = 0.9`) e não de uma busca.
- Os cossenos intra e entre grupos não foram medidos diretamente; as explicações das bordas (seção 2) são hipóteses. O `cos_rec*.log` lista os pares ordenados e permitiria checá-las (guia 4.9).
- O cenário é só rotação do MNIST; a janela de `τ` depende do tipo de heterogeneidade (no artigo, rotação × rótulos muda a janela, guia 4.9).
