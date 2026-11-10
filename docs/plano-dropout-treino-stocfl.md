# Plano: dropout com retorno no StoCFL em ambiente de aprendizado federado (`--train 1`)

- **Situação:** plano com as decisões tomadas ([D-043](decisoes.md)). **Nada foi executado** além de uma calibração curta (seção 3, 2026-11-10); o notebook ainda não existe.
- **Branch:** `dropout-stocfl`.
- **Antecedentes:** o [plano do dropout](plano-dropout-stocfl.md) e o teste só de clusterização (`--train 0`, 120 execuções, [D-035](decisoes.md) e [D-037](decisoes.md)), em que o ARI final foi 1,0 com e sem dropout e o dropout só atrasou a rodada estável (guia, seção 4.11).

## 1. Objetivo

O teste anterior mostrou que a **clusterização** sobrevive ao dropout. Este plano mede o efeito do dropout com retorno no **aprendizado**: o StoCFL completo (`StoCFL-FCC+CFL.py --train 1`), com o treino bi-nível, em Rotated MNIST.

- **O algoritmo não recebe o nº de clusters.** Quem decide quantos clusters existem é o `τ = 0.75`, sobre os dados. O `k` (nº de rotações dos dados) nunca é entrada da clusterização: só gera a partição dos dados e escolhe o conjunto de teste de cada cluster na avaliação (a rotação do primeiro cliente do cluster). Ele **deixa de ser fator da grade** (D-043).
- Perguntas: o dropout muda a acurácia do modelo de cluster e do modelo global? Atrasa a convergência? A partição final continua correta com treino?

## 2. Decisões

Respostas do usuário em 2026-11-10, registradas em [D-043](decisoes.md).

| Item | Decisão |
|---|---|
| Dados | Rotated MNIST padrão, **4 rotações** (0°, 90°, 180°, 270°), `n = 240` clientes (1.000 amostras por cliente). Sem `--k` na linha de comando, então a pasta de dados é `datasets/rotated_mnist_240_<seed>` |
| Seeds | 0 a 9, as mesmas da grade anterior |
| Dropout | `d` = 0,05 e 0,1, com `--drop_rounds 10` (como na D-035), e o cenário **sem dropout** como referência (escolha de Claude, necessária para medir o efeito) |
| `m` | 100% e 50% (`--num_per_round` 240 e 120) |
| `τ` | 0.75 |
| Rodadas | 50 |
| Treino | Do artigo (Rotated MNIST, Tabela 1): `--lr 0.1 --epochs 5 --mu 0.05`, batch cheio (sem `--batch_size`) |
| Onde | Notebook novo `projetos/StoCFL/teste-dropout-treino.ipynb`, com a política 7 desde o início |

**Grade:** 10 seeds × 2 `m` × 3 cenários de dropout = **60 execuções**. Cada uma é o script chamado por `subprocess`, sem alterar o código do StoCFL:

```bash
../../.venv/bin/python StoCFL-FCC+CFL.py --n 240 --dataset mnist --com_round 50 \
    --num_per_round 240 --train 1 --tau 0.75 --seed 0 --process 0 \
    --lr 0.1 --epochs 5 --mu 0.05 [--drop 0.05 --drop_rounds 10]
```

## 3. O que a calibração de 2026-11-10 mediu

Execuções de 3 rodadas, `n = 240`, `--train 1`, GPU RTX A4000 (uma execução por vez). Os logs foram apagados depois.

| Fato | Resultado |
|---|---|
| **O treino não muda o sorteio nem a partição** | Em 2 execuções (seed 0 com `k = 8` e seed 1 com `k = 16`, `m` = 50%, `d = 0,1`), os clientes sorteados, o cluster de cada cliente em cada rodada e o `availability.pkl` foram **idênticos** aos de `--train 0` guardados em `resultados-dropout.json`. Faz sentido pelo código: `Ψ` é calculado na âncora, o treino só usa o gerador do `torch`, e o sorteio usa o `random` global. Consequência: a clusterização desta grade **repete** o que o `--train 0` daria com os mesmos parâmetros, e o que é novo é a **acurácia**. |
| Tempo, 4 rotações, `m` = 50% (`d = 0,1`) | Rodada 0: 21,5 s (observa os clientes); rodadas 1 e 2: 11,4 e 9,6 s |
| Tempo, 4 rotações, `m` = 100% (sem dropout) | Rodada 0: 62,5 s (observa 240 clientes e calcula 28.680 cossenos); rodadas 1 e 2: 16,7 e 16,1 s |
| Tempo por nº de rotações | O tempo cresce com as amostras por cliente: com `m` = 50% e `d = 0,1`, as rodadas custam ~10 s (4 rotações, 1.000 amostras por cliente) e ~20 s (8 rotações, 2.000) |
| Paralelismo | Duas execuções ao mesmo tempo na GPU (8 e 16 rotações, seed 1) levaram 150 s e 197 s, contra 69 s da de 8 rotações sozinha (seed 0), então **não há ganho: rodar em série** |
| Disco | `psi.pkl` de 1,3 GB (`m` = 50%) a 1,5 GB (`m` = 100%) por execução |
| Acurácia nas 3 primeiras rodadas | O modelo global (4 rotações, `m` = 100%) vai de ~0,30 a ~0,46 na rodada 2, então 50 rodadas com 5 passos de SGD por rodada ainda podem deixá-lo longe da convergência |

**Estimativa da grade** (a partir dos tempos acima; o tempo da rodada escala com os participantes: ~0,068 s por participante com `m` = 100%):

| `m` | Cenário | Min por execução | Execuções | Horas |
|---|---|---|---|---|
| 50% | 3 cenários (120 participantes em quase todas as rodadas) | ~9 | 30 | ~4,5 |
| 100% | sem dropout (240 participantes) | ~14,5 | 10 | ~2,4 |
| 100% | `d = 0,05` (~189) | ~11 | 10 | ~1,8 |
| 100% | `d = 0,1` (~157) | ~9,5 | 10 | ~1,6 |
| | **Total** | | **60** | **~10,5** |

Mais a geração das 9 partições novas (seeds 1 a 9, ~0,9 GB cada, **tempo não medido**). Tudo isso é estimativa: a primeira execução do passo 4 deve conferi-la.

## 4. Métricas

**Clusterização** (do `cluster.pkl` e do log, como no `teste-dropout.ipynb`, com as funções copiadas): nº de clusters, ARI e pureza contra os 4 grupos reais, cobertura, rodada estável, participantes e disponibilidade.

**Aprendizado** (novas). O log traz, por rodada e por cluster sorteado, `Round r, Cluster c - Global Test loss: L, acc: A` (modelo do cluster) e a linha `Round r, Global acc: [...]` (o `gmodel` nos mesmos conjuntos de teste, na mesma ordem). O `accuracy.pkl` traz as mesmas acurácias sem o id do cluster, então o notebook lê o log e confere com o `accuracy.pkl`. O teste de cada cluster é o da rotação do **primeiro membro**.

| Métrica | Definição |
|---|---|
| `acc_cluster[r]`, `acc_global[r]` | Média, ponderada pelos participantes de cada cluster na rodada, da acurácia do modelo do cluster e do `gmodel` |
| `acc_*_final` | Média das rodadas 41 a 50 (suaviza o ruído de uma rodada) |
| `ganho` | `acc_cluster − acc_global`: quanto a especialização por cluster ajuda |
| `rodada_limiar` | Primeira rodada com `acc_cluster ≥ LIMIAR_ACC` (padrão 0,90; ajustar depois de ver as curvas) |

Comparação dropout − sem dropout por seed, com Wilcoxon (sem correção para comparações múltiplas), para `acc_cluster_final`, `acc_global_final`, `ganho`, `rodada_limiar` e `rodada estável`.

**Gráficos (Plotly):** por rodada (média e faixa mín–máx entre as seeds, uma coluna por `m`): nº de clusters, ARI, acurácia do cluster, acurácia global e participantes. Caixas por seed das métricas finais. Matrizes de confusão 4×4 da partição final somadas nas seeds, para ver se o `τ = 0.75` fundiu grupos.

## 5. Passo a passo

Cada etapa é um commit atômico (política 6), com a documentação e o registro em `decisoes.md` no mesmo commit.

1. **Plano e decisões** (este documento, D-043 e os índices). Feito em 2026-11-10.
2. **Notebook `teste-dropout-treino.ipynb`**, versionado sem saídas. Parte das funções do `teste-dropout.ipynb` (copiadas, sem editar o original) e acrescenta a leitura da acurácia, as métricas e os gráficos da seção 4. Inclui desde o início a política 7: `DADOS_JSON`, a trava que recusa relançar a grade quando faltam os logs e o JSON já existe, e a célula que grava `logs/resultados-dropout-treino.json` (estrito, via arquivo temporário), com os dados brutos de cada execução: o cluster de cada cliente por rodada, os sorteados e os indisponíveis por rodada, os cossenos da última rodada e, **novo**, a acurácia de cada cluster por rodada (id, rotação de teste, participantes, acurácia do cluster e do global). O notebook também captura a saída padrão de cada execução e a confere antes de apagar os logs.
3. **Smoke test** com uma cópia reduzida (`n = 48`, 6 rodadas, seeds 0 e 1, os 3 cenários de dropout e os 2 `m`: 12 execuções). Verifica as células, a segunda execução reaproveitando as 12, a igualdade da partição e do sorteio entre `--train 0` e `--train 1` (a observação da seção 3, agora com 4 rotações) e a cobertura do log igual às chaves do `psi.pkl` (I5 do [plano do dropout](plano-dropout-stocfl.md)).
4. **Grade completa** (60 execuções, ~10,5 h), em segundo plano e só **depois da sua autorização**. Com `APAGAR_PSI = True`, o `psi.pkl` de cada execução concluída é apagado, e o disco fica em ~8 GB de dados novos mais os logs pequenos. O notebook reaproveita execuções concluídas, então uma interrupção se retoma reexecutando.
5. **Verificação e limpeza (política 7).** O notebook em modo `DADOS_JSON` tem de gerar os mesmos gráficos e tabelas que o modo com logs, e o JSON tem de bater com os logs (recalcular as métricas a partir dos dados brutos). Listar os caminhos dos logs da grade, conferir que cada um consta no JSON e só então apagá-los. Guardar o JSON compactado (`gzip -9 -n`) em `docs/resultados/`, com o `README.md` da pasta atualizado.
6. **Relato.** Os números no [guia](guia.md), seção 4.11, e a atualização das notas "o efeito sobre o ARI e o nº de clusters não foi medido" (guia 4.9 e 4.12 #13) para o que a grade mostrar com treino.

## 6. Verificação

| # | Verifica | Como |
|---|---|---|
| V1 | `--train 1` não muda o sorteio nem a partição | `cluster.pkl` e os sorteados iguais aos de uma execução `--train 0` com os mesmos parâmetros (smoke test) |
| V2 | Cobertura | a do log igual às chaves de `psi.pkl` (I5) |
| V3 | Acurácia lida do log | igual à do `accuracy.pkl` em todas as rodadas, com o nº de clusters e de valores batendo |
| V4 | Uma entrada por rodada | `cluster.pkl` e `accuracy.pkl` com 50 entradas, inclusive em rodada sem participantes |
| V5 | JSON | estrito (sem `NaN`), 60 execuções, 50 linhas por rodada por execução, métricas recalculáveis dos dados brutos |
| V6 | Modo `DADOS_JSON` | mesmas figuras e tabelas que o modo com logs, comparadas campo a campo, sem alterar o JSON |

## 7. Limites e cuidados

- **Efeito possivelmente nulo.** Na grade anterior todo cliente foi observado e o ARI final foi 1,0 em todos os cenários. Com `τ = 0.75` e 4 rotações, a partição final deve ser a mesma, e o dropout pode aparecer só nas primeiras rodadas ou nem aparecer na acurácia. Isso é um resultado válido. Em 50 rodadas o treino também pode estar longe da convergência (seção 3).
- **Acurácia por cluster tem viés de composição.** Só clusters sorteados são avaliados, e o teste é o da rotação do primeiro membro. Nas primeiras rodadas, antes de a partição estabilizar, há clusters pequenos e eventualmente misturados, e a média ponderada reflete isso. Leia a acurácia junto com a rodada estável e o nº de clusters, e compare as primeiras rodadas à parte.
- **Pareamento só pela seed.** A seed fixa a partição dos dados e (pelo código, não verificado) o modelo inicial, que é igual entre os cenários. O sorteio só é igual quando `m` = 100% e `d = 0`: com `m` = 50% ou com dropout, ele diverge. Com 10 seeds o Wilcoxon tem pouco poder.
- **`τ = 0.75` com 4 rotações** está dentro da janela medida para `k = 4` (borda inferior prevista 0,339 e superior 0,926, seed 0, `n = 240`; [relatório](relatorio-m-k-tau.md)), com folga bem maior que a de `k = 16`. As seeds 1 a 9 não têm a matriz de cossenos guardada. As matrizes de confusão e o ARI dirão se algum `τ` colapsou.
- **`cos_rec.log` só guarda a última rodada**, então a janela de `τ` das seeds 1 a 9 não pode ser recalculada depois.
- **Alterações que não são deste plano:** `docs/clusterizacao-ao-longo-do-tempo.ipynb`, `projetos/StoCFL/teste-fracao-clientes.ipynb`, `projetos/StoCFL/teste-fracao-clientes copy.ipynb` e `mimic_codes/` estão sem commit e não fazem parte deste trabalho. Adicione arquivos ao commit por nome.
- **Só o `StoCFL-FCC+CFL.py`** tem `--drop` (passo 5 do plano do dropout segue pendente).

## 8. Documentação a atualizar na implementação

| Arquivo | O que muda |
|---|---|
| [guia.md](guia.md) | 4.11 (o notebook novo e os resultados), 4.9 (linha de `--drop`) e 4.12 #13 (o efeito com treino passa a estar medido), 4.10 se o notebook ler arquivos novos |
| [README do StoCFL](../projetos/StoCFL/README.md) | Seção de testes com o notebook novo |
| [plano-dropout-stocfl.md](plano-dropout-stocfl.md) | A situação aponta para este plano |
| [README de docs/](README.md) | Índice, e o JSON novo em `resultados/` |
| [resultados/README.md](resultados/README.md) | O JSON compactado da grade |
| [decisoes.md](decisoes.md) | Uma entrada para cada decisão nova |
| Diagramas do StoCFL | **Não mudam**: o notebook não altera o script nem o fluxo (conferido: os diagramas batem com o código no que este plano usa) |
