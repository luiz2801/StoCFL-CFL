# 9. Experimentos

> **Status:** proposta, nenhum experimento com rede neural foi rodado. Só existe o [toy do anexo A](anexo-a-simulacao.md). Atende, se aprovado, ao problema 9 da [especificação](../especificacao-isodata-fl.md) ("motivação sem evidência").
>
> **Futuro módulo:** `experimentos/` e `isodata_fl/dados.py`. **Depende de:** [roteiro](10-roteiro.md). **Decisões:** DP-19.

## 9.1 Hipóteses

Cada hipótese tem um critério que pode refutá-la. Resultado negativo é resultado e deve ser registrado.

| # | Hipótese | Refutada se | O toy indica |
|---|---|---|---|
| H1 | Em dados reais, existe `τ` que separa os grupos pelo `ψ`, e `ψ` concorda com o CFL | Em nenhum cenário há vão entre cossenos intra e intergrupo | Não testável no toy |
| H2 | Sem guardas, um merge por `ψ` desfaz splits corretos em qualquer calendário | Com dados reais, o híbrido sem guardas não oscila em nenhum `τ` razoável | Confirmada no cenário B |
| H3 | Com as guardas, o híbrido não é pior que o melhor baseline em nenhum cenário, e é melhor que cada algoritmo sozinho onde ele falha | Perde para o melhor baseline por mais de 1 ponto de acurácia em algum cenário | Confirmada na partição; na perda média perde para o StoCFL quando `ψ` é bom |
| H4 | O calendário de primos não piora a partição em relação a "toda rodada", com menos testes | ARI menor em mais de 0,05, ou partição correta mais de 25% mais tarde | Confirmada: mesmo ARI, 14% mais tarde, 4,3 vezes menos testes |
| H5 | **Os primos têm alguma vantagem sobre um período fixo** | Sem diferença significativa em nenhuma métrica. **Nesse caso, prefere-se o período fixo, se for mais simples de explicar** | Empate; sem evidência a favor |
| H6 | A partida por `ψ` converge mais cedo que a partida única, sem piorar a partição final | Partição final pior com `τ` calibrado | Confirmada |
| H7 | Com a média corrigida, a participação parcial mantém a partição correta | ARI menor em mais de 0,05 com 20% de participação | Confirmada até 10%. Sem a correção, falha já em 20% |

## 9.2 Cenários

Todos, exceto o FEMNIST, têm ground truth, necessário para calcular o ARI.

| # | Cenário | `N`, `K` | Modelo | O que exercita | Origem |
|---|---|---|---|---|---|
| C0 | Toy quadrático | 24, 1 a 12 | Nenhum | Dinâmica | [Anexo A](anexo-a-simulacao.md) |
| C1 | Homogêneo: MNIST IID | 20, 1 | `SimpleLinear` | Não deve dividir | Novo |
| C2 | Rotação 180° | 10, 2 | `ConvNet` | Reprodução do notebook | CFL, célula 5 |
| C3 | Rotated MNIST | 100, 4 | `SimpleLinear` | Splits em cascata, id de filhos | `RotatedMNIST` |
| C4 | C2 e C3 com `ε2` baixo | Iguais | Iguais | **Sobredivisão: é onde o merge é necessário** | Sugestão da [arquitetura anterior](../arquitetura-componentes-isodata-fl.md) |
| C5 | Shifted MNIST | 100, 4 | `SimpleLinear` | Incongruência forte em `P(y\|x)` | `ShiftedMNISTPartitioner` |
| C6 | Rotação × patologia | 400, 8 | `SimpleLinear` | Hierarquia, merge entre ramos, `τ` | Ablação do StoCFL (guia 4.15.6) |
| C7 | Patológico | 400, 4 | `SimpleLinear` | Modelo global é necessário? | Tabela 4 do StoCFL |
| C8 | Rotated CIFAR-10 | 200, 2 | `CNN_CIFAR10` | Rede convolucional, dificuldade maior | StoCFL (guia 4.17) |
| C9 | FEMNIST | 3.597, ? | `CNN_FEMNIST` | Dados reais, sem ground truth | StoCFL (guia 4.12, item 5) |

O cenário original do CFL (2 grupos) **não exercita o merge**, como a arquitetura anterior já registrava. Por isso, C4 é obrigatório.

## 9.3 Métricas

| Métrica | Mede | Observação |
|---|---|---|
| ARI e NMI contra o ground truth | Qualidade da partição | O artigo do StoCFL não usa nenhuma das duas (guia 4.15.8) |
| Acurácia de teste por cliente: média e 10º percentil | Utilidade do modelo, e quem sai perdendo | Com teste separado da validação |
| Área sob a curva de acurácia | Velocidade | Separa a partida por `ψ` da partida única |
| Rodada em que a partição correta é atingida | Atraso do calendário | |
| **M desfaz S** e **S desfaz M** | Oscilação | Principal métrica de estabilidade |
| Número de operações e de testes de fusão | Custo de decisão | |
| Censos | Custo de participação | |
| Modelos transferidos e épocas de cliente | Custo de comunicação e computação | Comparável entre métodos |
| Falsos splits em C1 | Sensibilidade do critério | |
| Recusas de `γ_max` com `ε` satisfeitos | Falha silenciosa | Alarme, ver [split](03-split-cfl.md) |

## 9.4 Baselines

| Baseline | Implementação | Função |
|---|---|---|
| FedAvg | Sem operadores | Limite inferior |
| **Oráculo** | Partição verdadeira desde a rodada 1 | Limite superior |
| CFL | Só split, com a configuração do notebook e a correção do bug 3.7 #1 | Comparação direta |
| StoCFL (só agrupamento) | Só merge, partida de clientes isolados, `μ = 0` | Comparação direta |
| ISODATA puro em `ψ` | ISODATA clássico sobre os vetores `ψ` | A leitura literal de "ISODATA como base" |

IFCA, FedAC e outros métodos da literatura ficam de fora: não existem no repositório e implementá-los é um projeto à parte (guia 4.15.6).

## 9.5 Experimentos

Em ordem. Cada um depende das conclusões do anterior.

| # | Pergunta | Configuração | Decide |
|---|---|---|---|
| **E0** | `ψ` e `ΔW` concordam em dados reais? Qual a janela de `γ_max`? | CFL baseline em C1 a C5, gravando as matrizes de cosseno de `ψ` e `ΔW` e `α_cross^max` em cada primo. `ψ` com `obep` de 1, 5, 10 e 20 | H1. Valores de `τ`, `γ_max` e `obep`. **Se `ψ` não separa nada, o papel do StoCFL precisa ser revisto antes de continuar** |
| **E1** | Quanto valem os baselines? | Todos os baselines em C1 a C5 | Referência para tudo |
| **E2** | Há oscilação em dados reais? | Híbrido sem guardas × calendários, em C3 e C4, com `τ` certo e errado | H2. Quais guardas são necessárias de fato |
| **E3** | Quais guardas pagam o custo? O merge faz falta? | Ablação da pilha em C1 a C4, incluindo CFL com `γ_max` sem merge; *single* × *complete* | Pilha final, e se o StoCFL se paga |
| **E4** | Como verificar um merge? | Ganho de fusão × perda cruzada × `α_cross` em `θ_m` × distância relativa; regras de modelo; `δ` em {0, 1, 2, 3} erros padrão; base da espera em {5, 10, 20, 40} | Verificação, regra do modelo, `δ` e espera. Mede também o erro padrão de `ΔL` contra o ganho de um split verdadeiro |
| **E5** | Quem deve agir primeiro? | Partida única × `ψ`, com e sem caminho de cluster pequeno, com `τ` certo, baixo e alto | H6 e DP-01 |
| **E6** | Qual calendário? | Com a pilha final: primos + pares, primos + interprimos, paridade, período fixo, evento, fases; parada do split em {50, 70, 90, 100}%; `t_min` em {7, 11, 23}; `p` em {1, 2, 3, 5}; estimativa de `K` por cima, se houver; `ε` automático; sem `ε2` | H4 e H5. Decide se a regra dos primos fica |
| **E7** | O modelo global ajuda? | `μ` em {0; 0,05; 1; 10} em C7 e C6 | Inclusão do modelo global |
| **E8** | E com participação parcial? | M1, M2, M3 com `frac` em {1; 0,5; 0,2; 0,1}, com e sem a média corrigida; se `ψ` real basta para os pendentes; reatribuição seletiva e completa | H7. Modos suportados |
| **E9** | Comparação final | Melhor configuração contra todos os baselines em C1 a C9, 5 sementes | H3 e o resultado |

## 9.6 Protocolo

- **Sementes:** 0, 42, 1998, 4421380 e 789190, a lista sugerida em um comentário do StoCFL (guia 4.16). Triagem com 1 semente; decisão com 5.
- **Comparações pareadas:** mesma semente, mesma partição de dados, mesma inicialização.
- **Calibração separada:** `ε`, `τ` e `γ_max` calibrados em uma semente, e essa semente não entra na comparação final.
- **Reportar:** média e desvio padrão, com a configuração gravada junto do resultado.
- **Fatorial reduzido:** o [toy](anexo-a-simulacao.md) serve de triagem barata, e as dimensões são exploradas em sequência (E2 fixa as guardas candidatas, E6 fixa o calendário). Um fatorial completo teria centenas de execuções e não é necessário.
- **Tempo de execução:** ainda não medido. A Fase 3 deve medir o custo de uma rodada para que o orçamento dos experimentos seja realista.

## 9.7 O que o toy já responde e o que não responde

| Responde (no modelo quadrático) | Não responde |
|---|---|
| O calendário não impede a oscilação | Acurácia em redes reais |
| Nenhuma guarda sozinha cobre os dois sentidos | Se `ψ` separa grupos em dados reais |
| Dois candidatos a métrica de merge são degenerados | Barreira de perda na média de modelos |
| `γ_max` tem falha silenciosa | Valores de `τ`, `γ_max`, `ε` em redes reais |
| Falsos splits se concentram no cruzamento de `ε1` | Se `ψ` real basta para colocar clientes pendentes |
| `W_merge` atrapalha, e parar os splits antes do fim ajuda | O benefício do modelo global |
| O critério do CFL não dispara com amostra, e a média corrigida resolve | Erro padrão real de `ΔL`, e se o ganho verdadeiro fica acima dele |

## 9.8 Critérios para parar

| Situação | Ação |
|---|---|
| E0 mostra que `ψ` não separa em nenhum cenário | Revisar o papel do StoCFL: merge só por perda, com `ψ` só para clientes novos |
| E2 mostra que não há oscilação com `τ` calibrado | Simplificar a pilha. Manter só o que E3 justificar |
| E3 mostra que o merge fica ocioso com `γ_max` calibrado | Considerar a versão só com split, e deixar o merge como opção. É o P-CON-5 de [01](01-conceito-e-mapeamento.md) |
| E9 mostra que o híbrido não supera o melhor baseline em nada | Registrar como resultado negativo, e manter o melhor baseline como recomendação |
| E6 mostra que os primos não têm vantagem sobre o período fixo | Escolher o calendário mais simples e registrar a decisão como substituição da hipótese original |
