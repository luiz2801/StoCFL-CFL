# Hipótese: dividir com o CFL os clusters encadeados pelo StoCFL

> **Situação:** hipótese em análise, **sem implementação**. Escrita em 2026-11-12 ([D-057](decisoes.md)). Os números da seção 6 foram medidos nos `Ψ` já guardados nos JSONs do StoCFL, com o simulador da fusão validado na [D-046](decisoes.md), sem treinar e sem rodar o script. Fatos medidos estão separados de hipóteses. As escolhas de design estão em aberto (seção 9) e serão perguntadas antes de qualquer implementação.

Neste documento, **CFL** é o algoritmo de Sattler et al. ([guia](guia.md), seção 3). O "CFL" do nome `StoCFL-FCC+CFL.py` é outra coisa: o treino bi-nível do próprio StoCFL (Bi-CFL, guia 4.15.3).

## 1. Resumo

- **A ideia.** Começar com os clientes separados e agrupar com o StoCFL. Quando um cluster tiver membros incompatíveis entre si (por exemplo, A~B e B~C, mas A≁C), aplicar o CFL nesse cluster para dividi-lo e depois continuar o StoCFL.
- **O problema existe e é grande nos dados do repositório.** No regime do cluster gigante (Dirichlet, `τ = 0.8`, `m = 100%`), o maior cluster tem em média 192 dos 240 clientes, 97% dos pares de membros têm cosseno ≤ `τ` e **metade dos pares tem cosseno negativo**. A causa medida é a transitividade da fusão dentro da rodada (*single linkage*). A atração pelo centro existe (seção 3.3), mas só ~1% das fusões medidas dependeram só dela. Nesse regime, o ganho dos modelos de cluster sobre o global cai de +1,3 a +1,6 ponto para +0,2 ponto ([D-055](decisoes.md)).
- **A divisão sobre o `Ψ` funciona onde o erro é claro e falha no resto.** Simulada sem treino (seção 6), a bipartição do CFL sobre os cossenos entre os `Ψ` corrige o encadeamento quando `τ` está abaixo da janela (Rotated MNIST com `k = 8`: borda inferior de 0.46 para ≤ 0.30). Mas há três problemas:
  - **Oscilação:** sem memória, 96–97% das divisões são desfeitas pelo próprio StoCFL nas rodadas seguintes.
  - **Divisões erradas:** com o gatilho literal ("algum par ≤ `τ`"), ela também divide clusters corretos (em `k = 4` e `τ = 0.9`, o ARI cai de 1,0 para 0,07) e, no Dirichlet, deixa de 70 a 138 dos 240 clientes sozinhos.
  - **Bloqueio:** com a aceitação do próprio CFL (`γ_max = 0.5`), ela não age em `k = 16` nem no Dirichlet.
- **Na versão estática, dividir equivale a trocar a regra de fusão.** O servidor já guarda o `Ψ` de todo cliente observado, então a mesma checagem pode ser feita **antes** da fusão. Fundir por *complete linkage* dá as mesmas janelas de `τ` que a divisão com memória, sem nenhuma divisão. Recalcular o centro depois de cada fusão desfaz o gigante (ARI contra o gabarito de 0,03 para 0,41), com bem menos singletons que a divisão (42 contra 105).
- **A versão que traz informação nova é a dinâmica:** o CFL completo, que treina o modelo do cluster até perto de um ponto estacionário e divide pelo cosseno das **atualizações**. Ela mede incongruência, que o `Ψ` na âncora não mede diretamente, e ataca a limitação registrada no guia (4.12 #9: fusões irreversíveis). É plausível, mas não foi testada e depende de memória contra a refusão, da participação dos membros, de limiares do CFL calibrados e de mais rodadas.
- **Recomendação:** separar a ideia em duas hipóteses e testá-las contra baselines simples (seção 8):
  - **H1**, estática: uma mudança da regra de fusão, testável no simulador em minutos;
  - **H2**, dinâmica: a hipótese do CFL de fato, que exige treino.

## 2. A ideia

### 2.1 Descrição

O StoCFL começa com cada cliente num cluster e funde clusters cujos centros têm cosseno acima de `τ`. As fusões nunca se desfazem. Com três clientes A, B e C, em que A e B são parecidos, B e C são parecidos e A e C não são, o StoCFL pode juntar os três de duas formas:

- na mesma rodada, pela cadeia A–B–C;
- em rodadas diferentes, porque o centro de {A, B} fica parecido com C mesmo que A sozinho não fique.

A proposta é aplicar o CFL de Sattler, que é divisivo, nos clusters em que existe essa incompatibilidade de cosseno entre membros, e depois deixar o StoCFL continuar fundindo.

### 2.2 O exemplo do esboço

O esboço da proposta tem oito clientes (I a VIII):

| Etapa | Partição | O que acontece |
|---|---|---|
| 1 | {I} {II} {III} {IV} {V} {VI} {VII} {VIII} | Início do StoCFL: um cluster por cliente. |
| 2 | {I, II} {III, IV} {V, VI} {VII, VIII} | O StoCFL funde os pares com cosseno > `τ`. |
| 3 | {I, II, III, IV} {V, VI, VII, VIII} | O StoCFL funde os pares de clusters cujos centros passam de `τ`, mesmo que, por exemplo, I e IV sejam incompatíveis. |
| 4 | {I} {II, III} {IV} e {V, VI} {VII, VIII} | O CFL divide os dois clusters, recursivamente, nos pontos de menor similaridade (as linhas tracejadas do esboço). O corte não precisa respeitar o histórico de fusões: I sai de perto de II, com quem tinha sido fundido na etapa 2. |
| 5 | {V, VI, I} {II, III} {IV} {VII, VIII} | O StoCFL continua: I se funde com {V, VI}. |

Duas consequências do exemplo orientam o resto do documento:

- a etapa 4 corta onde o cosseno entre membros é menor, e não onde a fusão aconteceu;
- a etapa 5 só é estável se as partes criadas na etapa 4 não voltarem a se fundir entre si (seção 5.2).

## 3. Por que o StoCFL encadeia

### 3.1 A regra de fusão no código

A cada rodada, o servidor faz três coisas (guia 4.1 e 4.16; `inter_cluster_union` e `unite` em [StoCFL-FCC+CFL.py](../projetos/StoCFL/StoCFL-FCC+CFL.py)):

1. calcula o centro de cada cluster sorteado, a média dos `ψ` de **todos** os membros (Eq. 2);
2. calcula **uma vez** o cosseno entre os centros;
3. percorre os pares em ordem decrescente e funde todo par com cosseno `> τ`.

O resultado de cada rodada são as componentes conexas do grafo "cosseno entre centros > `τ`" sobre os clusters sorteados. Há dois mecanismos de encadeamento.

### 3.2 Mecanismo 1: transitividade na rodada

Dentro da rodada, a fusão é *single linkage*: se A~B e B~C, os três se juntam, qualquer que seja `cos(A, C)`. Uma cadeia de vizinhos basta para unir grupos diferentes, e a cadeia pode atravessar a população inteira. Com `m = 100%`, a rodada 0 compara os 240 clientes entre si, e é aí que o cluster gigante do Dirichlet se forma (guia 4.11).

### 3.3 Mecanismo 2: o centro atrai

Entre rodadas, quem se compara são os centros. Para `ψ` unitários (o código normaliza o `Ψ`), com `s_ij = cos(ψ_i, ψ_j)`:

```text
cos(C, E) = s̄(C, E) / √(ρ_C · ρ_E)

s̄(C, E) = média de s_ij com i ∈ C e j ∈ E        (média dos cossenos entre os membros)
ρ_C     = ‖centro de C‖² = média de s_ij com i, j ∈ C, incluindo i = j
```

Para um cliente sozinho, `ρ = 1`; à medida que os membros se espalham, `ρ` cai. O cosseno entre centros é, então, a média dos cossenos entre membros **amplificada** por `1/√(ρ_C·ρ_E)`, e um cliente `e` entra em `C` pelo centro quando `s̄(C, e) > τ·√ρ_C`. Três consequências:

1. **O caso da proposta.** Com `cos(A,B) = cos(B,C) = 0,9`, `cos(A,C) = 0,7` e `τ = 0.8`: `cos({A,B}, C) = 0,8 / √0,95 = 0,821 > τ`. C entra, embora A e C não se unissem sozinhos.
2. **Pior que a proposta: nenhum par precisa passar de `τ`.** Com `τ = 0.5`, `cos(A,B) = 0,55` e `cos(A,C) = cos(B,C) = 0,49`: `cos({A,B}, C) = 0,49 / √0,775 = 0,557 > τ`. C entra no cluster sem ter cosseno acima de `τ` com nenhum membro.
3. **Efeito bola de neve.** Quanto mais espalhado o cluster, menor o limiar efetivo `τ·√ρ_C` para quem chega. No gigante do Dirichlet (`ρ = 0,095`), basta um cosseno médio de 0,25 com os membros para passar de `τ = 0.8`.

### 3.4 O que os dados mostram (resumo da seção 6)

- **O mecanismo 1 domina.** O gigante do Dirichlet é conexo no grafo "cos > `τ`" entre clientes em 18 das 20 execuções. Só 1,1% das fusões do Dirichlet e 0,4% das da rotação aconteceram sem nenhum par de membros acima de `τ`.
- **Os efeitos são os que a proposta descreve, em escala maior:** no gigante, 97% dos pares estão abaixo de `τ` e metade é negativa.

## 4. A hipótese estruturada

### 4.1 Enunciado

> **H.** Nos clusters do StoCFL cujos membros têm cosseno incompatível entre si, uma divisão no estilo do CFL, seguida da continuação do StoCFL, produz clusters mais coerentes e modelos de cluster melhores do que o StoCFL sozinho, sem fragmentar os clusters corretos.

"Aplicar o CFL" tem duas leituras, que precisam ser testadas em separado:

| | H1, estática | H2, dinâmica |
|---|---|---|
| O que se aplica do CFL | Só a bipartição (Alg. 1: *single linkage* até sobrarem 2 grupos, que minimiza o maior cosseno entre os lados) | O procedimento completo: treinar o modelo do cluster até perto de um ponto estacionário e dividir pelo cosseno das atualizações (Alg. 3 e 5, guia 3.9.4) |
| Sinal | Cosseno entre os `Ψ` dos membros, o mesmo da fusão | Cosseno entre as atualizações `ΔW` dos membros no modelo do cluster |
| Quando | A qualquer momento, inclusive na fusão | Depois que o cluster se estabiliza e o modelo dele converge |
| O que mede | Diferença entre os dados, na âncora | Incongruência: se existe um modelo bom para todos os membros (guia 3.9.1) |
| Custo | Nenhum treino; testável no simulador | Treino, rodadas a mais, limiares do CFL |

### 4.2 Peças do algoritmo e o que precisa ser escolhido

| Peça | Opções | Seção |
|---|---|---|
| Gatilho (quando checar) | algum par com cos ≤ `τ` (leitura literal); membros desconexos no grafo cos > `τ`; fração de pares ≤ `τ` acima de um limite; critério de norma do CFL (`‖média ΔW‖ < ε1` e `max ‖ΔW_i‖ > ε2`) | 5.3, 6.2 |
| Sinal da bipartição | `Ψ` (H1); `ΔW` do modelo do cluster; `ΔW` do modelo global, que cada sorteado já calcula | 4.1 |
| Bipartição | Alg. 1 do CFL, recursivo | 5.5 |
| Aceitação | a do CFL, `γ_max < √((1 − α_cross^max)/2)`; um limiar próprio; nenhuma | 5.4 |
| Depois da divisão | nada; proibir que as partes voltem a se fundir (*cannot-link*); histerese | 5.2 |
| Modelos das partes | cópia do modelo do pai (como no CFL); `ω₀`; o global | 9 |
| Membros fora da rodada | exigir todos; atribuir quando forem sorteados; atribuir pelo `Ψ` | 5.7 |

### 4.3 Esboço da versão dinâmica (H2)

```text
para cada rodada r:
    sorteia S_r e calcula o Ψ dos novos na âncora                      # StoCFL, sem mudança
    funde os clusters sorteados com cos(centros) > τ,
        exceto se a fusão juntar dois clientes com cannot-link          # StoCFL + memória
    treino bi-nível dos sorteados (modelo do cluster e global)          # StoCFL, sem mudança
    para cada cluster c com 2+ membros sorteados:
        ΔW_i = atualização do modelo do cluster feita pelo membro i
        se gatilho(c):                                                  # ex.: ‖média ΔW‖ < ε1 e max ‖ΔW_i‖ > ε2
            (c1, c2) = Alg. 1 sobre cos(ΔW_i, ΔW_j)
            se γ_max < √((1 − α_cross^max) / 2):
                divide c em c1 e c2, que herdam o modelo de c
                cannot-link entre os clientes de c1 e os de c2
                membros de c fora da rodada: decisão 7 (seção 9)
```

A versão estática (H1) é a mesma com o `Ψ` no lugar de `ΔW` e sem depender do treino, e pode ser checada logo depois de cada fusão.

## 5. Contrapontos

### 5.1 Com o mesmo `Ψ`, dividir depois é o mesmo que não fundir

O servidor guarda o `Ψ` de todo cliente observado (`self.psi`), e todo membro de um cluster fundido já foi observado (invariante 5, guia 4.5). Qualquer teste de compatibilidade entre membros que use o `Ψ` pode ser feito **antes** da fusão, com a mesma informação, e a H1 vira uma mudança da regra de fusão. A seção 6.3 mostra a equivalência na prática:

- na rotação, a divisão com o gatilho do par e com memória dá as mesmas janelas de `τ` que fundir por *complete linkage*, em 5 dos 6 pares (`k`, `m`);
- no Dirichlet, a regra de fusão fragmenta menos que a divisão (51 contra 105 singletons em `τ = 0.8`).

Isso não invalida a ideia, mas muda o que ela é. Na versão estática, o CFL só contribui com a bipartição do Alg. 1, que também é *single linkage*, a mesma família da fusão do StoCFL. O que o CFL tem de próprio é o **sinal** (as atualizações perto do ponto estacionário) e o **critério** de quando dividir (as normas), ou seja, a H2.

### 5.2 Oscilação: a regra de divisão e a de fusão se contradizem

A fusão do StoCFL compara **centros**, com a amplificação de 3.3. A divisão pelo gatilho do par exige que **todos os pares** passem de `τ`. Como o `Ψ` não muda, um cluster que passa na primeira regra e falha na segunda tende a ser refeito toda vez que é dividido. Medido (6.3):

- 96% a 97% das divisões são desfeitas;
- nas 80 execuções do Dirichlet, a divisão continua ativa nas últimas 10 rodadas;
- a partição final é a do momento em que a simulação parou.

Por isso, "continuar com o StoCFL" depois de dividir só é estável com memória. Há duas formas:

- proibir que clientes separados por uma divisão voltem a ficar juntos (*cannot-link*). Com ele o processo converge: cada divisão proíbe ao menos um par novo de clientes, e o número de pares é finito;
- usar histerese: dividir só abaixo de um limiar menor que o de fusão.

A literatura conhece o problema. O FedDAG agrupa uma vez só e registra que "oscillations due to re-clustering invalidate the descent decomposition" da sua análise. O FedAC só funde abaixo de um limiar e só divide acima de outro (seção 11).

### 5.3 O gatilho literal dispara quase sempre

"Algum par de membros com cosseno ≤ `τ`" é o mínimo de `n(n−1)/2` cossenos ruidosos, então dispara mesmo em clusters corretos:

- no Dirichlet, em 87–88% dos clusters de 3 a 5 clientes e em 100% dos maiores (6.2);
- na rotação, em todos os clusters mistos, mas também em clusters corretos perto da borda superior da janela (a partir de `τ ≈ 0.82` em `k = 4`).

O gatilho alternativo, "membros desconexos no grafo cos > `τ`", quase nunca dispara nos clusters mistos (eles são conexos pela cadeia) e quase não muda o resultado (6.3). Um gatilho útil precisa ficar entre os dois, por exemplo uma fração de pares ≤ `τ`, e precisa de calibração.

### 5.4 A aceitação do próprio CFL barra a maior parte das divisões

Se o cluster é conexo no grafo cos > `τ`, toda bipartição corta uma aresta acima de `τ`. Então o `α_cross^max` da bipartição do Alg. 1 é o **gargalo** `β` do cluster (a menor aresta da árvore geradora máxima entre os membros), e `β > τ`. A aceitação do CFL, `γ_max < √((1 − α_cross^max)/2)`, equivale a `β < 1 − 2·γ_max²`. Com o `γ_max = 0.5` do notebook do CFL (guia 3.5), só se divide com `β < 0,5`.

Nos dados, os encadeamentos têm `β` de 0,32–0,34 (`k = 4`), 0,41–0,46 (`k = 8`), 0,70–0,72 (`k = 16`) e ~0,80 (gigante do Dirichlet). Com 0.5, a aceitação deixa dividir os dois primeiros e barra os dois últimos. Baixar `γ_max` libera as divisões, inclusive as erradas (5.3).

### 5.5 A bipartição do Alg. 1 tende a isolar um cliente

O Alg. 1 minimiza o maior cosseno entre os lados e, sem um vão claro entre grupos, corta um cliente da borda (guia 3.10: com `g(α) ≤ 0`, ele tende a isolar um único cliente). No Dirichlet (`τ = 0.8`, `m = 100%`, sem memória), 65–72% das divisões isolam um cliente, e a recursão deixa ~100 dos 240 clientes sozinhos.

Isso conta contra a hipótese. Na grade com treino, os clusters de um cliente ficam iguais ou abaixo do modelo global, e o ganho vem dos clusters de 2+ clientes (+1,9 a +2,1 pontos com `α = 0.5`; [D-055](decisoes.md)).

### 5.6 Encadeamento nem sempre é erro

O que o CFL separa é **incongruência** (não existe um modelo bom para todos), e não diferença entre os dados: se as normas individuais vão a zero, os clientes são congruentes e o CFL não divide (guia 3.9.1 e 3.9.3). Duas consequências:

- **No Dirichlet do MNIST**, as classes são quase separáveis, e o que muda entre clientes é sobretudo a proporção de classes. O artigo do CFL critica o método de Ghosh et al. por dividir clientes "mesmo no non-IID clássico" (guia 3.9.10), ou seja, trata esse caso como congruente. Então a H2 pode simplesmente não dividir o gigante, e o ganho de personalização medido (+1,3 a +1,6 ponto) viria de outro efeito, ligado a capacidade e treino finitos. **Hipótese, não medida.**
- **Na rotação com `k = 16`**, grupos vizinhos (22,5°) podem ser congruentes para o modelo. Juntar dois desses grupos erra o gabarito e talvez não custe acurácia.

Por isso, o critério de sucesso da hipótese é a **acurácia** dos modelos de cluster (ponderada pela distribuição de rótulos, D-047), e não só o ARI contra o gabarito. Além disso, o termo proximal (`μ`) já atenua o dano de uma fusão ruim, porque puxa o modelo do cluster para o global (guia 4.15.3).

### 5.7 Participação parcial

O CFL supõe que **todos** os membros do cluster mandam a atualização no **mesmo** modelo (guia 3.9.9). O StoCFL sorteia `m` clientes por rodada, e, com `--drop`, alguns ficam fora várias rodadas. A bipartição feita com os sorteados não diz onde ficam os outros:

- o CFL resolve isso com a árvore de parâmetros (Alg. 4), que não está implementada ([backlog](backlog.md));
- atribuir pelo `Ψ` usa justamente o sinal que errou.

Com `m = 100%` e sem dropout o problema não existe, e esse é o cenário natural para o primeiro teste.

### 5.8 Tempo e limiares

O CFL só divide perto de um ponto estacionário. No artigo, as divisões saem nas rodadas 50, 100 e 150 (CIFAR) e 30, 60 e 90 (AG News) (guia 3.9.7). No notebook do CFL, o `EPS_1` é o menor valor testado que divide em todas as seeds dentro de 80 rodadas (D-015).

As grades do StoCFL deste repositório têm 50 rodadas, e a partição do Dirichlet estabiliza até 33 rodadas depois da cobertura total ([relatório do dropout](relatorio-dropout.md)). Sobra pouco tempo para o CFL agir.

`ε1` e `ε2` são normas absolutas, difíceis de calibrar (D-015). Um mesmo `ε1` serve mal a clusters de 2 e de 192 clientes, porque a média de poucos `ΔW` é mais ruidosa. A H2 acrescenta três hiperparâmetros (`ε1`, `ε2`, `γ_max`) aos dois do StoCFL (`τ`, `μ`).

### 5.9 Custo de manutenção

- O `StandaloneServer` existe em três cópias (guia 4.2 e 6).
- A invariante 3, "o nº de clusters nunca cresce" (guia 4.5), deixa de valer.
- O guia, os diagramas e o README dizem que os clusters nunca se dividem.

Nada disso impede a implementação, mas entra no custo (seção 10).

## 6. Verificação com os dados existentes, sem treino

### 6.1 Método

- **Dados:** a matriz de cossenos entre os `Ψ` dos 240 clientes, guardada nos JSONs:
  - Dirichlet com `α` = 0.5 e 1.0 e seeds 0 a 9 (`projetos/StoCFL/logs/resultados-varredura-tau-dirichlet.json`, 20 matrizes);
  - Rotated MNIST com `k` = 4, 8 e 16, só a seed 0 (`projetos/StoCFL/logs/resultados-fracao-clientes.json`, campo `cossenos_clientes_rodada_0`).

  Os sorteios são os do script (`random.seed(seed)`), sem dropout, com `m` = 100% e 50% e 50 rodadas.
- **Simulador:** o do [varredura-tau-dirichlet.ipynb](../projetos/StoCFL/varredura-tau-dirichlet.ipynb) (D-046), reimplementado fora do repositório. Ele reproduz, rodada a rodada:
  - as 9 execuções reais guardadas do Dirichlet;
  - 112 das 114 execuções de `n = 240` do teste de `m` e da busca de `τ`. Nas 2 restantes (`k = 8`, `τ = 0.9688`), um cosseno fica a 1,5e-5 de `τ`, o caso de precisão já descrito na D-046, e o nº final de clusters é o mesmo.
- **Variantes** (todas sobre o `Ψ`, ou seja, testam a H1):

| Rótulo | O que muda em relação ao StoCFL |
|---|---|
| E0 | Nada: o StoCFL como está. |
| D1 / D2 | Depois das fusões de cada rodada, divide pelo Alg. 1 os clusters com algum par ≤ `τ` (gatilho do par), recursivamente. D1 é sem memória; D2 tem *cannot-link* entre as partes. |
| D3 / D4 | Igual, com o gatilho da conexão (membros desconexos no grafo cos > `τ`). D3 é sem memória; D4 tem memória. |
| D5 | D2 com a aceitação do CFL, `γ_max = 0.5`. |
| F1 | Sem divisão: funde por *complete linkage* (menor cosseno entre membros > `τ`), recalculando depois de cada fusão. É "prevenir" no lugar de "dividir", para o gatilho do par. |
| F2 | Sem divisão: funde por *average linkage* (média dos cossenos entre membros > `τ`, sem a amplificação de 3.3), recalculando depois de cada fusão. |
| F3 | Sem divisão: funde pelo centro, como o StoCFL, mas recalcula depois de cada fusão, o que elimina a transitividade de 3.2. |

- **Custo:** 2.610 simulações em 34 s de CPU. Nenhum log foi gerado.

### 6.2 Anatomia do encadeamento no StoCFL (E0)

**Dirichlet:** todos os clusters de 2+ clientes da partição final, somados `α`, seeds e `m`:

| Tamanho | `τ = 0.8`: clusters / gatilho do par / gatilho da conexão / pares ≤ `τ` | `τ = 0.84683`: idem |
|---|---|---|
| 2 | 253 / 0% / 0% / 0% | 486 / 0% / 0% / 0% |
| 3 a 5 | 212 / 88% / 12% / 38% | 294 / 87% / 13% / 36% |
| 6 a 20 | 156 / 100% / 10% / 62% | 225 / 100% / 6% / 62% |
| 21 ou mais | 81 / 100% / 11% / 80% | 55 / 100% / 11% / 78% |

**O cluster gigante** (`τ = 0.8`, `m = 100%`; média de 10 seeds):

| | `α = 0.5` | `α = 1.0` |
|---|---|---|
| Tamanho | 192 | 132 |
| Pares de membros com cos ≤ `τ` | 97% | 96% |
| Pares com cos < 0 | 50% | 34% |
| Pior par, entre as seeds | −0,58 | −0,54 |
| Gargalo `β` (conexo se > 0,8) | 0,80 (conexo em 10 de 10) | 0,79 (conexo em 8 de 10) |
| `ρ` (‖centro‖²) e limiar efetivo `τ·√ρ` | 0,095 e 0,25 | 0,19 e 0,35 |

**Rotated MNIST (seed 0):**

- Clusters mistos (com mais de um grupo de rotação) só aparecem com `τ` abaixo da janela.
- Em todos eles o gatilho do par dispara. O da conexão só dispara num caso (`k = 8`, `τ = 0.42`, `m = 100%`): duas fusões só pelo centro levaram os 240 clientes a um cluster só, desconexo em > `τ` (`β = 0,411`). Nos outros, `β` vale 0,32–0,34 (`k = 4`), 0,43–0,46 (`k = 8`) e 0,70–0,72 (`k = 16`).
- O gatilho do par também dispara em clusters corretos quando `τ` passa de ~0.8:
  - `k = 4`: nos 4 grupos em `τ = 0.9`;
  - `k = 8`: em 3 de 8 grupos em `τ = 0.9` e em 8 de 8 em `τ = 0.94`;
  - `k = 16`: em 16 de 16 em `τ = 0.98`.

### 6.3 O que a divisão e as regras alternativas fazem

**Rotated MNIST:** janela de `τ` com ARI = 1, numa grade de 0.30 a 0.98 com passo 0.02 ("≤ 0.30" quer dizer no limite da grade). Os valores são os mesmos com `m` = 100% e 50%, exceto onde indicado:

| `k` | E0 StoCFL | D1/D2 gatilho do par | D3/D4 conexão | D5 par + `γ_max` 0.5 | F1 *complete* | F2 *average* | F3 centro recalculado |
|---|---|---|---|---|---|---|---|
| 4 | 0.34–0.92 | ≤ 0.30–0.80 | 0.34–0.92 | ≤ 0.30–0.92 | ≤ 0.30–0.80 | ≤ 0.30–0.88 | ≤ 0.30–0.90 |
| 8 | 0.46–0.94 | ≤ 0.30–0.88 | 0.46–0.94 | ≤ 0.30–0.94 | ≤ 0.30–0.88 (0.32 com 50%) | 0.38–0.92 | 0.40–0.94 |
| 16 | 0.74–0.96 | 0.70–0.94 | 0.74–0.96 | 0.74–0.96 | 0.70–0.94 | 0.72–0.96 | 0.74–0.96 |

- **A divisão corrige o encadeamento abaixo da janela.**
  - Em `k = 4` e `τ = 0.30`, o StoCFL junta 0° com 180° e 90° com 270° (ARI 0,50). O primeiro corte do Alg. 1 separa exatamente os grupos, e as partes não voltam a se fundir (cosseno entre os centros 0,26 < `τ`).
  - Em `k = 8` e `τ = 0.44`, acontece o mesmo com os grupos de 225° e 270°.
  - Quando tudo vira um cluster só (`k = 8`, `τ = 0.40`), o primeiro corte separa duas metades de 4 grupos cujos centros ainda passam de `τ` (0,51 > 0.40). Sem memória, elas voltam a se fundir.
- **Mas também divide clusters corretos.** D1 e D2 perdem o ARI 1 em 12 dos 60 pares (`m`, `τ`) em que o StoCFL acerta com `k = 4`, em 6 de 50 com `k = 8` e em 2 de 24 com `k = 16`, todos perto da borda superior. Em `k = 4` e `τ = 0.9`, o D1 faz 7.150 divisões e 7.007 refusões e termina com ARI 0,07.
- **Sem memória, oscila.** D1 e D3 têm 96–97% das divisões desfeitas, na rotação e no Dirichlet. D2 e D4 não oscilam.
- **Prevenir dá o mesmo que dividir.** F1 tem as mesmas janelas que D2 em 5 dos 6 pares (`k`, `m`), sem nenhuma divisão.
- **A aceitação do CFL acerta onde o vão entre grupos é grande.** D5 tem as janelas mais largas com `k` = 4 e 8: aceita os cortes entre grupos (`β < 0,5`) e rejeita os cortes dentro dos grupos (`β > 0,9`). Mas não faz nada com `k = 16`, em que a ponte entre grupos é 0,72.

**Dirichlet,** `α = 0.5`, `m = 100%`, média de 10 seeds. O ARI é contra o gabarito da D-046, que é fraco (silhueta de 0,15 a 0,26), então serve só para comparar variantes:

| Variante | `τ = 0.8`: clusters / maior / singletons / ARI | `τ = 0.84683`: idem | Observação |
|---|---|---|---|
| E0 StoCFL | 30,5 / 192 / 25 / 0,03 | 74,7 / 47 / 58 / 0,37 | |
| D1 par, sem memória | 148 / 9,5 / 102 / 0,16 | 164 / 7,8 / 119 / 0,11 | 98% das 4.924 divisões por execução desfeitas (`τ = 0.8`); ativa até o fim nas 10 seeds |
| D2 par, com memória | 150 / 9,5 / 105 / 0,16 | 166 / 7,8 / 123 / 0,11 | |
| D3 e D4 conexão | quase igual ao E0 | quase igual ao E0 | o gigante é conexo |
| D5 par + `γ_max` 0.5 | igual ao E0 | igual ao E0 | todas as divisões rejeitadas (`β` ≈ 0,8) |
| F1 *complete* | 117 / 8,9 / 51 / 0,17 | 143 / 8,0 / 84 / 0,13 | |
| F2 *average* | 100 / 14,4 / 48 / 0,29 | 131 / 11,4 / 82 / 0,20 | |
| F3 centro recalculado | 79 / 20 / 42 / 0,41 | 113 / 17,6 / 77 / 0,32 | |

- **Com `α = 1.0`, o padrão é o mesmo.** Em `τ = 0.8` e `m = 100%`: E0 tem 52 clusters, o maior com 132 e ARI 0,06; D2 tem 165, 6,1 e 0,16; F3 tem 102, 19 e 0,31.
- **Com `m = 50%` não há gigante,** e o E0 já fica perto do F3 (`α = 0.5`, `τ = 0.8`: ARI 0,40 contra 0,42; D2 0,17).

### 6.4 Leitura

- **Confirmado:** o encadeamento existe, é sobretudo transitivo e junta clientes com cosseno negativo. A bipartição do CFL sobre o `Ψ` acha o corte certo quando há um vão entre grupos.
- **Contra a versão estática como proposta:**
  - sem memória, ela oscila;
  - com o gatilho literal, ela divide clusters corretos e fragmenta o Dirichlet;
  - com a aceitação do CFL, ela não age onde o encadeamento é mais forte;
  - uma regra de fusão diferente faz o mesmo ou melhor, sem dividir. No Dirichlet, a regra que melhor desfaz o gigante (F3) não divide nada: só recalcula o centro depois de cada fusão.
- **Não testado:** a H2 e o efeito de qualquer variante na acurácia.

## 7. Limitações

- A verificação usa só o `Ψ`, que é fixo. Ela não diz nada sobre a H2, que usa o `ΔW`, nem sobre a acurácia.
- **Rotação:** uma seed (só a seed 0 tem a matriz guardada, D-040) e `n = 240`. As janelas valem até o vizinho da grade (passo 0.02, a partir de 0.30).
- **Dirichlet:** o gabarito é fraco (D-046, D-050). O ARI serve para comparar variantes entre si, não como verdade.
- Sem dropout nas simulações.
- As variantes são uma implementação possível de cada ideia:
  - a divisão é checada só nos clusters que mudaram na rodada (com o `Ψ` fixo, os outros não mudam);
  - o *cannot-link* é entre clientes;
  - a recursão vai até o gatilho parar de disparar.
- O script da análise não foi versionado (mesmo critério da D-013). O método está em 6.1, e o simulador de base é o do notebook versionado.
- A busca de trabalhos relacionados (seção 11) foi rápida, não uma revisão.

## 8. Como testar

**Fase 1, sem treino (H1 e calibração).** No simulador, sobre os `Ψ`:

1. Rodar mais seeds de rotação. Isso exige calcular o `Ψ`: uma rodada com `m = 100%` por seed e `k`, com ~1 min e ~1,5 GB de `psi.pkl` cada, apagado depois e com o JSON da política 7.
2. Comparar E0, F2, F3 e a melhor divisão com memória numa grade de `τ`, também com dropout, e escolher a regra de fusão e o gatilho.
3. Se F2 ou F3 resolverem o encadeamento estático, a H1 vira uma mudança da regra de fusão, mais simples que dividir.

**Fase 2, com treino (H2).** Implementação atrás de uma flag desligada por padrão no `StoCFL-FCC+CFL.py` (seção 10). O primeiro teste usa `m = 100%` e nenhum dropout (5.7).

| Cenário | Por quê |
|---|---|
| Rotated MNIST, `k = 16`, `τ = 0.70` | Encadeamento conhecido, com gabarito, onde a aceitação do CFL com `γ_max = 0.5` barraria a versão estática. |
| Dirichlet, `α = 0.5`, `τ = 0.8`, `m = 100%` | O gigante, com o ganho de personalização perdido (+0,2 ponto contra +1,3 a +1,6). |
| Rotated MNIST, `k = 8`, `τ = 0.75` | Controle: `τ` no meio da janela, nada a corrigir. A H2 não deveria dividir nada. |

- **Baselines:**
  - o E0;
  - o StoCFL com a regra de fusão escolhida na fase 1;
  - o StoCFL com o `τ` bem escolhido (0.84683 no Dirichlet);
  - o CFL de Sattler sozinho, se for viável.
- **Métricas:** as da grade com treino (D-047): acurácia do cluster ponderada pela distribuição de rótulos e ganho sobre o global, separados entre singletons e clusters de 2+. Também o ARI (rotação), o nº de divisões, de refusões bloqueadas e de singletons, e a rodada estável.
- **Rodadas:** mais de 50 (5.8).
- **Seeds:** 10, com Wilcoxon pareado por seed, como nas grades anteriores.
- **Critério de sucesso:** ganho de acurácia sobre o E0 e sobre a melhor regra de fusão, sem perda no cenário de controle.

## 9. Decisões em aberto

Pela política 4 do `CLAUDE.md`, cada item é perguntado antes da implementação e registrado em [decisoes.md](decisoes.md). As recomendações abaixo são só a leitura deste documento.

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| 1 | Qual hipótese seguir | H1, H2 ou as duas | As duas, separadas: H1 como regra de fusão (fase 1) e H2 como a hipótese do CFL (fase 2). |
| 2 | Sinal da divisão (H2) | `ΔW` do modelo do cluster; `ΔW` do modelo global, já calculado por todo sorteado; `Ψ` | `ΔW` do modelo do cluster, que é o sinal do CFL. |
| 3 | Gatilho | do par; da conexão; fração de pares ≤ `τ`; critério de norma do CFL; combinação | Critério de norma do CFL na H2. Os gatilhos sobre o `Ψ` disparam demais ou de menos (5.3). |
| 4 | Aceitação | `γ_max` do CFL (com qual valor); limiar próprio; nenhuma | `γ_max` calibrado no cenário. Com o `Ψ`, 0.5 barra os encadeamentos de `k = 16` e do Dirichlet; com o `ΔW`, o valor precisa ser medido. |
| 5 | Depois da divisão | *cannot-link*; histerese; nada | *Cannot-link* entre clientes. Sem memória, 96–97% das divisões se desfazem. |
| 6 | Modelos das partes | cópia do modelo do pai; `ω₀`; global | Cópia do pai, como no CFL. |
| 7 | Membros fora da rodada | só checar clusters com todos os membros sorteados; atribuir depois pelo `ΔW`; atribuir pelo `Ψ` | Começar com `m = 100%`, sem dropout, e decidir depois. |
| 8 | Onde implementar | só no `StoCFL-FCC+CFL.py`, com flag; nos três scripts | Só no FCC+CFL, com a flag desligada por padrão (precedente do `--drop`, D-032). |
| 9 | Nome da variante | — | Evitar "CFL" sozinho, que já aparece no nome do script para o treino bi-nível. |

## 10. O que mudaria no código e na documentação

Se a H2 for implementada:

- **Código** ([StoCFL-FCC+CFL.py](../projetos/StoCFL/StoCFL-FCC+CFL.py)):
  - um passo de divisão depois do treino, em `main`;
  - a matriz de *cannot-link*, consultada em `inter_cluster_union` e `unite`;
  - a guarda dos `ΔW` dos membros (hoje os modelos treinados são agregados e descartados na mesma rodada);
  - a cópia do modelo do pai para as partes, em `cluster_parameters`;
  - um registro das divisões nos logs.
- **Invariantes** (guia 4.5):
  - a 1 continua possível: a parte sem o id do pai recebe o menor id dos seus membros, que está livre porque aquele cliente foi absorvido antes;
  - a 3 deixa de valer;
  - a 5 continua, porque a divisão só separa clientes já observados.
- **Documentação:** o guia (4.1, 4.4, 4.5, 4.12 #9 e a seção 5), os diagramas de atividades e de sequência do StoCFL e os READMEs, que hoje dizem que os clusters nunca se dividem.

## 11. Trabalhos relacionados

Busca rápida em 2026-11-12, com leitura dos artigos no arXiv. Nenhum deles combina a fusão estocástica pelo `Ψ` do StoCFL com a divisão do CFL no ponto estacionário, mas a busca não foi uma revisão.

- **FedDAG** (Pramanik, Kantarcioglu, Oria e Sharma, [arXiv:2602.23504](https://arxiv.org/abs/2602.23504), aceito no ICLR 2026 segundo o arXiv) descreve a mesma lacuna desta hipótese: o CFL de Sattler "cannot merge clusters when needed", e Zeng et al. "supports merging clusters but not splitting them". O próprio FedDAG agrupa uma só vez, por clusterização hierárquica com limiar.
- **FedAC** (Zhang et al., [arXiv:2403.16460](https://arxiv.org/abs/2403.16460), 2024): a cada rodada, calcula a razão entre a distância intra e entre clusters, `G`. Funde se `G < a` e divide em dois se `G > b`, com `(a, b) = (0.2, 0.8)`. A faixa entre `a` e `b` funciona como histerese; a leitura é nossa, o artigo não usa o termo.
- **SOFA-FL** (Ni, Wang e Zhang, [arXiv:2512.08267](https://arxiv.org/abs/2512.08267), 2025): funde clusters abaixo de um limiar de distância e divide com K-Means, aceitando a divisão só se todos os subclusters passarem num limiar de incoerência. Não cita o CFL nem o StoCFL.
- **FL+HC** (Briggs, Fan e Andras, [arXiv:2004.11791](https://arxiv.org/abs/2004.11791), IJCNN 2020): clusterização hierárquica aglomerativa das atualizações locais.

## 12. Referências internas

- [Guia técnico](guia.md):
  - CFL em 3.1, 3.9 (teoria, critérios, Alg. 1 e aceitação) e 3.10;
  - StoCFL em 4.1, 4.5 (invariantes), 4.11 (grades e o gigante), 4.12 #9 e 4.16;
  - comparação na seção 5.
- [Relatório de m, k e τ](relatorio-m-k-tau.md): a janela de `τ` e a cadeia entre clientes.
- [Relatório do dropout](relatorio-dropout.md) e D-055: o ganho dos clusters de 2+ e dos singletons.
- Decisões ([decisoes.md](decisoes.md)): D-014 (o código segue os artigos), D-015 (limiares do CFL), D-046 (simulador da fusão) e D-057 (este documento).
