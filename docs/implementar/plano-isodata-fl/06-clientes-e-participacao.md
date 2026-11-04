# 6. Clientes e participação

> **Status:** proposta, nada implementado. Resolve, se aprovado, os problemas 3 e 4 da [especificação](../especificacao-isodata-fl.md).
>
> **Futuro módulo:** `isodata_fl/participacao.py`. **Depende de:** [calendário](02-calendario.md), [split](03-split-cfl.md), [merge](04-merge-stocfl.md). **Decisões:** DP-10, DP-11, DP-12.

## 6.1 O conflito

O CFL assume todos os membros do cluster em toda rodada (guia 3.9.9). Com `frac < 1`, o notebook usa o `dW` antigo de quem não participou, sem avisar (guia 3.5). O StoCFL existe para funcionar com participação parcial, e só consegue isso porque compara `ψ`, e não `ΔW`.

O híbrido precisa dos dois sinais. O calendário oferece uma saída: **o CFL só exige todo mundo nas raras rodadas em que age.**

## 6.2 Modos de participação

| Modo | Rodada comum | Rodada de split | Estatísticas do split | Quando |
|---|---|---|---|---|
| **M1. Total** | Todos | Todos | Exatas | v1. Reproduz o CFL e isola o problema |
| **M2. Censo** | Amostra de `frac` | Todos os membros dos clusters **candidatos** | Exatas nos candidatos | Fase 9 |
| **M3. Só amostra** | Amostra de `frac` | Amostra de `frac` | Estimadas, e a bipartição cobre só os amostrados | Só se M2 não bastar |

### Censo (M2)

Um cluster só vira candidato se a estimativa feita com a amostra disser que vale a pena (`mean_norm` persistente abaixo de `ε1` e `max_norm` acima de `ε2`). Então a rodada prima convoca apenas os seus membros.

O custo é o principal motivo prático para a raridade do calendário: até `R = 200` são no máximo 43 rodadas com censo, contra 180 em uma regra "toda rodada depois da 20".

Os vieses da estimativa com amostra são favoráveis:

| Estatística | Viés com amostra de tamanho `m` | Efeito no split |
|---|---|---|
| `mean_norm` | Para cima, porque o ruído da média cai com `1/√m` | Atrasa |
| `max_norm` | Para baixo, porque o máximo de uma amostra não passa do máximo de todos | Atrasa |

Os dois erros atrasam o split, em vez de causar um split falso. O risco é outro: com `m` pequeno, o cluster pode nunca virar candidato. A telemetria precisa mostrar quantas janelas cada cluster passou sem censo.

Se o censo terminar sem split (`γ_max` recusou), o cluster entra em espera crescente. Sem isso, um cluster com `max_norm` alto persistente custaria um censo a cada primo.

## 6.3 O destino dos clientes de clusters pequenos (`TN`)

O ISODATA descarta clusters com menos de `TN` pontos. Em FL isso não existe, porque o cliente continua lá e precisa de um modelo.

**Proposta em duas regras:**

1. **Antes do split:** só divide se `|C| > 2(TN_FL + 1)` e cada filho tiver ao menos `TN_FL + 1` membros. Com `TN_FL = 0`, é exatamente a regra `len(idc) > 2` do CFL.
2. **Depois:** um cluster com menos de `n_pequeno` membros entra no [merge](04-merge-stocfl.md) **sem precisar de `τ`**, comparado com o vizinho de `ψ` mais próximo e sujeito ao ganho de fusão. Se não houver ganho, continua sozinho.

A segunda regra também repara o ponto fraco da partida por `ψ`: com `τ` alto demais, ela começa com 24 clientes isolados (ARI 0,00 no [toy](anexo-a-simulacao.md), cenário E) e, com `n_pequeno = 6`, chega à partição correta usando só o ganho de fusão.

## 6.4 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-CLI-1 | O CFL exige todos os membros; o StoCFL existe para não exigir | M1 na v1, M2 depois | Separa dois riscos: primeiro testar a dinâmica, depois a participação. O guia 3.9.9 registra essa lacuna no CFL |
| P-CLI-2 | Quem não participou fica com `dW` velho, e o notebook o usa em silêncio (guia 3.5) | Estatísticas só sobre quem treinou **nesta** rodada. Nada guarda `ΔW` entre rodadas | `ΔW` é relativo ao modelo da rodada; misturar rodadas compara coisas diferentes |
| P-CLI-3 | Censo caro em clusters que não se dividem | Pré-filtro por estimativa e espera crescente após recusa | O viés da estimativa é conservador (6.2) |
| P-CLI-4 | Em M3, o split vê só parte dos membros. Onde ficam os demais? | Estado **pendente**: ficam com o filho cujo centro de `ψ` é mais próximo e são reavaliados ao participar | `ψ` já existe e não custa comunicação. Se `ψ` não separa aquele split, usar a menor perda entre os dois modelos (2 downloads) |
| P-CLI-5 | Cluster com menos de `TN` | Regras de 6.3 | O artigo descarta; em FL precisa de destino |
| P-CLI-6 | Filho unitário criado pela bipartição (*single linkage* isola outliers) | Recusar o split ou usar *complete* como reserva, se `TN_FL > 0` | No toy o menor filho médio é 1,8 (*single*) contra 2,7 (*complete*) em sobredivisão |
| P-CLI-7 | Cliente novo, sem `ψ` e sem cluster | Regra do artigo do StoCFL (guia 4.15.4): `max cos ≥ τ` entra, senão cria cluster a partir do mais próximo. **Fica para depois** | Não é necessário nos cenários iniciais (população fixa) |
| P-CLI-8 | Deriva de dados: `ψ` imutável não vê mudança | A v1 **não promete** lidar com deriva. Alternativa futura em 6.5 | Corrige a afirmação da especificação, seção 1, que não se sustenta |
| P-CLI-9 | Cliente mal encaixado depois de um split errado não tem como sair | v1: aceita; o merge corrige em bloco. Medir quantos clientes ficam no cluster errado | O ARI mostra se o problema existe de fato antes de pagar por reatribuição |
| P-CLI-10 | `random.sample` entre clusters pode não amostrar um cluster pequeno por muitas rodadas | Amostragem estratificada por cluster como opção, e medir | No StoCFL, um cluster não sorteado fica parado (guia 4.1). Com amostra uniforme, um cluster pequeno treina pouco |

## 6.5 Alternativas

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Reatribuição estilo IFCA em toda rodada** (cada cliente testa todos os modelos) | **Descartar** como padrão | Vários modelos por rodada, o custo que o artigo do StoCFL critica (guia 4.15.2), e o fenômeno de um modelo "dominar" os demais (guia 4.15.6). Precisa de `K` fixo no IFCA original |
| **Reatribuição periódica nas janelas de split** | **Testar** em E8, só se o ARI mostrar clientes presos | É o análogo direto da "classificação" do ISODATA. Só se paga se P-CLI-9 for real |
| **Reatribuição por `ψ`** | **Descartar** | `ψ` não muda: a resposta seria sempre a mesma, equivalente a um k-means estático no espaço de `ψ` |
| **ISODATA puro no espaço de `ψ`** (os clientes são os "pixels") | **Testar** como baseline em E1, sem fazer dele o algoritmo | É a leitura mais literal de "ISODATA como base", e barata de rodar. Não é o pedido (não usa o critério do CFL) e não reage ao treino, mas diz quanto vale o `ψ` sozinho |
| **Participação parcial desde a v1** | **Descartar** para a v1 | Mistura dois riscos, e o baseline do CFL não existe nesse modo |
| **M3 no lugar de M2** | **Adiar** | Bipartir só os amostrados exige o estado pendente e aumenta o erro. Reconsiderar se o censo for inviável no cenário real |
| **Atualizar `ψ` periodicamente** (nova observação a partir da âncora) | **Adiar**, junto com deriva | Mesmo com dados fixos o resultado é igual, e custa comunicação. Só faz sentido com dados que mudam. O FedDrift é a referência ([anexo B](anexo-b-literatura.md)) |
| **Descartar clientes muito pequenos do treino** | **Descartar** | Viola a premissa de que todo cliente recebe um modelo |

## 6.6 Critérios de aceite

- [ ] Em M1, `frac = 1` reproduz o conjunto de participantes do CFL em toda rodada.
- [ ] Nenhuma estatística de split usa `ΔW` de rodada anterior (teste com cliente ausente).
- [ ] Em M2, o censo só convoca membros de clusters candidatos; o número de censos é registrado.
- [ ] Depois de qualquer operação, todo cliente está em exatamente um cluster (invariante 2 do guia, 4.5).
- [ ] Com `TN_FL = 0` e `n_pequeno = 0`, o comportamento é o do CFL para clusters pequenos.
