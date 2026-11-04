# 7. Modelos e estado

> **Status:** proposta, nada implementado. Resolve, se aprovado, o problema 7 da [especificação](../especificacao-isodata-fl.md).
>
> **Futuro módulo:** `isodata_fl/estado.py`. **Depende de:** nada. **Decisões:** DP-07, DP-13, DP-15.

## 7.1 Estado do servidor

| Estrutura | Conteúdo | Origem |
|---|---|---|
| `membros: dict[int, list[int]]` | `id do cluster → clientes` | `find_cluster_content` do StoCFL |
| `cluster_de: list[int]` | `cliente → id do cluster` | `find_client_cluster` do StoCFL |
| `modelo: dict[int, Tensor]` | `id do cluster → θ` como vetor 1-D | `cluster_parameters` do StoCFL |
| `ancora: Tensor` | `θ0`, nunca muda | `anchor` do StoCFL |
| `psi: dict[int, Tensor]` | `cliente → ψ`, imutável | `psi` do StoCFL |
| `nascimento: dict[int, int]` | Rodada de criação do cluster, para a idade | Novo |
| `abaixo: dict[int, int]` | Rodadas seguidas com `mean_norm < ε1` | Novo |
| `nao_unir`, `nao_separar` | Rodada até a qual cada par de clientes está bloqueado | Novo |
| `historico` | Nós do grafo de splits e merges, com a evidência de cada um | Substitui `model_cache` e a árvore do artigo do CFL |

Modelos são **vetores 1-D**, como no StoCFL. O CFL mantém um modelo vivo por cliente (`Client.W`), o que custa `N` modelos em memória e obriga a cuidar das referências vivas (guia, seção 6). Treinar é carregar o vetor em um único `nn.Module`.

## 7.2 Identificadores e invariantes do StoCFL

A especificação (problema 7) aponta que o split quebra as invariantes do guia 4.5. A verificação mostra que quase todas sobrevivem:

| Invariante (guia 4.5) | Com split? | O que fazer |
|---|---|---|
| 1. O id do cluster é o menor id de cliente membro | **Mantida** | O filho com o menor id herda o id do pai. O outro recebe o menor id dos seus membros: esse id está livre porque um cluster vivo `k` sempre contém o cliente `k` |
| 2. A soma dos tamanhos é `client_num` | **Mantida** | Conferir depois de cada operação |
| 3. O número de clusters é não crescente | **Abandonada** | É a única que precisa cair. Nada no merge depende dela |
| 4. `psi[i]` é calculado uma vez, da mesma âncora | **Mantida** | É justamente a causa do problema de [estabilidade](05-estabilidade.md) |

O teste `i not in find_cluster_content[i]` de `unite` continua válido, porque depende só da invariante 1. Na reimplementação ele nem precisa existir: com a regra "cada cluster se funde uma vez por janela", não há fusão transitiva para redirecionar.

## 7.3 Modelo depois de um split

Cada filho parte do modelo do pai e recebe a média das atualizações **dos seus próprios membros** nesta rodada, como faz o CFL (split antes da agregação). Nenhum `±1` é necessário, porque os filhos divergem pelo treino.

## 7.4 Modelo depois de um merge

| Regra | Origem | A favor | Contra | Sugestão |
|---|---|---|---|---|
| **Média ponderada pelo número de membros** | ISODATA (artigo, `ISODATAKit.py:147`), FedDrift | Equivale a uma rodada de FedAvg e é "o verdadeiro ponto médio do subconjunto combinado", nas palavras do artigo | Em redes não convexas, a média pode cair em uma barreira de perda | **Padrão**, porque o ganho de fusão testa exatamente este modelo antes de adotá-lo |
| **O modelo do maior vence** | `unite` do StoCFL | Não há barreira, e é barato | Joga fora o treino do menor. No código nem é sempre o maior: se `j` não tem modelo, `i` mantém o seu (guia 4.16) | **Testar** em E4, como segundo candidato ao teste de ganho |
| **O melhor na validação da união** | Novo | É o mais seguro | Mais um download por cliente testado | **Testar** em E4 |
| **Voltar ao modelo do ancestral comum** | Cache do CFL | Modelo já validado | Perde o treino desde o split | **Descartar**, salvo como último recurso se tudo falhar no teste |

**Por que a média é razoável só aqui.** Frankle et al. mostram que redes treinadas a partir do mesmo ponto, depois de estáveis ao ruído de SGD, ficam em uma mesma região sem barreira na reta entre elas ([anexo B](anexo-b-literatura.md)). Dois clusters que merecem fundir têm dados de mesma distribuição e um ancestral comum, que é o caso favorável. O resultado não vale para distribuições diferentes, e é por isso que a média **só é adotada depois do teste**.

## 7.5 Modelo global e termo proximal do StoCFL

**Proposta: fora da v1** (`μ = 0`), por quatro motivos:

1. **Muda o significado de `ΔW`.** Com o termo proximal, o ponto estacionário do cluster não é mais o da sua própria perda, e `mean_norm`/`max_norm` passam a medir também a tração em direção ao global. Os limiares do CFL perdem a interpretação.
2. **Dobra o custo.** Cada cliente sorteado treina duas vezes por rodada (guia 4.12, item 11).
3. **Não é necessário na partida única.** O primeiro split guarda o modelo FL no histórico, que é o que o CFL oferece como referência.
4. **Divergência entre o guia e o código.** O guia dizia que o `gmodel` do código é FedAvg. **Não é:** nos cinco trainers, o segundo laço de `train` reatribui `gmodel` e cada cliente parte do resultado do anterior ([`trainer.py:273`](../../../projetos/StoCFL/trainer.py#L273)), o que é treino sequencial. O [diagrama de atividades do StoCFL](../../../projetos/StoCFL/diagrama-atividades-stocfl.md) já registrava isso. O guia foi corrigido nesta tarefa (4.1, 4.12 e 4.16).

**Quando reconsiderar:** no cenário patológico de rótulos, a Tabela 4 do artigo mostra acurácia de 24–38% com `λ ≤ 0,05`, contra 89% com `λ = 10` (guia 4.15.6). Se o híbrido dividir por rótulo, cada cluster perde classes e o modelo global volta a ser necessário. Experimento E7. Nesse caso, a rodada de split pode treinar com `μ = 0`, para que `ΔW` mantenha o significado.

## 7.6 Otimizador

| Item | CFL (notebook) | StoCFL (scripts) | Proposta |
|---|---|---|---|
| Momentum | 0,9, com buffer por cliente que persiste entre rodadas, mesmo depois de `reset()` (guia 3.10) | Nenhum | **Nenhum** na v1. O buffer antigo aponta para o ótimo do cluster anterior e contamina `ΔW` depois de um split ou merge. Além disso, cliente parcial não guarda estado |
| Decaimento de lr | ×0,99 a cada chamada (`fl_devices.py:108`) | Nenhum | Desligado, e configurável para reproduzir o notebook. O decaimento reduz as normas com o tempo e altera o efeito de `ε1` e `ε2` (guia 3.5) |
| Peso na agregação | Uniforme | Uniforme | Uniforme na v1. Ponderar por `|D_i|` no FEMNIST, onde os tamanhos diferem (guia 4.12, item 10) |

Para reproduzir o notebook (Fase 4), os três itens precisam ser configuráveis. Os limiares `ε` calibrados em um modo não valem no outro.

## 7.7 Histórico

Cada operação gera um nó com: rodada, tipo, clusters envolvidos, membros, modelo guardado (opcional) e **a evidência** (`mean_norm`, `max_norm`, `α_cross^max`, `cos ψ`, `ΔL`).

- **Por que grafo, e não árvore:** o artigo do CFL usa uma árvore de parâmetros, mas um merge entre ramos diferentes gera um nó com dois pais. A árvore não representa isso.
- **Modelos guardados:** apenas o modelo do pai em cada split, como o `cache_model` do CFL. Isso mantém a referência "pelo menos tão bom quanto o FL".
- **Registro das recusas:** split recusado pelo `γ_max` e merge reprovado também geram registro. Sem isso, as falhas silenciosas de [P-SPL-4](03-split-cfl.md) ficam invisíveis.

## 7.8 Modelo final de cada cliente

| Opção | Sugestão | Justificativa |
|---|---|---|
| **Modelo do cluster final** | **Padrão** | Simples, e é o que o StoCFL faz |
| Melhor modelo do histórico, por cliente (CFL) | **Testar** em E9 como pós-processamento | Pode dar ganho, mas precisa de uma validação separada do teste. O notebook escolhe e reporta na mesma validação, com viés otimista (guia 3.10) |

**Regra de avaliação:** cada cliente tem treino, validação e teste separados. A validação alimenta o ganho de fusão e a escolha de modelo. Só o teste entra nas tabelas de resultado.

## 7.9 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-MOD-1 | O split quebra as invariantes do StoCFL | Tabela de 7.2: só a invariante 3 cai | Verificado no código de `unite` |
| P-MOD-2 | Média de modelos pode cair em barreira de perda | Testar o modelo antes de adotar (ganho de fusão) | O teste mede o modelo que será usado, e não uma aproximação |
| P-MOD-3 | Termo proximal altera `ΔW` | `μ = 0` na v1 | 7.5 |
| P-MOD-4 | Momentum contamina `ΔW` depois de split ou merge | Sem momentum na v1 | Guia 3.10 |
| P-MOD-5 | Memória: `ψ` e `θ` por cliente | Vetores 1-D em `float32`, um modelo por cluster e `ψ` opcionalmente comprimido | `ψ` de 1,6 M parâmetros ocupa 6,5 MB por cliente (guia 4.17) |
| P-MOD-6 | O histórico cresce sem limite | Guardar modelo só nos splits, evidência sempre | Evidência são poucos números; o custo real é o modelo |
| P-MOD-7 | Escolha de modelo com viés | Validação separada do teste | Guia 3.10 |
| P-MOD-8 | Reprodutibilidade | Semente única, geradores por componente e registro da configuração | Guia 4.9: a semente entra na partição de dados |

## 7.10 Alternativas de estrutura

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Modelos vivos por cliente (CFL)** | **Descartar** | Custa `N` modelos em memória e tem armadilhas de referência (guia, seção 6) |
| **Reaproveitar o `dict` por string de `parse_matrix`** | **Descartar** | Chaves `"a,b"` existem só para ordenar. Um arranjo de pares é mais simples |
| **Union-find com caminho comprimido** | **Descartar** | Com poucos clusters é otimização prematura, e não trata splits |

## 7.11 Critérios de aceite

- [ ] Teste de propriedade: depois de qualquer sequência aleatória de splits e merges, valem as invariantes 1, 2 e 4.
- [ ] Um split em um subcluster devolve **ids de cliente**, e não posições (regressão do bug 3.7 #1 do guia).
- [ ] O modelo fundido é a média ponderada exata quando a regra é `media`.
- [ ] Todo nó do histórico tem a evidência da decisão, inclusive nas recusas.
