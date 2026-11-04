# 3. Operador de split (CFL)

> **Status:** proposta, nada implementado. Resolve, se aprovado, os problemas 5, 6 e 8 da [especificação](../especificacao-isodata-fl.md).
>
> **Futuro módulo:** `isodata_fl/split_cfl.py`. **Depende de:** [calendário](02-calendario.md), [estado](07-modelos-e-estado.md). **Decisões:** DP-05, DP-06, DP-08.

## 3.1 O que o operador faz

Recebe um cluster e as atualizações `ΔW_i` dos seus membros na rodada atual, e devolve dois filhos ou uma recusa com o motivo. As condições vão da mais barata para a mais cara, para evitar a matriz de cossenos quando ela não será usada:

| # | Condição | Origem | Custo | Papel |
|---|---|---|---|---|
| 1 | A rodada é janela de split | Calendário | Nulo | Quando pode agir |
| 2 | `|C| > 2(TN_FL + 1)` | ISODATA | Nulo | Há membros para dois filhos. Com `TN_FL = 0`, é o `len(idc) > 2` do CFL |
| 3 | `mean_norm < ε1` por `p` rodadas seguidas | CFL + persistência | Nulo | Perto de um ponto estacionário do objetivo conjunto |
| 4 | `max_norm > ε2` | CFL | Nulo | Algum cliente ainda está longe do próprio ótimo |
| 5 | Bipartição `(c1, c2)` da matriz `S = cos(ΔW_i, ΔW_j)` | CFL, Algoritmo 1 | `O(M²D)` | Quem fica com quem |
| 6 | Cada filho com ao menos `TN_FL + 1` membros | ISODATA | Nulo | Em FL não há descarte depois |
| 7 | `γ_max < √((1 − α_cross^max) / 2)` | CFL, Algoritmo 5 | Nulo | A bipartição é significativa? |
| 8 | Nenhum par entre `c1` e `c2` em `nao_separar` | [Estabilidade](05-estabilidade.md) | Nulo | Um merge verificado não é desfeito logo em seguida |

As condições 3 e 4 são o critério do CFL (Eq. 30 e 31 do artigo, guia 3.9.3). A condição 7 é do artigo, mas o notebook não a implementa (guia 3.10). Sem ela, no [toy](anexo-a-simulacao.md), o CFL com `ε2` baixo chega a cerca de 20 clusters em uma população de 2 grupos.

Se aprovado, o cluster é substituído pelos filhos **antes** da agregação, e cada filho recebe a média das atualizações dos seus membros.

## 3.2 A bipartição é o mesmo algoritmo do merge

O Algoritmo 1 do artigo do CFL ordena os pares por similaridade decrescente e funde os grupos até restarem 2 (*single linkage*, guia 3.9.4). O `inter_cluster_union` do StoCFL percorre os pares na mesma ordem e funde enquanto `cos ≥ τ` (*single linkage* com corte, guia 4.16). **São o mesmo procedimento com critérios de parada diferentes.**

```text
agrupar(S, parar_quando):           # uma função só
    CFL:    parar_quando = restam 2 grupos
    StoCFL: parar_quando = próximo par abaixo de τ
```

Isso reduz o código e dispensa o `scikit-learn`, eliminando a incompatibilidade de `affinity` na versão ≥ 1.4 (guia 3.7, item 4).

## 3.3 `γ_max`: útil e perigoso

A condição 7 equivale a exigir `α_cross^max < 1 − 2γ_max²`, ou seja, limita o maior cosseno entre clientes de lados opostos.

| `γ_max` | Exige `α_cross^max` abaixo de | Leitura |
|---|---|---|
| 0,707 | 0 | Nenhum par entre os lados aponta para o mesmo semiespaço |
| 0,72 | −0,037 | Levemente opostos |
| 0,75 | −0,125 | Claramente opostos |
| 0,80 | −0,280 | Fortemente opostos |

**O risco é uma falha silenciosa.** No ponto estacionário, o cosseno entre grupos diferentes é cerca de `−1/(K−1)`, então quanto mais grupos, menos negativo. Com `γ_max` alto demais o algoritmo **nunca divide**, não dá erro e se comporta como FedAvg. Com `γ_max` baixo demais, o ruído passa e surgem splits falsos.

Valores medidos no toy (detalhes no [anexo A](anexo-a-simulacao.md)):

| Caso | `α_cross^max`, `D = 200` | `√((1−α)/2)` | `α_cross^max`, `D = 20000` | `√((1−α)/2)` |
|---|---|---|---|---|
| `K = 2` | −0,896 | 0,974 | −0,919 | 0,980 |
| `K = 4` | −0,264 | 0,795 | −0,310 | 0,809 |
| `K = 8` | −0,093 | 0,739 | −0,132 | 0,752 |
| `K = 12` | −0,046 | 0,723 | −0,083 | 0,736 |
| `K = 1` (só ruído) | +0,095 | 0,673 | +0,010 | 0,704 |

`γ_max` precisa ficar **acima da linha do ruído e abaixo da linha de `K`**. A janela é estreita e se fecha em torno de 0,707 quando a dimensão cresce, porque o ruído fica mais ortogonal. No toy, 0,72 a 0,74 funcionam em todas as dimensões testadas com `K = 8`, e 0,76 já impede qualquer split.

> Os valores não valem para redes reais: `ΔW` real não é ruído isotrópico, e clientes congruentes costumam ter cosseno positivo. **A janela real é uma das perguntas do experimento [E0](09-experimentos.md).**

## 3.4 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-SPL-1 | `ε1` e `ε2` são normas absolutas e dependem de lr, épocas e arquitetura (guia 3.5) | Rodada de calibração sem split, por cenário, usando a regra do artigo: `ε1 ≈ max_t ‖ΔW̄‖/10`, `ε2 ∈ [ε1, 10·ε1]` (guia 3.9.8) | É a recomendação dos autores, e funciona desde que a calibração use a mesma configuração do experimento |
| P-SPL-2 | Falso split no momento em que `mean_norm` cruza `ε1`: ali, `max_norm` ainda contém o resíduo comum | Exigir `mean_norm < ε1` por `p = 3` rodadas seguidas. O monitoramento é gratuito | No toy, o 1º falso split se concentra na rodada 23, e a persistência o reduz de 0,93 para 0,01 |
| P-SPL-3 | Split falso em população homogênea | Condição 7 (`γ_max`), já prevista no Algoritmo 5 | No toy, cenário C: ARI 0,03 no CFL puro, 1,00 com ela. Também atende ao problema 6 da especificação |
| P-SPL-4 | `γ_max` errado causa falha silenciosa | Registrar `α_cross^max` em toda janela; alarme para recusas seguidas com `ε` satisfeitos; calibrar em E0 | A recusa tem que aparecer no registro, ou o resultado parece "população congruente" |
| P-SPL-5 | O "ou `σ_θ > TS`" da [especificação](../especificacao-isodata-fl.md), seção 3.2, enfraquece a salvaguarda do CFL | Manter o **e** do CFL e não usar `σ_θ` | `σ_θ` não separa os casos (3.5): no toy, fica entre 78,6° e 87,4° em todos eles, enquanto `α_cross^max` vai de +0,08 a −0,90 |
| P-SPL-6 | `cluster_clients` devolve posições, e o notebook as usa como ids (guia 3.7, item 1) | O operador recebe e devolve **ids de cliente**, e há um teste de regressão com split de subcluster | Bug conhecido. Só aparece a partir do 2º split |
| P-SPL-7 | *Single linkage* isola outliers, gerando filhos unitários | Condição 6, com *complete* como reserva quando `TN_FL > 0` | No toy, o menor filho médio é 1,8 (*single*) e 2,7 (*complete*) em sobredivisão |
| P-SPL-8 | `pairwise_angles` usa laço duplo em Python e refaz `flatten` a cada par | Vetorizar: normalizar a matriz `M × D` e multiplicar | `O(M²)` chamadas a `flatten`, sem necessidade. Roda só nas janelas |
| P-SPL-9 | Em rodada de split sem todos os membros, `S` fica incompleta | Censo, ver [clientes](06-clientes-e-participacao.md) | O CFL não define o caso parcial (guia 3.9.9) |
| P-SPL-10 | Após split ou merge, buffers de momentum apontam para o ótimo anterior | Sem momentum na v1, ver [estado](07-modelos-e-estado.md) | Guia 3.10 |
| P-SPL-11 | Bipartição correta só é garantida perto do ponto estacionário | Condições 3 e 4 continuam obrigatórias, em todos os calendários | Teorema 1 do artigo. O calendário só **permite**, não **manda** dividir |

## 3.5 Alternativas

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **`σ_θ,k > TS`** como critério (especificação) | **Descartar** | Em ruído puro e em dois grupos opostos, a média do cluster é pequena e o ângulo de cada cliente até ela é grande. No toy: 83,4° em população homogênea com desvio individual alto, contra 86,8° com dois grupos. A distinção de que precisamos é justamente a que `ε2` e `γ_max` fazem |
| **Deslocamento `±1` do ISODATA** seguido de reclassificação | **Descartar** | Sem reclassificação, não tem efeito. Com ela, é o custo do IFCA ([clientes](06-clientes-e-participacao.md)). Problema 8 da especificação |
| ***Complete linkage*** (o que o notebook usa) | **Testar** em E3 | Filhos mais equilibrados, mas sem a garantia do Corolário 1, que vale para o Algoritmo 1. Fica como reserva da condição 6 |
| **Agrupamento espectral ou k-means com `k = 2`** | **Adiar** | Sem garantia teórica, adiciona dependência e não há indício de que a bipartição seja o gargalo. Reconsiderar se E0 mostrar bipartições erradas com `S` limpa |
| **Dividir em mais de 2** | **Descartar** | O artigo do ISODATA considerou e achou "perigoso" sem a matriz de covariância. A recursão do CFL já chega a `K` |
| **Gradientes em vez de `ΔW`** | **Descartar** | O artigo do CFL observa que `ΔW` separa melhor e não muda o protocolo (guia 3.9.5) |
| **Tirar `ε2`, só `γ_max`** | **Testar** em E6 | Eliminaria uma calibração sensível à escala. Mas `ε2` evita calcular `S` e fazer censo à toa, e protege contra `γ_max` errado |
| **`ε1` automático** (`0,1 × max` observado até agora) | **Testar** em E6 | Dispensa a rodada de calibração. Risco: o máximo pode mudar depois de um split, o que exige um máximo por cluster |
| **Teste `d̄_k > D̄` do ISODATA** (dividir só os mais dispersos) | **Adiar** | Atrasa splits legítimos: se dois clusters são incongruentes, os dois devem dividir. Útil apenas com orçamento de censo |
| **Split forçado quando `N ≤ K/2`** | **Descartar** | Exige `K` e ignora a estacionariedade. É o oposto do que motiva o CFL (problema 2 da especificação) |
| **Média de `S` em várias janelas** | **Adiar** | Reduz ruído, mas `ΔW` de rodadas diferentes partem de modelos diferentes. Reconsiderar se E0 mostrar `S` instável |
| **Projeção aleatória de `ΔW` para calcular `S`** | **Adiar** | Preserva cossenos com menos custo, mas o custo só importa em escala maior que a dos cenários iniciais |

## 3.6 O que aproveitar do código do CFL

| Em `fl_devices.py` | Na reimplementação |
|---|---|
| `compute_max_update_norm`, `compute_mean_update_norm` | Mesma fórmula sobre vetores 1-D |
| `pairwise_angles` | Vetorizada; o nome passa a dizer "cosseno" |
| `cluster_clients` | Substituída por `agrupar` (3.2) |
| `cache_model` | Vira nó do [histórico](07-modelos-e-estado.md) |
| `aggregate_weight_updates` | Não usar: está quebrada (guia 3.7, item 2) |

## 3.7 Critérios de aceite

- [ ] Com `γ_max` desligado, `p = 1`, *complete*, calendário "toda rodada depois da 20" e o otimizador do notebook, reproduz a separação `[0–4]` e `[5–9]` do notebook.
- [ ] Vetores sintéticos com 2 grupos opostos: bipartição correta. Vetores só com ruído: recusa por `γ_max`.
- [ ] Um split de subcluster devolve ids de cliente, sem duplicados e sem faltantes.
- [ ] Toda recusa gera registro com o motivo e o valor que a causou.
- [ ] Nenhuma dependência de `scikit-learn` no operador.
