# Plano: dropout com retorno no StoCFL

- **Situação:** plano com as decisões tomadas ([D-032](decisoes.md)). **Passos 1 a 3 da seção 6 implementados em 2026-11-09** (baseline, `availability.py` com os testes e a integração no `StoCFL-FCC+CFL.py`, com os testes I1 a I4 da seção 8; detalhes em [D-033 e D-034](decisoes.md) e no [guia](guia.md), 4.11). Faltam os passos 4 a 6 e o teste I5.
- **Números de linha:** os do `StoCFL-FCC+CFL.py` neste documento são os do código **antes** da implementação (commit `ebb6390`). Para as linhas atuais, veja o [guia](guia.md), 4.4.
- **Branch:** `dropout-stocfl` (a partir de `main`, em 2026-11-09).
- **Fontes:** o artigo do MimiC (Sun, Mao e Zhang, *IEEE TMC*, 2024; PDF em `mimic_codes/MimiC.pdf`, fora do git) e o código do StoCFL lido em 2026-11-09 (`StoCFL-FCC+CFL.py`, `trainer.py`, `functional.py`).

## 1. Objetivo

Testar o efeito da **indisponibilidade temporária de clientes** (dropout com retorno) na clusterização do StoCFL: um cliente cai, fica fora por algumas rodadas, **não pode ser sorteado enquanto estiver fora** e volta depois. Quando ele cai, outro cliente entra no lugar dele no sorteio.

Hoje o StoCFL só tem participação parcial: o sorteio uniforme de `num_per_round` clientes (`m`), em [StoCFL-FCC+CFL.py:56](../projetos/StoCFL/StoCFL-FCC+CFL.py#L56).

| Elemento | Papel | Com `--drop > 0` |
|---|---|---|
| processo de disponibilidade (novo) | decide, a cada rodada, quais dos `N` clientes estão indisponíveis; gerador próprio | novo |
| `m` (`--num_per_round`) | quantos clientes participam | o sorteio passa a ser **entre os disponíveis** (`random.sample`, gerador global) |

Com `--drop 0` (padrão), o código se comporta exatamente como hoje, inclusive a chamada a `random.sample(self.client_id, m)`.

## 2. Por que o desenho escolhido tem efeito pequeno

O MimiC tem três padrões de dropout (seção VII-A do artigo; o código `mimic_codes/other_utils/dropout.py` os chama de `tau`, `static` e `random`). O terceiro, que sorteia a cada rodada `P·N` clientes com pesos aleatórios novos, tem a mesma distribuição que o `random.sample` do StoCFL. Foi verificado por simulação em 2026-11-09: a probabilidade de cada par de clientes é a mesma do sorteio uniforme (0,06661 a 0,06672 contra 0,06667, com N = 6 e 2 por rodada), e a chance de cada cliente estar ativo também (0,0989 a 0,1008 contra 0,1000, com N = 30 e 3 por rodada). Implementá-lo não mudaria nenhum resultado.

O desenho escolhido (D-032) é: cada cliente cai sozinho, com retorno, e o servidor sorteia `m` só entre os disponíveis. Foi simulado (`N = 240`, 50 rodadas, 4.000 repetições, `d = 0,1`, `L ~ U[1,10]`, disponibilidade média 0,645, começando com todos disponíveis, como numa execução real):

| `m` | Participantes por rodada | Clientes observados nas rodadas 1 / 5 / 10 / 25: sorteio atual → com `drop` |
|---|---|---|
| 10% | 24 (igual) | 0,100 / 0,409 / 0,651 / 0,928 → 0,100 / 0,397 / 0,617 / 0,909 |
| 50% | 120 (igual) | 0,500 / 0,969 / 0,999 / 1,000 → 0,500 / 0,886 / 0,969 / 1,000 |
| 100% | **157,5** (era 240) | 1,000 / 1,000 / 1,000 / 1,000 → 0,900 / 0,940 / 0,990 / 1,000 |

- **Atraso curto:** o `drop` atrasa a observação dos clientes em poucas rodadas, e a diferença some por volta da rodada 25. Só com `m` grande o nº de participantes cai de fato (com `d = 0,2`, `m = 100%` dá 116,6 participantes).
- **Participação desigual:** com `m = 50%`, o desvio do nº de participações por cliente em 50 rodadas vai de 3,5 para 5,8, porque quem tem ausências longas participa menos.
- **Efeito esperado:** pequeno na partição final e visível só nas primeiras ~10 rodadas. Só foram medidas presença e cobertura; o efeito sobre o ARI e o nº de clusters **não foi medido**. O script da simulação não foi versionado.
- **Pareamento perdido:** como `m` é sorteado entre os disponíveis, a sequência de clientes sorteados deixa de ser a mesma da execução sem `drop` assim que alguém cai. Com uma só seed, uma diferença pequena pode ser ruído de amostragem, então a análise precisa de várias seeds.

**Fora do escopo (D-032):** a lei por grupo de rotação, em que todos os clientes de uma mesma rotação caem e voltam juntos. Ela é o regime que o sorteio atual não reproduz (com `k = 4`, `d = 0,1` e `L = 5`, algum grupo fica fora em ~80% das rodadas, e com `k = 16`, em quase todas). Acrescentá-la depois é uma extensão pequena: mapear cliente → grupo (`⌊c·k/n⌋`) no módulo de disponibilidade.

O processo deste plano não reproduz nenhum dos três padrões do MimiC. Ele é inspirado na Suposição 1 do artigo (`τ(t,i) ≤ τ_max`): quedas aleatórias com ausência limitada.

## 3. O que o StoCFL já permite

O retorno é barato porque o StoCFL não guarda estado por cliente. Cada ponto abaixo foi conferido no código:

| Fato | Consequência |
|---|---|
| `Ψ` é calculado uma vez, na âncora fixa, e nunca é refeito ([StoCFL-FCC+CFL.py:60-66](../projetos/StoCFL/StoCFL-FCC+CFL.py#L60-L66)). | Quem volta usa o `Ψ` guardado. Nada fica obsoleto, e a invariante 5 (guia, 4.5) continua valendo. |
| O trainer recarrega o modelo do cluster e o `gmodel` do servidor a cada rodada ([trainer.py:243-255](../projetos/StoCFL/trainer.py#L243-L255)). | Quem volta recebe os modelos atuais. Não há variável de correção, como no MimiC. |
| O cliente fora continua no seu cluster, e o centro do cluster usa todos os membros ([functional.py:86](../projetos/StoCFL/functional.py#L86)). | A ausência não altera o centro. |
| Todo o laço de `main` depende só de `cid_this_round` ([StoCFL-FCC+CFL.py:56-91](../projetos/StoCFL/StoCFL-FCC+CFL.py#L56-L91)). | Como o `drop` age na seleção, o resto do laço **não muda**. |
| `fedavg_aggregate` faz `torch.stack` da lista. | Uma lista vazia falha, então a rodada sem nenhum cliente disponível precisa ser pulada. |
| `cluster.pkl` precisa ter uma partição por rodada (o notebook usa isso em `concluida`). | A rodada pulada ainda grava a partição. |

## 4. Decisões

Respostas do usuário em 2026-11-09, registradas em [D-032](decisoes.md).

| # | Pergunta | Decisão |
|---|---|---|
| P1 | Fase em que o `drop` atua | Na seleção: o cliente que cai **não pode ser sorteado** e outro entra no lugar. A fase `train` (cliente observado mas sem treinar) saiu do escopo, e o `gmodel` não é tocado. |
| P2 | Lei da queda | Cada cliente cai sozinho. A lei por grupo de rotação saiu do escopo. |
| P3 | Duração da ausência | `L` sorteado com distribuição uniforme. Interpretação: inteiro em `[1, L_max]`, um sorteio por queda. A duração fixa saiu do escopo. |
| P4 | Quem pode cair | Qualquer cliente, não só os sorteados em `m`. O processo roda para os `N` clientes. |
| P5 | Rodada sem clientes suficientes | A pergunta foi reformulada: com P1 e P4, só faltam clientes se houver menos de `m` disponíveis. Usar todos os disponíveis, e pular a rodada se nenhum estiver disponível (escolha de Claude, forçada por P1 e P4). |
| P6 | Escopo | `StoCFL-FCC+CFL.py` primeiro. Os outros dois scripts ficam para depois, com a lei por cliente. |
| P7 | Notebook | Notebook novo, `teste-dropout.ipynb`. |

Depois de ver a simulação da seção 2, o usuário confirmou o desenho ("manter como decidido") em vez de trocar para "só os sorteados caem, sem reposição" ou acrescentar a lei por grupo.

**Escolhas triviais de Claude, se o usuário não objetar:** nomes das flags, estado inicial com todos disponíveis (sem aquecimento), formato do log e do `availability.pkl`, e recusar o `--drop` com `--drop_rounds < 1`.

## 5. Especificação

### 5.1 Variáveis novas (linha de comando)

| Flag | Tipo | Padrão | Significado |
|---|---|---|---|
| `--drop` | float em `[0, 1)` | `0.0` | `d`: probabilidade de um cliente disponível cair em cada rodada. Com `0`, nenhum sorteio é feito. |
| `--drop_rounds` | int `≥ 1` | `1` | `L_max`: a duração de cada ausência é sorteada uniformemente em `{1, …, L_max}`. É o máximo de rodadas consecutivas fora. |

Não use `tau` no nome do atraso: `--tau` já é o limiar de cosseno do StoCFL.

### 5.2 Processo de disponibilidade

Um módulo novo, `projetos/StoCFL/availability.py`, sem dependência de `torch`, para ser testado sem GPU e reaproveitado pelos outros scripts. A classe `Availability(n, drop, rounds, seed)` tem o método `step()`, chamado **uma vez por rodada** (inclusive na primeira), que devolve `up[c]` para cada um dos `n` clientes.

Estado por cliente `c`: `down_left[c]` (rodadas de ausência que faltam depois da atual) e `grace[c]` (esta é a rodada de retorno). Em cada rodada, para cada cliente:

```text
se down_left[c] > 0:           # em ausência
    up[c] = falso
    down_left[c] -= 1
    grace[c] = (down_left[c] == 0)          # a próxima rodada é a de retorno
senão se grace[c]:             # rodada de retorno: disponível e sem sorteio
    up[c] = verdadeiro
    grace[c] = falso
senão se rng.random() < drop:  # cai agora e fica L rodadas (esta inclusa)
    L = rng.randint(1, rounds)              # uniforme em {1, ..., L_max}, um sorteio por queda
    up[c] = falso
    down_left[c] = L - 1
    grace[c] = (L == 1)
senão:
    up[c] = verdadeiro
```

- **Retorno garantido:** a rodada de retorno não tem sorteio, então entre duas ausências há pelo menos uma rodada disponível, e a ausência consecutiva nunca passa de `L_max` (a Suposição 1 do MimiC).
- **Disponibilidade média:** `a = 1 / (1 + d·ℓ)`, com `ℓ = (L_max + 1)/2`. Para `L_max = 10`, `d = 0,1` dá 0,645 e `d = 0,2` dá 0,476.
- **Gerador próprio:** `random.Random("drop-{seed}")`, determinístico entre execuções e sem consumir o gerador global.
- **Validação:** `0 ≤ drop < 1` e `rounds ≥ 1`; com `drop = 0`, `step()` devolve todos disponíveis sem tocar no gerador.

### 5.3 Integração no laço (`StoCFL-FCC+CFL.py`)

O servidor cria `self.availability` em `__init__` ([:29](../projetos/StoCFL/StoCFL-FCC+CFL.py#L29)). Em `main`, o sorteio de `m` ([:56](../projetos/StoCFL/StoCFL-FCC+CFL.py#L56)) passa a ser:

```python
if self.args.drop > 0:
    up = self.availability.step()
    disponiveis = [c for c in self.client_id if up[c]]
    cid_this_round = sorted(random.sample(disponiveis, min(self.args.num_per_round, len(disponiveis))))
else:
    cid_this_round = sorted(random.sample(self.client_id, self.args.num_per_round))   # exatamente como hoje
```

- **O resto do laço não muda:** observação de `Ψ`, clusterização e treino continuam usando `cid_this_round`, e todos os sorteados participam.
- **Invariante 5:** continua valendo, porque todo cliente sorteado é observado antes da fusão.
- **Menos disponíveis que `m`:** o sorteio usa todos os disponíveis, então a rodada tem menos de `m` participantes (acontece com `m` grande, seção 2).
- **Nenhum disponível:** `cid_this_round` fica vazio. `observe([])` e `inter_cluster_union([], [])` não fazem nada, o bloco de treino é pulado (`if self.args.train and cid_this_round:`), e a partição ainda é gravada em `cluster.pkl`. No bloco de treino, `accuracy_log` recebe `{"cluster": [], "global": []}` para manter uma entrada por rodada.
- **Tipos:** os ids ficam como `int` do Python. Um `np.int64` aparece no log como `np.int64(3)` com o numpy 2.5 e quebra a expressão regular `client id this round \[(.*?)\]` do notebook.

### 5.4 Logs e nome da pasta

- A linha `client id this round` **continua listando os participantes** (agora só os disponíveis), então a cobertura que o notebook calcula a partir dela continua correta.
- Com `drop > 0`, acrescentar a linha `Round {r}/{T}, unavailable {lista}` e gravar `availability.pkl` (lista, por rodada, dos clientes indisponíveis), no mesmo estilo do `cluster.pkl`. Isso dá a série de disponibilidade para a análise e para reproduzir a execução.
- Com `drop > 0`, o nome da pasta de logs ganha `-drop{d}-r{L_max}` antes de `-time-` (linha 247). O padrão de busca atual do notebook, `...-lambda{MU}{k}-time-*`, não casa com esses nomes, então os logs sem `drop` não se misturam com os novos.
- `args.exp_logger.info(str(args))` já registra as flags novas.

## 6. Passo a passo

Cada etapa é um commit atômico (política 6), com a documentação e o registro em `decisoes.md` no mesmo commit.

1. **Baseline (antes de editar o script).** Rodar `StoCFL-FCC+CFL.py` na `main` com uma configuração pequena e a mesma seed, e guardar fora do repositório o `cluster.pkl`, o `psi.pkl` e as linhas `client id this round`. É a referência do teste I1. Exemplo: `--n 40 --k 4 --dataset mnist --com_round 6 --num_per_round 8 --train 0 --seed 0 --process 1` (cria `datasets/rotated_mnist_40_0/`, ignorado pelo git).
2. **Módulo `availability.py` e testes unitários** (`tests/test_availability.py`). Commit: módulo, testes e a linha nova em 4.8 do guia.
3. **Integração no `StoCFL-FCC+CFL.py`**: flags, `self.availability`, o sorteio entre os disponíveis, a rodada vazia, as linhas de log, `availability.pkl` e o nome da pasta. Commit: código e a documentação da seção 7.
4. **Notebook `teste-dropout.ipynb`**, sem saídas de execução no commit. Reaproveita as funções de métricas do `teste-fracao-clientes.ipynb` (copiadas, sem editar o original) e compara execuções com e sem `drop` em várias seeds (seção 9).
5. **Outros scripts**, depois de confirmado: o mesmo bloco em `StoCFL-FCC.py` (linha 57) e `StoCFL-FEMNIST.py` (linha 56), só com a lei por cliente.
6. **Execuções e relatório**, como tarefa separada, depois da implementação.

## 7. Documentação a atualizar na implementação

Política 2 do `CLAUDE.md`: a documentação muda no mesmo commit do código.

| Arquivo | O que muda |
|---|---|
| [guia.md](guia.md) | 4.1 (a participação parcial passa a ter indisponibilidade opcional), 4.2 (o `StoCFL-FCC+CFL.py` tem `--drop`, os outros dois ainda não), 4.3 (grafo de chamadas: `availability.step()`), 4.4 e 4.5 (sorteio entre os disponíveis), 4.8 (módulo novo), 4.9 (tabela de variáveis: as duas flags), 4.10 (`availability.pkl` e a linha `unavailable`), 4.11 (como rodar) e 4.16 (mapa artigo ↔ código: o StoCFL do artigo não trata dropout; o MimiC é a origem da ideia) |
| [diagrama-atividades-stocfl.md](../projetos/StoCFL/diagrama-atividades-stocfl.md) | Antes de `S1`, o passo "aplicar disponibilidade" e o sorteio de `num_per_round` entre os disponíveis, com a saída da rodada vazia que pula o treino. Conferir a sintaxe Mermaid depois de editar. |
| [diagrama-sequencia-stocfl.md](../projetos/StoCFL/diagrama-sequencia-stocfl.md) | Uma mensagem `S->>S: availability.step()` antes do sorteio. Conferir a sintaxe. |
| [README do StoCFL](../projetos/StoCFL/README.md) | Exemplo de comando com `--drop` e a seção de testes com o notebook novo |
| [README de docs/](README.md) | Já aponta para este plano |
| [decisoes.md](decisoes.md) | Uma entrada para cada decisão nova durante a implementação |

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
| T3 | Nenhum cliente fica fora mais que `L_max` rodadas seguidas, há pelo menos uma rodada disponível entre duas ausências, e as durações observadas cobrem `1..L_max` |
| T4 | A disponibilidade média, em 200 clientes e 2.000 rodadas, fica a 0,01 de `1/(1 + d·ℓ)` |
| T5 | Valores inválidos (`drop < 0` ou `≥ 1`, `rounds < 1`) levantam `ValueError` |

**Integração (execuções pequenas, na configuração do baseline):**

| # | Verifica | Como |
|---|---|---|
| I1 | Regressão: `--drop 0` não muda nada | `cluster.pkl`, `psi.pkl` e as linhas `client id this round` iguais às do baseline |
| I2 | O sorteio respeita a disponibilidade | com `--drop 0.3 --drop_rounds 3`, nenhum participante aparece em `unavailable` na mesma rodada, e o nº de participantes é `min(m, disponíveis)` |
| I3 | Invariante 5 e cobertura | em todas as rodadas, todo membro de cluster com mais de um cliente está em `psi.pkl`, e as chaves de `psi.pkl` são exatamente a união dos participantes |
| I4 | Rodada vazia | com `--drop 0.99 --drop_rounds 10 --train 1`, o script termina, e `cluster.pkl` e `accuracy.pkl` têm uma entrada por rodada |
| I5 | O notebook lê as execuções novas | a cobertura calculada pelo notebook bate com as chaves de `psi.pkl` |

## 9. Cuidados

- **Alterações que não são deste plano:** `docs/clusterizacao-ao-longo-do-tempo.ipynb`, `projetos/StoCFL/teste-fracao-clientes.ipynb`, `projetos/StoCFL/teste-fracao-clientes copy.ipynb` e `mimic_codes/` estão sem commit e **não** fazem parte desta branch. Adicione arquivos ao commit por nome.
- **Licença:** `mimic_codes/` não tem arquivo de licença. O processo da seção 5 é novo e foi escrito a partir do artigo, sem copiar o código do MimiC.
- **Várias seeds:** sem pareamento (seção 2), uma só seed não separa o efeito do `drop` do ruído do sorteio. Cada seed gera uma nova partição dos dados (~750 MB), então planeje o disco. Os valores sugeridos para a grade, a confirmar na tarefa do relatório: `m` = 100%, 50% e 10%, `d` = 0,1 e 0,2, `L_max` = 10, `n = 240`, 50 rodadas, `τ = 0,9`, comparando com execuções sem `drop` da mesma seed.
- **Três cópias do servidor:** ao replicar nos outros scripts, aplicar o mesmo bloco da seção 5.3 e as mesmas flags. O módulo `availability.py` é único. Até lá, o guia (4.2) documenta que só o `StoCFL-FCC+CFL.py` tem `--drop`, como já acontece com o `--k` (D-029).
- **Disco:** cada execução grava `psi.pkl` (~1,6 GB com 240 clientes) a cada rodada, e cada combinação de parâmetros repete esse custo.
- **Início da execução:** todos começam disponíveis, então as primeiras rodadas têm disponibilidade acima de `a`.
- **Participação desigual:** quem tem ausências longas participa menos, e isso afeta quem contribui para `gmodel` e para os modelos de cluster quando se roda com `--train 1`. Esse efeito não foi medido.
