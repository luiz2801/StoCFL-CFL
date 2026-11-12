# Relatório: efeito do dropout com retorno no StoCFL

Fonte dos dados: as duas grades do dropout com retorno, ambas com o `StoCFL-FCC+CFL.py`, `n = 240` clientes, 50 rodadas e seeds 0 a 9 (GPU):

| Grade | Notebook | Executada em | Dados | Treino | Execuções | Resultados |
|---|---|---|---|---|---|---|
| 1. Clusterização | [teste-dropout.ipynb](../projetos/StoCFL/teste-dropout.ipynb) | 2026-11-09 ([D-037](decisoes.md)) | Rotated MNIST, `k` = 8 e 16 grupos de rotação, `τ = 0.75` | não (`--train 0`) | 120 | `projetos/StoCFL/logs/resultados-dropout.json` (cópia versionada: [resultados-dropout.json.gz](resultados/resultados-dropout.json.gz)) |
| 2. Aprendizado | [teste-dropout-treino.ipynb](../projetos/StoCFL/teste-dropout-treino.ipynb) | 2026-11-10 a 12 ([D-052](decisoes.md), [D-055](decisoes.md)) | MNIST sem rotação, rótulos non-IID por Dirichlet, `α` = 0.5 e 1.0, `τ` = 0.84683 e 0.8 | sim (`--train 1`, `lr = 0.1`, 5 épocas, `μ = 0.05`) | 240 | `projetos/StoCFL/logs/resultados-dropout-treino.json.gz` (fora do git, [D-053](decisoes.md)) |

Nas duas grades: `m` = 100% e 50% (240 e 120 clientes por rodada), sem dropout e com `d` = 0.05 e 0.1, ausências de 1 a 10 rodadas (`--drop_rounds 10`). Os números vêm dos JSONs e já estão no [guia](guia.md), seção 4.11, exceto dois fatos medidos para este relatório nos mesmos JSONs, sem rodar nada (seções 2 e 4.1). Médias nas 10 seeds; o Wilcoxon é pareado por seed (dropout − sem dropout), sem correção para comparações múltiplas, e com 10 seeds o menor `p` possível é 0,002. Fatos medidos estão separados de hipóteses no texto.

## 1. O que o dropout faz

A cada rodada, um cliente disponível cai com probabilidade `d` e fica fora de 1 a 10 rodadas (duração uniforme). Quem está fora não é sorteado, e os `m` clientes da rodada são sorteados **só entre os disponíveis** ([plano](plano-dropout-stocfl.md), D-032; guia 4.1). O dropout, portanto, não apaga nada do que o cliente já fez: o `Ψ` dele continua guardado, e o cluster dele continua existindo. O que muda é **quando** e **com quem** ele é sorteado.

| Grandeza (medida, igual nas duas grades) | Sem dropout | `d = 0.05` | `d = 0.1` |
|---|---|---|---|
| Disponibilidade média | 1 | 0,789 | 0,653 |
| Fórmula `1/(1 + d·(L_max+1)/2)` | 1 | 0,784 | 0,645 |
| Participantes por rodada, `m = 100%` | 240 | 189,4 | 156,8 |
| Participantes por rodada, `m = 50%` | 120 | 120 | 120 |
| 1ª rodada com todos os clientes observados, `m = 100%` | 1 | 10,7 | 10,9 |
| 1ª rodada com todos os clientes observados, `m = 50%` | 10,4 | 14,1 | 14,6 |

- **Com `m = 50%` o nº de participantes não muda**, porque sempre havia ao menos 120 clientes disponíveis. Muda só quem participa: quem tem ausências longas participa menos.
- **Com `m = 100%` o dropout corta 21% e 35% dos participantes** de cada rodada. É só nesse caso que ele reduz a quantidade de clientes vistos por rodada.
- A cobertura chegou a 100% em todas as 360 execuções: em 50 rodadas todo cliente foi observado, com ou sem dropout.

## 2. As duas grades usam exatamente o mesmo sorteio

Medido para este relatório: para cada seed, `m` e `d`, os clientes sorteados e os indisponíveis são **idênticos em todas as 50 rodadas** nas duas grades (comparadas as 240 execuções da grade 2 com as duas execuções da grade 1 de mesma seed, `m` e `d`: 480 pares, nenhuma diferença). O sorteio só depende de `random.seed(seed)`, de `n`, de `m` e do processo de disponibilidade, e não dos dados, de `τ`, de `k`, de `α` nem do treino. Na grade 2, o smoke test já tinha mostrado que `--train 1` não muda o sorteio nem a partição (V1, D-048).

Consequência: **a diferença de comportamento entre as duas grades vem só dos dados e do `τ`**, e não de uma realização diferente do dropout. A tabela da seção 1 vale para as duas.

## 3. Grade 1: clusterização em Rotated MNIST (`--train 0`)

| Resultado | Valor |
|---|---|
| Partição final | ARI = 1,0 e `k` clusters nas 120 execuções, com e sem dropout, para `k` = 8 e 16. Nenhum cluster misturado, nenhuma seed colapsou. |
| Rodada estável, `m = 100%` | 1 sem dropout; 10,7 (`d = 0.05`) e 10,9 (`d = 0.1`); Δ = +9,7 e +9,9 rodadas, `p = 0,002` |
| Rodada estável, `m = 50%` | 10,4; 14,1 e 14,6; Δ = +3,7 (`p = 0,098`) e +4,2 (`p = 0,027`) |
| Rodada estável × cobertura | Em todas as execuções, a rodada estável é **exatamente** a 1ª rodada com cobertura de 100%, e o ARI chega a 1,0 nela, nunca antes. Por isso `k` = 8 e 16 têm a mesma rodada estável. |

**Leitura:** com grupos de rotação bem separados, a partição final não depende da ordem em que os clientes são vistos. O dropout só **adia a observação do último cliente**, e a partição fica pronta quando ele aparece. Sem treino, `Ψ` é fixo (guia 4.5), então nada mais muda.

Com `k = 16` e `τ = 0.75`, porém, a margem até o colapso é pequena (0,010 na seed 0; [relatório de m, k e τ](relatorio-m-k-tau.md)). Nenhuma seed colapsou, mas a grade não testa o que o dropout faria com um `τ` ainda mais perto da borda.

## 4. Grade 2: aprendizado com rótulos Dirichlet (`--train 1`)

Sem rotação, não há gabarito de grupos: o nº de clusters é um resultado, decidido por `τ` sobre as distribuições de rótulos, que não formam grupos nítidos (silhueta 0,15 a 0,26; D-046).

### 4.1 Partição

| `τ` | `α` | `m` | Clusters finais: sem / `d = 0.05` / `d = 0.1` | Maior cluster | Singletons | Rodada estável | Δ clusters (`p`) |
|---|---|---|---|---|---|---|---|
| 0.84683 | 0.5 | 100% | 75 / 81 / 84 | 47 / 41 / 35 | 58 / 62 / 63 | 1,6 / 9,5 / 13,7 | +6,2 / +9,6 (0,002) |
| 0.84683 | 0.5 | 50% | 98 / 97 / 97 | 22 / 22 / 21 | 71 / 70 / 71 | 12,8 / 18,3 / 18,8 | −0,8 / −1,2 (≥ 0,19) |
| 0.84683 | 1.0 | 100% | 120 / 124 / 126 | 35 / 32 / 29 | 93 / 95 / 97 | 1,7 / 12,2 / 15,8 | +3,3 / +6,2 (0,002) |
| 0.84683 | 1.0 | 50% | 137 / 137 / 138 | 20 / 20 / 19 | 102 / 103 / 103 | 12,2 / 20,0 / 24,3 | −0,5 / +0,7 (≥ 0,14) |
| 0.8 | 0.5 | 100% | 31 / 40 / 45 | 192 / 167 / 152 | 25 / 31 / 34 | 1,1 / 10,2 / 14,1 | +9,4 / +14,5 (0,002) |
| 0.8 | 0.5 | 50% | 62 / 62 / 62 | 36 / 34 / 39 | 40 / 41 / 41 | 11,7 / 15,9 / 17,2 | +0,6 / −0,2 (≥ 0,72) |
| 0.8 | 1.0 | 100% | 52 / 60 / 66 | 132 / 118 / 105 | 40 / 44 / 48 | 1,7 / 11,4 / 13,0 | +7,4 / +13,8 (0,002) |
| 0.8 | 1.0 | 50% | 84 / 84 / 86 | 31 / 30 / 32 | 53 / 54 / 55 | 15,0 / 17,9 / 23,0 | +0,7 / +1,8 (≥ 0,28) |

- **Ao contrário da grade 1, o dropout muda a partição final**, mas só com `m = 100%`: mais clusters (+3 a +15), um maior cluster menor e mais singletons, em todas as seeds. Com `m = 50%`, o nº de clusters não muda.
- **Com `m = 100%`, o dropout aproxima a partição da de `m = 50%`.** Sem dropout, `m = 100%` dá menos clusters e um cluster maior do que `m = 50%` (com `τ = 0.8` e `α = 0.5`, 31 clusters e um gigante de 192 clientes, contra 62 e 36). Com dropout, o gigante encolhe para 152 e os clusters sobem para 45. Hipótese, compatível com os dados e com a leitura da D-050: com `m = 100%` todo cluster é comparado com todos em toda rodada, e a fusão por *single linkage* encadeia mais. Com menos participantes por rodada, os encontros são menos frequentes, e como a fusão depende da ordem (o centro de um cluster muda a cada fusão, e as fusões são irreversíveis, guia 4.12 #9), o caminho acaba numa partição mais fragmentada. Com `m = 50%` o nº de participantes é o mesmo com e sem dropout, e a partição também.
- **A rodada estável deixa de ser a da cobertura total.** Medido para este relatório: por execução, a rodada estável fica de 9 rodadas antes a 33 rodadas depois da 1ª rodada com todos os clientes observados (na grade 1, sempre igual). Antes: os últimos clientes observados ficam singletons e não mudam a partição. Depois: clusters já observados ainda se fundem quando são sorteados juntos, porque os cossenos ficam perto de `τ`. Mesmo assim, o dropout atrasa a estabilização: +7,9 a +14,1 rodadas com `m = 100%` (`p = 0,002`) e +2,9 a +12,1 com `m = 50%`.

### 4.2 Acurácia

Acurácia final = média das rodadas 41 a 50, ponderada pelos participantes de cada cluster avaliado. "Ponderada" = no teste balanceado, mas com o recall de cada classe pesado pela distribuição de rótulos do cluster (`Σ_c p_c · recall_c`, D-047), que mede o modelo do cluster nos dados que ele representa.

| `τ` | `α` | `m` | Cluster, teste balanceado: sem / 0.05 / 0.1 | Cluster, ponderada: sem / 0.05 / 0.1 | Global | Ganho ponderado sobre o global, sem dropout |
|---|---|---|---|---|---|---|
| 0.84683 | 0.5 | 100% | 0,763 / 0,747 / 0,734 | 0,912 / 0,912 / 0,910 | 0,895–0,896 | +0,016 (10 de 10 seeds) |
| 0.84683 | 0.5 | 50% | 0,704 / 0,702 / 0,705 | 0,911 / 0,910 / 0,909 | 0,895 | +0,014 (10 de 10) |
| 0.84683 | 1.0 | 100% | 0,773 / 0,765 / 0,756 | 0,904 / 0,902 / 0,899 | 0,899 | +0,005 (10 de 10) |
| 0.84683 | 1.0 | 50% | 0,737 / 0,736 / 0,736 | 0,898 / 0,897 / 0,897 | 0,899 | −0,002 (1 de 10) |
| 0.8 | 0.5 | 100% | 0,854 / 0,836 / 0,817 | 0,898 / 0,899 / 0,899 | 0,895–0,896 | +0,002 (7 de 10) |
| 0.8 | 0.5 | 50% | 0,759 / 0,759 / 0,759 | 0,910 / 0,909 / 0,908 | 0,895 | +0,013 (10 de 10) |
| 0.8 | 1.0 | 100% | 0,847 / 0,834 / 0,822 | 0,900 / 0,899 / 0,898 | 0,899 | +0,001 (5 de 10) |
| 0.8 | 1.0 | 50% | 0,782 / 0,781 / 0,781 | 0,901 / 0,900 / 0,900 | 0,899 | +0,002 (10 de 10) |

- **O modelo global não muda** com o dropout (diferença de no máximo 0,0004). Hipótese: o `gmodel` é o FedAvg de todos os participantes, e 157 a 240 clientes por rodada, ou 120 com outra composição, dão médias equivalentes nesses dados.
- **A acurácia ponderada dos modelos de cluster quase não muda:** o ganho ponderado varia de −0,48 ponto (`τ = 0.84683`, `α = 1.0`, `m = 100%`, `d = 0.1`) a +0,17 (`τ = 0.8`, `α = 0.5`, `m = 100%`). Com `d = 0.1` há perda em 7 dos 8 casos, consistente entre as seeds (`p` de 0,002 a 0,027), mas abaixo de meio ponto.
- **A única melhora vem do cluster gigante:** com `τ = 0.8`, `α = 0.5` e `m = 100%`, o dropout quebra o cluster de 192 clientes, que é quase o modelo global, e o ganho ponderado sobe de +0,2 para +0,4 ponto (`p = 0,004` com `d = 0.05`).
- **No teste balanceado, a acurácia do cluster cai até 3,7 pontos, mas só com `m = 100%`** (`p = 0,002`); com `m = 50%`, no máximo 0,2 ponto. É efeito de composição: o dropout deixa clusters menores e mais especializados, que medem pior num teste de 10 classes balanceadas, sem perder nos próprios dados (a ponderada não muda). O teste balanceado, sozinho, faria o dropout parecer muito pior do que é.

### 4.3 Onde a clusterização ajuda

Separando os clusters avaliados em singletons e clusters de 2 ou mais clientes (D-051), com `τ = 0.84683`:

- os de **2 ou mais** ganham +1,9 a +2,1 pontos sobre o global com `α = 0.5` e +1,0 a +1,3 com `α = 1.0`;
- os **singletons** ficam perto ou abaixo do global (de +0,6 a −1,9 pontos, o pior com `α = 1.0` e `m = 50%`; com `τ = 0.8`, até −2,3) e são 24% a 45% dos participantes.

O ganho da clusterização vem dos clusters de mais de um cliente; o modelo de um cliente só (perto do Ditto, guia 4.9) não ajuda. O dropout mexe pouco nisso: com `m = 100%` ele aumenta a fração de participantes em singletons (de 24% para 27% com `α = 0.5` e de 39% para 41% com `α = 1.0`) e piora o ganho dos singletons (de +0,6 para 0,0 e de −0,8 para −1,5 pontos com `d = 0.1`), enquanto o dos clusters de 2+ quase não muda (−0,3 ponto ou menos).

### 4.4 Velocidade

- A acurácia ponderada do cluster passa de 0,90 **1,8 a 7,1 rodadas mais tarde** com `τ = 0.84683` e `m = 100%` (`p` ≤ 0,012); com `m = 50%`, de 0,2 a 3,7 rodadas mais tarde, com significância só em 2 dos 8 casos.
- Com `τ = 0.8` e `m = 100%`, 2 a 5 seeds não chegam a 0,90, e a média só das que chegam não é comparável entre os cenários.
- O atraso é o mesmo fenômeno da grade 1: o dropout adia a observação dos clientes e a formação dos clusters, e os modelos de cluster partem de mais longe.

## 5. As duas grades lado a lado

| Pergunta | Grade 1 (rotação, sem treino) | Grade 2 (Dirichlet, com treino) |
|---|---|---|
| O dropout muda a partição final? | Não (ARI 1,0 em todas) | Sim com `m = 100%` (mais clusters e menores); não com `m = 50%` |
| O dropout atrasa a estabilização? | Sim: +10 rodadas com `m = 100%`, +4 com `m = 50%` | Sim: +8 a +14 com `m = 100%`, +3 a +12 com `m = 50%` |
| A rodada estável é a da cobertura total? | Sempre | Não (de −9 a +33 rodadas) |
| O dropout muda a acurácia? | — | Global: não. Cluster, ponderada: menos de 0,5 ponto. Cluster, teste balanceado: até −3,7 pontos com `m = 100%`, por composição |
| Por que | Grupos bem separados: a ordem de observação não importa | Cossenos perto de `τ`, sem grupos nítidos: a ordem das fusões importa |

O mecanismo é um só nas duas grades: **o dropout atrasa a observação e reduz os encontros entre clusters**. Ele só vira mudança de resultado quando a partição depende da ordem dos encontros, como com os rótulos Dirichlet, e só quando reduz os participantes por rodada, como com `m = 100%`.

## 6. Resumo operacional

1. **Com o sorteio entre os disponíveis, o dropout com retorno não é um risco para a qualidade final** nestes cenários: a partição em Rotated MNIST é a mesma, e os modelos de cluster perdem menos de meio ponto nos próprios dados.
2. **O custo é tempo:** conte com ~10 rodadas a mais até a partição estabilizar com `d` de 0,05 a 0,1 e ausências de até 10 rodadas, e com algumas rodadas a mais para a acurácia.
3. **Se `m` for menor do que os clientes disponíveis, o dropout quase não aparece** (`m = 50%`). Ele pesa quando o servidor quer todos (`m = 100%`) e fica com menos.
4. **Avalie o modelo de cluster nos dados que ele representa.** No teste balanceado, a fragmentação causada pelo dropout parece perda de acurácia.
5. **A conclusão depende do `τ`.** Com dados non-IID, um `τ` que gera um cluster gigante (0.8 com `m = 100%`) é o que o dropout mais muda, e de um jeito que até ajuda; com um `τ` que gera muitos singletons, a clusterização ajuda pouco com ou sem dropout.

## 7. Limites deste relatório

- **Cobertura sempre de 100%.** Em 50 rodadas, todo cliente foi observado em todas as execuções. As grades não mostram o que acontece quando o dropout deixa clientes nunca observados (menos rodadas, `m` menor, `d` ou ausências maiores).
- **Só a lei por cliente.** A queda de um grupo inteiro de uma vez, o regime que o sorteio uniforme não reproduz, ficou fora do escopo (D-032).
- **Treino longe da convergência.** O modelo global ainda sobe ~0,5 ponto entre as rodadas 40 e 50 (de 0,892 para 0,898 com `α = 0.5`, `m = 100%`, sem dropout), então as acurácias finais são de um treino em andamento.
- **10 seeds e muitos testes.** O Wilcoxon tem pouco poder e não foi corrigido para comparações múltiplas; os `p = 0,002` significam "mesmo sinal nas 10 seeds", não um efeito grande.
- **`τ` e gabarito.** A grade 2 vale para os dois `τ` testados, escolhidos contra um gabarito fraco (D-046, D-050). A grade 1 vale para `τ = 0.75`, perto da borda inferior de `k = 16`.
- **Hipóteses não testadas:** a explicação da seção 4.1 (por que o dropout fragmenta a partição com `m = 100%`) e a do modelo global (seção 4.2) são compatíveis com os dados, mas não foram isoladas por um experimento. O simulador da fusão (D-046), que refaz a partição a partir dos `Ψ` e do sorteio, permitiria testá-las sem rodar o script.
- **Conferência da cobertura.** Na grade 2, a conferência contra o `psi.pkl` se perdeu em 232 das 240 execuções (D-055); no lugar dela, o simulador reproduziu a partição de 238 das 240 em todas as rodadas.
- **Um modelo, um conjunto de dados, um script.** Só o `StoCFL-FCC+CFL.py` tem `--drop` (guia 4.12 #13).
