# Plano: dropout com retorno no StoCFL em ambiente de aprendizado federado (`--train 1`), com dados non-IID

- **Situação:** plano com as decisões tomadas ([D-043](decisoes.md) e [D-044](decisoes.md), que substitui parte da D-043). **Nada foi implementado nem executado.** Só foram feitas uma calibração de tempo (seção 3) e uma análise do non-IID (seção 4), ambas com scripts descartáveis fora do repositório. O código novo e o notebook ainda não existem.
- **Branch:** `dropout-stocfl`.
- **Antecedentes:** o [plano do dropout](plano-dropout-stocfl.md) e o teste só de clusterização (`--train 0`, 120 execuções, [D-035](decisoes.md) e [D-037](decisoes.md)), em que o ARI final foi 1,0 com e sem dropout e o dropout só atrasou a rodada estável (guia, seção 4.11).

## 1. Objetivo

O teste anterior mostrou que a **clusterização** sobrevive ao dropout, mas com dados IID dentro de cada rotação. Este plano mede o efeito do dropout com retorno no **aprendizado**: o StoCFL completo (`StoCFL-FCC+CFL.py --train 1`), em MNIST com **rótulos non-IID (Dirichlet)**, como no D-PRIDE.

- **O algoritmo não recebe o nº de clusters.** Quem decide quantos clusters existem é o `τ`, sobre os dados. Sem rotação, não há gabarito de grupos: o nº de clusters é um **resultado** da simulação (D-043, D-044).
- Perguntas: o dropout muda a acurácia do modelo de cluster e do modelo global? Atrasa a convergência? Como a partição (nº e tamanho dos clusters) muda com o dropout quando os dados são non-IID?

## 2. Decisões

Respostas do usuário em 2026-11-10, registradas em [D-043](decisoes.md) e [D-044](decisoes.md).

| Item | Decisão |
|---|---|
| Dados | **MNIST non-IID por Dirichlet nos rótulos, sem rotação**, `n = 240` clientes (D-044). No script, `k = 1`: um só conjunto de teste, o MNIST de teste inteiro, não rotacionado |
| `α` do Dirichlet | **0.5 e 1.0** (D-044). O D-PRIDE usa 0.1, 0.5, 1 e 2 mais IID; `α = 0.1` falha na partição com a regra atual (seção 4) e ficou de fora |
| Seeds | 0 a 9, as mesmas da grade anterior. A seed também define a partição Dirichlet |
| Dropout | `d` = 0,05 e 0,1, com `--drop_rounds 10` (como na D-035), e o cenário **sem dropout** como referência (escolha de Claude, D-043) |
| `m` | 100% e 50% (`--num_per_round` 240 e 120) |
| `τ` | **Definido por uma varredura antes da grade** (seção 6). O `0.75` da D-043 deixou de valer (D-044) |
| Rodadas | 50 |
| Treino | Do artigo (Rotated MNIST, Tabela 1): `--lr 0.1 --epochs 5 --mu 0.05`, batch cheio (sem `--batch_size`) |
| Onde | Notebook novo `projetos/StoCFL/teste-dropout-treino.ipynb`, com a política 7 desde o início |

**Grade:** 10 seeds × 2 `m` × 3 cenários de dropout × 2 `α` = **120 execuções**. Cada uma é o script chamado por `subprocess`. O script **precisa de mudança** para gerar a partição Dirichlet (seção 5), então esta grade já não roda "sem alterar o código do StoCFL".

## 3. O que a calibração de 2026-11-10 mediu

Execuções de 3 rodadas, `n = 240`, `--train 1`, GPU RTX A4000 (uma execução por vez), com **dados rotacionados** (4, 8 e 16 rotações). Os logs foram apagados depois.

| Fato | Resultado |
|---|---|
| **O treino não muda o sorteio nem a partição** | Em 2 execuções (seed 0 com `k = 8` e seed 1 com `k = 16`, `m` = 50%, `d = 0,1`), os clientes sorteados, o cluster de cada cliente em cada rodada e o `availability.pkl` foram **idênticos** aos de `--train 0` guardados em `resultados-dropout.json`. Faz sentido pelo código: `Ψ` é calculado na âncora, o treino só usa o gerador do `torch`, e o sorteio usa o `random` global. Consequência: a clusterização desta grade **repete** o que o `--train 0` daria com os mesmos parâmetros, e o que o treino acrescenta é a **acurácia** |
| Tempo, 4 rotações (1.000 amostras por cliente), `m` = 50% (`d = 0,1`) | Rodada 0: 21,5 s (observa os clientes); rodadas 1 e 2: 11,4 e 9,6 s |
| Tempo, 4 rotações, `m` = 100% (sem dropout) | Rodada 0: 62,5 s (observa 240 clientes e calcula 28.680 cossenos); rodadas 1 e 2: 16,7 e 16,1 s |
| Tempo por amostras por cliente | Com `m` = 50% e `d = 0,1`, as rodadas custam ~10 s (1.000 amostras por cliente) e ~20 s (2.000) |
| Paralelismo | Duas execuções ao mesmo tempo na GPU (seed 1, 8 e 16 rotações) levaram 150 s e 197 s, contra 69 s da de 8 rotações sozinha (seed 0), então **não há ganho: rodar em série** |
| Disco | `psi.pkl` de 1,3 GB (`m` = 50%) a 1,5 GB (`m` = 100%) por execução |
| Acurácia nas 3 primeiras rodadas | O modelo global (4 rotações, `m` = 100%) vai de ~0,30 a ~0,46 na rodada 2, então 50 rodadas com 5 passos de SGD por rodada ainda podem deixá-lo longe da convergência |

**Estimativa da grade.** Os tempos acima são de 4 rotações. Com Dirichlet puro cada cliente tem ~250 amostras (60.000 ÷ 240), e a rodada deve custar menos, mas **isso não foi medido**. Como limite superior, se o custo fosse o das 4 rotações, a grade de 60 execuções levaria ~10,5 h (9 min por execução com `m` = 50%, 9,5 a 14,5 min com `m` = 100%), e as 120 execuções, ~21 h. A primeira execução do passo 5 deve medir o custo real.

## 4. Non-IID: como o D-PRIDE faz e o que se aplica aqui

### 4.1 No D-PRIDE (`/home/luiz/D-PRIDE`, lido em 2026-11-10)

- `teste/task.py::prepare_partitions` escolhe entre `iid` (`IidPartitioner`, fatias contíguas) e `dirichlet` (`DirichletPartitioner` do `flwr_datasets` 0.5.0 com `partition_by` nos rótulos, `alpha`, `min_partition_size = nº de partições`, `self_balancing=True` e `seed`).
- `α` ∈ {0.1, 0.5, 1, 2} e IID; o padrão é 0.1 (variável `DIRICHLET_ALPHA`). **A seed vai para o particionador**: sem isso todas as seeds cairiam na mesma partição. O cache do `FederatedDataset` é chaveado por (dataset, regime, α, nº de partições, seed). Regime e α entram no nome da pasta do dataset (`MNIST_A0.5`, `MNIST_IID`).
- Só há skew de **rótulos** (sem rotação), com teste global e **sem gabarito de cluster**: eles avaliam com heatmap cluster × classe e TVD, e registram a matriz de confusão e o recall por classe.
- O guia deles registra duas armadilhas. (i) Com `α = 0.1` a lib esgota as 10 tentativas de `min_partition_size` e levanta `ValueError`, de forma determinística (§19.8). (ii) A avaliação em test set **global** mede pior um modelo de cluster especializado, por construção (§7.5).

### 4.2 Aplicável aqui: o mecanismo sim, com mudança de código

O `fedlab` 1.2.1, já instalado, tem `hetero_dir_partition(targets, num_clients, num_classes, dir_alpha, min_require_size)`, o mesmo algoritmo (Dirichlet por classe com balanceamento). Ele substituiria o `random_slicing` de `RotatedMNIST.pre_process` ([datasets.py:135](../projetos/StoCFL/datasets.py#L135)), sem dependência nova (o `flwr_datasets` não está no `.venv` da raiz). Ele usa o `np.random` global (é preciso semear antes) e **não limita as tentativas**, então com `α` pequeno pode demorar muito ou travar.

### 4.3 O que se mediu (2026-11-10, scripts descartáveis)

Calculei `Ψ` (gradiente normalizado na âncora, como em `dataset_representation`) para os 240 clientes com a partição Dirichlet do D-PRIDE e apliquei a regra de fusão do StoCFL aos cossenos. É a partição depois da rodada 0 com `m` = 100%, que é exatamente o grafo "cosseno > `τ`" (relatório de m, k e τ). Conferido com dados IID: a janela de `τ` saiu em 0,34 a 0,91 (o relatório tem 0,339 a 0,926 para a seed 0).

| Dados | Resultado |
|---|---|
| IID dentro da rotação (grade anterior) | 4 clusters e ARI 1,0 com `τ = 0.75` |
| Dirichlet **dentro** de cada rotação, `α` = 2, 1, 0.5, 0.1 | O cosseno mediano dentro do grupo cai de 0,92 para 0,23, 0,12, 0,00 e −0,10. Com `τ = 0.75`: 97–117 clusters (`α` = 2 e 1), 56–69 (`α` = 0.5), 18 (`α` = 0.1) e ARI de 0,01 a 0,22. **Nenhum `τ` separa as rotações**: a borda inferior fica acima da superior nos 10 casos medidos (`α = 0.1` só deu partição em 1 das 3 seeds). Com `τ` ≤ 0,6 tudo colapsa em 1 a 3 clusters com as rotações misturadas |
| Dirichlet **puro**, 240 clientes, sem rotação (a escolha) | `τ = 0.5`: 1 cluster. `τ = 0.75`: 12–57 clusters, com **um gigante de 168 a 227 clientes** e 10 a 49 singletons. `τ = 0.9`: 154 a 236 clusters, quase todos singletons |

Varredura mais fina de `τ` no Dirichlet puro (seed 0), em nº de clusters / maior cluster / singletons:

| `τ` | `α = 0.5` | `α = 1.0` |
|---|---|---|
| 0.70 | 6 / 235 / 5 | 9 / 231 / 7 |
| 0.75 | 12 / 227 / 10 | 33 / 175 / 26 |
| 0.80 | 39 / 161 / 31 | 81 / 66 / 70 |
| 0.85 | 96 / 30 / 77 | 142 / 20 / 124 |
| 0.90 | 168 / 13 / 146 | 212 / 6 / 196 |

**Leitura:** com rótulos desbalanceados, `Ψ` é dominado pela composição de classes, e o *single linkage* encadeia os clientes. Não há planalto nem janela de `τ`: o nº de clusters cresce de forma contínua com `τ`, que passa a ser um botão de **granularidade** (consistente com o artigo, em que `τ` maior dá clusters mais finos). Em `τ = 0.75`, o StoCFL vira um cluster gigante (perto do FedProx global) mais singletons (perto do Ditto).

**Limites da medição:** só a rodada 0 com `m` = 100%; 3 seeds; `α = 0.1` falhou na partição; nada foi testado com `m` = 50%, dropout ou nas rodadas seguintes, em que o centro de um cluster fundido é a média dos `Ψ` e a fusão pode se comportar diferente. A regra `min_partition_size = nº de partições` do D-PRIDE **não escala**: com 240 clientes ela exige 240 amostras por cliente com média de 250 e falhou até com `α = 2`; usei 50, que funcionou para `α` = 0.5, 1 e 2 nas seeds 0 a 2.

## 5. Mudanças no código (a implementar, depois da sua autorização)

O pedido original deste plano era não alterar o script. Com o Dirichlet, isso muda, e as mudanças afetam o código do StoCFL, então cada uma será confirmada na implementação (pendências na seção 10). Proposta:

- **Particionamento:** um ramo novo em `RotatedMNIST.pre_process` (ou um particionador novo em `datasets.py`) que usa `hetero_dir_partition` com `min_require_size = 50`, semeando o `np.random` com a seed da execução. Ele gera uma partição de `n` clientes sobre o MNIST de treino inteiro, sem rotação.
- **Flag nova** no `StoCFL-FCC+CFL.py`, por exemplo `--dirichlet_alpha` (padrão: nenhum, que mantém o comportamento atual), exigindo `k = 1`. O nome das pastas de dados e de logs ganha o `α` para os dados não se misturarem (`rotated_mnist_240_<seed>_k1_a0.5`).
- **Verificação do particionador:** gerar as 20 partições (10 seeds × 2 `α`) antes da grade e conferir tamanho mínimo, máximo e mediano, e que nenhuma falhou nem travou.
- **Histograma de rótulos por cliente** gravado no JSON (240 × 10 por seed e `α`), para o cluster × classe e a TVD sem os dados.
- **Testes** do particionador (determinismo por seed, `α` e tamanhos), sem GPU, e uma execução pequena de regressão: sem a flag, o script deve repetir exatamente o comportamento de hoje.

## 6. Varredura de `τ` (antes da grade)

O critério de escolha do `τ` será combinado com você depois de ver os números, porque não há janela (seção 4.3). Duas etapas, só de clusterização (`--train 0`):

1. **Etapa A, barata:** uma execução de 1 rodada com `m` = 100% por (`α`, seed), para `α` = 0.5 e 1.0 e seeds 0 a 2. O `cos_rec.log` guarda os cossenos entre os 240 clientes na rodada 0, e com eles o nº e o tamanho dos clusters saem para qualquer `τ` sem rodar de novo (o método do relatório de m, k e τ). Isso valida com o script real a medição da seção 4.3.
2. **Etapa B, dinâmica:** execuções completas de 50 rodadas com `m` = 50% e 100%, `d` = 0 e 0,1, nos 2 ou 3 `τ` candidatos da etapa A, nas mesmas 3 seeds. Mostra se o nº de clusters e o encadeamento mudam com a amostragem parcial e com o dropout.

Saída: uma tabela de nº de clusters, maior cluster e singletons por `τ`, e a proposta do `τ` da grade, para você decidir.

## 7. Métricas

**Clusterização** (do `cluster.pkl` e do log): nº de clusters, tamanho do maior cluster, nº de singletons, cobertura, rodada estável, participantes e disponibilidade; **cluster × classe** e **TVD** entre a distribuição de rótulos de cada cliente e a do seu cluster. **ARI e pureza contra a rotação não se aplicam** (não há rotação).

**Aprendizado.** O log traz, por rodada e por cluster sorteado, `Round r, Cluster c - Global Test loss: L, acc: A` (modelo do cluster) e a linha `Round r, Global acc: [...]` (o `gmodel` nos mesmos conjuntos de teste, na mesma ordem). O `accuracy.pkl` traz as mesmas acurácias sem o id do cluster, então o notebook lê o log e confere com o `accuracy.pkl`. Com `k = 1`, o teste de todo cluster é o MNIST de teste inteiro (10 classes balanceadas).

| Métrica | Definição |
|---|---|
| `acc_cluster[r]`, `acc_global[r]` | Média, ponderada pelos participantes de cada cluster na rodada, da acurácia do modelo do cluster e do `gmodel` |
| `acc_*_final` | Média das rodadas 41 a 50 (suaviza o ruído de uma rodada) |
| `ganho` | `acc_cluster − acc_global` |
| `rodada_limiar` | Primeira rodada com `acc_cluster ≥ LIMIAR_ACC` (padrão 0,90; ajustar depois de ver as curvas) |

**Atenção:** no teste global balanceado, um modelo de cluster especializado em poucas classes mede **pior** do que o global, por construção (D-PRIDE, guia §7.5). O `ganho` pode sair negativo sem que isso seja defeito. A avaliação mais justa, com o recall por classe ponderado pela distribuição de rótulos do cluster, exige mudar o script (pendência da seção 10).

Comparação dropout − sem dropout por seed, com Wilcoxon (sem correção para comparações múltiplas), para `acc_cluster_final`, `acc_global_final`, `ganho`, `rodada_limiar`, rodada estável e nº de clusters.

**Gráficos (Plotly):** por rodada (média e faixa mín–máx entre as seeds, uma coluna por `m` e uma figura por `α`): nº de clusters, maior cluster, acurácia do cluster, acurácia global e participantes. Caixas por seed das métricas finais. Heatmaps cluster × classe da partição final.

## 8. Passo a passo

Cada etapa é um commit atômico (política 6), com a documentação e o registro em `decisoes.md` no mesmo commit.

1. **Plano e decisões** (este documento, D-043, D-044 e os índices). Feito em 2026-11-10.
2. **Particionador Dirichlet e flag** no script, com os testes e a regressão da seção 5. Resolve antes as pendências da seção 10.
3. **Varredura de `τ`** (seção 6) e escolha do `τ` com você.
4. **Notebook `teste-dropout-treino.ipynb`**, versionado sem saídas. Parte das funções do `teste-dropout.ipynb` (copiadas, sem editar o original) e acrescenta a leitura da acurácia, as métricas e os gráficos da seção 7. Inclui a política 7 desde o início: `DADOS_JSON`, a trava que recusa relançar a grade quando faltam os logs e o JSON já existe, e a célula que grava `logs/resultados-dropout-treino.json` (estrito, via arquivo temporário), com os dados brutos de cada execução: o cluster de cada cliente por rodada, os sorteados e os indisponíveis por rodada, os cossenos da última rodada, o histograma de rótulos por cliente e a acurácia de cada cluster por rodada (id, participantes, acurácia do cluster e do global). O notebook também captura a saída padrão de cada execução e a confere antes de apagar os logs.
5. **Smoke test** com uma cópia reduzida (`n = 48`, 6 rodadas, seeds 0 e 1, os 3 cenários de dropout, os 2 `m` e os 2 `α`). Verifica as células, a segunda execução reaproveitando tudo, a igualdade da partição e do sorteio entre `--train 0` e `--train 1` e a cobertura do log igual às chaves do `psi.pkl` (I5 do [plano do dropout](plano-dropout-stocfl.md)). Mede também o tempo real por execução.
6. **Grade completa** (120 execuções), em segundo plano e só **depois da sua autorização**. Com `APAGAR_PSI = True`, o `psi.pkl` de cada execução concluída é apagado. O notebook reaproveita execuções concluídas, então uma interrupção se retoma reexecutando.
7. **Verificação e limpeza (política 7).** O notebook em modo `DADOS_JSON` tem de gerar os mesmos gráficos e tabelas que o modo com logs, e o JSON tem de bater com os logs. Listar os caminhos dos logs da grade, conferir que cada um consta no JSON e só então apagá-los. Guardar o JSON compactado (`gzip -9 -n`) em `docs/resultados/`, com o `README.md` da pasta atualizado.
8. **Relato.** Os números no [guia](guia.md), seção 4.11, e a atualização das notas "o efeito sobre o ARI e o nº de clusters não foi medido" (guia 4.9 e 4.12 #13) para o que a grade mostrar com treino.

## 9. Verificação

| # | Verifica | Como |
|---|---|---|
| V1 | `--train 1` não muda o sorteio nem a partição | `cluster.pkl` e os sorteados iguais aos de uma execução `--train 0` com os mesmos parâmetros (smoke test) |
| V2 | Cobertura | a do log igual às chaves de `psi.pkl` (I5) |
| V3 | Acurácia lida do log | igual à do `accuracy.pkl` em todas as rodadas, com o nº de clusters e de valores batendo |
| V4 | Uma entrada por rodada | `cluster.pkl` e `accuracy.pkl` com 50 entradas, inclusive em rodada sem participantes |
| V5 | JSON | estrito (sem `NaN`), 120 execuções, 50 linhas por rodada por execução, métricas recalculáveis dos dados brutos |
| V6 | Modo `DADOS_JSON` | mesmas figuras e tabelas que o modo com logs, comparadas campo a campo, sem alterar o JSON |
| V7 | Regressão do script | sem a flag nova, `cluster.pkl`, `psi.pkl` e os sorteados iguais aos de antes da mudança (como o I1 do plano do dropout) |
| V8 | Particionador | 20 partições geradas (10 seeds × 2 `α`), determinísticas por seed, sem falha, com tamanhos registrados |

## 10. Pendências (decisões que ainda faltam, a perguntar antes de implementar)

| # | Pergunta | Recomendação de Claude |
|---|---|---|
| P1 | **Avaliação dos modelos de cluster.** Manter só a acurácia no teste global balanceado (comparável ao D-PRIDE, mas penaliza a especialização) ou acrescentar o recall por classe, ponderado pela distribuição de rótulos do cluster (mudança no `evaluate` do script e no `accuracy.pkl`) | Acrescentar o recall por classe, mantendo a acurácia global |
| P2 | **FedAvg sem ponderação** (guia 4.12 #10) com clientes de 52 a 599 amostras: manter, como no código e no artigo, ou ponderar por tamanho (muda o algoritmo) | Manter e registrar |
| P3 | **Critério de escolha do `τ`** na varredura (seção 6) | Decidir depois de ver as tabelas |
| P4 | Nomes da flag e das pastas de dados e de logs (seção 5) | Os propostos, por serem triviais |

## 11. Limites e cuidados

- **Sem janela de `τ`.** Os resultados dependem do `τ` escolhido: o nº de clusters é uma função contínua dele. A conclusão sobre o dropout vale para o `τ` e os `α` da grade, não em geral.
- **Efeito possivelmente nulo.** O dropout só atrasa a observação dos clientes (guia 4.11). Com muitos singletons e um cluster gigante, o efeito pode aparecer só nas primeiras rodadas, ou nem aparecer na acurácia. Isso é um resultado válido. Em 50 rodadas o treino também pode estar longe da convergência (seção 3).
- **Acurácia por cluster tem viés de composição.** Só clusters sorteados são avaliados. Com `τ` alto, muitos clusters são singletons, e a média ponderada reflete modelos de um só cliente. Leia a acurácia junto com o nº e o tamanho dos clusters.
- **Pareamento só pela seed.** A seed fixa a partição dos dados e (pelo código, não verificado) o modelo inicial, que é igual entre os cenários. O sorteio só é igual quando `m` = 100% e `d = 0`. Com 10 seeds o Wilcoxon tem pouco poder.
- **`cos_rec.log` só guarda a última rodada**, então a matriz de cossenos entre clientes só fica disponível nas execuções de 1 rodada da etapa A.
- **Alterações que não são deste plano:** `docs/clusterizacao-ao-longo-do-tempo.ipynb`, `projetos/StoCFL/teste-fracao-clientes.ipynb`, `projetos/StoCFL/teste-fracao-clientes copy.ipynb` e `mimic_codes/` estão sem commit e não fazem parte deste trabalho. Adicione arquivos ao commit por nome.
- **Só o `StoCFL-FCC+CFL.py`** tem `--drop` (passo 5 do plano do dropout segue pendente), e a flag do Dirichlet também ficará só nele.

## 12. Documentação a atualizar na implementação

| Arquivo | O que muda |
|---|---|
| [guia.md](guia.md) | 4.7 (o particionador Dirichlet), 4.9 (flag nova e `τ`), 4.10 (nomes de pastas), 4.11 (notebook novo, varredura e resultados), 4.12 #10 (pesos do FedAvg com clientes desiguais) e #13 (o efeito do dropout com treino passa a estar medido), 4.16 (mapa artigo ↔ código) |
| [diagrama-atividades-stocfl.md](../projetos/StoCFL/diagrama-atividades-stocfl.md) | O nó `pre_process` (partição por rotação ou Dirichlet) e a lista de argumentos. Conferir a sintaxe Mermaid depois de editar |
| [diagrama-sequencia-stocfl.md](../projetos/StoCFL/diagrama-sequencia-stocfl.md) | A mensagem `pre_process(shards)` do bloco `process == 1`. Conferir a sintaxe |
| [README do StoCFL](../projetos/StoCFL/README.md) | A flag nova e a seção de testes com o notebook novo |
| [plano-dropout-stocfl.md](plano-dropout-stocfl.md) | A situação aponta para este plano |
| [README de docs/](README.md) e [resultados/README.md](resultados/README.md) | Índice e o JSON novo |
| [decisoes.md](decisoes.md) | Uma entrada para cada decisão nova |
