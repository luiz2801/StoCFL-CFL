# Guia do projeto: CFL e StoCFL

Este guia explica os dois códigos de *Clustered Federated Learning* deste diretório: o que cada algoritmo faz, quais funções fazem o quê, o fluxo de execução, as variáveis e o efeito de cada uma no resultado, além de bugs conhecidos e orientações para quem for modificar o código, seja uma pessoa ou um agente de IA.

> Todas as referências `arquivo:linha` são relativas a `cfl_stocfl/projetos/`. O guia foi escrito a partir da leitura do código **e dos dois artigos** (os PDFs em `docs/`: CFL no *IEEE TNNLS* 2021 e StoCFL na *Neural Networks* 2025). O `.venv` da raiz é o ambiente único do repositório e, desde 2026-11-05, tem tudo para rodar o código (`requirements.txt` da raiz; ver a seção 4.11). As verificações por execução de 2026-11-04 foram feitas em ambientes temporários fora do repositório (ver o fim da seção 8).
>
> Onde ler o quê: as seções 3.1–3.8 e 4.1–4.14 descrevem **o código**. As seções **3.9–3.10** e **4.15–4.17** descrevem **os artigos** (teoria, experimentos, hiperparâmetros recomendados) e o **mapa artigo ↔ código**, isto é, onde a implementação segue ou diverge do que o artigo propõe.

---

## Sumário

1. [Visão geral do repositório](#1-visão-geral-do-repositório)
2. [Conceitos comuns](#2-conceitos-comuns)
3. [CFL: Clustered Federated Learning (Sattler et al.)](#3-cfl--clustered-federated-learning-sattler-et-al)
4. [StoCFL: Stochastic Clustered Federated Learning (Zeng et al.)](#4-stocfl--stochastic-clustered-federated-learning-zeng-et-al)
5. [CFL × StoCFL: comparação](#5-cfl--stocfl--comparação)
6. [Orientações para agentes de IA e mantenedores](#6-orientações-para-agentes-de-ia-e-mantenedores)
7. [Glossário](#7-glossário)
8. [Referências e versões dos artigos](#8-referências-e-versões-dos-artigos)

---

## 1. Visão geral do repositório

```
cfl_stocfl/
├── requirements.txt                    # dependências do ambiente único
├── .venv/                              # Python 3.12 único, com torch, fedlab etc.
├── docs/
│   ├── Clustered_Federated_Learning_...pdf # artigo do CFL (IEEE TNNLS, 2021)
│   ├── StoCFL.pdf                      # artigo do StoCFL (Neural Networks, 2025)
│   ├── resultados/                     # resultados das execuções em JSON compactado (D-041)
│   └── guia.md                         # este guia
└── projetos/
    ├── clustered-federated-learning/   # CFL (Sattler, Müller, Samek, 2019)
    │   ├── clustered_federated_learning.ipynb   # PONTO DE ENTRADA: experimento completo
    │   ├── fl_devices.py                   # Client, Server, operações sobre pesos, similaridade
    │   ├── data_utils.py                   # partição Dirichlet não-IID + Subset com transform
    │   ├── models.py                       # ConvNet (EMNIST, 62 classes)
    │   └── helper.py                       # logger de experimento + gráficos
    └── StoCFL/                         # StoCFL (Zeng et al., 2023)
        ├── StoCFL-FCC.py                   # PONTO DE ENTRADA: só clusterização (vários cenários)
        ├── StoCFL-FCC+CFL.py               # PONTO DE ENTRADA: clusterização + treino bi-nível (Rotated MNIST/CIFAR)
        ├── StoCFL-FEMNIST.py               # PONTO DE ENTRADA: FEMNIST (LEAF)
        ├── trainer.py                      # "clientes" simulados: um Trainer por cenário de dados
        ├── datasets.py                     # Partitioners: geram/carregam os dados de cada cliente (.pkl)
        ├── functional.py                   # similaridade de cosseno, ordenação de pares, seed
        ├── availability.py                 # disponibilidade dos clientes com retorno (--drop, só no FCC+CFL); sem torch
        ├── tests/test_availability.py      # testes unittest do availability.py
        ├── settings.py                     # utilitários legados (label skew, datasets antigos)
        ├── models/cnn.py, models/linear.py # modelos usados (models/model.py não é usado)
        ├── config/*.pkl, *_partition.py    # partições pré-computadas (legado, não usadas pelos scripts principais)
        ├── leaf/                           # adaptador LEAF do FedLab (usado só pelo FEMNIST)
        ├── fedscale/                       # cópia do FedScale, NÃO é importada por nenhum script
        ├── datasets/femnist/               # README + notebook de estatísticas
        └── requirements.txt                # fedlab==1.2.1, torch, torchvision, tqdm, scikit-learn, cvxopt, spacy
```

| Projeto | Linguagem/stack | Como roda | Framework FL |
|---|---|---|---|
| CFL | PyTorch puro | Notebook Jupyter | implementação própria (`fl_devices.py`) |
| StoCFL | PyTorch + **FedLab 1.2.1** | Scripts Python via CLI (`argparse`) | `fedlab` (serialização, agregação, classes base) |

Os dois são simulações em uma única máquina: não há rede, e "clientes" e "servidor" são objetos no mesmo processo.

---

## 2. Conceitos comuns

- **Federated Learning (FL):** vários clientes treinam um modelo com dados locais que nunca saem do cliente. O servidor só recebe pesos ou atualizações e os agrega.
- **FedAvg:** o servidor faz a média dos pesos (ou atualizações) dos clientes. Nos dois códigos a média é **uniforme**, sem ponderar pelo tamanho do dataset de cada cliente.
- **Heterogeneidade (não-IID):** quando os clientes têm distribuições de dados diferentes, um único modelo global fica ruim para todos. Exemplos usados aqui:
  - *rotação* (mesmos rótulos, imagens rotacionadas): muda P(x) e P(y|x);
  - *label shift* (mesmas imagens, rótulos deslocados): muda P(y|x);
  - *label skew* (cada cliente vê só algumas classes): muda P(y);
  - *feature skew* (MNIST × FashionMNIST): domínios de entrada diferentes.
- **Clustered FL:** agrupar clientes com distribuições parecidas e treinar **um modelo por cluster**.
- **Sinal de similaridade:** os dois algoritmos comparam clientes pela **similaridade de cosseno entre vetores de atualização de pesos**. Clientes com a mesma distribuição tendem a "puxar" o modelo na mesma direção.

---

## 3. CFL: Clustered Federated Learning (Sattler et al.)

Artigo: *Sattler, Müller, Samek. "Clustered Federated Learning: Model-Agnostic Distributed Multitask Optimization Under Privacy Constraints", IEEE TNNLS 32(8), 2021, pp. 3710–3722 (arXiv:1910.01991).* Teoria e experimentos em 3.9; correspondência com o notebook em 3.10.

### 3.1 O que o algoritmo faz

O CFL é **divisivo (top-down)**:

1. Começa com **um único cluster** com todos os clientes, o que equivale a FedAvg comum.
2. A cada rodada, cada cliente calcula sua atualização `ΔW_i` (treino local a partir do modelo do seu cluster).
3. Para cada cluster, o servidor mede:
   - `mean_norm = ‖ média_i ΔW_i ‖`: se é pequeno, o modelo do cluster chegou perto de um ponto estacionário do objetivo **conjunto**;
   - `max_norm = max_i ‖ΔW_i‖`: se é grande, algum cliente ainda está longe do **seu próprio** ótimo.
4. **Critério de divisão (Algoritmo 5 do artigo):** se `mean_norm < EPS_1` **e** `max_norm > EPS_2`, os clientes do cluster têm distribuições incongruentes. O servidor calcula a bipartição com o Algoritmo 1 do artigo, equivalente a *single linkage*, sobre a matriz de similaridade de cosseno entre os `ΔW_i`, e calcula `α_cross^max`, o maior cosseno entre os dois lados. A divisão só é aceita se `GAMMA_MAX < √((1 − α_cross^max)/2)`.
5. Cada cluster continua o FedAvg separadamente. Clusters **só se dividem**, nunca se fundem.
6. Antes de cada divisão, e no fim, o modelo do cluster é guardado em cache. No final, cada cliente pode escolher, entre os modelos guardados, o que dá maior acurácia na sua validação.

Intuição: o FedAvg converge para um ponto que é ótimo "em média". Se ali a média dos gradientes é ~0 mas os gradientes individuais são grandes, os clientes estão puxando em direções opostas, e o cosseno entre eles mostra quem puxa para onde. A justificativa matemática (Teorema da Separação e critérios de norma) está em 3.9.

### 3.2 Arquivos e funções

#### `fl_devices.py`: núcleo do algoritmo

| Função/método | Linha | O que faz |
|---|---|---|
| `device` | [fl_devices.py:6](clustered-federated-learning/fl_devices.py#L6) | `"cuda"` se disponível, senão `"cpu"` (global). |
| `train_op(model, loader, optimizer, epochs)` | [fl_devices.py:8](clustered-federated-learning/fl_devices.py#L8) | Treino SGD padrão com `CrossEntropyLoss`. Retorna a loss média da **última** época. |
| `eval_op(model, loader)` | [fl_devices.py:25](clustered-federated-learning/fl_devices.py#L25) | Acurácia no loader. ⚠️ Chama `model.train()` em vez de `model.eval()` (inofensivo para a `ConvNet`, que não tem dropout/BN). |
| `copy(target, source)` | [fl_devices.py:43](clustered-federated-learning/fl_devices.py#L43) | `target[k].data = source[k].data.clone()` para cada parâmetro (in-place no modelo). |
| `subtract_(target, minuend, subtrahend)` | [fl_devices.py:47](clustered-federated-learning/fl_devices.py#L47) | `target = minuend − subtrahend` (usado para `dW = W − W_old`). |
| `reduce_add_average(targets, sources)` | [fl_devices.py:51](clustered-federated-learning/fl_devices.py#L51) | Para cada `target`: `target += média(sources)`. É a agregação FedAvg sobre atualizações. |
| `flatten(source)` | [fl_devices.py:57](clustered-federated-learning/fl_devices.py#L57) | Concatena todos os tensores de um dict de parâmetros em um vetor 1-D. |
| `pairwise_angles(sources)` | [fl_devices.py:61](clustered-federated-learning/fl_devices.py#L61) | Matriz N×N de **similaridade de cosseno** entre as atualizações (apesar do nome, não é ângulo). |
| `FederatedTrainingDevice` | [fl_devices.py:73](clustered-federated-learning/fl_devices.py#L73) | Base: cria o modelo e `self.W` = dict `{nome: Parameter}` (referências **vivas** aos parâmetros do modelo). |
| `Client.__init__` | [fl_devices.py:85](clustered-federated-learning/fl_devices.py#L85) | Cria otimizador, divide os dados em treino/validação (`train_frac`), cria `dW` e `W_old`. |
| `Client.synchronize_with_server` | [fl_devices.py:102](clustered-federated-learning/fl_devices.py#L102) | `W ← W_servidor`. Usado só na rodada 1, para todos partirem da mesma inicialização. |
| `Client.compute_weight_update` | [fl_devices.py:105](clustered-federated-learning/fl_devices.py#L105) | `W_old ← W`; treina; `dW ← W − W_old`. |
| `Client.reset` | [fl_devices.py:111](clustered-federated-learning/fl_devices.py#L111) | `W ← W_old`. Desfaz o treino local; o efeito fica guardado só em `dW`. |
| `Server.select_clients` | [fl_devices.py:121](clustered-federated-learning/fl_devices.py#L121) | Amostra `frac` dos clientes (o notebook usa `frac=1.0`). |
| `Server.aggregate_weight_updates` | [fl_devices.py:124](clustered-federated-learning/fl_devices.py#L124) | ⚠️ **Quebrado e não usado**: passa `target=` em vez de `targets=`. |
| `Server.compute_pairwise_similarities` | [fl_devices.py:127](clustered-federated-learning/fl_devices.py#L127) | `pairwise_angles` sobre os `dW` de todos os clientes. |
| `Server.cluster_clients(S)` | [fl_devices.py:130](clustered-federated-learning/fl_devices.py#L130) | Algoritmo 1 do artigo: percorre os pares em ordem decrescente de similaridade e funde os grupos que os contêm até restarem 2. Retorna `c1, c2` como **posições dentro de S**, e não ids de cliente; o notebook os converte com `idc[c1]` e `idc[c2]`. |
| `Server.aggregate_clusterwise` | [fl_devices.py:144](clustered-federated-learning/fl_devices.py#L144) | Para cada cluster: `W_i += média(dW_j, j ∈ cluster)` em todos os membros. |
| `Server.compute_max_update_norm` | [fl_devices.py:150](clustered-federated-learning/fl_devices.py#L150) | `max_i ‖dW_i‖`. |
| `Server.compute_mean_update_norm` | [fl_devices.py:154](clustered-federated-learning/fl_devices.py#L154) | `‖média_i dW_i‖`. |
| `Server.cache_model` | [fl_devices.py:158](clustered-federated-learning/fl_devices.py#L158) | Guarda `(ids, cópia dos pesos, acurácias desses clientes)` em `server.model_cache`. |

O servidor **nunca atualiza o próprio `W`**. A agregação é aplicada diretamente nos `W` dos clientes. Como todos os membros de um cluster partem do mesmo `W` e recebem a mesma média, eles continuam idênticos ("modelo do cluster" = `W` de qualquer membro).

#### `data_utils.py`

| Função | Linha | O que faz |
|---|---|---|
| `split_noniid(train_idcs, train_labels, alpha, n_clients)` | [data_utils.py:4](clustered-federated-learning/data_utils.py#L4) | Para cada classe, sorteia proporções `Dirichlet(alpha)` entre os clientes e divide as amostras da classe nessas proporções. Os clientes ficam com tamanhos e distribuições de rótulos diferentes. |
| `CustomSubset` | [data_utils.py:26](clustered-federated-learning/data_utils.py#L26) | `Subset` com `subset_transform` próprio. É por ele que cada cliente recebe sua transformação (ex.: rotação 180°). |

#### `models.py`

`ConvNet` ([models.py:5](clustered-federated-learning/models.py#L5)): `1×28×28 → conv5(6) → pool → conv5(16) → pool → 256 → Linear(62)`. As 62 saídas correspondem às classes do EMNIST `byclass`.

#### `helper.py`

- `ExperimentLogger.log(dict)` ([helper.py:5](clustered-federated-learning/helper.py#L5)): acumula cada chave em uma lista (`cfl_stats.acc_clients`, `cfl_stats.split`, ...).
- `display_train_stats(...)` ([helper.py:15](clustered-federated-learning/helper.py#L15)): à esquerda, acurácia média ± desvio dos clientes com linhas verticais nas divisões; à direita, `mean_norm` e `max_norm` com as retas `EPS_1`/`EPS_2`.

### 3.3 Fluxo de execução (notebook `clustered_federated_learning.ipynb`)

| Célula | O que acontece |
|---|---|
| 0 | Imports; `torch.manual_seed(42)`, `np.random.seed(42)`. |
| 2 | Baixa EMNIST `byclass` (62 classes). Embaralha e pega 10.000 amostras de treino e 10.000 de teste. `split_noniid` divide o treino entre `N_CLIENTS` com `DIRICHLET_ALPHA`. |
| 3 | Histograma da distribuição de rótulos por cliente. |
| 5 | **Cria a estrutura de clusters real:** clientes `0–4` recebem `RandomRotation((180,180))` e clientes `5–9` não. O ground truth são 2 grupos. |
| 6 | Cria `Client`s (`ConvNet`, `SGD(lr=0.1)`, batch 128, 80/20 treino/val) e o `Server`. |
| 7 | Mostra amostras dos clientes 0 e 5. |
| 9 | **Loop principal do CFL** (pseudocódigo abaixo). |
| 11–12 | Monta a tabela `clientes × modelos em cache` com acurácias e destaca o melhor modelo por cliente. |

Pseudocódigo da célula 9:

```text
cluster_indices = [[0, 1, ..., N-1]]                  # 1 cluster com todos
for r in 1..COMMUNICATION_ROUNDS:
    if r == 1: todo cliente copia W do servidor        # mesma inicialização
    participating = server.select_clients(clients, frac=1.0)
    for c in participating:
        c.compute_weight_update(epochs=1)              # W_old←W; treina; dW←W−W_old
        c.reset()                                      # W←W_old
    S = cos(dW_i, dW_j) para TODOS os clientes (N×N)

    novos = []
    for C in cluster_indices:
        max_norm  = max_{i∈C} ‖dW_i‖
        mean_norm = ‖mean_{i∈C} dW_i‖
        if mean_norm < EPS_1 and max_norm > EPS_2 and |C| > 1:
            c1, c2 = Alg1(S[C][:, C])                 # c1 e c2 são posições dentro de C
            alpha_cross_max = max S entre C[c1] e C[c2]
            if GAMMA_MAX < sqrt((1 - alpha_cross_max) / 2):
                server.cache_model(C, W de C[0], acc_clients da rodada anterior)
                novos += [C[c1], C[c2]]
                log split = r
            else:
                novos += [C]
        else:
            novos += [C]
    cluster_indices = novos
    server.aggregate_clusterwise(...)                  # W_i += média(dW) do seu cluster
    acc_clients = [c.evaluate() for c in clients]      # acurácia na validação local (20%)
    log(acc_clients, mean_norm, max_norm, r, cluster_indices); plota

ao final: cache_model de cada cluster final
```

```text
 rodada r ──► clientes treinam (dW) ──► reset W ──► S = cos(dW)
                                                     │
            ┌────────────── para cada cluster C ◄────┘
            │  mean_norm < EPS_1  e  max_norm > EPS_2 ?
            │        sim ──► bipartição de C por S ──► GAMMA_MAX < √((1−α_cross^max)/2) ?
            │                     sim ──► cache do modelo e divisão de C
            │                     não ──► mantém C
            │        não ──► mantém C
            └──► agregação por cluster (FedAvg intra-cluster) ──► avaliação ──► r+1
```

### 3.4 Estado e estruturas de dados

| Estrutura | Onde | Conteúdo |
|---|---|---|
| `client.W` | `Client` | dict `nome → Parameter` (pesos vivos do modelo do cliente). |
| `client.W_old` / `client.dW` | `Client` | pesos antes do treino local / atualização da rodada. |
| `client.optimizer` | `Client` | SGD puro **por cliente**, sem estado entre rodadas. |
| `cluster_indices` | notebook | lista de arrays de ids de cliente; define a partição atual. |
| `client_clusters` | notebook | mesma partição, como listas de objetos `Client`. |
| `server.model_cache` | `Server` | lista de `(ids, pesos, acurácias)`; a 1ª entrada costuma ser o modelo FL global. |
| `cfl_stats` | notebook | `acc_clients`, `mean_norm`, `max_norm`, `rounds`, `clusters`, `split`. |

### 3.5 Variáveis e impacto no resultado

| Variável | Valor | Onde | Efeito |
|---|---|---|---|
| `N_CLIENTS` | 10 | célula 2 | Nº de clientes. ⚠️ A regra de rotação `i < 5` (célula 5) e `np.zeros([10, ...])` (célula 11) estão fixas no código e precisam ser ajustadas junto. |
| `DIRICHLET_ALPHA` | 1.0 | célula 2 | Heterogeneidade de rótulos **dentro** dos grupos. α pequeno (ex. 0.1) faz cada cliente ver poucas classes; isso aumenta o ruído na similaridade e pode atrapalhar a separação por rotação. α grande deixa os rótulos quase uniformes e a rotação vira o único sinal. |
| tamanho treino/teste | 10.000 / 10.000 | célula 2 | Menos dados por cliente geram `dW` mais ruidosos. O conjunto de teste do servidor **não é usado** no loop. |
| rotação 180° em `i<5` | — | célula 5 | Define o ground truth (2 clusters). Trocar ou adicionar transformações cria outros cenários. |
| `lr` | 0.1 | célula 6 | Escala diretamente `‖dW‖`; **EPS_1/EPS_2 precisam ser recalibrados** se mudar. |
| `batch_size` | 128 | `Client.__init__` | Menor batch dá mais passos por época, normas maiores e mais ruído. |
| `train_frac` | 0.8 | `Client.__init__` | Fração para treino; o resto é a validação usada em `evaluate`. |
| `epochs` | 1 | `compute_weight_update` | Mais épocas dão `dW` maiores e mais "específicos" do cliente (sinal mais forte, mas também mais deriva). |
| `COMMUNICATION_ROUNDS` | 80 | célula 9 | Duração total. |
| `EPS_1` | 0.2 | célula 9 | Limiar de "convergência" do cluster (`mean_norm < EPS_1`). **Maior** divide mais cedo, possivelmente antes do FL convergir, com similaridades ruidosas. **Menor** espera mais ou nunca divide. Regra do artigo: o mais pequeno que o tempo permitir, em torno de `max_t ‖média dW‖ / 10` (3.9.8). Aqui a regra daria 0.03–0.04, que nunca dispara: o ruído do SGD mantém `mean_norm` em ~0.10–0.15 mesmo em 200 rodadas. Com `EPS_1 = 0.15`, 2 de 4 seeds não dividiram em 80 rodadas (D-015). |
| `EPS_2` | 0.8 | célula 9 | Limiar de "incongruência" (`max_norm > EPS_2`). **Menor** divide com mais facilidade (risco de dividir grupos homogêneos): com 0.5, houve de 3 a 6 divisões extras por seed, algumas nas rodadas 3 e 4. **Maior** divide menos (risco de nunca separar). Regra do artigo: `EPS_2 ∈ [EPS_1, 10·EPS_1]`; aqui a razão é 4. |
| `GAMMA_MAX` | 0.5 | célula 9 | Limite assumido para o erro relativo do gradiente empírico (`γ_max` do artigo, em `[0, 1)`, sem valor informado). A divisão só é aceita se `GAMMA_MAX < √((1−α_cross^max)/2)`, ou seja, com 0.5 são rejeitadas as bipartições em que os dois lados têm um par com cosseno acima de 0.5. **Maior** rejeita mais; 0 nunca rejeita. No cenário do notebook, nenhum valor separa as divisões corretas das extras: os limites se sobrepõem (corretas 0.712–0.766; extras 0.716 e 0.785, em 13 seeds). D-015. |
| `frac` | 1.0 | célula 9 | ⚠️ Com `frac < 1`, quem não participou mantém o `dW` antigo, mas entra mesmo assim na similaridade e na agregação. O código assume participação total. |
| seeds | 42 | célula 0 | Reprodutibilidade da partição e da inicialização. |

Regra prática: `EPS_1` e `EPS_2` são valores **absolutos de norma** e dependem de lr, épocas, batch, tamanho dos dados e arquitetura. Para calibrar, rode sem divisões e observe as curvas `mean_norm`/`max_norm` no gráfico da direita. Aplicando a recomendação do artigo (3.9.8): escolha `EPS_1` perto de um décimo do valor máximo que `mean_norm` atingiu, e `EPS_2` entre `EPS_1` e `10·EPS_1`, abaixo do nível em que `max_norm` estaciona. Se `max_norm` cai a zero junto com `mean_norm`, os clientes são congruentes e **não** deve haver divisão.

### 3.6 Saídas

- Gráficos ao vivo (`display_train_stats`) a cada rodada.
- `cfl_stats.split`: rodadas em que houve divisão (repetida se mais de um cluster dividiu na mesma rodada).
- `cfl_stats.clusters[-1]`: partição final.
- Tabela final (células 11–12): `results[cliente, modelo]` = acurácia do cliente com cada modelo do cache (0 se o cliente não pertencia àquele cluster). O máximo por cliente é destacado. A coluna do modelo FL é a do momento da 1ª divisão, então parte do ganho vem das rodadas a mais: sem divisão, o FL chega a ~0.60 em 80 rodadas, e os modelos de cluster, a ~0.71.

Obs.: `mean_norm`/`max_norm` registrados por rodada são os do **último** cluster iterado, não de todos.

### 3.7 Bugs, pegadinhas e compatibilidade

1. **Bug de índices na 2ª divisão em diante (corrigido em 2026-11-04).** `cluster_clients` recebe a submatriz `S[idc][:, idc]` e devolve **posições** dentro de `idc`, mas o notebook fazia `cluster_indices_new += [c1, c2]` como se fossem ids de cliente. Na 1ª divisão `idc = [0..N-1]` e funcionava por coincidência. Ao dividir um subcluster (ex. `[5..9]`) os ids saíam errados: clientes duplicados ou faltando. Agora é `cluster_indices_new += [idc[c1], idc[c2]]`. Antes da correção, executando o `cluster_clients` real: com 10 clientes em três grupos (`{0,1,2}`, `{3–6}`, `{7–9}`), a 2ª divisão de `[3..9]` gerou `[[0,1,2], [4,5,6], [0,1,2,3]]`, sem os clientes 7, 8 e 9 e com 0, 1 e 2 duplicados. O bug afetava o cenário do próprio notebook: em 12 seeds com EMNIST real, 7 fizeram mais de uma divisão e 4 terminaram com partição inválida. Na seed 7 a partição foi `[[0,1,3], [2,4], [0,1,2,3,4]]`, com os clientes 5 a 9 fora de todos os clusters. A acurácia final dessas 4 seeds ficou entre 0.61 e 0.72, e a correção a levou a 0.72–0.76. A seed 42, a do notebook, faz uma só divisão, e por isso a saída salva não mostrava o problema. A recursão do Algoritmo 3 do artigo (até K−1 divisões) também não funcionava.
2. `Server.aggregate_weight_updates` está quebrado (`target=` em vez de `targets=`, e `server.W` não é lista). Não é usado.
3. `eval_op` usa `model.train()`; troque por `model.eval()` se usar um modelo com dropout/BN.
4. **Compatibilidade com versões novas (corrigida em 2026-11-04):** o código usava `AgglomerativeClustering(affinity=...)`, removido no scikit-learn 1.4; `iter(loader).next()`; `data.train_labels`; e um `CustomSubset` sem `__getitems__`, que o torch 2.15 exige. O notebook inteiro foi executado com Python 3.12, torch 2.15 e scikit-learn 1.9.
5. Não há `requirements.txt`. Dependências: `torch`, `torchvision`, `numpy`, `matplotlib`, `pandas`, `IPython/jupyter`.
6. `acc_clients` usado em `cache_model` é o da rodada **anterior**; na rodada 1, é o do modelo inicial, calculado logo depois da sincronização.

### 3.8 Como rodar

```bash
pip install torch torchvision numpy matplotlib pandas jupyter
cd clustered-federated-learning
jupyter notebook clustered_federated_learning.ipynb
```

O EMNIST é baixado em `./EMNIST` (`root="."`).

### 3.9 Fundamentos do artigo (por que o algoritmo funciona)

Fonte: versão publicada no *IEEE TNNLS*, vol. 32, nº 8, 2021, pp. 3710–3722 (PDF em `docs/`). A numeração de equações abaixo é a dessa versão; a do arXiv v1 difere em 1 ou 2 números. As fórmulas estão em texto simples. Para o que o notebook de fato implementa, veja 3.10.

#### 3.9.1 Problema e suposições

- Há `M` clientes. O cliente `i` tem dados `D_i` amostrados de uma distribuição `φ_I(i)`. A função `I` (cliente → distribuição) é **desconhecida do servidor**, e o número `K` de distribuições também.
- FL padrão: `Δθ_i = SGD(θ, D_i) − θ` e `θ ← θ + Σ_i (|D_i|/|D|)·Δθ_i`.
- **Suposição 1 (FL):** existe um `θ*` que minimiza (localmente) o risco de **todos** os clientes ao mesmo tempo. Quando isso vale, os clientes são **congruentes**; senão, **incongruentes**.
- **Suposição 2 (CFL):** existe uma partição `C = {c_1, …, c_K}` dos clientes em que cada `c` satisfaz a Suposição 1.
- **Definição 1 (bipartição correta):** `c1 ∪ c2 = c` é correta se nenhum par `(i ∈ c1, j ∈ c2)` tem a mesma distribuição.
- O artigo **não** exige convexidade nem suavidade explícita: objetivos não-convexos (redes profundas) são permitidos. A convergência do FL a um ponto estacionário é assumida de trabalhos anteriores.

#### 3.9.2 Por que o cosseno separa os clientes

Com duas distribuições, o objetivo do FL é `F(θ) = a1·R1(θ) + a2·R2(θ)`, e em um ponto estacionário `0 = a1·∇R1(θ*) + a2·∇R2(θ*)`. Há duas possibilidades:

- ambos os gradientes são zero: os clientes são congruentes;
- `∇R1(θ*) = −(a2/a1)·∇R2(θ*) ≠ 0`: são incongruentes, e os gradientes dos dois grupos têm **normas positivas e direções opostas**. O cosseno vale +1 dentro de um grupo e −1 entre grupos (caso sem ruído).

Com dados finitos há ruído, e o **Teorema 1 (Separação)** quantifica o efeito:

- **Hipótese:** em todo ponto estacionário `θ*` do FL, `‖∇R_I(i)(θ*)‖ > ‖∇R_I(i)(θ*) − ∇r_i(θ*)‖`. Em outras palavras, o gradiente empírico do cliente é uma aproximação razoável do gradiente verdadeiro. Define-se `γ_i := ‖∇R − ∇r_i‖ / ‖∇R‖ ∈ [0, 1)`.
- **Conclusão:** existe uma bipartição `(c1*, c2*)` tal que, com `H_ij = −γ_i·γ_j + √(1−γ_i²)·√(1−γ_j²)`:
  - `α_cross^max` (maior cosseno entre clientes de lados opostos) é no máximo `cos(π/(K−1))·H + sin(π/(K−1))·√(1−H²)` quando `H ≥ cos(π/(K−1))`, e no máximo 1 caso contrário;
  - `α_intra^min` (menor cosseno entre clientes de mesma distribuição) é no mínimo `min H_ij`, sobre os pares de mesma distribuição;
  - para `K = 2`: `α_cross^max ≤ max(−H_ij)` e `α_intra^min ≥ min H_ij`. Sem ruído (`γ = 0`), `H = 1` e voltamos a ±1.
- **Corolário 1:** se `α_intra^min > α_cross^max`, a bipartição `argmin_{c1∪c2=c} max_{i∈c1, j∈c2} α_ij` (Eq. 23) é **sempre correta**.
- **Gap de separação:** `g(α) = α_intra^min − α_cross^max`. Se `g > 0`, a clusterização é correta. Calcular `g` exige conhecer `I`, então ele é um diagnóstico de experimento; o servidor não o calcula.
- **Condição implantável:** `α_intra^min ≥ 1 − 2·γ_max²`, logo a bipartição é correta se **`γ_max < √((1 − α_cross^max) / 2)`**, independentemente de `K`. `γ_max` é um limite **assumido** (o artigo o chama de "hiperparâmetro interpretável"), não estimado dos dados.

O teorema é um limite de **pior caso**. Na prática `α_intra^min` é bem maior e `α_cross^max` bem menor, principalmente quando a dimensão `d` dos parâmetros é grande. Em uma simulação com `d = 100`, `M = 3K` e gradientes gaussianos, a clusterização saiu correta com probabilidade ≈ 1 até para `K > 10` e `γ_max > 1`, fora das hipóteses do teorema.

#### 3.9.3 Quando dividir: os critérios de norma

Só se divide quando as duas condições valem:

1. **Perto de um ponto estacionário do FL** (Eq. 30): `0 ≤ ‖Σ_i (|D_i|/|D|)·∇r_i(θ*)‖ < ε1`.
2. **Clientes longe do estacionário local** (Eq. 31): `max_i ‖∇r_i(θ*)‖ > ε2 > 0`.

Critério de parada (Eq. 32): se `max_i ‖∇r_i(θ*)‖ < ε2`, todos os clientes já estão perto do seu próprio ótimo, são congruentes, e o CFL devolve o modelo FL.

A intuição é a seguinte. Se os clientes são incongruentes, o ponto estacionário do FL não pode ser estacionário para cada cliente, então alguma norma individual fica longe de zero. Se são congruentes, as normas individuais também vão a zero. A Fig. 8 do artigo mostra isso em dois clientes MNIST ao longo de 1000 rodadas: no caso congruente a norma máxima converge a zero; no incongruente ela estagna ou cresce, enquanto a norma média vai a zero nos dois casos.

No notebook, `mean_norm` aproxima o termo (30) e `max_norm` aproxima (31), ambos calculados com atualizações de pesos em vez de gradientes (3.9.5).

**Garantia "pelo menos tão bom quanto o FL".** O CFL só divide depois de calcular a solução FL. Se a divisão piorar o desempenho, é possível voltar a ela. O artigo afirma isso, mas não descreve como detectar a piora.

#### 3.9.4 Algoritmos do artigo

| Alg. | Nome | O que faz |
|---|---|---|
| 1 | Bipartição ótima | Ordena todos os pares `(i, j)` por similaridade decrescente e funde os grupos que contêm `i` e `j` até restarem 2. Resolve a Eq. 33 (minimiza o maior `α` entre os dois lados) em `O(M³)`. **Equivale a *single linkage*.** |
| 2 | FL | Rodadas de FedAvg ponderado por `|D_i|/|D_c|` até `‖Σ_i (|D_i|/|D_c|)·Δθ_i‖ < ε1`. |
| 3 | CFL recursivo | Roda o FL; se `max_i ‖∇r_i‖ ≥ ε2` e `√((1 − α_cross^max)/2) > γ_max`, faz a bipartição (Alg. 1) e repete em cada metade partindo de `θ*`; senão devolve `θ*`. Termina em no máximo `K−1` divisões. |
| 4 | Novo cliente | Desce a árvore de parâmetros (abaixo) escolhendo, em cada nível, o ramo mais similar. |
| 5 | CFL prático | Usa atualizações de pesos, checa os critérios **a cada rodada** e aceita a permutação de privacidade `P`. É o que o notebook implementa (3.10). |

**Algoritmo 5 em detalhe.** Cada cliente faz `θ_i ← θ_i + P⁻¹·Δθ_c(i)` e depois `Δθ_i ← P(SGD(θ_i, D_i) − θ_i)`. O servidor, para cada cluster `c`:

1. calcula `Δθ_c = (1/|c|)·Σ_{i∈c} Δθ_i` (média simples);
2. se `‖Δθ_c‖ < ε1` e `max_i ‖Δθ_i‖ > ε2`, calcula `α_ij` (cosseno entre os `Δθ`) e a bipartição `(c1, c2)` da Eq. 33;
3. calcula `α_cross^max`;
4. divide somente se `γ_max < √((1 − α_cross^max)/2)`.

`P` é uma permutação ortonormal opcional, gerada por uma semente trocada entre os clientes.

**Árvore de parâmetros e clientes novos (seção IV-C).** O servidor mantém uma árvore em que:

- cada nó guarda um cluster e o modelo `θ*` dele;
- a raiz é o modelo FL de todos os clientes;
- cada aresta guarda os updates pré-divisão dos clientes do filho.

Um cliente novo calcula `Δθ_new = SGD(θ*_v, D_new) − θ*_v` em cada nível e desce para o ramo cujo update armazenado tem maior similaridade máxima com o dele. O caminho raiz → folha também dá ao cliente modelos de especificidade crescente; combiná-los (ensemble) é indicado como trabalho futuro. O pseudocódigo impresso do Alg. 4 tem índices inconsistentes (`v0`/`v1` num lugar, `v1`/`v2` em outro).

#### 3.9.5 Atualizações de pesos no lugar de gradientes

O teorema é sobre gradientes completos, mas na prática o servidor só recebe `Δθ` depois de `n` épocas. O artigo usa o argumento de que, para perda suave e lr baixo, o update de uma época aproxima a direção do gradiente completo (Taylor; o resto "pode ser limitado", sem cota explícita). Empiricamente, `Δθ` separa **melhor**, com menos dados e mais longe do ponto estacionário. A vantagem é não alterar o protocolo de FL.

#### 3.9.6 Privacidade e custo

- O CFL usa só o que o FL já envia (os updates).
- A permutação `P` preserva normas e cossenos, então o servidor clusteriza sem ver os updates na ordem original.
- O próprio artigo reconhece um novo vazamento: o servidor aprende **quão parecidos** os clientes são. Não há análise formal de privacidade nem experimentos com privacidade diferencial ou compressão de updates; os dois aparecem só como trabalho futuro. O artigo cita mecanismos como o secure aggregation como forma de evitar vazamento por inversão de modelo.
- Custo no servidor: matriz `M × M` e `O(M³)` por bipartição, considerado desprezível.

#### 3.9.7 Experimentos do artigo

| Experimento | Configuração | Resultado |
|---|---|---|
| Label-swap, MNIST e CIFAR-10 | `M = 20`, `K = 4`, partição aleatória de tamanho igual, cada cluster troca 2 rótulos, CNNs, 3 épocas locais | `g(α)` cresce com o tamanho dos dados: MNIST precisa de ~20 pontos por cliente e CIFAR de ~500. A separação correta aparece em ~10 rodadas de FL. `Δθ` separa melhor que gradientes. |
| Congruente × incongruente | MNIST, 2 clientes, 1000 rodadas | Confirma os critérios de norma (30)/(31). |
| CIFAR-10 "permuted labels" | `M = 20`, `K = 4`, uma permutação aleatória de rótulos por cluster, CNN de 5 camadas, 3 épocas, batch 100 | O FL estaciona em ~20% nas primeiras 50 rodadas. Divisões nas rodadas 50, 100 e 150 levam a ~60%, mais que o dobro do FL. |
| AG News | 120.000 artigos, 4 tópicos, 20 sub-corpora (1 tópico cada), LSTM de 2 camadas, previsão da próxima palavra | Divisões nas rodadas 30, 60 e 90 recuperam os 4 tópicos. Perplexidade < 36, contra 42 do FL. |

O artigo **não informa**: lr, momentum, valores usados de `ε1`/`ε2`/`γ_max`, número de repetições ou barras de erro. Também não compara com baselines de aprendizado multitarefa federado, apenas com o FL.

#### 3.9.8 Como escolher ε1 e ε2 (recomendação do artigo)

1. **`ε1`** deve ser "tão pequeno quanto as restrições de tempo permitirem", porque a qualidade da separação melhora monotonicamente perto do ponto estacionário. Regra prática: `ε1 ≈ (1/10)·max_t ‖Δθ_c‖`, um décimo da maior norma média de update observada.
2. **`ε2`** deve refletir o número de clientes e/ou o conhecimento prévio sobre a heterogeneidade dos dados. Quanto menor, mais provável que a população seja dividida. O artigo obteve bons resultados com **`ε2 ∈ [ε1, 10·ε1]`**.

No notebook, `EPS_2 / EPS_1 = 4`, dentro dessa faixa. A regra de `ε1` daria 0.03–0.04, abaixo do que o ruído do SGD permite atingir, então o notebook usa `EPS_1 = 0.2`, o menor valor testado que divide em todas as seeds dentro de 80 rodadas (D-015). As normas dependem de lr, épocas e arquitetura, então os valores não são portáveis entre setups.

#### 3.9.9 Limitações (declaradas ou evidentes)

- A garantia vale para (aproximações de) gradientes em um ponto estacionário. O artigo não discute mínimos locais nem pontos de sela.
- O limite do teorema é de pior caso e frouxo. `γ_max` é assumido, não estimado.
- Assume que **todos** os clientes de um cluster participam em **toda** rodada. Amostragem parcial não é tratada, e é a lacuna que o StoCFL ataca.
- A passagem de gradientes para `Δθ` é heurística (sem cota explícita).
- Só compara com o FL, sem baselines de aprendizado multitarefa federado.
- Clientes adversários, privacidade diferencial, compressão e clientes que saem do sistema não são analisados.

#### 3.9.10 Posicionamento frente a outros métodos

- **Custo de comunicação do CFL:** cresce no máximo linearmente com o número de divisões, e só depois que a solução FL foi atingida.
- **MOCHA** (Smith et al.): modela a similaridade entre clientes por uma matriz de correlação, com otimização biconvexa alternada. Só serve para objetivos convexos e escala mal.
- **Corinzia e Buhmann:** rede Bayesiana com inferência variacional. Lida com modelos não-convexos, mas é cara porque os modelos dos clientes são refinados sequencialmente.
- **Ghosh et al.** (precursor do IFCA): agrupa por distância `l2` em vez de cosseno. Segundo o artigo, só funciona com riscos convexos e mínimos bem separados, não distingue o caso congruente do incongruente (divide clientes mesmo no non-IID clássico) e decide agrupar já após a primeira rodada.
- **CFL:** não altera o protocolo de FL, não precisa de `K`, aceita objetivos não-convexos, decide de forma adaptativa se deve dividir e traz garantias sobre a qualidade da clusterização.

### 3.10 Mapa artigo ↔ notebook

O notebook implementa o **Algoritmo 5**, sem a permutação opcional `P`. Até 2026-11-04 ele tinha simplificações e acréscimos próprios, corrigidos pela D-014 em [decisoes.md](decisoes.md). A tabela mostra onde ele segue o artigo e o que mudou.

| Elemento | Artigo | Notebook / `fl_devices.py` | Consequência |
|---|---|---|---|
| Critério de divisão | `‖Δθ_c‖ < ε1` e `max‖Δθ_i‖ > ε2` e `γ_max < √((1−α_cross^max)/2)` | `mean_norm < EPS_1` e `max_norm > EPS_2` e `GAMMA_MAX < √((1−α_cross^max)/2)` (célula 9), mais `len(idc) > 1` | **Segue o artigo.** `len(idc) > 1` só garante que os dois lados da bipartição existam (Definição 1). O notebook original não tinha a checagem de `γ_max` e exigia `len(idc) > 2` e `c_round > 20`. |
| Algoritmo de bipartição | Alg. 1: ordem decrescente de `α`, fundindo até restarem 2 (≡ *single linkage*; minimiza o maior `α` entre os lados) | `Server.cluster_clients` transcreve o Alg. 1 ([fl_devices.py:130](clustered-federated-learning/fl_devices.py#L130)) | **Segue o artigo.** Atinge o ótimo da Eq. 33 em todas as matrizes testadas. O notebook original usava *complete linkage*. Com `g(α) > 0` os dois dão o mesmo resultado, porque qualquer linkage acerta (Corolário 1). Com `g(α) ≤ 0` eles divergem, e a garantia do artigo não vale: em matrizes sintéticas, o *complete* acertou os grupos verdadeiros mais vezes (652 contra 447 de 1391), porque o Alg. 1 tende a isolar um único cliente. |
| Agregação | Alg. 2 pondera por `|D_i|/|D_c|`; Alg. 5 usa `1/|c|` | Média uniforme (`reduce_add_average`) | Consistente com o Alg. 5. |
| Quando divide | Alg. 3: só depois do FL convergir. Alg. 5: checa a cada rodada. | Checa a cada rodada | **Segue o Alg. 5.** A proximidade do ponto estacionário depende só de `EPS_1`: com `EPS_2` baixo, as divisões podem sair cedo demais (nas rodadas 3 e 4, com `EPS_2 = 0.5`). |
| Otimizador local | `SGD(θ, D)`: SGD com minilotes, função só de `θ` e `D` (Eq. 1); lr e momentum não informados | `SGD(lr=0.1)`, um otimizador por cliente, sem momentum e sem decaimento | **Segue o artigo.** O notebook original usava `momentum=0.9`, com buffers que persistiam entre rodadas (`dW` ~1,8× maior e cosseno ~0.86 com os buffers zerados), e decaimento ×0.99 por rodada, que levava `mean_norm` abaixo de `EPS_1` mais cedo. |
| Similaridade | Cosseno entre `Δθ` (Eq. 47) | `pairwise_angles` entre `dW` | OK. |
| Árvore de parâmetros / Alg. 4 | Árvore com cache dos updates pré-divisão; novos clientes descem a árvore | `server.model_cache`: lista plana de `(ids, pesos, acurácias)`. **Sem árvore e sem clientes novos.** | Não há como atribuir um cliente novo a um cluster. Está no [backlog](backlog.md). |
| Permutação de privacidade `P` | Opcional | Ausente | Sem proteção; irrelevante para simulação. |
| Escolha do modelo final | Fallback para o FL se a divisão piorar | Células 11–12 escolhem, por cliente, o modelo de maior acurácia **na mesma validação usada para reportar** | Viés otimista leve nos ganhos reportados (~10%). Não é um procedimento do artigo. |
| Participação | Todos os clientes do cluster em toda rodada | `frac = 1.0` | Consistente. |
| Dados e setup | Label-swap/permutação em MNIST e CIFAR-10, AG News, `M = 20`, 3 épocas, batch 100 | **EMNIST** (62 classes), Dirichlet α = 1, rotação 180°, `M = 10`, 1 época, batch 128, 80 rodadas | O notebook **não reproduz nenhum experimento do artigo**; EMNIST, Dirichlet, rotação e 80 rodadas não aparecem lá. |
| `ε1`, `ε2` | Regra: `ε1 ≈ max‖Δθ_c‖/10`, `ε2 ∈ [ε1, 10·ε1]` | 0.2 e 0.8 (razão 4) | `ε2` dentro da faixa. `ε1` acima da regra de bolso, porque ela nunca dispara nesse cenário (3.9.8). |

---

## 4. StoCFL: Stochastic Clustered Federated Learning (Zeng et al.)

Artigo: *Zeng, Hu, Liu, Yu, Wang, Xu. "StoCFL: A stochastically clustered federated learning framework for Non-IID data with dynamic client participation", Neural Networks 187 (2025) 107278 (arXiv:2303.00897; a v1 de 2023 se chamava "Stochastic Clustered Federated Learning").* Teoria, experimentos e hiperparâmetros em 4.15; correspondência com o código em 4.16; como reproduzir em 4.17.

### 4.1 O que o algoritmo faz

O StoCFL é **aglomerativo (bottom-up)** e funciona com **participação parcial**: só `num_per_round` clientes por rodada.

**Indisponibilidade opcional (dropout com retorno, `--drop`).** Só no `StoCFL-FCC+CFL.py` (4.2) e desligada por padrão (`--drop 0` não muda nada, nem o sorteio). Com `--drop > 0`, a cada rodada um cliente disponível cai com probabilidade `drop` e fica fora `L ~ U{1, …, drop_rounds}` rodadas; na rodada seguinte à ausência ele volta e não pode cair de novo (processo em 4.8; decisões em D-032). Quem está fora **não é sorteado**: os `num_per_round` clientes são sorteados só entre os disponíveis, e, se houver menos disponíveis que `num_per_round`, participam todos. Se não houver nenhum, a rodada é pulada (a partição é gravada e o treino não roda). O resto do algoritmo não muda: `Ψ` continua sendo calculado uma vez na âncora, quem volta usa o `Ψ` guardado e recebe os modelos atuais, e o cliente que está fora continua no seu cluster e conta no centro dele. O efeito esperado é um **atraso curto** na observação dos clientes, e não foi medido no ARI ([plano](plano-dropout-stocfl.md), seção 2).

**Fase 0, inicialização.**
- Cada cliente começa como um cluster sozinho: `cluster(i) = {i}`.
- `anchor` (âncora) = pesos iniciais do modelo. **Nunca muda.**
- `gmodel` (modelo global) = cópia da âncora.

**Fase 1, representação do cliente (feita uma única vez por cliente).**
Na primeira vez que um cliente é sorteado, ele calcula, no modelo âncora e sem treinar, o gradiente da perda em todo o seu dataset, e devolve o vetor normalizado
`ψ_i = Normalize(∇ℓ(anchor; D_i))`, o `Ψ` do artigo. Esse vetor resume a distribuição de dados do cliente: clientes com a mesma distribuição produzem `ψ` quase paralelos. Como **todos usam o mesmo ponto fixo**, os `ψ` de clientes observados em rodadas diferentes continuam comparáveis. É isso que permite clusterizar com amostragem estocástica, diferente do CFL, que precisa de todos ao mesmo tempo.

**Fase 2, clusterização estocástica (toda rodada).**
1. Sorteia `S_r` (clientes da rodada; com `--drop > 0`, só entre os disponíveis) e agrupa esses clientes pelo cluster atual.
2. Centro de cada cluster amostrado = **média dos `ψ` de todos os seus membros** (Eq. 2 do artigo), não só dos sorteados na rodada.
3. Calcula o cosseno entre as direções de todos os pares de clusters amostrados.
4. Percorre os pares em ordem **decrescente** de similaridade: se `cos > τ`, **funde** os dois clusters; no primeiro par que não passa de `τ`, para.
   - Como a fusão é transitiva, o resultado equivale a ***single-linkage* com limiar τ** entre os clusters amostrados na rodada: `A~B` e `B~C` juntam `A,B,C` mesmo que `cos(A,C) < τ`.
5. Clusters **só se fundem, nunca se dividem**: um erro de fusão é permanente.

Ao longo das rodadas, clusters de clientes com a mesma distribuição vão se juntando, e o número de clusters converge para o nº de distribuições reais (se `τ` estiver bem calibrado).

**Fase 3, otimização bi-nível (só se `--train 1`).** Para cada cliente sorteado:
- **Modelo do cluster:** treina o modelo do seu cluster com
  `loss = CE + (μ/2)·‖w − gmodel‖²` (termo proximal estilo FedProx, puxando o modelo do cluster para o global; μ é o λ do artigo).
- **Modelo global:** treina o `gmodel` com CE pura, com todos os clientes partindo do mesmo `gmodel` da rodada (FedAvg, como no artigo).
- Servidor: `gmodel ← média dos globais treinados`; `modelo[k] ← média dos modelos treinados pelos membros sorteados do cluster k`.
- Cluster sem modelo ainda recebe uma cópia de `ω₀` (`anchor`), como na inicialização do artigo (`ω₀ = θ₁ = ⋯ = θ_N`). A cópia é feita só quando o cluster é sorteado, para não ocupar memória com `N` modelos.

### 4.2 Pontos de entrada

| Script | Propósito | Cenários | Estado |
|---|---|---|---|
| [StoCFL-FCC.py](StoCFL/StoCFL-FCC.py) | **FCC = Federated Client Clustering**: avaliar só a clusterização (`--train 0` por padrão). | `fskewed`, `lskewed`, `shifted`, `rotated` | Roda com `--train 0` em `shifted`, `fskewed` e `lskewed` (este com `--process 0`, 4.12 #3). `rotated` não funciona neste script (4.12 #2). |
| [StoCFL-FCC+CFL.py](StoCFL/StoCFL-FCC+CFL.py) | Clusterização + treino bi-nível (`--train 1` por padrão). | Rotated MNIST (4 rotações, ou `--k`) / Rotated CIFAR-10 (2 rotações) / MNIST com rótulos non-IID por Dirichlet (`--dirichlet_alpha`, `k = 1`) | **Script principal e mais consistente.** |
| [StoCFL-FEMNIST.py](StoCFL/StoCFL-FEMNIST.py) | StoCFL em FEMNIST (particionamento natural por escritor, sem ground truth de cluster). | FEMNIST (LEAF) | Roda; fluxo testado com pickles LEAF falsos, sem o dataset real (4.12 #5). |

Os três definem **sua própria cópia** da classe `StandaloneServer` com a mesma lógica de clusterização e pequenas diferenças de avaliação e log. Uma mudança no algoritmo precisa ser replicada nos três.

**Exceção atual:** `--drop` e `--drop_rounds` (dropout com retorno, 4.1) e `--dirichlet_alpha` (rótulos non-IID, 4.7) só existem no `StoCFL-FCC+CFL.py`, e o recall por classe no `accuracy.pkl` (4.10) também. O `StoCFL-FCC.py` e o `StoCFL-FEMNIST.py` ainda não os têm e sorteiam `num_per_round` entre todos os clientes, como antes (D-032; mesmo precedente do `--k`, D-029). A replicação nos dois é o passo 5 do [plano](plano-dropout-stocfl.md): o mesmo bloco de sorteio e as mesmas flags, com o módulo `availability.py` compartilhado.

### 4.3 Grafo de chamadas (StoCFL-FCC+CFL.py)

```text
__main__                                                    StoCFL-FCC+CFL.py:207
 ├─ argparse → args  (inclui --drop, --drop_rounds, --dirichlet_alpha)
 ├─ setup_seed(args.seed)                                   functional.py:197
 ├─ args.k = --k (default: 4 mnist, 2 cifar); exige n % k == 0 e, no cifar, k = 2
 ├─ exige 0 <= drop < 1, drop_rounds >= 1 e, com drop > 0, num_per_round <= n; com --dirichlet_alpha, mnist, k = 1 e α > 0
 ├─ args.root = ./datasets/{dataset}/ ; args.save_dir = ./datasets/rotated_{dataset}_{n}_{seed}[_k{k}][_a{α}]/   (sufixos só se k ≠ padrão e com --dirichlet_alpha)
 ├─ [--process 1, sem --dirichlet_alpha] RotatedMNIST.pre_process(thetas=[360·i/k], shards=n/k)   datasets.py:157
 │  [--process 1, --dirichlet_alpha α]  RotatedMNIST.pre_process_dirichlet(n, α, seed)   datasets.py:188
 │                                        └─ dirichlet_partition → hetero_dir_partition (fedlab)   datasets.py:13
 │               RotatedCIFAR10Partitioner.pre_process(shards=n/2)  datasets.py:284
 ├─ model = SimpleLinear (mnist) | CNN_CIFAR10 (cifar)
 ├─ trainer = RotatedMNISTTrainer(model, args)              trainer.py:231  (serve para mnist E cifar)
 ├─ os.mkdir(./logs/runs-rotated-...[-k{k}][-a{α}][-drop{d}-r{L_max}]-time-...)  ; Logger
 ├─ StandaloneServer(model, cuda, trainer, args)            StoCFL-FCC+CFL.py:30  (cria self.availability)
 └─ .main()                                                 StoCFL-FCC+CFL.py:54
      └─ para cada rodada:
          ├─ [--drop > 0] availability.step() → up[c]       availability.py:25
          │     ├─ log "Round r/T, unavailable [...]" e availability.pkl
          │     └─ random.sample(disponíveis, min(num_per_round, nº de disponíveis))
          │  [--drop 0]   random.sample(clientes, num_per_round)   (como antes)
          ├─ trainer.observe(não_observados, anchor)        trainer.py:257
          │     ├─ dataset.get_data_loader(id, obbs)        trainer.py:260
          │     └─ dataset_representation(self, anchor, loader)   trainer.py:21
          ├─ cluster_center (média dos ψ de todos os membros)   functional.py:86
          ├─ inter_cluster_union                            StoCFL-FCC+CFL.py:132
          │     ├─ dt_matrix → cosine_sim                   functional.py:77, :54
          │     ├─ parse_matrix (ordena pares)              functional.py:90
          │     └─ unite(i, j)                              StoCFL-FCC+CFL.py:155
          ├─ get_cluster (log + assert)                     StoCFL-FCC+CFL.py:194
          ├─ [--train 1, rodada sem participantes] accuracy_log recebe {"cluster": [], "global": []}; sem treino
          └─ [--train 1, com participantes]
                ├─ trainer.train(cids, modelos_cluster, gmodel)        trainer.py:243
                │     ├─ train_alone_prox (cluster, com μ)  trainer.py:284
                │     └─ _train_alone (global)              trainer.py:269
                ├─ gmodel ← fedavg(gmodels)
                ├─ modelo[k] ← fedavg(updates do cluster k)
                └─ evaluate_recall (functional.py:103; loss e acc iguais às do evaluate do fedlab, mais o recall por classe)
                   com trainer.get_test_dataloader(⌊cid·k/n⌋)
```

### 4.4 Funções do servidor (`StandaloneServer`)

Linhas referentes a [StoCFL-FCC+CFL.py](StoCFL/StoCFL-FCC+CFL.py); a lógica é idêntica nos outros dois scripts, exceto o sorteio entre os disponíveis (`--drop`, 4.2).

| Método | Linha | O que faz |
|---|---|---|
| `__init__` | [:30](StoCFL/StoCFL-FCC+CFL.py#L30) | Inicializa clusters unitários, `psi = {}`, `cluster_parameters = {}`, `gmodel`, `anchor` (= pesos iniciais) e `availability` (`Availability`, 4.8; só avança com `--drop > 0`). |
| `main` | [:54](StoCFL/StoCFL-FCC+CFL.py#L54) | Loop de rodadas (fases 1–3 de 4.1) + logs/arquivos. Com `--drop > 0`, chama `availability.step()` e sorteia os `num_per_round` só entre os disponíveis; com `--drop 0`, sorteia entre todos, como antes. Rodada sem participantes: não treina, mas grava a partição e uma entrada vazia em `accuracy_log`. |
| `bucket(client_list, items)` | [:181](StoCFL/StoCFL-FCC+CFL.py#L181) | Agrupa `items` (os modelos treinados) pelo cluster atual de cada cliente. Retorna `(ids_de_cluster_presentes, listas)` em ordem crescente de id. |
| `inter_cluster_union(clusters, direções)` | [:132](StoCFL/StoCFL-FCC+CFL.py#L132) | Calcula o cosseno entre pares, grava `cos_rec.log`, funde pares com `cos > τ` em ordem decrescente e para no primeiro que não passa de `τ`. Com ≤ 1 cluster amostrado não faz nada. |
| `unite(i, j)` | [:155](StoCFL/StoCFL-FCC+CFL.py#L155) | Union-find com relabel imediato. (a) Se `i` já foi absorvido nesta rodada (`i ∉ conteúdo[i]`), redireciona para o cluster atual do cliente `i`; idem `j`. (b) Mantém o **menor id**. (c) **Modelo:** se `|C_i| < |C_j|` e `j` tem modelo, `i` herda o modelo de `j` (o cluster maior "vence"); caso contrário `i` mantém o seu. (d) Move membros, esvazia `j` e apaga o modelo de `j`. |
| `get_cluster` | [:194](StoCFL/StoCFL-FCC+CFL.py#L194) | Reescreve `cluster_rec.log` com a partição atual e faz `assert` de que todos os clientes estão em exatamente um cluster. |

### 4.5 Estado do servidor e invariantes

| Estrutura | Tipo | Significado |
|---|---|---|
| `find_cluster_content` | `dict[int, list[int]]` | `cluster_id → ids dos clientes`. Clusters mortos ficam com lista vazia. |
| `find_client_cluster` | `list[int]` | `cliente → cluster_id` atual. |
| `psi` | `dict[int, Tensor1D]` | Representação ψ de cada cliente já observado; **imutável** depois de calculada. |
| `anchor` | `Tensor1D` | Pesos iniciais; fixo. |
| `gmodel` | `Tensor1D` | Modelo global (FedAvg dos clientes sorteados). |
| `cluster_parameters` | `dict[int, Tensor1D]` | Modelo de cada cluster (criado sob demanda). |
| `availability` | `Availability` | Estado de disponibilidade dos `N` clientes (`down_left`, `grace`) e gerador próprio. Só avança com `--drop > 0`, e não guarda nada do algoritmo de clusterização. |

Os modelos circulam como **vetores 1-D serializados** (`SerializationTool.serialize_model`) e são carregados num `nn.Module` com `deserialize_model`.

**Invariantes**, para preservar ao modificar o código:
1. O id de um cluster vivo é o **menor id de cliente** entre seus membros, e um cluster vivo `k` sempre contém o cliente `k`. O teste `i not in find_cluster_content[i]` em `unite` depende disso.
2. A soma dos tamanhos dos clusters é igual a `client_num` (verificado em `get_cluster`).
3. O nº de clusters é monotonicamente **não crescente**.
4. `psi[i]` é calculado uma vez, a partir da mesma `anchor`.
5. Todo cluster sorteado na rodada, e todo cluster com mais de um membro, contém só clientes já observados, isto é, com `psi` calculado. Só clusters sorteados se fundem, e todo cliente sorteado é observado antes da fusão; por indução, nenhum cluster unido tem membro sem `psi`. Verificado em 2026-11-04 por esse argumento e por simulação com o código real de `unite`, `bucket` e `inter_cluster_union` (5 seeds × 40 rodadas, zero violações). `cluster_center` depende disso para encontrar o `psi` de todos os membros. A invariante deixa de valer se um dia houver fusão de clusters não sorteados ou cliente sem observação (por exemplo, ao implementar clientes novos). **Com `--drop > 0` ela continua valendo**, porque o sorteio entre os disponíveis só muda quem é sorteado, e todo sorteado é observado antes da fusão; um cliente indisponível não é observado nem funde, e fica no seu cluster. Verificado em 2026-11-09 com execuções pequenas (`--drop 0.3`, `n = 40`): em cada rodada, todo membro de cluster com mais de um cliente já tinha sido sorteado, e as chaves de `psi.pkl` eram exatamente a união dos participantes.

### 4.6 Trainers (`trainer.py`): os "clientes"

Cada Trainer herda de `fedlab.SerialTrainer` e simula **todos os clientes** com um único `nn.Module` (`self._model`), recarregando os pesos de cada cliente antes de treinar. Interface que o `StandaloneServer` espera:

| Membro | Uso |
|---|---|
| `client_num` | nº total de clientes |
| `observe(ids, anchor) → [ψ]` | Fase 1 |
| `dataset_representation(trainer, anchor, loader) → Ψ` | função do módulo `trainer.py`, usada por todos os `observe`: gradiente normalizado na âncora, sem treino |
| `train(ids, modelos_cluster, gmodel) → (modelos_cluster_treinados, globais_treinados)` | Fase 3 |
| `train_alone_prox(params, gmodel, loader)` | treino com termo proximal `0.5·μ·‖w−w_g‖²` |
| `_train_alone(params, loader)` | treino local simples |
| `get_test_dataloader(cid)` | avaliação (só com `--train 1`) |
| `evaluate(ids, model, crit)` | só em `StoCFL-FCC.py` com `--train 1` |
| `dataset.pre_process()` | só em `StoCFL-FCC.py` com `--process 1` |

Todos usam `SGD(lr=args.lr)` **sem momentum** (`self.optimizer` compartilhado, sem estado, então compartilhar não causa problema).

| Trainer | Linha | Cenário | Clientes | Ground truth (id → grupo) | Dados da observação | Batch de treino |
|---|---|---|---|---|---|---|
| `FEMNISTTrainer` | [trainer.py:34](StoCFL/trainer.py#L34) | FEMNIST (LEAF) | `--client_num` (3597) | não há | dataset inteiro, lote `obbs` | `batch_size` |
| `ShiftedMNISTTrainer` | [trainer.py:117](StoCFL/trainer.py#L117) | MNIST com rótulo `(y+s) % 10`, `s ∈ {0,3,6,9}` | 400 (fixo) | `cid // 100` | 80% dos dados do cliente (`random_split`), lote cheio | **batch cheio** (ignora `batch_size`) |
| `RotatedMNISTTrainer` | [trainer.py:231](StoCFL/trainer.py#L231) | Rotated MNIST **ou** CIFAR (via `args.dataset`) | `args.n` | `⌊cid·k/n⌋` | dataset inteiro, lote `obbs` | `batch_size` |
| `LabelSkewMNISTTrainer` | [trainer.py:309](StoCFL/trainer.py#L309) | label skew: `k=4` grupos de classes `[0,1,2],[3,4],[5,6],[7,8,9]`; `k=10` um grupo por classe | ~400 (k=4) / ~1000 (k=10) | blocos contíguos de ~100 | dataset inteiro, lote `batch_size` | `batch_size` |
| `FeatureSkewHybridMNISTTrainer` | [trainer.py:407](StoCFL/trainer.py#L407) | 100 clientes MNIST + 100 FashionMNIST | 200 (fixo) | `cid < 100` → MNIST | dataset inteiro, lote cheio | `batch_size` |

A observação é **um único gradiente** em todo o dataset do cliente, acumulado por lotes, então o tamanho do lote não muda o resultado (diferença de ~1e-8 no teste). O modelo fica em modo `eval`, para que o dropout do `CNN_FEMNIST` não torne `Ψ` aleatório: o artigo define `Ψ` como função de `D`, sem mencionar dropout.

### 4.7 Dados (`datasets.py`) e modelos

Os Partitioners geram, em `--process 1`, um arquivo `data{cid}.pkl` (um `BaseDataset`) por cliente em `save_dir/train/` e um `data{g}.pkl` por grupo em `save_dir/test/`. Depois, `get_data_loader(id, batch_size, type)` faz `torch.load` **do disco a cada chamada** e cria um `DataLoader` **sem shuffle** (`batch_size=None` = batch com o dataset inteiro).

| Classe | Linha | Geração |
|---|---|---|
| `BaseDataset` | [datasets.py:23](StoCFL/datasets.py#L23) | Dataset trivial `(x, y)`. |
| `RotatedMNIST` | [datasets.py:147](StoCFL/datasets.py#L147) | `pre_process`: para cada θ em `thetas` (default {0, 90, 180, 270}; o script passa `k` ângulos igualmente espaçados, `360·i/k`), faz `random_slicing` do MNIST inteiro em `shards` partes IID. Cliente `cid = índice_θ·shards + shard`. Teste: 1 arquivo por θ. `pre_process_dirichlet(n, α, seed)` ([:188](StoCFL/datasets.py#L188), com `--dirichlet_alpha`): **rótulos non-IID, sem rotação**. Divide o MNIST de treino inteiro entre os `n` clientes com `dirichlet_partition` e grava um só teste, o MNIST de teste inteiro (`test/data0.pkl`), no mesmo formato de arquivos; por isso o script exige `k = 1`, e o `RotatedMNISTTrainer` e o `get_test_dataloader` funcionam sem mudança. |
| `dirichlet_partition(targets, n, α, seed, min_require_size=50)` | [datasets.py:13](StoCFL/datasets.py#L13) | Para cada classe, sorteia proporções `~ Dir(α)` entre os `n` clientes, com o balanceamento do FedLab (cliente que já passou de `amostras/n` não recebe mais), e repete até todo cliente ter `min_require_size` amostras (`hetero_dir_partition` do `fedlab` 1.2.1, o mesmo algoritmo do `DirichletPartitioner` usado pelo D-PRIDE). Semeia o `np.random` global com a `seed` e **restaura o estado** ao sair, então é determinística por `(α, seed)` e não muda o resto da execução. **Não limita as tentativas**: com `α` pequeno pode demorar ou não terminar (com `n = 240` e `min_require_size = 50`, `α` = 0.5 e 1.0 terminam; `α = 0.1` não foi testado aqui, e a regra do D-PRIDE falha nele; [plano](plano-dropout-treino-stocfl.md), seção 4). Testes em `tests/test_dirichlet.py`. |
| `RotatedCIFAR10Partitioner` | [datasets.py:270](StoCFL/datasets.py#L270) | Igual, com θ ∈ {0, 180}, normalização `(0.5, 0.5, 0.5)`, baixa o CIFAR. |
| `ShiftedMNISTPartitioner` | [datasets.py:216](StoCFL/datasets.py#L216) | Shifts {0,3,6,9} × `shards=100`. |
| `HybridMNISTPartitioner` | [datasets.py:34](StoCFL/datasets.py#L34) | 100 partes IID do MNIST (ids 0–99) + 100 do FashionMNIST (ids 100–199); o teste usa os datasets torchvision originais. |
| `ComplexMNISTPartitioner` | [datasets.py:93](StoCFL/datasets.py#L93) | ⚠️ Não usado e quebrado (`label_skew_parition(..., slice=50)` não aceita `slice`). |

Cada grupo de rotação usa **as mesmas 60.000 (ou 50.000) imagens**, só que rotacionadas e com outra partição aleatória. Por cliente: MNIST tem `60000 / (n/k)` amostras (`k = 4` por padrão) e CIFAR tem `50000 / (n/2)`. Com `--dirichlet_alpha`, cada imagem vai para um só cliente e os tamanhos variam (média `60000 / n`; os números das 20 partições de `n = 240` estão em 4.11).

| Modelo | Arquivo | Arquitetura | Usado em |
|---|---|---|---|
| `SimpleLinear` | [models/linear.py](StoCFL/models/linear.py) | MLP 784→2048→10 + `log_softmax` (CE sobre log_softmax é equivalente) | MNIST (todos os cenários) |
| `CNN_CIFAR10` | [models/cnn.py:83](StoCFL/models/cnn.py#L83) | conv5(6)→pool→conv5(16)→pool→120→10 | Rotated CIFAR |
| `CNN_FEMNIST` | [models/cnn.py:13](StoCFL/models/cnn.py#L13) | conv3(32)→conv3(64)→pool→dropout(0.5)→9216→128→62 | FEMNIST |
| `CNN_MNIST`, `AlexNet_CIFAR10` | models/cnn.py | importados, não usados | — |
| `models/model.py` | — | duplicatas (ConvNet, MLP, ...) | não usado |

### 4.8 `functional.py` e `availability.py`

| Função | Linha | Uso |
|---|---|---|
| `Availability(n, drop, rounds, seed).step()` | [availability.py:25](StoCFL/availability.py#L25) | Processo de disponibilidade dos clientes, com retorno (dropout, [plano](plano-dropout-stocfl.md) e D-032). `step()` é chamado uma vez por rodada e devolve `up[c]` para os `n` clientes: cada cliente disponível cai com probabilidade `drop` e fica fora `L ~ U{1..rounds}` rodadas; a rodada seguinte à ausência é de retorno (disponível, sem sorteio), então a ausência consecutiva nunca passa de `rounds`. Gerador próprio (`random.Random("drop-{seed}")`), sem `torch` e sem consumir o gerador global; com `drop = 0` devolve todos disponíveis sem sorteio. Valida `0 ≤ drop < 1` e `rounds ≥ 1` (`ValueError`). Disponibilidade média `1 / (1 + d·ℓ)`, com `ℓ = (L_max + 1)/2` (0,645 com `d = 0,1` e `L_max = 10`). **Usado pelo `StoCFL-FCC+CFL.py`** (`self.availability`, 4.4); os outros dois scripts ainda não o usam (4.2). Testes: `../../.venv/bin/python -m unittest tests/test_availability.py -v`, a partir de `projetos/StoCFL/`. |
| `cosine_sim(a, b)` | [functional.py:54](StoCFL/functional.py#L54) | Cosseno (eps=1e-6). **Métrica de similaridade usada.** |
| `dt_matrix(lista)` | [functional.py:77](StoCFL/functional.py#L77) | Matriz triangular superior de `cosine_sim`. A linha comentada permite trocar para `dt`. |
| `dt(a, b)` | [functional.py:59](StoCFL/functional.py#L59) | Alternativa (norma mínima no segmento entre gradientes normalizados, estilo MGDA). Não usada. |
| `cluster_center(psi, membros)` | [functional.py:86](StoCFL/functional.py#L86) | Centro do cluster: média dos `ψ` de todos os membros (Eq. 2). |
| `parse_matrix(M, ids, descending)` | [functional.py:90](StoCFL/functional.py#L90) | Converte a matriz em `{"a,b": sim}` com os **ids de cluster** e devolve as chaves ordenadas. |
| `evaluate_recall(model, crit, loader)` | [functional.py:103](StoCFL/functional.py#L103) | Avaliação usada pelo `StoCFL-FCC+CFL.py`: devolve `(loss, acc, recall)`, com `loss` e `acc` calculados como no `evaluate` do FedLab (loss somada sobre os lotes, acertos / total; idênticos bit a bit, conferido no teste e na regressão) e `recall[c]` = acertos da classe `c` / amostras de `c` (`None` se o teste não tem `c`). Uma só passada pelo teste. Com o `recall` e a distribuição de rótulos de um cluster dá para calcular a acurácia ponderada pela distribuição do cluster, que o teste global balanceado não mede (D-045). |
| `setup_seed(seed)` | [functional.py:197](StoCFL/functional.py#L197) | Seeds de torch/cuda/numpy/random + `cudnn.deterministic`. |
| `quadprog`, `optim_lambdas` | :14, :28 | Resto de MGDA (cvxopt). Não usados, mas exigem `cvxopt` no import. |
| `evaluate_personalization` | :127 | ⚠️ Quebrado (desempacota 4 listas em 2 variáveis; `range(lista)`). Não usado. |
| `evaluate_fairness`, `MnistRotated` | :137, :146 | Não usados. |

O `os` usado pelos scripts principais chega via `from functional import *`.

### 4.9 Variáveis e impacto no resultado

#### Hiperparâmetros do algoritmo

| Variável | Papel | Aumentar | Diminuir |
|---|---|---|---|
| `--tau` (τ) | Limiar de cosseno para fundir clusters. **É o principal parâmetro de clusterização.** | Menos fusões, **mais clusters**. Se for alto demais, clientes da mesma distribuição ficam separados e cada cluster tem poucos dados. | Mais fusões, **menos clusters**. Se for baixo demais, distribuições diferentes se fundem de forma **irreversível**. Casos limites do artigo: τ = −1 junta tudo num cluster só (com μ > 0 equivale ao FedProx; com μ = 0, ao FedAvg) e τ = 1 nunca funde (cada cliente é um cluster; com μ > 0 equivale ao Ditto). |
| `--mu` (μ/λ) | Peso do termo proximal `(μ/2)‖w_cluster − gmodel‖²`. | Modelos de cluster mais próximos do global: mais compartilhamento entre clusters, menos personalização. μ→∞ faz cluster = global. | Clusters mais independentes; μ=0 é o CFL convencional (FedAvg puro dentro de cada cluster). Bom quando os grupos são muito diferentes e têm dados suficientes. No artigo, o melhor μ depende do cenário (Tabela 4 em 4.15.6): 0.05 em Rotated/Shifted, e 10 no patológico, onde μ pequeno derruba a acurácia para 24–38%. |
| `--num_per_round` | Clientes por rodada. | Mais clusters comparados por rodada: a clusterização converge mais rápido e as direções médias ficam menos ruidosas; custo maior. | Convergência lenta; um cluster só se funde quando membros dele e do outro são sorteados juntos. |
| `--com_round` | Nº de rodadas. | Mais chances de observar todos os clientes e concluir as fusões; mais treino. | Pode terminar com clientes nunca observados (continuam como clusters unitários). |
| `--obbs` | Lote usado só para acumular o gradiente de `Ψ` (`None` = dataset inteiro). Não muda o resultado; serve para caber na memória. | — | — |
| `--lr` | lr do SGD de treino. | Treino mais rápido ou instável. | O inverso. |
| `--epochs` | Épocas locais no treino do cluster e do global. | Mais progresso por rodada, mais *client drift*. | O inverso. |
| `--batch_size` | Batch do treino local. Em `StoCFL-FCC+CFL.py` **omitir o argumento** (`None`) dá batch cheio, que é o que o artigo usa no Rotated MNIST. | Menos passos por época. | Mais passos e mais ruído. |
| `--train` | `0` = só clusterização; `1` = também treina. | — | — |
| `--drop` (só FCC+CFL) | `d`: probabilidade de um cliente disponível cair em cada rodada, em `[0, 1)` (dropout com retorno, 4.1). `0` (padrão) desliga tudo, inclusive o gerador de disponibilidade. | Mais clientes indisponíveis por rodada e **atraso maior** na observação deles. Só com `num_per_round` grande o nº de participantes cai de fato (simulação do [plano](plano-dropout-stocfl.md): `m = 100%`, `d = 0,1`, `L_max = 10` dá 157,5 participantes em vez de 240). Quem tem ausências longas participa menos. O efeito sobre o ARI e o nº de clusters **não foi medido**. | Menos quedas; `0` volta ao comportamento sem dropout. |
| `--drop_rounds` (só FCC+CFL) | `L_max`: cada ausência dura `L ~ U{1, …, L_max}` rodadas (um sorteio por queda). Padrão `1`. Não confundir com `--tau`, que é o limiar de cosseno. | Ausências mais longas e disponibilidade média menor: `1 / (1 + d·(L_max + 1)/2)`. | `1`: toda ausência dura uma rodada. Só tem efeito com `--drop > 0`. |

**Como escolher τ na prática:** rode com `--train 0` e veja `cos_rec*.log`, que lista os pares de clusters ordenados por similaridade. Escolha τ no "vão" entre as similaridades intragrupo (altas) e intergrupo (baixas). Valores do artigo: `0.5` (Rotated/Shifted/Hybrid), o padrão dos scripts, e `0.55` e `0.60` (FEMNIST/FedCelebA). A ablação do artigo (cenário com 8 clusters reais, rotação × rótulos) mostra o efeito: `τ > 0.76` separa por feature **e** label, e `τ < 0.67` separa só por label e ignora a rotação. Um τ maior dá clusters mais finos (4.15.6). Com rótulos non-IID por Dirichlet (`--dirichlet_alpha`) **não há vão**: o nº de clusters cresce de forma contínua com `τ`, e o `τ` da simulação do dropout com treino (0.84683) foi escolhido por Monte Carlo contra um gabarito construído (4.11, D-046).

#### Variáveis de cenário e infraestrutura

| Variável | Script | Efeito |
|---|---|---|
| `--n` | FCC+CFL | Nº de clientes. Precisa ser divisível por `k` (4 no mnist por padrão, 2 no cifar). Mais clientes = menos dados por cliente = ψ mais ruidoso. Faz parte do nome do diretório de dados. |
| `--dataset` | FCC+CFL | `mnist` define `SimpleLinear` e `k = 4` por padrão (rotações {0,90,180,270}); `cifar` define `CNN_CIFAR10` e `k = 2` (rotações {0,180}). |
| `--k` | FCC+CFL | Nº de grupos de rotação (D-029). Default 4 (mnist) ou 2 (cifar), que mantêm os nomes antigos de dados e logs. No mnist, outro `k` gera `k` ângulos igualmente espaçados (`k = 8`: 0°, 45°, ...) e acrescenta `_k{k}` à pasta de dados e `-k{k}` à pasta de logs. No cifar só vale 2. Exige `n % k == 0`. |
| `--dirichlet_alpha` | FCC+CFL | `α` do Dirichlet: **rótulos non-IID, sem rotação** (`RotatedMNIST.pre_process_dirichlet`, 4.7). Padrão `None`, que mantém a partição por rotação, sem nenhuma mudança (regressão V7 em 4.11). Exige `--dataset mnist`, `--k 1` e `α > 0`. `α` menor = clientes com menos classes (maior classe com ~43% das amostras do cliente com `α = 0.5` e ~32% com `α = 1.0`, contra 10% no IID). Acrescenta `_a{α}` à pasta de dados e `-a{α}` à de logs. Não há gabarito de grupos: o nº de clusters é resultado, e o `τ` vira um botão de granularidade ([plano](plano-dropout-treino-stocfl.md), seção 4). |
| `--seed` | FCC+CFL, FEMNIST | Seeds e **partição dos dados** (está no `save_dir`; no Dirichlet, a seed também semeia o particionador). Sem default: precisa ser passado. Em FCC.py é fixo `0`. |
| `--process` | FCC, FCC+CFL | `1` gera as partições (rodar uma vez por combinação dataset/n/seed). Default é `1` em FCC.py e `0` em FCC+CFL. |
| `--setting` | FCC | `fskewed` / `lskewed` / `shifted` / `rotated`: escolhe o Trainer. |
| `--k` | FCC | Para `lskewed`, 4 ou 10 grupos (outros valores geram 0 clientes). Em `fskewed` é forçado para 2 (só afeta nomes). Usado no nome do diretório de log. |
| `--client_num` | FEMNIST | Nº de clientes FEMNIST (3597). |
| `--dataset` (FCC.py) | FCC | Declarado como `float` (resto de código); só usado pelo `rotated`, que já está quebrado. |

#### Defaults por script

| Arg | FCC.py (default / README) | FCC+CFL.py (default / README) | FEMNIST.py (default) |
|---|---|---|---|
| `com_round` | 100 / 100 | — / 200 | — |
| `num_per_round` | 20 / 20 | — / 20 | — |
| `batch_size` | 128 / 50 | — / 50 | — |
| `lr` | 0.01 / 0.1 | 0.1 / 0.1 | — |
| `epochs` | 5 / 20 | 5 / 5 | — |
| `mu` | 0.1 / 0.1 | 0.05 / 0.05 | — |
| `tau` | 0.5 / 0.5 | 0.5 / 0.5 | — |
| `obbs` | n/a | None | None |
| `train` | 0 | 1 | 0 |
| `drop` | n/a | 0.0 | n/a |
| `drop_rounds` | n/a | 1 | n/a |
| `dirichlet_alpha` | n/a | None | n/a |
| `seed` | fixo 0 | — / 0 | — |

"—" indica argumento sem default (obrigatório na prática).

### 4.10 Saídas e logs

Todos os scripts criam `./logs/runs-.../` com `os.makedirs`.

| Arquivo | Script | Conteúdo |
|---|---|---|
| `rotated_{dataset}.log` / `{setting}-k{k}-time-*.log` / `femnist-seed*.log` | todos | Log principal: args, clientes por rodada, acurácia por cluster e global. No FCC+CFL, `client id this round` lista só os **participantes** (com `--drop > 0`: os disponíveis sorteados, que podem ser menos que `num_per_round` ou nenhum, e então a lista é `[]`). Com `--drop > 0`, cada rodada ganha antes dela a linha `Round {r}/{T}, unavailable [...]`. |
| `cluster_rec*.log` | todos | **Partição atual** (reescrito toda rodada). |
| `cos_rec*.log` | todos | Pares de clusters da **última** rodada com fusão possível, ordenados por cosseno. |
| `psi.pkl` | FCC+CFL | `dict cliente → ψ` (salvo toda rodada). ⚠️ Pode ficar grande: `SimpleLinear` tem ~1,6 M parâmetros, então 200 clientes ≈ 1,3 GB. |
| `cluster.pkl` | FCC+CFL | Lista com a partição de cada rodada (uma entrada por rodada, inclusive na rodada sem participantes). |
| `accuracy.pkl` | FCC+CFL | Lista por rodada de `{"cluster": [acc de cada cluster amostrado], "global": [acc do gmodel no teste do grupo de cada cluster], "cluster_recall": [...], "global_recall": [...]}`. As duas últimas chaves (desde 2026-11-10, D-045) têm, na mesma ordem de `cluster`, uma lista com o recall de cada classe no mesmo teste (`evaluate_recall`, 4.8); as duas primeiras não mudaram. A ordem é a dos clusters sorteados em ordem crescente de id, a mesma das linhas `Round r, Cluster c` do log, que trazem o id. Na rodada sem participantes (só com `--drop > 0`), a entrada tem as quatro listas vazias. |
| `availability.pkl` | FCC+CFL, só com `--drop > 0` | Lista, por rodada, dos ids (`int`, em ordem crescente) dos clientes **indisponíveis**, no mesmo estilo do `cluster.pkl`. É a série de disponibilidade da execução. |
| `exp_{setting}_logs.pkl` | FCC | `{"cluster": partição por rodada}`, salvo no final. |

Avaliação em FCC+CFL: cada cluster amostrado é testado no conjunto de teste do grupo do seu **primeiro membro** (`⌊cid·k/n⌋`). O `gmodel` é testado no mesmo conjunto, o que permite comparar a especialização do cluster com o modelo global.

**Nome da pasta de logs do FCC+CFL:** `runs-rotated-{dataset}-n{n}-p{m}-seed{seed}-lambda{mu}[-k{k}][-a{α}][-drop{d}-r{L_max}]-time-{hora}`. O `-k{k}` só aparece com `k` diferente do padrão (D-029), o `-a{α}` só com `--dirichlet_alpha` (por exemplo `-k1-a0.5`; a pasta de dados correspondente é `rotated_mnist_240_<seed>_k1_a0.5`) e o `-drop{d}-r{L_max}` só com `--drop > 0`. ⚠️ A hora tem só minutos (`%m-%d-%H:%M`) e o nome não traz o `τ`: duas execuções com os mesmos `n`, `m`, seed, `μ`, `k`, `α` e `drop` iniciadas no **mesmo minuto** (por exemplo, com `τ` diferentes) gravam na mesma pasta (`os.makedirs(exist_ok=True)`) e misturam os arquivos. Os notebooks que rodam execuções curtas precisam esperar o minuto mudar. Por isso o padrão de busca do notebook de teste de `m` (`...-lambda{MU}{k}-time-*`) não casa com as execuções com `drop`, e os logs sem `drop` não se misturam com os novos.

### 4.11 Como rodar

```bash
cd StoCFL
pip install -r requirements.txt

# 1ª execução: --process 1 gera ./datasets/rotated_{dataset}_{n}_{seed}/
python StoCFL-FCC+CFL.py --n 200 --com_round 200 --num_per_round 20 --batch_size 50 \
    --lr 0.1 --epochs 5 --mu 0.05 --tau 0.5 --seed 0 \
    --dataset cifar --process 1
# execuções seguintes com o mesmo dataset/n/seed: --process 0
```

Observações de ambiente:
- `spacy` é obrigatório mesmo sem NLP: `trainer.py` importa `leaf.dataloader → leaf.pickle_dataset → leaf.nlp_utils.util → spacy`.
- `torch ≥ 2.6` usa `torch.load(weights_only=True)` por padrão. Os `get_dataset` passam `weights_only=False` para carregar os `BaseDataset`, o que exige `torch ≥ 1.13`.
- Testado com Python 3.12, torch 2.15, scikit-learn 1.9 e `fedlab==1.2.1`. O `.venv` da raiz tem tudo isso (`pip install -r requirements.txt` na raiz; torch 2.15.0 com CUDA, e os scripts usam a GPU se houver). Rode os scripts com `../../.venv/bin/python` a partir de `projetos/StoCFL/`.
- Os scripts usam GPU se `torch.cuda.is_available()`, e CPU caso contrário.
- Em `StoCFL-FCC+CFL.py`, `--batch_size` e `--obbs` omitidos valem `None`, e os loaders usam o dataset inteiro como um único batch. Os outros argumentos sem default (`--n`, `--com_round`, `--num_per_round`, `--seed`) são obrigatórios na prática.

**Dropout com retorno (`--drop`, só no `StoCFL-FCC+CFL.py`).** Exemplo (não executado nesse tamanho; os testes abaixo usam `n` pequeno), a partir de `projetos/StoCFL/`, com 10% de chance de cair por rodada e ausências de 1 a 10 rodadas:

```bash
../../.venv/bin/python StoCFL-FCC+CFL.py --n 240 --k 4 --dataset mnist --com_round 50 \
    --num_per_round 120 --train 0 --tau 0.9 --seed 0 --process 1 \
    --drop 0.1 --drop_rounds 10
```

Os testes do módulo `availability.py` (sem GPU): `../../.venv/bin/python -m unittest tests/test_availability.py -v`. Verificação do script integrado, em 2026-11-09, com `--n 40 --k 4 --dataset mnist --com_round 6 --num_per_round 8 --train 0 --seed 0 --process 1` (a execução sem `--drop` é a referência):

| Verifica | Resultado |
|---|---|
| Regressão: sem `--drop`, igual ao código anterior | `cluster.pkl`, `psi.pkl` (31 tensores) e as linhas `client id this round` idênticos aos da execução feita antes da mudança; sem linha `unavailable` e sem `availability.pkl`. |
| Sorteio respeita a disponibilidade (`--drop 0.3 --drop_rounds 3`, também com `m = n = 40` e 12 rodadas) | Nenhum participante indisponível na mesma rodada, e nº de participantes igual a `min(m, disponíveis)` em todas as rodadas (21 a 29 com `m = 40`). Ausência consecutiva máxima: 3. |
| Invariante 5 e cobertura | Em cada rodada, todo membro de cluster com mais de um cliente já havia sido sorteado, e as chaves de `psi.pkl` eram a união dos participantes. |
| Rodada vazia (`--drop 0.99 --drop_rounds 10`, `--train 1` e `--train 0`) | Com `n = 40` e seed 0 nenhuma rodada ficou vazia, então esse caso não provou nada. Com `n = 8`, `m = 4`, 15 rodadas, as rodadas 0, 3, 4 e 6 ficaram sem participantes: o script terminou, e `cluster.pkl` e `accuracy.pkl` tiveram 15 entradas, com `{"cluster": [], "global": []}` nas rodadas vazias. |

Cuidado com `--drop` alto: com `n` pequeno e `drop` perto de 1, rodadas inteiras ficam vazias.

**Rótulos non-IID por Dirichlet (`--dirichlet_alpha`, só no `StoCFL-FCC+CFL.py`).** Passo 2 do [plano do dropout com treino](plano-dropout-treino-stocfl.md) (D-045). Exemplo, a partir de `projetos/StoCFL/`:

```bash
../../.venv/bin/python StoCFL-FCC+CFL.py --n 240 --k 1 --dirichlet_alpha 0.5 --dataset mnist --com_round 50 \
    --num_per_round 120 --train 1 --tau 0.8 --seed 0 --process 1
```

Os dados vão para `datasets/rotated_mnist_240_0_k1_a0.5/` (240 clientes em `train/`, o MNIST de teste inteiro em `test/data0.pkl`) e os logs para `logs/runs-rotated-mnist-n240-p120-seed0-lambda0.05-k1-a0.5-time-...`. Com `k = 1`, todo cluster é avaliado no mesmo teste, de 10 classes balanceadas, e o `accuracy.pkl` traz também o recall por classe (4.10). Testes, sem GPU (precisam do MNIST em `datasets/mnist/`): `../../.venv/bin/python -m unittest tests/test_dirichlet.py -v` (determinismo por seed, seeds e `α` diferentes dão partições diferentes, cada amostra num só cliente, mínimo de 50, `α` menor dá mais skew, o gerador global do `numpy` fica intacto, e o `evaluate_recall` dá a mesma loss e acurácia que o `evaluate` do FedLab).

Verificação, em 2026-11-10:

| Verifica | Resultado |
|---|---|
| V7: sem a flag, igual ao código anterior | `--n 40 --k 4 --com_round 4 --num_per_round 20 --train 1 --tau 0.5 --seed 0`, sem e com `--drop 0.3 --drop_rounds 3`, antes e depois da mudança: `cluster.pkl`, `psi.pkl`, `availability.pkl`, as chaves `cluster` e `global` do `accuracy.pkl` (acurácias iguais bit a bit) e as linhas do log (fora a hora e a linha de argumentos, que ganhou `dirichlet_alpha=None`) idênticos. |
| Execução com a flag | `--n 40 --k 1 --dirichlet_alpha 0.5`, 3 rodadas, `--train 1`: roda, grava as pastas com `_k1_a0.5`/`-k1-a0.5`, e em todos os clusters a acurácia é igual a `Σ_c recall_c · fração_c` no teste (até 1e-9). |
| V8: as 20 partições de `n = 240` (seeds 0 a 9, `α` = 0.5 e 1.0) | Todas geradas, ~3 s cada, 60.000 amostras sem repetição. `α = 0.5`: mínimo de 51 a 74 amostras por cliente, máximo de 448 a 709, mediana de 253 a 258, maior classe com 41–44% das amostras do cliente (média). `α = 1.0`: mínimo de 71 a 121, máximo de 379 a 608, mediana de 254 a 259, maior classe com 32–33%. Duas delas (`α = 0.5` seed 0 e `α = 1.0` seed 7), geradas de novo noutra pasta, deram arquivos idênticos (pixels e rótulos). Ocupam 228 MB cada (4,5 GB as 20). |

**Escolha de `τ` para o Dirichlet por Monte Carlo (`varredura-tau-dirichlet.ipynb`).** Passo 3 do [plano do dropout com treino](plano-dropout-treino-stocfl.md) (D-046). O notebook [varredura-tau-dirichlet.ipynb](StoCFL/varredura-tau-dirichlet.ipynb) sorteia 400 valores de `τ ~ U[0.3, 1.0]` e, para cada um, roda a clusterização (`--train 0`) nas 120 combinações da grade (`α` = 0.5 e 1.0, seeds 0 a 9, `m` = 100% e 50%, `d` = 0, 0.05 e 0.1, `--drop_rounds 10`, 50 rodadas, `n = 240`). O `τ` da grade é o de **maior ARI médio contra um gabarito**: o agrupamento hierárquico (Ward, euclidiano) das proporções de classes dos clientes, com `k` de 2 a 40 escolhido pela maior silhueta. As 48.000 simulações não usam o script, e sim um **simulador da fusão**: com `--train 0`, a partição só depende dos `Ψ` e do sorteio, e o cosseno entre centros de clusters sai da matriz de Gram `G = ΨΨᵀ` (`S_AB/√(S_AA·S_BB)`, com `S` a soma dos blocos). Os `Ψ` vêm do script real (uma execução de 1 rodada com `m = 100%` por `α` e seed), e o sorteio repete o do script (`random.seed(seed)` e `Availability`). Execução de 2026-11-10: 20 execuções de `Ψ` (~45–60 s cada), Monte Carlo em 43 s (20 processos na CPU), 9 execuções de validação (95–332 s), ~42 min no total.

| Verifica | Resultado |
|---|---|
| Cossenos da rodada 0 (saída padrão, 6 casas) contra `G` | Diferença máxima de 2,4e-5 a 2,9e-5. **Não é só arredondamento:** o `Ψ` sai normalizado em float32 na GPU (norma 1 + ~1e-5) e o script calcula o cosseno em float32 na CPU (`cosine_sim`), com erro dessa ordem; o simulador usa o valor exato em float64. Uma fusão só divergiria se um cosseno ficasse a menos de ~3e-5 de `τ`. |
| Simulador × script, 9 execuções reais de 50 rodadas (`α` = 0.5 e 1.0; `m` = 50% com `d = 0.1` e `m` = 100% com `d = 0.05`; `τ` = 0.75, 0.85 e o escolhido) | Sorteados, indisponíveis, partição e pares de clusters comparados **iguais em todas as rodadas das 9**; cossenos a até 2,9e-5. |
| Modo `DADOS_JSON` (política 7) | As mesmas 2 figuras e 7 tabelas que o modo com logs, comparadas campo a campo, sem alterar o JSON; depois de apagados os logs, o modo com logs para com `RuntimeError` e o modo JSON replota em 3 s. Essa checagem achou um erro: o `df.to_json` do pandas grava só 10 algarismos, e a conferência que refaz linhas do Monte Carlo pelo simulador falhava; o notebook passou a gravar em precisão completa. |

Etapa A do plano (partição depois da rodada 0 com `m = 100%`, o grafo "cosseno > `τ`" entre clientes; média nas 10 seeds), que confirma a medição da seção 4.3 do plano com o script real:

| `τ` | `α = 0.5`: clusters / maior / singletons | `α = 1.0`: clusters / maior / singletons |
|---|---|---|
| 0.70 | 2,7 / 238 / 1,7 | 2,5 / 238 / 1,3 |
| 0.75 | 10,0 / 230 / 8,3 | 13,6 / 225 / 10,8 |
| 0.80 | 30,6 / 192 / 25,4 | 53,5 / 132 / 40,3 |
| 0.85 | 79,8 / 39 / 62,0 | 127,0 / 34 / 99,6 |
| 0.90 | 142,3 / 17 / 117,2 | 197,1 / 12 / 177,1 |

Resultado do Monte Carlo (médias nas 120 combinações para o `τ` sorteado mais próximo de cada valor):

| `τ` | ARI | clusters | maior | singletons | TVD cliente–cluster |
|---|---|---|---|---|---|
| 0.70 | 0,024 | 18,2 | 173,9 | 9,6 | 0,397 |
| 0.75 | 0,081 | 32,0 | 141,4 | 19,6 | 0,357 |
| 0.80 | 0,194 | 61,2 | 88,9 | 42,2 | 0,275 |
| **0.84683** (escolhido) | **0,305** | 109,5 | 28,6 | 82,3 | 0,154 |
| 0.90 | 0,180 | 172,8 | 12,6 | 149,1 | 0,064 |
| 0.95 | 0,034 | 221,2 | 5,1 | 210,6 | 0,014 |

- **`τ = 0.84683`** (o sorteado era 0,8468334; o arredondamento para 3 casas mudava o ARI médio e foi descartado). 12 dos 400 `τ` ficam a até 0,01 do ARI máximo, de 0,837 a 0,859. Cada `α` sozinho escolheria 0,851 (`α = 0.5`, ARI 0,381) e 0,841 (`α = 1.0`, ARI 0,238).
- Em `τ = 0.84683`: `α = 0.5` dá 75 a 98 clusters em média por cenário, com 58 a 71 singletons e ARI 0,37–0,39; `α = 1.0` dá 120 a 138 clusters, com 93 a 103 singletons e ARI 0,23–0,24. Com `m = 100%` há menos clusters que com `m = 50%` (75 contra 98 com `α = 0.5`), porque todo cluster é comparado com todos em toda rodada. O dropout muda pouco: com `m = 100%` aumenta o nº de clusters (74,7 → 80,9 → 84,3 com `α = 0.5`) e diminui o maior cluster (46,9 → 41,4 → 35,3); com `m = 50%` quase não muda. A cobertura é 1,0 em todas.
- **O gabarito é fraco.** A silhueta é baixa (0,20–0,26 com `α = 0.5` e 0,15–0,17 com `α = 1.0`): as proporções de classes do Dirichlet não formam grupos nítidos. O `k` escolhido é 10 em 7 das 10 seeds de `α = 0.5` (34 e 39 nas outras) e varia de 2 a 40 com `α = 1.0`, **batendo no limite de 40 em 5 seeds**. O ARI máximo é baixo (0,30), e o `τ` escolhido depende desse gabarito.
- **Regime do `τ` escolhido:** muitos clusters pequenos (~110 de 240 clientes, ~82 singletons, maior cluster ~29), perto do extremo "cada cliente é um cluster" (Ditto, 4.9). O plano (seção 11) avisa que a acurácia por cluster tem viés de composição nesse caso.
- Os logs (29 pastas e 29 saídas, 42 GB) foram apagados depois da verificação (D-046). Os dados estão em `logs/resultados-varredura-tau-dirichlet.json` (25 MB; cópia em `docs/resultados/resultados-varredura-tau-dirichlet.json.gz`): `G` de cada `(α, seed)`, histogramas, gabarito, sorteios, as 48.000 linhas do Monte Carlo e a validação. Com `G` e os sorteios, o simulador refaz qualquer simulação sem rodar o script.

**Notebook do dropout com treino (`teste-dropout-treino.ipynb`).** Passo 4 do [plano](plano-dropout-treino-stocfl.md) (D-047). O [teste-dropout-treino.ipynb](StoCFL/teste-dropout-treino.ipynb) roda `StoCFL-FCC+CFL.py --train 1 --k 1 --dirichlet_alpha α` por `subprocess` na grade do plano: `α` = 0.5 e 1.0, `m` = 100% e 50%, sem dropout e `d` = 0.05 e 0.1 (`--drop_rounds 10`), seeds 0 a 9, 50 rodadas, `n = 240`, `τ = 0.84683`, `lr = 0.1`, 5 épocas, `μ = 0.05`, batch cheio (120 execuções). Por execução, lê a partição, os sorteados, os indisponíveis, a acurácia e o recall de cada cluster avaliado (`accuracy.pkl`, com os ids das linhas `Round r, Cluster c` do log) e os cossenos da última rodada, e confere V3 (acurácia do log = `accuracy.pkl`, mesmos clusters), V4 (50 entradas) e a saída padrão; antes de apagar o `psi.pkl` (`APAGAR_PSI = True`), confere que as chaves dele são os clientes sorteados (I5). Métricas: acurácia do modelo do cluster e do global, ponderadas pelos participantes de cada cluster avaliado, no teste balanceado e **ponderadas pela distribuição de rótulos do cluster** (`Σ_c p_c · recall_c`), o valor final (média das últimas `JANELA_FINAL = 10` rodadas), o ganho, a rodada em que a acurácia do cluster passa de `LIMIAR_ACC = 0.90`, o nº de clusters, o maior, os singletons, a TVD e a rodada estável; dropout − sem dropout por seed com Wilcoxon. Gráficos em Plotly: curvas por rodada (por `α`, uma coluna por `m`), caixas por seed e heatmaps cluster × classe dos 20 maiores clusters da partição final. A última célula grava `logs/resultados-dropout-treino.json` com os dados brutos (política 7), e com `DADOS_JSON = True` o notebook só lê o JSON. **A grade não foi executada.**

**Notebook do dropout.** O [teste-dropout.ipynb](StoCFL/teste-dropout.ipynb) (passo 4 do [plano](plano-dropout-stocfl.md); D-035) roda `StoCFL-FCC+CFL.py --train 0` por `subprocess` em Rotated MNIST com `n = 240`, 50 rodadas, `τ = 0.75` e 10 seeds (0 a 9), **sem dropout** e com `--drop` = 0.05 e 0.1 (`--drop_rounds 10`), para `m` = 100% e 50% e `k` = 8 e 16: 120 execuções, ~190 GB de `psi.pkl` e ~54 GB de dados (`APAGAR_PSI = True` apaga o `psi.pkl` de cada execução concluída). Lê o `cluster.pkl`, o `availability.pkl` e o log, e mostra em Plotly: nº de clusters, ARI, cobertura e participantes por rodada (média e faixa mín–máx entre as seeds), o resultado final por seed, **matrizes de confusão** (grupo real × grupo previsto somada nas seeds, e cluster × grupo real por seed) e a diferença dropout − sem dropout por seed com o teste de Wilcoxon. Reaproveita execuções concluídas só se o `τ`, o `k`, o `m`, a seed e o `drop` registrados na linha de argumentos do log baterem (o nome da pasta não traz o `τ`). A última célula grava `logs/resultados-dropout.json` (~13 MB; o git ignora `logs/`, e a cópia versionada é a compactada em `docs/resultados/resultados-dropout.json.gz`, D-041) com os parâmetros, uma entrada por execução (métricas finais, a partição final e os dados brutos `rotulos_por_rodada`, `sorteados_por_rodada`, `indisponiveis_por_rodada` e `cossenos_entre_clusters`), as métricas de cada rodada, as duas tabelas de resumo e as matrizes de confusão somadas nas seeds. Com `DADOS_JSON = True` (célula 1), o notebook lê esse arquivo no lugar dos logs e só plota; sem as execuções e com o JSON desta grade já gravado, ele para com um aviso em vez de rodar tudo de novo (`REEXECUTAR = True` força a nova execução) (D-039).

Verificação do notebook, em 2026-11-09, com uma cópia reduzida (`n = 48`, 6 rodadas, seeds 0 e 1, os demais parâmetros iguais; 24 execuções):

| Verifica | Resultado |
|---|---|
| As 15 células rodam | Sem erro, com 12 figuras Plotly (2 por `k` por rodada, 2 de caixas e 8 de matrizes de confusão). Uma segunda execução, com as 24 execuções já prontas, reaproveitou todas. |
| I5 do plano: o notebook lê as execuções novas | A cobertura calculada a partir do log foi igual às chaves de `psi.pkl` nas 24 execuções. |
| Participantes com dropout | Com `m = 100%`, 41,3 (`d = 0.05`) e 37,8 (`d = 0.1`) de 48 em média, coerente com a disponibilidade medida (0,86 e 0,79 nas 6 rodadas); com `m = 50%`, 24, igual ao sem dropout. |
| Reaproveitamento de logs antigos | Com `τ = 0.75`, só duas execuções antigas de `n = 240` valem (seed 0, `m = 100%`, `k` = 8 e 16, sem dropout, da busca de `τ` do notebook de `m`); com `τ = 0.9` valem as do notebook de `m`. Logs anteriores à flag `--drop` valem como `drop = 0`. |
| Célula do JSON | Testada fora do notebook sobre 3 execuções reais de `n = 240` (seed 0, `k = 8`, `m = 100%`, os 3 cenários): JSON estrito (sem `NaN`), nº de clusters de cada partição igual ao da execução e 50 linhas por rodada e por execução. |

**Execução da grade completa, em 2026-11-09** (D-037). São 120 execuções: 118 novas, em 205 min na GPU, e 2 reaproveitadas da busca de `τ` de 2026-11-06 (seed 0, `m` = 100%, sem dropout, `k` = 8 e 16). O notebook rodou sem erro e gravou `logs/resultados-dropout.json` (o git ignora `logs/`; a cópia versionada é `docs/resultados/resultados-dropout.json.gz`, D-041; conferido: JSON estrito, 120 execuções, 6000 linhas por rodada, última rodada igual às métricas finais). Em 2026-11-10, a pedido do usuário, as 118 pastas de logs novas (~180 GB, a maior parte `psi.pkl`) e os 118 arquivos `pipeline-dropout-*.txt` foram **apagados**, depois de o JSON passar a guardar os dados brutos (D-039); as 2 execuções de 06/11 e as pastas dos outros notebooks foram apagadas depois (D-040). O `pipeline-dropout-*.txt` apagado guardava também a lista de cossenos de **cada rodada**, que não foi salva: no JSON só há a da última rodada (`cossenos_entre_clusters`). O campo `pasta` do JSON é só histórico. Para ver os gráficos, há uma cópia do notebook com as saídas em `StoCFL/logs/teste-dropout-executado.ipynb` (D-038), gerada no modo `DADOS_JSON`.

| Resultado | Valor |
|---|---|
| Partição final | ARI = 1,0 e nº de clusters = `k` nas 120 execuções, com e sem dropout, inclusive `k = 16` com `τ = 0.75` (`seeds_colapso` = 0 em todos os cenários). Nenhum par misturado ou separado e nenhum cliente fora da diagonal nas 12 matrizes de confusão somadas. Cobertura final de 1,0 em todas. |
| Rodada estável (média; mín–máx entre as seeds) | `m` = 100%: 1 sem dropout, 10,7 (10–11) com `d = 0.05` e 10,9 (10–11) com `d = 0.1`. `m` = 50%: 10,4 (6–19), 14,1 (12–20) e 14,6 (13–20). Os valores são os mesmos para `k` = 8 e 16. |
| Dropout − sem dropout (Wilcoxon por seed, sem correção para comparações múltiplas) | ARI final: Δ = 0, `p` = 1 nos 8 casos. Rodada estável: `m` = 100%, +9,7 e +9,9 rodadas (`p` = 0,002 nas duas); `m` = 50%, +3,7 (`p` = 0,098) e +4,2 (`p` = 0,027). |
| Participantes por rodada (média) | `m` = 100%: 240 sem dropout, 189,4 (`d = 0.05`) e 156,8 (`d = 0.1`). `m` = 50%: 120 nos três, porque sempre havia ao menos 120 clientes disponíveis. |
| Disponibilidade média medida | 0,789 (`d = 0.05`) e 0,653 (`d = 0.1`), dentro de 0,01 da fórmula `1/(1 + d·(L_max+1)/2)` (0,784 e 0,645). |
| Folga até a fusão de clusters já formados (`τ` menos o maior cosseno entre os clusters da partição final, do `cos_rec.log`) | `k = 8`: 0,380 em média (0,364–0,407). `k = 16`: 0,027 (0,019–0,036), isto é, o maior cosseno entre clusters distintos fica em 0,714–0,731 contra `τ = 0.75`. É a mesma em todos os cenários de `m` e de dropout (depende só de `k` e da seed), coerente com a partição final ser a mesma. **Não é a margem até o colapso**: a borda inferior real de `τ` vem dos cossenos entre clientes na rodada 0 e é maior (para `k = 16` e seed 0, 0,7397; margem real em `τ = 0.75` de só 0,010; ver o [relatório](relatorio-m-k-tau.md)). Só a seed 0 tem essa matriz guardada (D-040). |

**Replot sem os logs (verificado antes de apagar).** O notebook em modo `DADOS_JSON`, sem ler logs, gerou as mesmas 12 figuras (dados e layout, comparados campo a campo) e as mesmas 2 tabelas que o modo com logs, e não alterou o JSON. Com os logs já apagados, ele recusa rodar a grade (erro `RuntimeError` com a instrução) e o modo `DADOS_JSON` plota em ~6 s. Na checagem, a chave nova `participantes` (os sorteados) colidia com a métrica `participantes` (a média por rodada) e foi renomeada para `sorteados_por_rodada`.

Nas 120 execuções, a rodada estável é exatamente a primeira rodada com cobertura de 100%, e o ARI chega a 1,0 nessa mesma rodada, nunca antes. Por isso `k` = 8 e `k` = 16 têm a mesma rodada estável em todas as execuções: com `--train 0` a partição só depende de quais clientes já foram observados (`Ψ` é fixo, seção 4.5), e o efeito do dropout é só **atrasar** a rodada em que o último cliente aparece.

**Limites:** como o ARI final é 1,0 em todas as execuções, a grade só distingue os cenários pela rodada estável e pelos participantes. Ela **não mostra se o dropout piora a partição final**, porque em 50 rodadas todo cliente foi observado em todos os cenários. Para isso, seria preciso um cenário em que a cobertura não chegue a 100% (menos rodadas, `m` menor, `d` ou `L` maiores). O `τ = 0.75` ficou na borda inferior da janela de `k = 16` ([relatório de m, k e τ](relatorio-m-k-tau.md)) e não colapsou em nenhuma das 10 seeds, mas com margem real de só 0,010 para a seed 0 (borda inferior em 0,7397; as outras seeds não têm a matriz de cossenos guardada), e isso vale só para `n = 240`, `m` = 100% e 50%. Os gráficos foram conferidos só pela estrutura (nº de figuras e de traços), **não visualmente**: não há `kaleido` nem outra forma de renderizar imagem no ambiente.

**Teste da fração de clientes por rodada (`m`).** O notebook [teste-fracao-clientes.ipynb](StoCFL/teste-fracao-clientes.ipynb) roda `StoCFL-FCC+CFL.py --train 0` por `subprocess` em Rotated MNIST (`n = 200`, `k = 4`, `τ = 0.5`, 50 rodadas, seed 0) com `m` = 100%, 50%, 25% e 10%, e mede nº de clusters, ARI, pureza e cobertura por rodada a partir do `cluster.pkl` e do log. Execução de 2026-11-05 com `τ = 0.5` (1 seed, 1 execução por `m`, GPU), em ~5 min no total. Depois dela, o notebook passou a vir com `τ = 0.9` e `m` = 5% a mais na lista (D-024), e depois com `n = 240` e a lista `KS = [4, 8, 16]` de grupos reais (D-029; o `k = 4` de `n = 240` não reaproveita a partição de `n = 200`); os resultados dessa configuração (execução de 2026-11-06, 15 execuções do teste de `m` e a busca de `τ` por `k`) estão analisados no [relatório de m, k e τ](relatorio-m-k-tau.md). As pastas de logs dessas execuções (153, ~222 GB) foram **apagadas em 2026-11-10** e o que importa está em `logs/resultados-fracao-clientes.json` (~23 MB; cópia versionada compactada em `docs/resultados/resultados-fracao-clientes.json.gz`; D-040, D-041): por execução, os parâmetros, as métricas finais e por rodada, o cluster de cada cliente e os clientes sorteados em cada rodada, os cossenos entre clusters da última rodada e o maior cosseno de cada rodada, mais a matriz de cossenos entre clientes da rodada 0 para cada `n` e `k` (`cossenos_clientes_rodada_0`). O notebook ainda **não lê** esse JSON: executar as células de execução do notebook roda tudo de novo. A tabela abaixo continua valendo só para `n = 200`, `k = 4` e `τ = 0.5`:

| `m` | Clientes/rodada | Clusters finais | 1ª rodada com 4 clusters | ARI final |
|---|---|---|---|---|
| 100% | 200 | 4 | 1 | 1.000 |
| 50% | 100 | 4 | 11 | 1.000 |
| 25% | 50 | 4 | 20 | 1.000 |
| 10% | 20 | 6 | não atingiu | 0.987 |

Nenhum cluster misturou grupos reais (pureza 1.0 em todos). Com `m = 10%`, 1% dos clientes ainda não tinha sido sorteado na rodada 50 (cobertura 0.99), então a clusterização não terminou. Isso mostra que a rapidez da convergência segue a cobertura (4.1, 4.5), mas com uma só seed, a diferença exata entre os `m` pode ser ruído de amostragem. Custos observados: a rodada 0 com `m = 100%` calcula 19.900 cossenos entre vetores de ~1,6 M de parâmetros, e o script grava `psi.pkl` (~1,3 GB) a cada rodada.

**Busca de τ (seção 5 do mesmo notebook).** A execução abaixo é de antes da lista `KS` (D-029): Rotated MNIST, `n = 200`, `k = 4`, 50 rodadas, seed 0, `m` = 100%, 25% e 10%, `τ` em 0.05, 0.25, 0.5, 0.75 e 1.0 mais 6 bisseções (D-026). O critério é o ARI final contra os 4 grupos reais. Execução de 2026-11-06 (33 execuções, 1 seed, GPU):

| `m` | Clusters finais no ótimo | ARI máx | Intervalo de `τ` ótimo avaliado | `τ` sugerido (centro) | Borda inferior em | Borda superior em |
|---|---|---|---|---|---|---|
| 100% | 4 | 1.000 | 0.344 a 0.906 | 0.625 | (0.3125, 0.3438] | [0.9062, 0.9375) |
| 25% | 4 | 1.000 | 0.344 a 0.906 | 0.625 | (0.3125, 0.3438] | [0.9062, 0.9375) |
| 10% | 6 | 0.987 | 0.312 a 0.906 | 0.609 | (0.2812, 0.3125] | [0.9062, 0.9375) |

- **`τ` baixo demais** (≤ 0.25 com `m` = 100% e 25%): tudo se funde num cluster só (ARI 0, pureza 0.25). Em 0.3125 sobram 2 ou 3 clusters, com grupos misturados (fusão irreversível, 4.9). Com `m` = 10% já em 0.05 há só 3 clusters, porque nem todos os clientes foram sorteados.
- **`τ` alto demais:** em 0.9375 já há mais clusters que grupos (5, 9 e 11 para `m` = 100%, 25% e 10%), sem misturar grupos (pureza 1.0). Em `τ = 1.0` nenhum par se funde (200 clusters, ARI 0), como previsto em 4.9.
- **Faixa ampla:** os `τ` de 0.34 a 0.91 dão a mesma partição nos três `m`, então neste cenário o `τ = 0.5` do artigo e o `τ = 0.9` atual do notebook estão dentro da faixa, e a faixa não depende de `m`. As bordas são conhecidas só até o vizinho avaliado (as bisseções pararam em 6 passos, com intervalos de ~0.03).
- Com `m` = 10% o ARI máximo é 0.987 e há 6 clusters, pelo mesmo motivo da tabela acima: clientes ainda não sorteados na rodada 50. Isso é efeito de `m`, não de `τ`.
- Só uma seed: as bordas podem mudar com outra partição dos dados.

### 4.12 Bugs e limitações conhecidos (StoCFL)

1. **Corrigido em 2026-11-04.** `StoCFL-FCC.py` e `StoCFL-FEMNIST.py` não importavam, porque pediam `femnist` de `settings.py`, onde ele está comentado.
2. **FCC.py, `--setting rotated`:** `RotatedMNISTTrainer` lê `args.dataset` (que é float), `args.root`, `args.save_dir`, `args.n` e `args.obbs`, nenhum deles definido nesse script. Use `StoCFL-FCC+CFL.py` para rotated.
3. **FCC.py, `--setting lskewed` com `--process 1`** (default) quebra: `LabelSkewMNISTTrainer` não tem `.dataset`. Use `--process 0`. Ele também lê MNIST de `./dataset/mnist/` (sem "s") sem `download=True`.
4. **FCC.py com `--train 1`:** em `ShiftedMNISTTrainer`, `get_test_dataloader` usa `client_id/5` (deveria ser `client_id // 100`; só existem 4 arquivos de teste) e `evaluate` faz `range(id_list)` com uma lista. `FeatureSkewHybridMNISTTrainer` e `LabelSkewMNISTTrainer` não têm `evaluate`/`get_test_dataloader`. Na prática FCC.py só funciona com `--train 0`.
5. **FEMNIST:** "Global Model - Global Test" avalia `self._model` **sem** carregar o `gmodel` antes ([StoCFL-FEMNIST.py:84](StoCFL/StoCFL-FEMNIST.py#L84)). Os pickles são lidos de `./leaf/pickle_datasets/femnist/{train,test}/`; gere-os com `leaf/gen_pickle_dataset.sh femnist <data_root>` a partir de JSONs no formato LEAF. O README em `datasets/femnist/` descreve o formato FedScale (CSV), que é diferente.
6. **`ShiftedMNISTTrainer._get_dataloader`** faz `random_split` 80/20 **a cada chamada**: o subconjunto de treino muda toda vez e a validação se sobrepõe ao treino entre chamadas.
7. **Assinatura do `SerialTrainer` (verificada, não é bug):** as subclasses chamam `super().__init__(model, None|0, cuda, logger)` de forma posicional. No `fedlab==1.2.1`, a versão fixada em `requirements.txt`, a assinatura é `SerialTrainer(model, client_num, cuda=False, logger=None)` (conferido no código-fonte em 2026-11-04). Então `cuda` e `logger` chegam aos parâmetros certos e o trainer usa a GPU.
8. **Corrigido em 2026-11-04.** Os centros de cluster usavam só os membros sorteados na rodada. Agora usam todos, como na Eq. 2 e na linha 9 do Alg. 1 do artigo (`cluster_center` em [functional.py](StoCFL/functional.py#L86)). Nenhum cluster sorteado tem membro sem `psi` (invariante 5 de 4.5).
9. Fusões são irreversíveis e não há mecanismo de divisão.
10. FedAvg sem ponderação por tamanho do dataset (irrelevante nos cenários sintéticos, que têm clientes de tamanho igual, mas não no FEMNIST nem com `--dirichlet_alpha`, em que os clientes de `n = 240` têm de 51 a 709 amostras). **Mantido de propósito** na simulação do dropout com treino (D-045): é o que o código e o artigo fazem, e ponderar mudaria o algoritmo. Consequência: um cliente pequeno pesa tanto quanto um grande no `gmodel` e no modelo do cluster.
11. Custo: cada cliente sorteado treina **duas vezes** por rodada (cluster + global), mais a observação única. Os dados são relidos do disco a cada `get_data_loader`.
12. **Modelo global encadeado (corrigido em 2026-11-04).** Nos cinco Trainers, o segundo laço de `train` reatribuía `gmodel` a cada cliente, e cada cliente partia do resultado do anterior. Isso não é o FedAvg do artigo (4.15.3), em que todos partem de `ω_t`, então agora todos partem do mesmo `gmodel`. **Consequência importante:** isso afasta os resultados dos números publicados. Com MNIST real nos parâmetros da Tabela 1 (1200 clientes, 10%, 100 rodadas, 1 seed), o `gmodel` encadeado dava 95.00, contra 94.96 da linha FedAvg do artigo, e o FedAvg de verdade dá 78.04, próximo da linha FedProx (77.82). Isso sugere que as tabelas do artigo vieram do código encadeado; é uma inferência, não prova. Esta correção segue o texto do artigo por decisão do usuário (D-014).
13. **As três cópias de `StandaloneServer` deixaram de ser idênticas.** O `StoCFL-FCC+CFL.py` tem o dropout com retorno (`--drop` e `--drop_rounds`, 4.1), e o `StoCFL-FCC.py` e o `StoCFL-FEMNIST.py` ainda não (passo 5 do [plano](plano-dropout-stocfl.md)): eles sorteiam `num_per_round` entre todos os clientes. Com `--drop > 0`, quem tem ausências longas participa menos; com `--train 1`, isso muda quem contribui para o `gmodel` e para os modelos de cluster, e esse efeito não foi medido. O efeito do `--drop` sobre o ARI e o nº de clusters também não foi medido.

### 4.13 Código legado ou não usado

- `fedscale/`: não é importado por nenhum script.
- `config/*.pkl` e `config/*_partition.py`: usados só por `settings.mnist()` e `settings.cifar10()`, que são importados mas não chamados.
- `settings.py`: `RotatedMNIST`, `RotatedCIFAR10`, `ShiftedMNIST`, `FskewedFashionMNIST` e `AddGaussianNoise` são versões antigas. Em `trainer.py`, `RotatedMNIST` é importado de `settings` e depois **sobrescrito** pelo de `datasets` ([trainer.py:16-19](StoCFL/trainer.py#L16-L19)). Só `label_skew_parition` ([settings.py:70](StoCFL/settings.py#L70)) é usado de fato.
- `models/model.py`, `CNN_MNIST`, `AlexNet_CIFAR10`, `ComplexMNISTPartitioner`, `LabelSkewMNISTTrainer.local_process`, `functional.quadprog/optim_lambdas/dt/evaluate_*`, `MnistRotated`.

### 4.14 Dependências do FedLab usadas

| Símbolo | Uso no projeto |
|---|---|
| `SerializationTool.serialize_model / deserialize_model` | Modelo ↔ vetor 1-D de parâmetros. |
| `Aggregators.fedavg_aggregate(lista)` | Média (uniforme quando não há pesos) de vetores; usada para o `gmodel` e os modelos de cluster. |
| `ModelMaintainer` | Base do `StandaloneServer` (`self._model`, `self.model_parameters`). |
| `SerialTrainer` | Base dos Trainers (`self._model`, `self.cuda`, `self.gpu`, `self.model_parameters`). |
| `fedlab.utils.functional.evaluate(model, crit, loader)` | Retorna `(loss, acc)`; a loss é **somada** sobre os batches, como na cópia em `ShiftedMNISTTrainer.evaluate`. |
| `random_slicing(dataset, num_clients)` | Partição IID: `dict cliente → índices`. |
| `Logger(nome, arquivo)`, `SubsetSampler`, `load_dict` | Logging, amostragem por índices e leitura dos `.pkl` de config. |

### 4.15 Fundamentos do artigo (por que o algoritmo funciona)

Fonte: versão publicada na *Neural Networks* 187 (2025) 107278, intitulada "StoCFL: A stochastically clustered federated learning framework for Non-IID data with dynamic client participation" (PDF `docs/StoCFL.pdf`). A versão original do arXiv (v1, março de 2023) se chamava "Stochastic Clustered Federated Learning"; as diferenças relevantes estão em 4.15.8. O artigo chama a etapa de agrupamento de **SFCC** (*stochastic federated client clustering*) e a de treino de **Bi-CFL**; os scripts do repositório usam "FCC". Quando a numeração de equações aparece, é a da versão publicada.

#### 4.15.1 Problema

- `N` clientes, cada um com um dataset local `D_i`. Existem `K` distribuições latentes `P_k`, e **o servidor não conhece `K`**.
- Quatro tipos de Non-IID (seguindo Hsieh et al.), com o cenário do artigo e o equivalente neste repositório:

| Tipo (artigo) | Cenário do artigo | `--setting` / Trainer neste repo | Partição |
|---|---|---|---|
| *Feature distribution skew* (muda P(x)) | Rotated MNIST (0/90/180/270°) e Rotated CIFAR-10 (0/180°) | `rotated` (FCC.py, quebrado) ou `StoCFL-FCC+CFL.py` / `RotatedMNISTTrainer` | `RotatedMNIST`, `RotatedCIFAR10Partitioner` |
| *Label distribution skew* (muda P(y)) | Pathological MNIST `{0,1,2},{3,4},{5,6},{7,8,9}`, 400 clientes | `lskewed` / `LabelSkewMNISTTrainer` | `label_skew_parition` |
| *Label concept skew* (muda P(y\|x)) | Shifted MNIST `y' = (y+s) % 10`, `s ∈ {0,3,6,9}` | `shifted` / `ShiftedMNISTTrainer` | `ShiftedMNISTPartitioner` |
| *Feature concept skew* (muda P(x\|y)) | Hybrid MNIST + FashionMNIST, 200 clientes | `fskewed` / `FeatureSkewHybridMNISTTrainer` | `HybridMNISTPartitioner` |
| Real | FEMNIST (3.597 clientes) e FedCelebA (9.343 clientes) | `StoCFL-FEMNIST.py` / `FEMNISTTrainer` | LEAF. **FedCelebA não tem trainer nem script no repositório** (só existe `leaf/dataset/celeba_dataset.py`). |

- **Suposição 1 (CFL, citada de Sattler et al.):** existe uma partição `C = {c_1, …, c_K}` dos clientes, com `N ≥ K ≥ 2`, em que os clientes de cada `c_k` têm distribuições similares.
- O CFL convencional resolve, para cada cluster `k`, `min f_k(θ_k) = E[ℓ(θ_k; D^(k))]` (Eq. 1), treinando cada cluster **isoladamente**. O artigo aponta dois problemas:
  1. **Falta de flexibilidade do sistema.** Os métodos anteriores exigem todos os clientes presentes, ou conhecimento prévio do número de clusters.
  2. **Baixa eficiência de dados.** Sem troca de informação entre clusters, um cluster pequeno gera um modelo ruim.

#### 4.15.2 SFCC: clusterização estocástica

- **Extrator de distribuição:** `Ψ(D) = Normalize(∇_ψ ℓ(ψ; D))`, o **gradiente normalizado da perda no modelo âncora `ψ`**. O artigo o interpreta como a direção do modelo âncora até um mínimo local de `D`. A âncora **não é otimizada** durante o FL, e a loss é a mesma para todos os clientes (entropia cruzada).
- **Similaridade:** `cos(Ψ(D_i), Ψ(D_j)) = Ψ(D_i)·Ψ(D_j) / (‖Ψ(D_i)‖·‖Ψ(D_j)‖)`.
- **Por que dá para comparar clientes vistos em rodadas diferentes:** `ψ` e `ℓ` são fixos e compartilhados, então `Ψ(D_i)` é a mesma função de `D_i` em qualquer rodada. O algoritmo calcula `Ψ` só para clientes sorteados que ainda não participaram (Alg. 1, linha 5).
- **Evidência empírica** (Fig. 3): matrizes de cosseno entre clientes mostram que clientes com mais rótulos em comum, menor diferença de rotação, mesmo shift ou mesmo domínio têm cosseno maior. Não há prova formal.
- **Objetivo (Eq. 2):** `min_C Σ_{i<j} cos(Ψ(D̃_i), Ψ(D̃_j))`, onde `Ψ(D̃_j)` é a **média** de `Ψ(D_i)` sobre os clientes do cluster `j`, ou seja, clusters tão distantes entre si quanto possível. O limiar `τ` é a similaridade mínima para considerar dois datasets parecidos.
- **Algoritmo (Alg. 1, linhas 4–13):** cada cliente começa como um cluster, com `K̃ = N`. A cada rodada o servidor sorteia `m` clientes, calcula `Ψ` dos novos, atualiza a representação dos clusters, monta a matriz de cosseno `M` e **funde os pares com `M_ij > τ`**, reduzindo `K̃` em 1 por fusão. A minimização de Eq. 2 é gulosa; o artigo não prova que ela é atingida.
- **Caso limite:** se todos os clientes fossem sorteados na primeira rodada, o StoCFL vira clusterização aglomerativa clássica sobre a métrica do extrator.
- **Custo de comunicação:** uma comunicação adicional por cliente (baixar a âncora e subir o vetor `Ψ`), feita uma vez. Os métodos baseados em hipótese (IFCA) mandam vários modelos a cada rodada.
- **Âncora nos experimentos:** `ψ = ω_0`, o modelo global inicial. O artigo "argumenta" que `Ψ` é robusto à inicialização com base em 5 sementes, sem teste formal.

#### 4.15.3 Bi-CFL: treino bi-nível

Para cada cluster `k`:

```
min over θ_k:  h_k(θ_k; ω*) = f_k(θ_k) + (λ/2)·‖θ_k − ω*‖²          (Eq. 3)
s.t.  ω* ∈ argmin_ω G(f_1(ω), …, f_N(ω))
```

`G` é o objetivo global; **neste artigo `G` é o FedAvg**. O modelo global `ω*` é treinado com os dados de todos os clientes e funciona como regularizador, o que permite a transferência de conhecimento entre clusters. O treino é **alternado** (Alg. 1, linhas 14–23):

| Passo | Quem | O que |
|---|---|---|
| 1 | Servidor | Envia ao cliente `i` o modelo global `ω_t` e o modelo do cluster dele, `θ_k`. |
| 2 | Cliente | `θ_k^i ← θ_k − η·(∇f_i(θ_k) + λ·(θ_k − ω))`, ou seja, o modelo do cluster com termo proximal em direção a `ω`. |
| 3 | Cliente | `ω^i ← ω − η·∇f_i(ω)`: o modelo global com SGD puro, sem regularização. |
| 4 | Servidor | `ω_{t+1} ← FedAvg` dos `ω^i` de todos os sorteados; `θ_k ← FedAvg` dos `θ_k^i` dos sorteados do cluster `k`. |

O pseudocódigo mostra um passo de gradiente por modelo, mas o texto diz que os clientes executam "vários passos de SGD". Quando dois clusters se fundem, o texto diz apenas que "o servidor funde os modelos de cluster correspondentes", **sem especificar a regra**.

**Casos limites** (a base da interpretação de `τ` e `λ`):

| Configuração | Equivale a |
|---|---|
| `λ = 0` | CFL convencional (Eq. 1), clusters independentes |
| `λ` grande | Modelos de cluster ≈ modelo global. O artigo afirma que isso garante que os modelos de cluster "não serão piores que o global" (uma afirmação, não um teorema). |
| `τ = 1` | Nenhuma fusão: `K̃ = N`, equivale ao Ditto (FL personalizado) |
| `τ = −1` | Tudo em um cluster: equivale ao FedProx (FL global) |
| `λ = 0` e `τ = −1` | FedAvg (indicado na v1) |

#### 4.15.4 Inferência para clientes novos

Um cliente novo com dataset `D̂` envia `Ψ(D̂)`. O servidor:

1. calcula `d̂ = max_j cos(Ψ(D̂), Ψ(D̃_j))` e guarda o cluster `ĉ` que atinge o máximo;
2. se `d̂ ≥ τ`, atribui o cliente a `ĉ`; senão cria o cluster `K̃ + 1` com `θ_{K̃+1} = θ_ĉ`.

Mesmo sem cluster adequado, o cliente herda o modelo do cluster mais próximo como boa inicialização, e depois do treino o modelo mais próximo serve para predizer dados de clientes novos. Note a assimetria: a fusão usa `>` e a inferência usa `≥`. **Esta etapa não está implementada neste repositório.**

#### 4.15.5 Teoria

A versão publicada **não tem teoremas, lemas nem provas**. Só há a Suposição 1, citada de Sattler et al. Os resultados de convergência do CFL são atribuídos a Ghosh et al. e Ma et al. (2022). Também não há análise formal de complexidade ou de comunicação. As garantias do artigo são **empíricas**, em contraste com o Teorema da Separação do CFL (3.9.2).

#### 4.15.6 Experimentos do artigo

Todos usam 5 sementes (média ± desvio), PyTorch e FedLab.

| Experimento | Configuração | Resultado |
|---|---|---|
| Clusterização (seção 5.1) | MNIST patológico, rotacionado e shifted com 400 clientes cada (`K = 4`); Hybrid com 200 (`K = 2`). **50 rodadas, τ = 0.5, 10% por rodada**, âncora aleatória | Avaliado só por t-SNE de `Ψ` e pela curva do nº de clusters e do valor de Eq. 2 por rodada: o algoritmo "encontra o número correto de clusters sem conhecê-lo". **Sem ARI/NMI/pureza.** |
| Rotated MNIST/CIFAR (seção 5.2.1) | MNIST: `N ∈ {4800, 2400, 1200}` com `\|D\| ∈ {50, 100, 200}`, 100 rodadas, 5 épocas, **batch cheio**, lr 0.1. CIFAR: `N = 200`, `\|D\| = 500`, 200 rodadas, 5 épocas, **batch 50**, lr 0.1. **τ = 0.5, λ = 0.05**. Amostragem 10% e 100% | Tabela 1 abaixo |
| Shifted MNIST/CIFAR (5.2.2) | `N = 20`, `K = 4`, shifts `{0,3,6,9}`, todos participam, batch 128 e lr 0.1 para IFCA/FedSEM | Tabela 2 abaixo |
| FEMNIST e FedCelebA (5.2.3) | FEMNIST: 3.597 clientes; FedCelebA: 9.343 clientes, 200.288 imagens. **100 rodadas, 5% por rodada**, τ ∈ {0.55, 0.60}, dropout 0.5 | Tabela 3 abaixo. O StoCFL acha 2 clusters principais no FEMNIST (Fig. 8), coerente com Ghosh et al. e Marfoq et al. |
| Ablação de λ (5.3) | 50 rodadas, λ ∈ {0, 0.01, 0.05, 0.5, 1, 10} nos quatro cenários MNIST | Tabela 4 |
| Ablação de τ (5.3) | Rotated MNIST em 0° e 180° × 4 partições patológicas = 8 clusters, 400 clientes | Qualitativo (t-SNE, Fig. 9) |
| Clientes novos (5.4) | 30% dos clientes ficam de fora do FL e entram só na inferência | Tabela 5 |

Os baselines são FedAvg, FedInit, FedProx, Ditto (modelos global e personalizado), e IFCA, CFL e FedSEM (clusterizados), sob as mesmas condições Non-IID relatadas nos respectivos artigos. **Nenhum baseline está implementado neste repositório.**

**Tabela 1: acurácia de teste (%), recorte** (Rotated MNIST `K = 4`, Rotated CIFAR `K = 2`; nas colunas, taxa de amostragem 10% / 100%).

| Método | MNIST 4800×50 | MNIST 1200×200 | CIFAR 200×500 |
|---|---|---|---|
| FedAvg | 95.72 / 96.10 | 94.96 / 95.72 | 48.26 / 47.98 |
| FedInit | 96.29 / 97.04 | 96.03 / 96.65 | 48.09 / 48.79 |
| FedProx | 76.45 / 76.47 | 77.82 / 77.90 | 47.17 / 47.15 |
| Ditto | 65.05 / 73.60 | 79.38 / 83.96 | 46.91 / 46.61 |
| IFCA(4) | 91.74 / 90.43 | 91.00 / 88.69 | 50.80 / 51.40 |
| FedSEM(4) | 89.04 / 90.27 | 90.92 / 92.42 | 46.06 / 48.30 |
| **StoCFL** (τ = 0.5, λ = 0.05) | **97.00 / 97.36** | **96.71 / 97.40** | **52.84 / 54.99** |

O artigo também reporta MNIST 2400×100, IFCA(2)/(6) e FedSEM(2)/(6); o StoCFL fica sempre à frente, e a vantagem sobre o FedAvg no MNIST é de ~1 a 2 pontos. O artigo explica que o IFCA falha no MNIST porque um modelo pode "dominar" o outro desde o início: se ele se ajusta bem a duas distribuições nas primeiras rodadas, o outro nunca é atualizado. O FedSEM mostra o mesmo fenômeno, o que o artigo atribui à dependência da inicialização.

**Tabela 2: Shifted** (`N = 20`, todos participam).

| Método | Shifted MNIST (20 × 9600) | Shifted CIFAR-10 (20 × 8000) |
|---|---|---|
| FedAvg | 24.44 | 13.01 |
| FedInit | 25.13 | 13.53 |
| IFCA(4) | 98.11 | 54.05 |
| FedSEM(4) | 98.03 | 54.79 |
| CFL | **98.20** | 55.23 |
| StoCFL | 98.14 | **55.42** |

No Shifted MNIST o CFL é numericamente um pouco melhor; o artigo descreve o resultado como "desempenho de modelo próximo" e diz que a curva do StoCFL é melhor na maioria das rodadas, porque ele termina a clusterização cedo e o CFL só divide em estágios tardios, com participação total.

**Tabela 3: FEMNIST e FedCelebA** (100 rodadas, 5% por rodada).

| Método | FEMNIST | FedCelebA |
|---|---|---|
| FedAvg | 86.27 | 87.48 |
| CFL | 79.64 | 88.71 |
| IFCA(2) / IFCA(3) | 73.11 / 69.11 | 88.38 / 85.38 |
| FedSEM(2) / FedSEM(3) | 85.81 / 88.14 | 89.20 / 88.2 |
| StoCFL (τ = 0.55) | **90.92** | 91.12 |
| StoCFL (τ = 0.60) | 90.71 | **91.73** |

No FEMNIST, CFL e IFCA ficam **abaixo do FedAvg**, e o artigo atribui a vantagem do StoCFL ao uso dos dados de todos os clientes pelo modelo global. No FedCelebA, um τ pequeno produz 2 clusters principais e um τ maior produz 4; o desempenho é robusto à escolha.

**Tabela 4: efeito de λ** (acurácia %; "Global" é o `ω` final em todos os testes, as demais colunas são a média dos modelos de cluster).

| Cenário | Global | λ = 10 | 1 | 0.5 | 0.05 | 0.01 | 0 |
|---|---|---|---|---|---|---|---|
| Pathological | 92.17 | **89.28** | 86.89 | 83.49 | 37.83 | 24.12 | 24.05 |
| Rotated | 92.65 | 62.06 | 94.88 | 95.28 | **95.86** | 94.20 | 92.25 |
| Shifted | 24.46 | 32.69 | 92.36 | 93.85 | **95.12** | 93.80 | 92.22 |
| Hybrid | 92.50 | 92.26 | 92.75 | **92.77** | 92.69 | 91.99 | 90.11 |

Leitura: o melhor `λ` **depende do cenário** (o artigo conclui isso). Em Rotated e Shifted o melhor está em `λ = 0.05`, e o `λ = 0` (CFL puro) é pior, o que sustenta a ideia de que o regularizador transfere conhecimento. O contraste mais forte é o patológico, em que `λ ≤ 0.05` derruba a acurácia para 24–38% e `λ = 10` chega a 89%. Interpretação nossa, não do artigo: cada cluster vê só 2 ou 3 classes, então seu modelo precisa do conhecimento do global.

**Tabela 5: clientes novos** (acurácia %, 30% dos clientes só na inferência).

| Método | FEMNIST (participantes / novos) | FedCelebA (participantes / novos) |
|---|---|---|
| FedAvg | 85.93 / 86.70 | 88.79 / 89.65 |
| CFL | 79.78 / 73.24 | 89.38 / 85.73 |
| IFCA(2) | 74.82 / 75.78 | 89.82 / 88.29 |
| StoCFL | **91.00 / 91.06** | **90.79 / 91.46** |

O FedSEM não suporta inferência de clusters para clientes novos e ficou de fora. O CFL é quem mais perde acurácia nos clientes novos; segundo o artigo, FedAvg e IFCA ficam consistentes.

**Ablação de τ.** No cenário combinado (rotação 0°/180° × 4 partições patológicas), `τ > 0.76` agrupa apenas clientes parecidos **tanto em feature quanto em label** (clusters mais finos), enquanto `τ < 0.67` foca só na distribuição de rótulos e ignora a rotação. Em geral, **τ maior dá granularidade mais fina**. A relação exata entre τ e granularidade fica como trabalho futuro. A robustez a τ mostrada na Tabela 3 é atribuída ao modelo global.

**Estabilidade com a taxa de amostragem** (Tabela 1 e Fig. 6): o StoCFL varia pouco entre 10% e 100% (97.00 contra 97.36 no MNIST 4800×50). O IFCA exige a suposição prévia `M̃` do número de clusters e é sensível a ela.

#### 4.15.7 Orientação do artigo sobre hiperparâmetros

- **τ:** "determina o foco da clusterização"; maior τ dá clusters mais finos. Não há regra de escolha. Os valores usados foram 0.5 (Rotated/Shifted/Hybrid), 0.55 e 0.60 (FEMNIST/FedCelebA). Uma estratégia prática, nossa: rode com `--train 0` e olhe `cos_rec*.log` (4.9).
- **λ:** "o melhor λ depende do cenário Non-IID"; sugere ajustá-lo dinamicamente durante o treino (sem método) e consultar FedProx e Ditto para estratégias de escolha. Valor usado nas comparações com IFCA/FedSEM (Tabela 1): 0.05.
- **Âncora:** `ψ = ω_0`, aleatória.

#### 4.15.8 Limitações, trabalhos futuros e versões

Declarados pelos autores: combinar técnicas de transferência de conhecimento na otimização local, criar um mecanismo dinâmico de entrada e saída de clientes (dados locais que mudam, exclusão de clientes bizantinos de um cluster benigno) e estender o método para *prompt-tuning* federado.

Evidentes no texto (leitura nossa):

- Sem teoria; todas as garantias são empíricas.
- Fusões são irreversíveis, e um erro precoce não se corrige.
- `τ` e `λ` são escolhidos à mão.
- A qualidade da clusterização é avaliada visualmente, sem métricas como ARI/NMI.
- O pseudocódigo deixa em aberto a ordem dos pares, se `M` é recalculada após cada fusão e a regra de fusão de modelos. Também fica em aberto quais clusters entram em `M` e o que fazer com clientes nunca observados: a linha 8 percorre todos os clusters de `C`, inclusive os unitários de clientes ainda sem `Ψ`, enquanto o texto fala em fundir os clusters sorteados a cada rodada. O código segue o texto. Entre os clusters comparados, o centro não é ambíguo: a Eq. 2 usa todos os membros, e nenhum cluster sorteado tem membro sem `Ψ` (4.5, invariante 5).
- O pseudocódigo usa um passo de gradiente, o texto diz "vários passos".

Diferenças entre a v1 (arXiv, 2023) e a publicada: a publicada acrescenta os baselines FedInit e FedSEM, o dataset FedCelebA, a informação explícita de que `G` é o FedAvg e a seção de clientes novos em dois datasets; a Tabela 3 passou a listar só τ = 0.55 e 0.60 (a v1 listava também 0.65). O restante do método é o mesmo. As afirmações sobre a v1 vêm de leitura de segunda mão da versão HTML do arXiv; a publicada foi lida diretamente do PDF.

### 4.16 Mapa artigo ↔ código

#### Nomes

| Artigo | Código |
|---|---|
| SFCC (clusterização estocástica) | fase `# cluster` de `main` + `bucket` + `inter_cluster_union` + `unite` |
| Bi-CFL | fase `# clustered federated optimization` de `main` (`--train 1`) |
| `Ψ(D_i)` | `self.psi[cid]` |
| Âncora `ψ` | `self.anchor` |
| Modelo global `ω` | `self.gmodel` |
| Modelo de cluster `θ_k` | `self.cluster_parameters[k]` |
| Matriz `M` | `dt_matrix` + `parse_matrix` (`M_ij = cosine_sim`) |
| `τ`, `λ`, `η`, `m`, `T` | `args.tau`, `args.mu`, `args.lr`, `args.num_per_round`, `args.com_round` |
| Conjunto `P` de clientes já observados | `self.psi.keys()` |
| `K̃` | número de entradas não vazias de `find_cluster_content` |
| Clientes que saem e voltam (dropout com retorno) | O artigo não trata. É uma extensão deste repositório: `Availability` (4.8) e o sorteio entre os disponíveis (`--drop`, só no FCC+CFL). A ideia vem do MimiC (Sun, Mao e Zhang, *IEEE TMC*, 2024), cuja Suposição 1 (`τ(t,i) ≤ τ_max`) limita a ausência; o processo daqui foi escrito do zero, sem copiar o código do MimiC ([plano](plano-dropout-stocfl.md), D-031 e D-032). |

#### Onde o código segue ou diverge do artigo

| Elemento | Artigo | Código | Consequência |
|---|---|---|---|
| **Representação `Ψ`** | `Normalize(∇ℓ(ψ; D))`: **um gradiente** no modelo âncora, sem treino | `dataset_representation` ([trainer.py:21](StoCFL/trainer.py#L21)) | **Segue o artigo.** O código original usava `ψ_i = anchor − θ` depois de `obep` épocas de SGD, sem normalizar: em MNIST real, cosseno com `∇ℓ` de 0.96 com `obep=10` e de 0.50 com `obep=20`, lote 50. A partição final em Rotated MNIST foi a mesma. |
| Centro do cluster | Eq. 2: média de `Ψ` sobre **todos os membros** do cluster (o Alg. 1, linha 9, escreve soma, o que dá o mesmo cosseno) | `cluster_center`: média dos `ψ` de todos os membros | **Segue o artigo.** O código original usava só os membros sorteados na rodada. Em Rotated MNIST real, a partição foi idêntica nas duas formas (2 seeds), porque as rotações se separam com folga (fim da seção 8). |
| Limiar | Fusão com `M_ij > τ` | `result[key] > self.tau` | **Segue o artigo.** |
| Ordem e regra das fusões | Não especificada | Pares em ordem decrescente de cosseno; para no primeiro que não passa de `τ`. A matriz é calculada **uma vez** por rodada. | Equivale a *single linkage* com corte em `τ`, com transitividade: `A~B` e `B~C` juntam `A,B,C` mesmo com `cos(A,C) < τ`. |
| Fusão de modelos | "O servidor funde os modelos" (sem regra) | `unite`: se `\|C_i\| < \|C_j\|` e `j` tem modelo, `i` herda o de `j`; senão `i` mantém o seu (pode não ter nenhum, e então volta a `ω₀`). `i` é o menor id. | O modelo do cluster maior tende a vencer, mas não sempre: se `j` não tem modelo ainda, `i` mantém o seu mesmo sendo menor. |
| Passos locais | Alg. 1: um passo; texto: vários | `args.epochs` épocas completas | Mais deriva do cliente com `epochs` alto. |
| Termo proximal | `λ·(θ − ω)` no gradiente | `loss = CE + 0.5·mu·Σ‖w − w0‖²` com `w0 = gmodel` do início da rodada | Idêntico, com `mu = λ`. |
| Modelo global `G` | FedAvg: todos partem de `ω_t`, e o servidor faz a média | `_train_alone` a partir do mesmo `gmodel` para cada cliente + `fedavg_aggregate`, média uniforme | **Segue o texto do artigo**, mas não as tabelas: o código encadeado original é o que chega perto dos números publicados (4.12 #12). |
| Agregação | `FedAvg` | `Aggregators.fedavg_aggregate` sem pesos por tamanho | Irrelevante nos cenários sintéticos (clientes de tamanho igual). |
| Cliente novo | Seções 4 e 5.4: regra do cosseno com `τ` | **Não implementado** | Tabela 5 não é reproduzível. Está no [backlog](backlog.md). |
| Indisponibilidade de clientes | Participação parcial por sorteio uniforme de `m` clientes por rodada. Um "mecanismo dinâmico de entrada e saída de clientes" é trabalho futuro declarado (4.15.8). | **Extensão opcional** no `StoCFL-FCC+CFL.py`: `--drop` e `--drop_rounds`. Quem está fora não é sorteado, e `m` é completado só entre os disponíveis. Com `--drop 0` (padrão), o código se comporta como o do artigo. | Nenhum resultado do artigo usa isso. O efeito esperado é um atraso curto na observação dos clientes, e o efeito no ARI não foi medido (4.1, 4.9). |
| Baselines | FedAvg, FedInit, FedProx, Ditto, IFCA, CFL, FedSEM | **Nenhum implementado** (o `gmodel` é o FedAvg dos clientes sorteados, com o mesmo treino local) | Tabelas 1–3 não são reproduzíveis só com este repo. |
| Métrica | Acurácia média dos modelos de cluster nos testes dos respectivos clusters, e do modelo global em todos os testes | Cada cluster sorteado é testado no grupo do **primeiro membro**; resultado em `accuracy.pkl` (FCC+CFL), com o recall por classe ao lado (`evaluate_recall`, extensão deste repositório) | Sem agregação por sementes e sem ARI/NMI. Com `--dirichlet_alpha` só há um teste (balanceado), que penaliza o modelo de um cluster especializado; o recall por classe permite ponderar pela distribuição de rótulos do cluster. |
| Dados non-IID nos rótulos | O artigo usa rotação, shift e skew patológico de rótulos (grupos de classes) | **Extensão opcional:** `--dirichlet_alpha` (Dirichlet nos rótulos, sem rotação, `k = 1`) | Nenhum resultado do artigo usa isso. Sem grupos reais, não há ARI contra um gabarito. |
| Modelo CIFAR | "Duas camadas conv + duas FC", sem informar os tamanhos | `CNN_CIFAR10`: duas conv + duas FC (120→10) | **Segue o artigo.** O código original tinha três FC (120→84→10). O tamanho 120 é uma escolha (D-016). |
| Modelo FEMNIST | Duas conv, max pooling, duas FC, inicialização Xavier e dropout 0.5 **entre as camadas convolucionais e as FC** | `CNN_FEMNIST` ([models/cnn.py:13](StoCFL/models/cnn.py#L13)): dropout 0.5 logo após a convolução; Xavier | **Segue o artigo.** O código original tinha dropout 0.25 após a convolução e 0.5 entre as duas FC. |
| Inicialização dos modelos de cluster | `ω₀ = θ₁ = ⋯ = θ_N`: todos os modelos de cluster começam em `ω₀` | `cluster_parameters` começa vazio, e um cluster sem modelo recebe `deepcopy(self.anchor)` na primeira vez que um membro é sorteado ([StoCFL-FCC+CFL.py:98](StoCFL/StoCFL-FCC+CFL.py#L98)) | **Segue o artigo**, com a cópia feita sob demanda. O código original usava o `gmodel` atual. O efeito foi desprezível em Rotated MNIST real (até 0.0001). |
| Objetivo da Eq. 2 (Fig. 5) | Curva do nº de clusters e do valor da Eq. 2 por rodada | O código não calcula a Eq. 2. O nº de clusters sai de `cluster.pkl` (FCC+CFL) ou de `exp_*_logs.pkl` (FCC) | A Fig. 5 não é reproduzível só com os logs existentes. |
| Sementes | 5 sementes | Um comentário em [StoCFL-FCC+CFL.py:241](StoCFL/StoCFL-FCC+CFL.py#L241) lista `[0, 42, 1998, 4421380, 789190]` | Provável conjunto usado nos experimentos. |

### 4.17 Reproduzindo os experimentos do artigo com este repositório

**Desde a D-014, o código segue o texto do artigo, e os resultados de treino ficam abaixo das tabelas publicadas** (seção 8), que parecem ter vindo do código original (4.12 #12). A clusterização continua correta. Para chegar perto das tabelas, use o código original, até o commit `3159d55`.

Os parâmetros abaixo são os do artigo; os comandos são **aproximados**, porque o artigo não informa vários hiperparâmetros do FEMNIST.

| Experimento | Parâmetros do artigo | Comando aproximado | Cuidados |
|---|---|---|---|
| Rotated MNIST (Tab. 1) | `N ∈ {4800, 2400, 1200}`, 100 rodadas, 5 épocas, batch cheio, lr 0.1, τ 0.5, λ 0.05, 10% ou 100% | `python StoCFL-FCC+CFL.py --n 4800 --com_round 100 --num_per_round 480 --lr 0.1 --epochs 5 --mu 0.05 --tau 0.5 --seed 0 --dataset mnist --process 1` | **Omita `--batch_size`** (= `None` = batch cheio). Memória: `psi` guarda um vetor de ~1,63 M parâmetros (6,5 MB) por cliente, então 4800 clientes ocupam **~31 GB**, e o script ainda grava `psi.pkl` inteiro a cada rodada. Para `N = 1200`, ~7,8 GB. `--process 1` gera `N` arquivos `.pkl`. |
| Rotated CIFAR (Tab. 1) | `N = 200`, 200 rodadas, 5 épocas, batch 50, lr 0.1, τ 0.5, λ 0.05 | `python StoCFL-FCC+CFL.py --n 200 --com_round 200 --num_per_round 20 --batch_size 50 --lr 0.1 --epochs 5 --mu 0.05 --tau 0.5 --seed 0 --dataset cifar --process 1` | Use `--num_per_round 200` para 100% de amostragem. |
| Qualidade da clusterização (5.1) | 400 clientes (Hybrid: 200), 50 rodadas, τ 0.5, 10% por rodada, `--train 0` | `python StoCFL-FCC.py --setting shifted --k 4 --com_round 50 --num_per_round 40 --tau 0.5 --process 1` | Em `lskewed`, use também `--process 0` (4.12 #3). Hybrid (`fskewed`): `--num_per_round 20`. O artigo avalia por t-SNE e curva de nº de clusters; o repo só grava `cluster_rec_*.log` e `exp_*_logs.pkl`, sem t-SNE nem ARI/NMI. |
| Shifted `N = 20` (Tab. 2) | 20 clientes, todos participam | **Não reproduzível sem editar o código** | `ShiftedMNISTTrainer` tem `client_num = 400` fixo. Há resquícios do cenário de 20 clientes: `int(client_id/5)  # 20clients` em `get_test_dataloader` ([trainer.py:164](StoCFL/trainer.py#L164)), e 80% de 60000/5 dá os 9600 da Tabela 2. Falta o particionador de Shifted CIFAR. |
| FEMNIST (Tab. 3) | 3.597 clientes, 100 rodadas, 5% por rodada, τ 0.55 ou 0.60 | `python StoCFL-FEMNIST.py --com_round 100 --client_num 3597 --num_per_round 180 --tau 0.55 --train 1 --seed 0 --batch_size <B> --lr <lr> --epochs <E> --mu <λ>` | O artigo não informa lr, épocas, batch nem λ do FEMNIST. Precisa dos pickles LEAF (`leaf/gen_pickle_dataset.sh femnist`). A linha "Global Model" do log está errada (4.12 #5). |
| Ablação de λ (Tab. 4) | 50 rodadas, λ ∈ {0, 0.01, 0.05, 0.5, 1, 10} | `--mu <λ> --train 1` | O treino do `StoCFL-FCC.py` está quebrado (4.12 #4); use `StoCFL-FCC+CFL.py` com rotated. |
| Clientes novos (Tab. 5), FedCelebA | — | **Não implementado** | Sem trainer de CelebA e sem inferência de clientes novos. |

Para as 5 sementes, faça uma execução por valor de `--seed` (0, 42, 1998, 4421380 e 789190, do comentário do código). Como `--seed` entra no nome do diretório de dados (`rotated_{dataset}_{n}_{seed}`), cada semente exige `--process 1` e gera uma nova partição.

---

## 5. CFL × StoCFL: comparação

| Aspecto | CFL | StoCFL |
|---|---|---|
| Direção | **Divisivo**: 1 cluster que se bipartiu | **Aglomerativo**: N clusters que se fundem |
| Sinal de similaridade | `ΔW` da rodada atual, a partir do modelo do cluster (muda a cada rodada) | `Ψ`, o gradiente normalizado calculado **uma vez** em uma âncora fixa |
| Participação | Assume **todos** os clientes em toda rodada | **Parcial** (`num_per_round`); ψ de rodadas diferentes são comparáveis. No `StoCFL-FCC+CFL.py`, opcionalmente com clientes indisponíveis por algumas rodadas (`--drop`, 4.1) |
| Quando agrupa | Só depois que o FL converge (`mean_norm < EPS_1`, `max_norm > EPS_2`, `γ_max`) | Desde a 1ª rodada (independe do treino; dá para rodar com `--train 0`) |
| Nº de clusters controlado por | `EPS_1`, `EPS_2` (normas absolutas, sensíveis a lr etc.) | `τ` (cosseno, invariante à escala) |
| Algoritmo de agrupamento | Bipartição que minimiza a maior similaridade entre os lados (Alg. 1 do artigo, ≡ *single linkage* até restarem 2) | *Single linkage* com limiar τ entre os clusters amostrados |
| Erros | Divisões irreversíveis | Fusões irreversíveis |
| Modelos | 1 por cluster + cache dos modelos ancestrais | 1 por cluster **+ 1 global**, com termo proximal μ (bi-nível) |
| Escolha final do modelo | O cliente escolhe o melhor modelo do cache | Modelo do seu cluster |
| Código | Notebook + PyTorch puro | Scripts CLI + FedLab 1.2.1 |
| Garantias teóricas | **Teorema da Separação**: sob hipóteses sobre o ruído do gradiente (`γ`), a bipartição por cosseno é correta; o notebook verifica a condição de `γ_max` | **Nenhuma**: só evidência empírica (t-SNE, curvas, tabelas) |
| Regra de escolha dos limiares | `ε1 ≈ max‖Δθ_c‖/10`, `ε2 ∈ [ε1, 10·ε1]` | Nenhuma para `τ` e `λ`; só ablações |
| Clientes novos | Árvore de parâmetros (Alg. 4); **não implementada** no notebook | Regra do cosseno com `τ` (4.15.4); **não implementada** nos scripts |
| Baselines nos experimentos | Só o FL | FedAvg, FedInit, FedProx, Ditto, IFCA, CFL, FedSEM (nenhum implementado no repo) |
| Setup dos experimentos | 20 clientes, label-swap/permutação, 3 épocas, batch 100; AG News | 200 a 4800 clientes (rotação), 400 (shift, label skew), 200 (hybrid), FEMNIST; amostragem parcial |

---

## 6. Orientações para agentes de IA e mantenedores

**Antes de mudar algo:**
- O `StandaloneServer` está **triplicado** (FCC, FCC+CFL, FEMNIST) e os métodos `_train_alone`/`train_alone_prox` estão **repetidos em 5 Trainers**. Toda mudança de algoritmo precisa ser aplicada em todas as cópias, ou o código deve ser refatorado primeiro. Exceção atual: o `--drop` só existe no `StoCFL-FCC+CFL.py` (4.2 e 4.12 #13).
- No CFL, os pesos (`client.W`) são **referências vivas** aos `Parameter`s do modelo, e `copy()` altera o modelo in-place.
- No StoCFL, modelos são vetores 1-D. Use `SerializationTool` para ir e voltar de `nn.Module`.
- Preserve os invariantes de 4.5, especialmente "id do cluster = menor id de cliente membro".

**Onde mexer para...**

| Objetivo | Onde |
|---|---|
| Trocar a métrica de similaridade (StoCFL) | `functional.dt_matrix` ([functional.py:77](StoCFL/functional.py#L77)); a alternativa `dt` já existe. |
| Trocar a métrica de similaridade (CFL) | `pairwise_angles` ([fl_devices.py:61](clustered-federated-learning/fl_devices.py#L61)). |
| Mudar o critério de divisão do CFL | Condição `if mean_norm<EPS_1 and ...` na célula 9 do notebook. |
| Mudar a regra de fusão (ex.: average linkage, recalcular similaridade após cada fusão) | `inter_cluster_union` + `unite` em cada script StoCFL. |
| Mudar herança de modelo na fusão (ex.: média ponderada) | `unite`, bloco `# merge cluster model`. |
| Mudar a lei de indisponibilidade dos clientes (ex.: queda por grupo de rotação) | `availability.py` ([availability.py:25](StoCFL/availability.py#L25)), com os testes em `tests/test_availability.py`. O sorteio entre os disponíveis fica em `main` ([StoCFL-FCC+CFL.py:59](StoCFL/StoCFL-FCC+CFL.py#L59)). |
| Desligar o acoplamento com o global | `--mu 0`. |
| Novo cenário de dados (StoCFL) | Criar um Partitioner (`pre_process`, `get_dataset`, `get_data_loader`) em `datasets.py` e um Trainer com a interface de 4.6; registrar em `__main__`. |
| Novo cenário no CFL | Célula 5 (transformações por cliente) e/ou `split_noniid`. |
| Medir a qualidade da clusterização | Comparar `cluster.pkl` / `exp_*_logs.pkl` com o ground truth de 4.6 (ex.: ARI/NMI do sklearn); hoje isso não é calculado. |
| Implementar clientes novos no StoCFL | Calcular o `ψ` do cliente novo, comparar com os centros e aplicar a regra `≥ τ` ou criar cluster (4.15.4). |

**Checklist para rodar o StoCFL sem surpresas:** passar `--n --com_round --num_per_round --seed` (sem default; `--batch_size` e `--obbs` podem ser omitidos e valem batch cheio); usar `--process 1` só na primeira vez.

**Checklist para o CFL:** manter `frac=1.0`.

---

## 7. Glossário

| Termo | Significado |
|---|---|
| Rodada (*communication round*) | Ciclo servidor → clientes treinam → servidor agrega. |
| `ΔW` / `dW` | Atualização de pesos de um cliente em uma rodada (CFL). |
| Âncora (`anchor`) | Modelo inicial fixo em que o StoCFL calcula o gradiente de cada cliente. |
| ψ (`psi`) | No código, `psi[cid]` é a representação de um cliente, o `Ψ(D_i)` do artigo. No artigo, `ψ` (sem índice) é a **âncora**, e no código ela se chama `anchor`. |
| τ (`tau`) | Limiar de similaridade de cosseno para fusão (StoCFL). |
| μ (`mu`, λ no artigo) | Peso do termo proximal entre o modelo do cluster e o global. |
| `EPS_1`, `EPS_2` | Limiares de norma do critério de divisão do CFL. |
| FCC / SFCC | *(Stochastic) Federated Client Clustering*: só a etapa de agrupamento do StoCFL. O artigo publicado usa SFCC; os scripts, FCC. |
| Bi-nível | Otimização simultânea de modelos de cluster e de um modelo global acoplados por μ. |
| Ground truth de cluster | Grupo "real" de um cliente nos cenários sintéticos (rotação, shift, domínio). |
| Shard | Pedaço IID de um dataset atribuído a um cliente (`random_slicing`). |
| Dropout com retorno / disponibilidade | Opção `--drop` do `StoCFL-FCC+CFL.py`: um cliente cai, fica fora até `--drop_rounds` rodadas, não é sorteado enquanto estiver fora e volta depois. Não confundir com o *dropout* das camadas de rede neural do `CNN_FEMNIST`, nem com `--tau`, o limiar de cosseno. |
| Bi-CFL | Etapa de treino do StoCFL: modelo de cluster com termo proximal para o modelo global (Eq. 3). |
| `G` | Objetivo global do StoCFL; no artigo é o FedAvg. |
| Clientes congruentes / incongruentes | Congruentes: existe um único modelo bom para todos (Suposição 1 do CFL). Incongruentes: não existe, e vale a pena separá-los. |
| `γ_i`, `γ_max` | Erro relativo do gradiente empírico do cliente `i` em relação ao verdadeiro, `‖∇R−∇r_i‖/‖∇R‖`, e seu máximo. É um limite assumido, não medido. |
| `α_intra^min`, `α_cross^max` | Menor cosseno entre clientes da mesma distribuição e maior cosseno entre clientes de lados opostos de uma bipartição. |
| Gap de separação `g(α)` | `α_intra^min − α_cross^max`; se for maior que 0, a bipartição por cosseno é correta. Só pode ser calculado conhecendo os clusters reais. |
| Árvore de parâmetros | Estrutura do CFL que guarda o modelo e o cluster de cada divisão, usada para atribuir clientes novos. |
| Single / complete linkage | Em agrupamento aglomerativo, a distância entre clusters é a do par mais próximo (*single*) ou a do par mais distante (*complete*). |

---

## 8. Referências e versões dos artigos

| Artigo | Versão usada | Observações |
|---|---|---|
| Sattler, Müller, Samek. *Clustered Federated Learning: Model-Agnostic Distributed Multitask Optimization Under Privacy Constraints*. IEEE TNNLS 32(8):3710–3722, 2021. DOI 10.1109/TNNLS.2020.3015958. arXiv:1910.01991 | PDF local (versão TNNLS, 13 páginas) | A versão TNNLS inclui a **recomendação de `ε1` e `ε2`** (3.9.8), que o texto do arXiv v1 não tem. A numeração de equações citada neste guia é a da TNNLS. |
| Zeng, Hu, Liu, Yu, Wang, Xu. *StoCFL: A stochastically clustered federated learning framework for Non-IID data with dynamic client participation*. Neural Networks 187 (2025) 107278. DOI 10.1016/j.neunet.2025.107278. arXiv:2303.00897 | PDF local `StoCFL.pdf` (versão publicada, 12 páginas); código oficial indicado em nota de rodapé do artigo | A v1 do arXiv (2023) se chamava *Stochastic Clustered Federated Learning*. As diferenças estão em 4.15.8; o que este guia afirma sobre a v1 vem de leitura de segunda mão da versão HTML do arXiv. |

Como as fórmulas foram verificadas: o texto dos PDFs foi extraído com `pdftotext`. Onde os símbolos gregos saíram truncados (por exemplo, no Teorema 1), as expressões foram conferidas com a versão HTML do arXiv. As tabelas de resultados foram copiadas do PDF publicado do StoCFL (recorte na Tabela 1).

O que **não** foi verificado: treino real do StoCFL em label skew, shifted, hybrid, CIFAR e FEMNIST (este último só rodou com dados falsos), e os experimentos do artigo do CFL (label swap, CIFAR, AG News).

**Verificação com dados sintéticos (2026-11-04).** Os trechos abaixo são o código real do repositório, extraído por AST e executado em ambientes temporários fora do repositório. Eles mostram a correção lógica, e não o desempenho. Os scripts não foram versionados (D-013 em [decisoes.md](decisoes.md)).

| O que | Como | Resultado |
|---|---|---|
| CFL: bug de índices na 2ª divisão (3.7 #1) | `Server.cluster_clients` real, 10 clientes em 3 grupos, scikit-learn 1.3.2 | Confirmado: com `[c1, c2]` faltam clientes e há duplicados; com `idc[c1], idc[c2]` sai correto. |
| CFL: `affinity` (3.7 #4) | A mesma chamada em scikit-learn 1.3.2 e 1.9.1 | `FutureWarning` no 1.3.2; `TypeError` no 1.9.1. |
| CFL: *complete* × Alg. 1 (3.10) | 3000 matrizes de cosseno (grupos compactos e alongados, 2 a 5 clientes por grupo, ruído variável), comparadas com o Alg. 1 transcrito do artigo e com a força bruta da Eq. 33 | Com `g(α) > 0` (1609 casos): 0 divergências. Com `g(α) ≤ 0` (1391): 729 divergências, e em todas o *complete* fica pior que o ótimo da Eq. 33. O Alg. 1 achou o ótimo em todos os casos. |
| StoCFL: fusão por limiar (4.1, 4.16) | `unite`, `bucket` e `inter_cluster_union` reais, com `cosine_sim` e `fedavg_aggregate` em Python puro; 5 seeds × 40 rodadas | O resultado de cada rodada é exatamente o das componentes conexas do grafo `cos ≥ τ` (*single linkage* com corte em τ). Invariante 1 de 4.5 mantida. |
| StoCFL: invariante 5 de 4.5 | A mesma simulação | Nenhum cluster sorteado, nem cluster com mais de um membro, teve cliente sem `psi`. |
| FedLab 1.2.1 | Leitura do código-fonte baixado com `pip download`, sem instalar nem executar | `SerialTrainer(model, client_num, cuda, logger)` (4.12 #7). `fedavg_aggregate` é média uniforme com `weights=None`. `evaluate` devolve a loss **somada** sobre os batches e a acurácia média. `random_slicing` gera partes IID de tamanho igual. |

**Treino real, código original (2026-11-04).** Python 3.12, torch 2.15 em CPU, scikit-learn 1.3.2 e FedLab 1.2.1, com EMNIST e MNIST reais. O CFL rodou com as células do próprio notebook, e o StoCFL com as classes reais extraídas por AST. Só foram trocados a GPU, a gravação em disco e o gráfico. Cada variante mudou um único ponto no código. Estes resultados descrevem o código **antes** das correções de D-014.

| O que | Configuração | Resultado |
|---|---|---|
| CFL: notebook como está | 12 seeds, parâmetros do notebook | A seed 42 divide na rodada 33 (a figura salva mostra ~32), com os grupos corretos e acurácia de 0.62 para 0.74. A 1ª divisão saiu correta em 12 de 12. 7 seeds fizeram divisões extras, e 4 terminaram com partição inválida (3.7 #1). |
| CFL: correção de índices | As 4 seeds inválidas | Acurácia final de 0.718, 0.708, 0.631 e 0.612 para 0.757, 0.718, 0.720 e 0.728. |
| CFL: `γ_max = 0.75` (com os índices corrigidos) | 7 seeds com divisão extra; valor escolhido depois de ver os dados | 6 de 7 ficaram só com os 2 grupos; acurácia parecida. |
| CFL: outras variantes | 3 seeds por variante | Sem decaimento do lr: 1ª divisão na rodada 53, na 80 ou nunca, contra 28 a 34 com ele. Buffers de momentum zerados: acurácia final de 0.737–0.742, contra 0.734–0.738. SGD puro com os limiares antigos: só 1 de 3 seeds dividiu. Sem o aquecimento de 20 rodadas: resultado idêntico. *Single* × *complete*: coincidem na 1ª divisão. |
| StoCFL: operações do treino | MNIST real, 40 clientes | `train` real: cada cliente parte do resultado do anterior. `train_alone_prox` bate com a linha 21 do Alg. 1 (erro de 7e-9). Com `obep=1` e batch cheio, `ψ = η∇ℓ`. |
| StoCFL: variantes, cenário da seção 5.1 | 400 clientes, 10%, 50 rodadas, τ=0.5, λ=0.05, 2 a 3 seeds | Código: global ~0.91, cluster ~0.94, ARI 1.0. Com FedAvg de verdade: global ~0.68, cluster ~0.90. Centro com todos os membros, `Ψ` do artigo e `θ` em `ω₀` não mudaram a partição nem a acurácia além de 0.0001. A Tabela 4 do artigo traz 92.65 e 95.86. |
| StoCFL: Tabela 1 | 1200 clientes, `\|D\| = 200`, 10%, 100 rodadas, 1 seed | StoCFL 96.65 (artigo: 96.71). `gmodel` encadeado 95.00 (FedAvg no artigo: 94.96). FedAvg de verdade 78.04 e um único cluster com termo proximal sem encadear 77.98 (FedProx no artigo: 77.82). O artigo não informa o μ do FedProx. |

**Depois das correções de D-014 (2026-11-04).** Mesmo ambiente, com scikit-learn 1.9. A clusterização e o notebook rodaram com os scripts e as células reais. O treino do StoCFL usou as classes reais extraídas por AST, sem GPU e sem gravar em disco.

| O que | Configuração | Resultado |
|---|---|---|
| CFL: notebook inteiro | Todas as células, seed 42 | Roda sem erro. Uma divisão, com os grupos `[0–4]` e `[5–9]`. |
| CFL: limiares | `ε1 = 0.2`, `ε2 = 0.8`, SGD puro, Alg. 1, 80 rodadas, 13 seeds | Todas dividem, a 1ª divisão sempre acerta e nenhum cluster mistura grupos. 11 terminam exatamente nos 2 grupos, e 2 têm uma divisão extra dentro de um grupo. Acurácia final de 0.64 a 0.73. Sem divisão, o FL fica em ~0.60. Testado com `γ_max = 0`; o valor 0.5 não rejeitaria nenhuma dessas tentativas, porque todos os limites ficaram acima de 0.71. |
| StoCFL: clusterização da seção 5.1 | Scripts reais, 50 rodadas, 10% por rodada, τ = 0.5 | Rotated, Shifted e Pathological (400 clientes): 4 clusters e 1 cliente ainda não sorteado. Hybrid (200 clientes): 2 clusters e 2 clientes ainda não sorteados. ARI 1.0 em todos, nos clusters com mais de um membro. Confirma a afirmação do artigo de que o algoritmo encontra o número correto de clusters. |
| StoCFL: treino, cenário da seção 5.1 | Rotated MNIST, 400 clientes, 10%, 50 rodadas, λ = 0.05, 3 seeds | Global ~0.68 e cluster ~0.90, contra 92.65 e 95.86 na Tabela 4 do artigo. |
| StoCFL: treino, Tabela 1 | Rotated MNIST, 1200 clientes, 10%, 100 rodadas, λ = 0.05, 1 seed | Global 78.04 e cluster 90.99, contra 94.96 (FedAvg) e 96.71 (StoCFL) no artigo. Antes das correções, eram 95.00 e 96.65. |
| StoCFL: fluxo | CIFAR com 8 clientes e 2 rodadas; FEMNIST com pickles LEAF falsos | Os scripts rodam até o fim. A acurácia não foi medida. |
