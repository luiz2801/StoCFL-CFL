# 1. Conceito e mapeamento

> **Status:** proposta, nada implementado. Termos e códigos de problema seguem o [README](README.md).
>
> **Depende de:** nada. **Decisões relacionadas:** DP-01, DP-02, DP-03, DP-14 em [11-decisoes-pendentes.md](11-decisoes-pendentes.md).

## 1.1 A ideia

O ISODATA é um laço que alterna dois operadores sobre um conjunto de clusters: dividir o que está disperso e fundir o que está próximo. O CFL e o StoCFL são, cada um, metade disso.

| Papel no laço | Quem faz | O que se aproveita |
|---|---|---|
| Laço, alternância, limites por iteração, consolidação final | **ISODATA** | O fluxo de controle de `doISODATAGray` |
| Operador de divisão | **CFL** | Critério de normas e bipartição por cosseno sobre `ΔW` |
| Operador de fusão | **StoCFL** | Representação `ψ` a partir da âncora, centros por cluster e limiar `τ` |
| Quando cada operador pode agir | **Calendário** | Hipótese do usuário: CFL em rodadas primas a partir da 7. Proposta: StoCFL nas pares |
| Treino entre as operações | **FedAvg por cluster** | Comum aos dois algoritmos |

O treino acontece em **toda** rodada. O que não roda toda rodada são os operadores: muitas rodadas são só FedAvg dentro de cada cluster.

### O que "base" significa aqui

A base é o **fluxo do algoritmo**, não os arquivos. `ISODATAKit.py` trabalha com `Pixel`, `Cluster.pixelList` e imagem, em laços de Python puro, e não tem nada reaproveitável diretamente em um laço federado. Duas formas de honrar a base estão na [arquitetura](08-arquitetura-do-codigo.md): a recomendada é um esqueleto genérico com um adaptador de pixels, que usa o `ISODATAKit.py` atual como oráculo de teste (DP-14).

## 1.2 Mapeamento passo a passo

Linhas de [`ISODATAKit.py`](../../../projetos/ISODATA-python/ISODATAKit.py), função `doISODATAGray`.

| Passo do ISODATA | Linhas | No ISODATA-FL | Origem | Observação |
|---|---|---|---|---|
| Sortear `NROWS` centros iniciais | 46–47 | 1 cluster com todos, modelo `θ0` (partida única) ou partição por `ψ` (DP-01) | CFL / StoCFL | Equivale a `NROWS = 1` |
| Classificar cada ponto no centro mais próximo | 62–72 | **Não existe na v1.** O cliente fica no seu cluster até um split ou merge | Nenhuma | É a maior diferença, ver 1.4 |
| Recalcular os centros | 77–83 | FedAvg por cluster | CFL e StoCFL | `aggregate_clusterwise` |
| Calcular `σ`, `d̄` e `D̄` | 88–101 | `mean_norm`, `max_norm`, persistência e `α_cross` | CFL | `σ` não se transpõe, ver [split](03-split-cfl.md) |
| Descartar clusters com menos de `TN` | 105–109 | Nunca descarta cliente. Cluster pequeno vai para o caminho de fusão sem `τ` | Novo | [Clientes](06-clientes-e-participacao.md) |
| Parar em `I` iterações | 112–113 | `R_max`, com as últimas `F` rodadas sem operadores | ISODATA | O artigo pede iteração final só de consolidação |
| Escolher split ou merge | 116 | Calendário | Usuário | [Calendário](02-calendario.md) |
| Dividir | 120–125 | Operador CFL | CFL | Bipartição de membros, sem `±1` |
| Fundir | 131–155 | Operador StoCFL com verificação | StoCFL e ISODATA | Mantém "só pares" e "no máximo `L`" |

## 1.3 Mapeamento de hiperparâmetros

| ISODATA | ISODATA-FL | Valor inicial | Fonte do valor | Observação |
|---|---|---|---|---|
| `NROWS` | `partida` | `unica` | Pedido do usuário | Alternativa: `psi` |
| `K` | `K_max` (opcional) | desligado | CFL e StoCFL não precisam de `K` | Limite de segurança, não meta |
| `TN` | `TN_FL` | 0 | Reproduz `len(idc) > 2` do CFL | `\|C\| > 2(TN_FL+1)` |
| `TS` | `ε2` e `γ_max` | calibrar | Artigo do CFL (3.9.8) | Ver [split](03-split-cfl.md) |
| `TC` | `τ` | calibrar | `cos_rec.log` (guia 4.9) | Vira só um filtro, ver [merge](04-merge-stocfl.md) |
| `L` | `L_FL` | 1 por janela | Conservador | Regra de pares vem do artigo |
| `I` | `R_max` | por cenário | Experimento | |
| Paridade | `t_min` e calendário | Split em primos a partir de 7, até 70% das rodadas; merge nas pares | Hipótese do usuário e toy | Paridade original é um dos casos testados |
| — | `ε1`, persistência `p` | calibrar, 3 | Artigo do CFL; toy | `p = 1` reproduz o CFL |
| — | `espera` | 10 | Toy, a calibrar | [Estabilidade](05-estabilidade.md). `W_merge` foi testado e descartado (DP-09) |
| — | `δ` | 0 mais o ruído da validação | Toy, a calibrar | Tolerância do ganho de fusão |
| — | `F` | 10 | Artigo do ISODATA | Rodadas finais sem operadores |

## 1.4 O que o ISODATA traz e o que não se transpõe

**Três regras do artigo valem como estão.** O texto de Ball & Hall justifica cada uma ([isodata.pdf](../../../isodata.pdf)):

1. **Alternância.** A figura 1 do artigo manda para o divisor nas iterações ímpares e para o fundidor nas pares, na última iteração ou com clusters demais. Isso confirma que a paridade é do algoritmo original, e não invenção do código.
2. **Só pares, no máximo `L` por iteração.** O artigo considerou fundir trios e descartou porque "parecia mudar a partição radicalmente demais para o procedimento iterativo convergir de forma satisfatória". Isso corrige o StoCFL, cujo `unite` encadeia fusões transitivas na mesma rodada (guia 4.1).
3. **Iteração final de consolidação.** "Nenhuma divisão ou fusão é permitida nesta iteração final." Vira as `F` rodadas finais, e inspira a parada dos splits antes do fim ([02](02-calendario.md), 2.8).

**Quatro coisas não se transpõem:**

| Item do ISODATA | Por quê | Substituto |
|---|---|---|
| Deslocamento `±1` | Serve para que a reclassificação separe os pontos. Em `R^D`, sem reclassificação, não tem função | Bipartição explícita dos membros |
| Descarte por `TN` | Em FL não se descarta cliente | Fusão verificada do cluster pequeno |
| Meta `K` | CFL e StoCFL existem justamente para não precisar dela | `K_max` opcional |
| Reclassificação a cada iteração | Exige que cada cliente avalie todos os modelos | Nenhum na v1, ver [clientes](06-clientes-e-participacao.md) |

**A última linha é o ponto conceitual mais importante do plano.** No ISODATA, um split errado se corrige sozinho: os dois centros nascem colados, a reclassificação os move, e na iteração seguinte a fusão mede a distância atual entre eles. A fusão enxerga **evidência nova**.

Trocando o merge pelo do StoCFL, essa propriedade some, porque `ψ` é medido uma vez e nunca muda (invariante 4 do guia, seção 4.5). Se `ψ` disse "juntar" uma vez, dirá para sempre, e nenhum calendário muda isso. Esse é o motivo da [verificação no merge](04-merge-stocfl.md) e de todo o [módulo de estabilidade](05-estabilidade.md).

## 1.5 Uma rodada

```text
estado: partição P, modelo θ_c por cluster, âncora θ0, ψ = {}, histórico H

para t = 1 .. R_max:
    ação = calendário(t)                     # SPLIT, MERGE ou NADA; NADA nas últimas F rodadas
    S_t  = amostrar(P, ação)                 # v1: todos; depois: amostra ou censo, com média corrigida
    observar ψ_i dos clientes que ainda não têm   # uma vez por cliente
    ΔW_i = treino local a partir de θ_c(i), para i em S_t
    monitorar(P, ΔW)                         # normas e persistência, em TODA rodada

    se ação == SPLIT:
        para cada cluster c elegível:
            operador_split(c, ΔW)            # antes da agregação, como no CFL

    agregar FedAvg por cluster, na partição já atualizada

    se ação == MERGE:
        operador_merge(P, ψ, θ)              # depois da agregação, com modelos atualizados

    registrar(t)                             # toda operação grava a evidência que a justificou
```

Os diagramas estão em [12-diagramas.md](12-diagramas.md).

> **Divergência com a proposta anterior.** O [diagrama de atividades do ISODATA-FL](../diagramas-isodata-fl.md) agrega **antes** de decidir o split. O CFL do notebook faz o contrário (célula 9): divide e depois agrega na partição nova, de modo que cada filho recebe só as atualizações dos seus membros. Este plano segue o CFL, porque agregar antes aplicaria ao modelo uma média de atualizações que acabaram de ser consideradas incongruentes.

## 1.6 Partida: quem age primeiro

Esta é a decisão de maior efeito do plano (DP-01), e a sua formulação ("o CFL separa, o StoCFL agrupa se necessário") aponta para a primeira opção.

| | Partida única (pedido) | Partida por `ψ` (alternativa) |
|---|---|---|
| Início | 1 cluster com todos | Componentes do grafo `cos(ψ_i, ψ_j) ≥ τ`, já na rodada 1 |
| Quem é a rede de segurança | O StoCFL corrige excesso de divisão | O CFL corrige o que `ψ` juntou errado |
| Rodadas 1 a 6 | FedAvg global | Já treina por cluster |
| Se `ψ` é bom | Espera o FL convergir para dividir | Acerta desde a rodada 1 |
| Se `τ` é baixo demais | Sem efeito | Tudo em um cluster, e cai na partida única |
| Se `τ` é alto demais | Sem efeito | Clientes isolados, e precisa do caminho de cluster pequeno |

No [toy](anexo-a-simulacao.md), as duas chegam à partição correta nos cenários A a D. A partida por `ψ` tem perda média bem menor quando `ψ` é bom (0,029 contra 0,119 no cenário A), mas falha sem o caminho de cluster pequeno se `τ` é alto demais (cenário E, ARI 0,00). A comparação de perda é otimista para clientes isolados, porque no toy eles aprendem quase tão bem quanto um cluster.

**Recomendação:** implementar as duas, porque a diferença é uma configuração. Manter a partida única como referência, que é o pedido e é robusta a `τ`, e comparar no experimento E5 com dados reais. O dilema está detalhado em [DP-01](11-decisoes-pendentes.md#dp-01-quem-age-primeiro). Vale notar que a partida por `ψ` dá um sentido natural ao "a partir do 7": rodadas 1 a 6 só para o StoCFL e, depois, o CFL começa a poder corrigir.

## 1.7 Escopo

| Entra na v1 | Fica para depois | Fora do escopo |
|---|---|---|
| Partida única e por `ψ` | Participação parcial, com média corrigida | Privacidade (permutação `P`, DP, agregação segura) |
| Participação total | Modelo global com termo proximal | Clientes bizantinos |
| Calendário configurável | Reatribuição de clientes | Rede real: tudo é simulação em um processo, como hoje |
| Split com `γ_max` e persistência | Clientes novos e árvore de parâmetros | |
| Merge com ganho de fusão e regras do ISODATA | Deriva de dados (*drift*) | |
| | Reatribuição seletiva, com a partida por `ψ` | |

> **Afirmação a não repetir.** O diagrama da [especificação](../especificacao-isodata-fl.md), seção 1, diz que o ISODATA-FL "adapta-se a drifts nos dados". Com `ψ` imutável isso não é verdade: `ψ` não vê deriva nenhuma. Ver [clientes](06-clientes-e-participacao.md), P-CLI-8.

## 1.8 Problemas de alto nível

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-CON-1 | "ISODATA como base" pode ser lido como reaproveitar o código, que só serve para pixels | A base é o fluxo, e isso é provado por um teste de oráculo ([08](08-arquitetura-do-codigo.md), 8.4) | Transforma uma afirmação vaga em uma propriedade verificável |
| P-CON-2 | Sem reclassificação, um split errado não se corrige sozinho como no ISODATA | Evidência nova no merge, com o [ganho de fusão](04-merge-stocfl.md) | É a função que a reclassificação cumpria no original (1.4) |
| P-CON-3 | Os dois algoritmos usam sinais diferentes, e eles podem discordar | Nenhum decide sozinho: cada operador prova o que afirma ([05](05-estabilidade.md)) | Medir a discordância real é o primeiro experimento (E0) |
| P-CON-4 | CFL e StoCFL têm premissas opostas sobre participação | Participação total primeiro, depois amostra ou censo, sempre com média corrigida ([06](06-clientes-e-participacao.md)) | Separa dois riscos. Sem a correção, o critério do CFL nem dispara com amostra |
| P-CON-5 | **O merge pode ficar ocioso.** No toy, com `γ_max` bem calibrado, quase não há split falso, e o StoCFL não faz nada | Medir em E3. Se repetir em redes reais, considerar a versão só com split, deixando o merge como rede de segurança ou retirando-o | Honestidade sobre o valor da combinação. O toy só mostra benefício claro quando `γ_max` está mal calibrado: ARI 0,04 sem merge e 0,94 com ele |
| P-CON-6 | A combinação pode não superar os originais em dados reais | Hipóteses com critério de refutação e condição de parada ([09](09-experimentos.md)) | O problema 9 da especificação registra que a motivação ainda não tem evidência |

## 1.9 Alternativas de alto nível

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **ISODATA puro sobre os vetores `ψ`** (clientes como "pixels") | **Testar** como baseline em E1 | É a leitura mais literal do pedido, e é barata. Não usa o critério do CFL, nem reage ao treino |
| **CFL com `γ_max`, sem merge** | **Testar** como baseline em E3 | Se bastar, o StoCFL não se paga (P-CON-5). É a alternativa que mais ameaça a proposta, e por isso precisa ser medida |
| **Sequencial: StoCFL agrupa uma vez, CFL refina depois, sem volta** | **Testar** em E5 | É a partida por `ψ` sem o operador de merge. Simples, mas não corrige excesso de divisão |
| **Rodar CFL e StoCFL separados e escolher o melhor modelo por cliente** | **Descartar** | Dobra o custo, e não há interação entre eles, que é o objetivo |
| **Trocar tudo por um método da literatura** (FedAC, SR-FCA) | **Adiar** | Não é o pedido, mas são referências importantes. Reconsiderar se E9 for negativo ([anexo B](anexo-b-literatura.md)) |
| **Reclassificar como no ISODATA, deixando o CFL só para o primeiro split** | **Adiar** | Mais fiel ao ISODATA, mas é o IFCA com outro início, com o custo de vários modelos por rodada ([06](06-clientes-e-participacao.md)) |
