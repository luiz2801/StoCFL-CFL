# Plano do ISODATA-FL: CFL como split e StoCFL como merge

Plano modular para implementar o CFL e o StoCFL sobre o laço do ISODATA: o **CFL separa** os clientes, o **StoCFL agrupa** quando necessário, e os dois agem só em rodadas definidas por um calendário.

> **Status (2026-11-04): planejamento. Nada foi implementado, e nenhuma das recomendações foi aprovada.** As decisões em aberto, com o dilema de cada uma, estão em [11-decisoes-pendentes.md](11-decisoes-pendentes.md). Os números vêm de um modelo de brinquedo (o [*toy*](anexo-a-simulacao.md)), que mostra mecanismos, mas não prevê acurácia em redes neurais.

> **Atenção (2026-11-04): o código do CFL e do StoCFL mudou depois deste plano.** A D-014 em [decisoes.md](../../decisoes.md) corrigiu os dois para seguir o texto dos artigos. Onde este plano descreve o "notebook" ou o "código do StoCFL" (momentum, decaimento do lr, aquecimento, *complete linkage*, `obep`, modelo global encadeado), ele se refere ao código original, disponível até o commit `3159d55`. Para reproduzir aquele comportamento, use esse commit.

## O essencial

1. **O calendário de primos não impede que um algoritmo desfaça o outro.** No toy, sem guardas, quase todo split é desfeito em qualquer calendário. Os primos só reduzem a frequência, de 112 para 25 oscilações. O motivo é o sinal: `ψ` nunca muda, então o merge dá sempre a mesma resposta. A regra dos primos pode ficar, por custo e simplicidade ([02](02-calendario.md)).

2. **O que evita a oscilação são as guardas: cada operador prova o que afirma.** O split precisa passar pelo teste `γ_max`, que o artigo do CFL prevê. O merge precisa mostrar que o modelo fundido não piora a perda dos membros. Nenhuma das duas guardas basta sozinha, e com as duas todos os calendários chegam à mesma partição ([05](05-estabilidade.md)).

3. **O híbrido traz algo que os originais não têm, ao menos no toy.** Com as guardas, acerta a partição nos cinco cenários, o que nenhum dos dois algoritmos faz sozinho:

   | ARI final | A: `ψ` separa | B: `ψ` não separa | C: `ε2` baixo | D: homogêneo | E: `τ` alto |
   |---|---|---|---|---|---|
   | FedAvg | 0,00 | 0,00 | 0,00 | 1,00 | 0,00 |
   | CFL puro | 1,00 | 1,00 | **0,03** | **0,00** | 1,00 |
   | StoCFL puro | 1,00 | **0,00** | 1,00 | 1,00 | **0,00** |
   | Híbrido sem guardas | 1,00 | **0,33** | **0,77** | **0,00** | 1,00 |
   | **Híbrido com guardas** | **1,00** | **1,00** | **1,00** | **1,00** | **1,00** |

   **Ressalva importante:** com `γ_max` bem calibrado, o merge quase não age, e o StoCFL vira uma rede de segurança para quando `γ_max` erra. Se isso se repetir em redes reais, a versão só com split pode bastar ([01](01-conceito-e-mapeamento.md), P-CON-5).

4. **A ordem pedida pode não ser a melhor.** Começar com o StoCFL (partição por `ψ` na rodada 1) e deixar o CFL corrigir atinge a partição correta bem mais cedo quando `ψ` é bom: perda média de 0,029 contra 0,119 no cenário A. Mas falha se `τ` for alto demais, salvo com uma regra extra. **É a primeira decisão a tomar** ([01](01-conceito-e-mapeamento.md), 1.6).

5. **A forma final do calendário:** o CFL age nas rodadas primas a partir da 7, até 70% das rodadas, e o StoCFL nas pares. Parar os splits antes do fim dá a última palavra ao merge, que tem uma prova, e foi o que limpou os erros restantes: ARI de 0,94 para 1,00 com `γ_max` mal calibrado ([02](02-calendario.md), 2.8).

6. **Participação parcial tem uma armadilha, com solução.** Em um cluster incongruente, a média de uma amostra não se cancela, e o critério do CFL nunca dispara: ARI 0,00 com 10% dos clientes. Um estimador corrigido, sem custo de comunicação, resolve: ARI 1,00 ([06](06-clientes-e-participacao.md), 6.2).

7. **Há outras armadilhas que este plano já evita:**
   - Dois candidatos naturais a métrica de merge são degenerados e dão o mesmo valor para split certo e errado ([04](04-merge-stocfl.md), 4.4).
   - `γ_max` alto demais faz o algoritmo nunca dividir, sem erro nenhum ([03](03-split-cfl.md), 3.3).
   - Tabu permanente parece resolver a oscilação, mas torna os erros do CFL irreversíveis ([05](05-estabilidade.md), 5.3).
   - Uma idade mínima antes do merge parece prudente, mas derruba o ARI de 0,94 para 0,12 ([05](05-estabilidade.md), 5.4).

**Uma ressalva de licença:** o repositório original do CFL não declara licença nenhuma, e por isso o plano reescreve em vez de copiar ([DP-17](11-decisoes-pendentes.md#dp-17-a-licença-do-cfl)).

## Módulos

Cada módulo corresponde a uma parte do código futuro e pode ser lido e implementado separadamente. Os módulos 02 a 08 seguem a mesma estrutura: proposta, problemas e soluções, alternativas, critérios de aceite. O módulo 01 traz os problemas e as alternativas de alto nível.

| Arquivo | Conteúdo | Código futuro |
|---|---|---|
| [01-conceito-e-mapeamento.md](01-conceito-e-mapeamento.md) | A ideia, ISODATA passo a passo, hiperparâmetros, uma rodada, quem age primeiro | `nucleo.py` |
| [02-calendario.md](02-calendario.md) | Análise da regra dos primos, merge nas pares, parada do split, início na rodada 7 | `calendario.py` |
| [03-split-cfl.md](03-split-cfl.md) | CFL como operador: critérios, `γ_max`, bipartição | `split_cfl.py` |
| [04-merge-stocfl.md](04-merge-stocfl.md) | StoCFL como operador: `ψ`, candidatos a métrica, ganho de fusão | `merge_stocfl.py` |
| [05-estabilidade.md](05-estabilidade.md) | Como um não desfaz o outro: mecanismos, proteções, limite | `estabilidade.py` |
| [06-clientes-e-participacao.md](06-clientes-e-participacao.md) | Participação parcial, média corrigida, censo, clusters pequenos, reatribuição | `participacao.py` |
| [07-modelos-e-estado.md](07-modelos-e-estado.md) | Ids, invariantes, modelo no split e no merge, modelo global | `estado.py` |
| [08-arquitetura-do-codigo.md](08-arquitetura-do-codigo.md) | Pacote, interfaces, reaproveitamento, licenças, testes | Estrutura |
| [09-experimentos.md](09-experimentos.md) | Hipóteses, cenários, métricas, baselines, E0 a E9 | `experimentos/` |
| [10-roteiro.md](10-roteiro.md) | **O passo a passo**: 11 fases com aceite e pontos de decisão | — |
| [11-decisoes-pendentes.md](11-decisoes-pendentes.md) | **As 19 decisões:** o dilema de cada uma, como cada opção ajuda, o que custa e o que os testes mostraram. Traz também os 9 problemas da especificação | — |
| [12-diagramas.md](12-diagramas.md) | Atividades, sequência, estados, dependências | — |
| [anexo-a-simulacao.md](anexo-a-simulacao.md) | Modelo de brinquedo e protótipo do esqueleto: código e resultados | — |
| [anexo-b-literatura.md](anexo-b-literatura.md) | Trabalhos relacionados | — |

## Como usar

**Para decidir:** este README, depois [11](11-decisoes-pendentes.md), consultando o módulo de cada decisão.

**Para implementar:** [10](10-roteiro.md) diz a fase. O módulo correspondente diz o que fazer e como aceitar. Antes de alterar qualquer coisa, leia também o que a política 1 do [CLAUDE.md](../../../CLAUDE.md) exige.

**Para entender o raciocínio:** 01, 05 e 02, nessa ordem.

## Convenções

| Código | Significado |
|---|---|
| `P-XXX-n` | Problema de um módulo: `CON`, `CAL`, `SPL`, `MRG`, `EST`, `CLI`, `MOD`, `COD` |
| `DP-n` | Decisão pendente |
| `E0` a `E9` | Experimentos |
| `C0` a `C9` | Cenários |
| `H1` a `H7` | Hipóteses |
| `D-n` | Decisão já registrada em [decisoes.md](../../decisoes.md) |

Nas tabelas de alternativas, a coluna "Sugestão" usa quatro valores:

| Valor | Significado |
|---|---|
| **Recomendada** | Proposta atual, aguardando aprovação |
| **Testar** | Vale comparar em um experimento citado |
| **Adiar** | Não agora, e a justificativa diz quando reconsiderar |
| **Descartar** | Não vale testar, e a justificativa diz por quê |

Notação: `θ` modelo, `ΔW` atualização de pesos, `ψ` movimento a partir da âncora, `ψ̄` média de `ψ` em um cluster, `θ_m` modelo fundido candidato, `S` matriz de cossenos, `ΔL` ganho de fusão. As demais vêm do [guia](../../guia.md), seção 7. As referências "guia 3.7" apontam para aquele documento.

## Relação com os documentos anteriores

Os outros documentos de [`docs/implementar/`](../README.md) continuam valendo como contexto. Onde houver divergência, vale este plano, depois de aprovado:

| Documento | O que muda |
|---|---|
| [Especificação](../especificacao-isodata-fl.md) | Critério de merge, "ou `σ`" no split, alternância por paridade. Os 9 problemas da seção 5 estão encaminhados em [11](11-decisoes-pendentes.md) |
| [Diagramas](../diagramas-isodata-fl.md) | Ordem split-agregação, calendário e verificação no merge. Novos em [12](12-diagramas.md) |
| [Arquitetura](../arquitetura-componentes-isodata-fl.md) | Laço único em vez de duas integrações; roteiro de 4 fases substituído por [10](10-roteiro.md) |

Em particular, este plano corrige duas afirmações anteriores: que o ISODATA-FL "adapta-se a drifts" ([06](06-clientes-e-participacao.md), P-CLI-8) e que a direção média de `ΔW` é uma candidata viável ao merge ([04](04-merge-stocfl.md), 4.4).
