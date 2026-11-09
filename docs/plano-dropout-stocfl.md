# Plano: dropout com retorno no StoCFL

- **Situação:** plano, nada implementado. O código do StoCFL não foi alterado.
- **Branch:** `dropout-stocfl` (a partir de `main`, em 2026-11-09).
- **Decisão que originou o plano:** [D-031](decisoes.md). As escolhas que ainda estão abertas estão na seção 4.
- **Fontes:** o artigo do MimiC (Sun, Mao e Zhang, *IEEE TMC*, 2024; PDF em `mimic_codes/MimiC.pdf`, fora do git) e o código do StoCFL lido em 2026-11-09 (`StoCFL-FCC+CFL.py`, `trainer.py`, `functional.py`).

## 1. Objetivo

Testar o efeito do **dropout temporário** na clusterização e no treino do StoCFL: um cliente sorteado não participa da rodada e **volta depois**. Hoje o StoCFL só tem participação parcial, o sorteio uniforme de `num_per_round` clientes (`m`), em [StoCFL-FCC+CFL.py:56](../projetos/StoCFL/StoCFL-FCC+CFL.py#L56).

Os dois sorteios ficam separados:

| Sorteio | Papel | Muda? |
|---|---|---|
| `m` (`--num_per_round`) | escolhe os clientes da rodada, que preenchem a matriz de cosseno | **não**: continua `random.sample` do gerador global |
| `drop` (novo) | processo de disponibilidade: decide quais dos `m` não participam | novo, com gerador próprio |

Com `--drop 0` (padrão), o código se comporta exatamente como hoje.

## 2. Por que não basta variar `m`

O MimiC tem três padrões de dropout (seção VII-A do artigo; o código `mimic_codes/other_utils/dropout.py` os chama de `tau`, `static` e `random`). O terceiro, que sorteia a cada rodada `P·N` clientes com pesos aleatórios novos, tem a mesma distribuição que o `random.sample` do StoCFL. Foi verificado por simulação em 2026-11-09: a probabilidade de cada par de clientes é a mesma do sorteio uniforme (0,06661 a 0,06672 contra 0,06667, com N = 6 e 2 por rodada), e a chance de cada cliente estar ativo também (0,0989 a 0,1008 contra 0,1000, com N = 30 e 3 por rodada). Implementá-lo não mudaria nenhum resultado.

Para o dropout fazer diferença, ele precisa quebrar a simetria entre os clientes ou ter memória no tempo. Foi simulado o processo especificado na seção 5 (`N = 240`, 4 grupos, 50 rodadas, 3.000 repetições, mesma disponibilidade média nos três cenários com queda). Com `m = 24` (10%), `d = 0,1` e `L = 5` fixo (disponibilidade média 0,667):

| Cenário | Sobreviventes por rodada | Clientes observados (r10 / r25 / r50) | Rodadas com algum grupo sem sobrevivente |
|---|---|---|---|
| sem `drop` | 24,0 | 0,652 / 0,928 / 0,995 | 0,3% |
| sem memória (equivale a um `m` menor) | 16,0 | 0,500 / 0,823 / 0,968 | 4,2% |
| por cliente, com retorno | 16,0 | 0,487 / 0,811 / 0,964 | 4,4% |
| por grupo de rotação, com retorno | 16,0 | 0,486 / 0,810 / 0,963 | **80,4%** |

- **Por cliente com retorno** é quase equivalente a reduzir `m`: a cobertura fica 1 a 2 pontos atrás, porque as ausências se repetem por rodadas seguidas. Com `m = 25%`, a fração de execuções com todos os clientes observados na rodada 50 cai de 0,978 (sem memória) para 0,939.
- **Por grupo** tem a mesma cobertura, mas em cerca de 80% das rodadas algum grupo de rotação fica sem nenhum sobrevivente, tanto com `m = 10%` quanto com `m = 25%`. Esse regime não é reproduzível variando `m`, e é o cenário da Fig. 1 do MimiC.
- **Limites:** só foram medidas presença e cobertura. O efeito sobre o ARI, o nº de clusters e a acurácia **não foi medido**. O script da simulação não foi versionado.
- **Início da execução:** a simulação compara regimes estacionários (150 rodadas de aquecimento). Uma execução real começa com todos disponíveis, então as primeiras rodadas têm disponibilidade acima da média.

O MimiC de verdade (tipo 1, `tau`) usa períodos fixos por cliente. O processo deste plano é diferente: quedas aleatórias com ausência limitada, inspirado na Suposição 1 do artigo (`τ(t,i) ≤ τ_max`). Ele não reproduz nenhum dos três padrões do MimiC.

## 3. O que o StoCFL já permite

O retorno é barato porque o StoCFL não guarda estado por cliente. Cada ponto abaixo foi conferido no código:

| Fato | Consequência |
|---|---|
| `Ψ` é calculado uma vez, na âncora fixa, e nunca é refeito ([StoCFL-FCC+CFL.py:60-66](../projetos/StoCFL/StoCFL-FCC+CFL.py#L60-L66)). | Quem volta usa o `Ψ` guardado. Nada fica obsoleto, e a invariante 5 (guia, 4.5) continua valendo. |
| O trainer recarrega o modelo do cluster e o `gmodel` do servidor a cada rodada ([trainer.py:243-255](../projetos/StoCFL/trainer.py#L243-L255)). | Quem volta recebe os modelos atuais. Não há variável de correção, como no MimiC. |
| O cliente fora continua no seu cluster, e o centro do cluster usa todos os membros ([functional.py:86](../projetos/StoCFL/functional.py#L86)). | A ausência não altera o centro. |
| `bucket` agrupa só os modelos recebidos, e `cluster_parameters` só é atualizado para clusters com sobrevivente ([StoCFL-FCC+CFL.py:160-171](../projetos/StoCFL/StoCFL-FCC+CFL.py#L160-L171)). | Um grupo inteiro ausente deixa o modelo do cluster parado, enquanto o `gmodel` muda. Ao voltar, o termo proximal o puxa para o `gmodel` atual. É a versão do StoCFL para a obsolescência, e é uma expectativa pela leitura do código, não uma medida. |
| `observe` e `train` aceitam qualquer lista de ids; o `train` pareia `id_list` com `cluster_models` por `zip`. | Uma lista menor funciona. |
| `fedavg_aggregate` faz `torch.stack` da lista. | Uma lista vazia falha, então rodada sem sobreviventes precisa de tratamento. |
| `cluster.pkl` precisa ter uma partição por rodada (o notebook usa isso em `concluida`). | Rodada pulada ainda grava a partição. |

## 4. Decisões pendentes

Nenhuma destas foi decidida. O plano das seções 5 a 8 está escrito para a **opção recomendada**, e cada linha diz o que muda se a escolha for outra. Antes de implementar, o usuário decide (política 4 do `CLAUDE.md`), e a escolha vira uma nova entrada em `decisoes.md`.

| # | Decisão | Opções | Recomendação | Se for outra |
|---|---|---|---|---|
| P1 | Fase em que o `drop` atua (`--drop_stage`) | `round`: o cliente fica fora da rodada inteira (sem `Ψ` e sem treino). `train`: o cliente é observado e entra na matriz, mas não treina. Ou só uma das duas. | Implementar as duas, com `round` como padrão. O custo é pequeno: duas listas no laço. | Só `round`: remove a lista `cid_train`. Só `train`: o notebook atual não serve, porque usa `--train 0`. |
| P2 | Lei da queda (`--drop_law`) | `client`: cada cliente cai sozinho. `group`: o grupo de rotação inteiro cai e volta junto. | Implementar as duas. A `group` é a única que `m` não aproxima. | Só `client`: o experimento seria quase equivalente a um `m` menor (seção 2). |
| P3 | Duração da ausência (`--drop_dur`) | `fixed`: sempre `L` rodadas. `uniform`: sorteada em `[1, L]`. | Implementar as duas, com `fixed` como padrão. | Só `fixed`: simplifica o gerador. |
| P4 | Quem pode cair | Só os sorteados em `m` (o `m` fica como está, e os indisponíveis são perdidos). Ou o servidor sorteia `m` só entre os disponíveis. | A primeira. A segunda deixa de ser dropout e vira disponibilidade conhecida. | Na segunda, o sorteio de `m` muda, e o pareamento com o caso sem `drop` se perde. |
| P5 | Rodada sem sobreviventes | Pular a rodada. Ou completar com clientes disponíveis até um mínimo (o MimiC usa 2). | Pular, sem promoção de clientes. Um sobrevivente já basta para o treino. | Com mínimo, entra uma regra de escolha dos clientes extras e o `m` efetivo deixa de ser o sorteado. |
| P6 | Escopo | Só `StoCFL-FCC+CFL.py`, ou também `StoCFL-FCC.py` e `StoCFL-FEMNIST.py`. | Começar só pelo `StoCFL-FCC+CFL.py` (o único que o notebook usa). O módulo novo é compartilhado, então replicar custa poucas linhas por script. | O `StoCFL-FEMNIST.py` não tem `args.k`, então só aceitaria a lei `client`. O `StoCFL-FCC.py` só roda com `--train 0` (guia, 4.12). |
| P7 | Notebook de teste | Notebook novo `teste-dropout.ipynb`, ou nova seção no `teste-fracao-clientes.ipynb`. | Notebook novo: o `teste-fracao-clientes.ipynb` tem alterações do usuário ainda não commitadas e é a referência reproduzível dos resultados de `m`. | Na seção nova, é preciso combinar com o usuário o que fazer com as alterações pendentes antes de editar. |

## 5. Especificação

### 5.1 Variáveis novas (linha de comando)

| Flag | Tipo | Padrão | Significado |
|---|---|---|---|
| `--drop` | float em `[0, 1)` | `0.0` | `d`: probabilidade de uma unidade disponível cair em cada rodada. Com `0`, nenhum sorteio é feito. |
| `--drop_rounds` | int `≥ 1` | `1` | `L`: duração da ausência, em rodadas. É o máximo de rodadas consecutivas fora. |
| `--drop_dur` | `fixed` ou `uniform` | `fixed` | `fixed`: ausência de exatamente `L` rodadas. `uniform`: sorteada em `[1, L]`. |
| `--drop_law` | `client` ou `group` | `client` | Unidade que cai: cada cliente, ou cada grupo de rotação (`⌊c·k/n⌋`, o mesmo gabarito do trainer e do notebook). |
| `--drop_stage` | `round` ou `train` | `round` | `round`: o cliente fica fora da rodada inteira. `train`: só não treina. |

Não use `tau` no nome do atraso: `--tau` já é o limiar de cosseno do StoCFL.

### 5.2 Processo de disponibilidade

Um módulo novo, `projetos/StoCFL/availability.py`, sem dependência de `torch`, para ser testado sem GPU e compartilhado pelos scripts. A classe `Availability(n, k, drop, rounds, dur, law, seed)` tem o método `step()`, chamado **uma vez por rodada**, que devolve `up[c]` para cada cliente.

Estado por unidade `u` (um cliente ou um grupo): `down_left[u]` (rodadas de ausência que faltam depois da atual) e `grace[u]` (esta é a rodada de retorno). Em cada rodada, para cada unidade:

```text
se down_left[u] > 0:           # em ausência
    up[u] = falso
    down_left[u] -= 1
    grace[u] = (down_left[u] == 0)          # a próxima rodada é a de retorno
senão se grace[u]:             # rodada de retorno: disponível e sem sorteio
    up[u] = verdadeiro
    grace[u] = falso
senão se rng.random() < drop:  # cai agora e fica L rodadas (esta inclusa)
    L = duração()                           # rounds, ou sorteio em [1, rounds]
    up[u] = falso
    down_left[u] = L - 1
    grace[u] = (L == 1)
senão:
    up[u] = verdadeiro
```

- **Retorno garantido:** a rodada de retorno não tem sorteio, então entre duas ausências há pelo menos uma rodada disponível, e a ausência consecutiva nunca passa de `L` (a Suposição 1 do MimiC).
- **Disponibilidade média:** `a = 1 / (1 + d·ℓ)`, com `ℓ` a duração média (`L` em `fixed`, `(L + 1)/2` em `uniform`). A simulação deu 0,667 para `d = 0,1` e `L = 5`, e 0,784 para `d = 0,05` e `L ~ U[1,10]`, que é o que a fórmula prevê.
- **Gerador próprio:** `random.Random("drop-{seed}")`, que é determinístico entre execuções e não consome o gerador global. Assim, a sequência dos sorteios de `m` é idêntica com e sem `drop`, o que permite comparar as duas execuções de forma pareada.
- **Lei `group`:** a unidade é `c * k // n`, e todo cliente do grupo recebe o mesmo `up`.
- **Validação:** `0 ≤ drop < 1` e `rounds ≥ 1`; com `drop = 0`, `step()` devolve tudo disponível sem tocar no gerador.

### 5.3 Integração no laço (`StoCFL-FCC+CFL.py`)

O servidor cria `self.availability` em `__init__` ([:29](../projetos/StoCFL/StoCFL-FCC+CFL.py#L29)). Em `main`, logo depois do sorteio de `m` ([:56](../projetos/StoCFL/StoCFL-FCC+CFL.py#L56)):

```python
cid_this_round = sorted(random.sample(self.client_id, self.args.num_per_round))   # inalterado
up = self.availability.step()
alive = [c for c in cid_this_round if up[c]]
cid_cluster = alive if self.args.drop_stage == "round" else cid_this_round
cid_train = alive
```

Onde cada lista entra (o resto do laço não muda):

| Trecho | Hoje | Passa a usar |
|---|---|---|
| observação de `Ψ` ([:60-67](../projetos/StoCFL/StoCFL-FCC+CFL.py#L60-L67)) | `cid_this_round` | `cid_cluster` |
| clusters sorteados ([:70](../projetos/StoCFL/StoCFL-FCC+CFL.py#L70)) | `cid_this_round` | `cid_cluster` |
| inicialização dos modelos de cluster, `cluster_models`, `trainer.train` e `bucket` ([:79-91](../projetos/StoCFL/StoCFL-FCC+CFL.py#L79-L91)) | `cid_this_round` | `cid_train` |

- **Invariante 5:** continua valendo, porque só entram na clusterização clientes observados nesta rodada ou antes (`cid_cluster ⊇ cid_train`, e todo cliente de `cid_cluster` é observado antes da fusão).
- **Rodada sem sobreviventes (P5):** as listas ficam vazias, `observe([])` e `inter_cluster_union([], [])` não fazem nada, o bloco de treino é pulado (`if self.args.train and cid_train:`), e a partição ainda é gravada em `cluster.pkl`. No bloco de treino, `accuracy_log` recebe `{"cluster": [], "global": []}` para manter uma entrada por rodada.
- **Tipos:** os ids ficam como `int` do Python. Um `np.int64` aparece no log como `np.int64(3)` com o numpy 2.5 e quebra a expressão regular `client id this round \[(.*?)\]` do notebook.

### 5.4 Logs e nome da pasta

- A linha `client id this round` **não muda** (continua listando os sorteados).
- Com `drop > 0`, acrescentar a linha `Round {r}/{T}, alive {alive}, dropped {dropped}`, onde `dropped` são os sorteados que caíram, e gravar `availability.pkl` (lista, por rodada, dos clientes **fora**, sorteados ou não), no mesmo estilo do `cluster.pkl`. Isso dá a série de disponibilidade para a análise e para reproduzir a execução.
- Com `drop > 0`, o nome da pasta de logs ganha `-drop{d}-r{L}{f|u}-{law}-{stage}` antes de `-time-` (linha 247). O padrão de busca atual do notebook, `...-lambda{MU}{k}-time-*`, não casa com esses nomes, então os logs sem `drop` não se misturam com os novos.
- `args.exp_logger.info(str(args))` já registra as flags novas.

### 5.5 O que cada fase mede

- **`round`** altera a clusterização: nº de clusters, ARI, cobertura (clientes já observados) e a rodada em que a partição estabiliza. Roda com `--train 0`, como o notebook atual.
- **`train`** não altera a clusterização, só `gmodel` e os modelos de cluster. Os ARI e nº de clusters devem sair **idênticos** aos da execução sem `drop`, e esse é um teste da implementação (I6). O efeito aparece em `accuracy.pkl`, que passa a ter menos entradas de cluster por rodada (só clusters com sobrevivente são avaliados), então a comparação entre níveis de `drop` precisa levar isso em conta. Exige `--train 1`.

## 6. Passo a passo

Cada etapa é um commit atômico (política 6), com a documentação e o registro em `decisoes.md` no mesmo commit.

1. **Baseline (antes de editar o script).** Rodar `StoCFL-FCC+CFL.py` na `main` com uma configuração pequena e a mesma seed, e guardar fora do repositório o `cluster.pkl`, o `psi.pkl` e as linhas `client id this round`. É a referência do teste I1. Exemplo: `--n 40 --k 4 --dataset mnist --com_round 6 --num_per_round 8 --train 0 --seed 0 --process 1` (cria `datasets/rotated_mnist_40_0/`, ignorado pelo git).
2. **Módulo `availability.py` e testes unitários** (`tests/test_availability.py`). Commit: módulo, testes e a linha nova em 4.8 do guia.
3. **Integração no `StoCFL-FCC+CFL.py`**: flags, `self.availability`, listas `cid_cluster` e `cid_train`, linhas de log, `availability.pkl` e nome da pasta. Commit: código e a documentação da seção 7.
4. **Notebook `teste-dropout.ipynb`** (P7), sem saídas de execução no commit. Reaproveita as funções de métricas do `teste-fracao-clientes.ipynb` (copiadas, sem editar o original) e acrescenta a cobertura medida com as linhas `alive` e a fração de rodadas com algum grupo sem sobrevivente.
5. **Outros scripts** (P6), se aprovado: o mesmo bloco em `StoCFL-FCC.py` (linha 57) e `StoCFL-FEMNIST.py` (linha 56).
6. **Execuções e relatório**, como tarefa separada, depois da implementação.

## 7. Documentação a atualizar na implementação

Política 2 do `CLAUDE.md`: a documentação muda no mesmo commit do código.

| Arquivo | O que muda |
|---|---|
| [guia.md](guia.md) | 4.1 (a participação parcial passa a ter dropout opcional), 4.3 (grafo de chamadas: `availability.step()`), 4.4 e 4.5 (listas `cid_cluster` e `cid_train`; invariante 5 com `drop`), 4.8 (módulo novo), 4.9 (tabela de variáveis: as cinco flags), 4.10 (`availability.pkl` e a linha `alive`), 4.11 (como rodar) e 4.16 (mapa artigo ↔ código: o StoCFL do artigo não trata dropout; o MimiC é a origem da ideia) |
| [diagrama-atividades-stocfl.md](../projetos/StoCFL/diagrama-atividades-stocfl.md) | Depois de `S1`, um passo "aplicar disponibilidade: sobreviventes = sorteados ∩ disponíveis" e uma decisão "há sobreviventes?", com a saída que pula o treino. Conferir a sintaxe Mermaid depois de editar. |
| [diagrama-sequencia-stocfl.md](../projetos/StoCFL/diagrama-sequencia-stocfl.md) | Uma mensagem `S->>S: availability.step()` e a variação das listas de `observe` e `train` conforme `drop_stage`. Conferir a sintaxe. |
| [README do StoCFL](../projetos/StoCFL/README.md) | Exemplo de comando com `--drop` e a seção de testes com o notebook novo |
| [README de docs/](README.md) | Já aponta para este plano |
| [decisoes.md](decisoes.md) | Uma entrada por escolha das pendências P1 a P7 |
| [relatorio-m-k-tau.md](relatorio-m-k-tau.md) | Só um aviso de que o relatório não cobre dropout, se for útil |

## 8. Plano de verificação

Os testes unitários usam `unittest` (o `pytest` não está no `.venv`). A partir de `projetos/StoCFL/`:

```bash
../../.venv/bin/python -m unittest tests/test_availability.py -v
```

**Unitários (sem GPU):**

| # | Teste |
|---|---|
| T1 | `drop = 0`: tudo disponível e o estado do gerador não muda |
| T2 | Mesma seed gera o mesmo traço; seeds diferentes geram traços diferentes |
| T3 | Nenhuma unidade fica fora mais que `L` rodadas seguidas (exatamente `L` em `fixed`), e há pelo menos uma rodada disponível entre duas ausências |
| T4 | A disponibilidade média, em 200 unidades e 2.000 rodadas, fica a 0,01 de `1/(1 + d·ℓ)`, em `fixed` e em `uniform` |
| T5 | Lei `group`: todos os clientes do grupo `⌊c·k/n⌋` têm o mesmo estado em cada rodada, e os grupos não são idênticos entre si |
| T6 | Valores inválidos (`drop < 0` ou `≥ 1`, `rounds < 1`) levantam `ValueError` |

**Integração (execuções pequenas, na configuração do baseline):**

| # | Verifica | Como |
|---|---|---|
| I1 | Regressão: `--drop 0` não muda nada | `cluster.pkl`, `psi.pkl` e as linhas `client id this round` iguais às do baseline |
| I2 | Pareamento: o sorteio de `m` não depende do `drop` | com `--drop 0.3 --drop_rounds 3`, as linhas `client id this round` são iguais às do baseline |
| I3 | `round`: só os sobreviventes são observados | `psi.pkl` só tem clientes que apareceram em algum `alive` |
| I4 | Invariante 5 | em todas as rodadas, todo membro de cluster com mais de um cliente está em `psi.pkl` |
| I5 | Rodada pulada | com `--drop 0.99 --train 1`, o script termina, `cluster.pkl` e `accuracy.pkl` têm uma entrada por rodada |
| I6 | `train` não muda a clusterização | com `--drop_stage train --train 1`, o `cluster.pkl` é igual ao do baseline e o `accuracy.pkl` é diferente |
| I7 | Lei `group` | no log, todos os sorteados de um mesmo grupo caem e voltam juntos |
| I8 | O notebook lê as execuções novas | a cobertura calculada com as linhas `alive` bate com as chaves de `psi.pkl` |

## 9. Cuidados

- **Alterações que não são deste plano:** `docs/clusterizacao-ao-longo-do-tempo.ipynb`, `projetos/StoCFL/teste-fracao-clientes.ipynb`, `projetos/StoCFL/teste-fracao-clientes copy.ipynb` e `mimic_codes/` estão sem commit e **não** fazem parte desta branch. Adicione arquivos ao commit por nome.
- **Licença:** `mimic_codes/` não tem arquivo de licença. O processo desta seção 5 é novo e foi escrito a partir do artigo, sem copiar o código do MimiC.
- **Três cópias do servidor:** ao replicar nos outros scripts (P6), aplicar o mesmo bloco da seção 5.3 e as mesmas flags. O módulo `availability.py` é único.
- **Disco:** cada execução grava `psi.pkl` (~1,6 GB com 240 clientes) a cada rodada. As execuções de `drop` repetem esse custo por combinação de parâmetros, e com `--train 1` o treino roda duas vezes por cliente. Estime o tempo e o espaço com uma execução pequena antes de montar a grade.
- **Início da execução:** todos começam disponíveis, então as primeiras rodadas têm disponibilidade acima de `a`. Ao comparar com os números da seção 2, descarte ou reporte esse transitório.
- **Interpretação:** a lei `group` usa o gabarito (`⌊c·k/n⌋`) só para simular a queda. O algoritmo não o usa.
