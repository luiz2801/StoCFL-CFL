# 4. Operador de merge (StoCFL)

> **Status:** proposta, nada implementado. Resolve, se aprovado, o problema 1 da [especificação](../especificacao-isodata-fl.md) (métrica do merge).
>
> **Futuro módulo:** `isodata_fl/merge_stocfl.py`. **Depende de:** [calendário](02-calendario.md), [estado](07-modelos-e-estado.md), [estabilidade](05-estabilidade.md). **Decisões:** DP-04, DP-07, DP-11.

## 4.1 O que é "agrupar caso necessário"

O pedido é que o StoCFL agrupe os clientes **caso seja necessário**. Este plano traduz isso em duas perguntas, feitas nesta ordem:

| Pergunta | Sinal | Papel | Custo |
|---|---|---|---|
| **Vale a pena olhar este par?** | `cos(ψ̄_a, ψ̄_b) ≥ τ`, ou cluster pequeno | **Filtro**: é o StoCFL | Nenhuma comunicação |
| **Fundir faz bem?** | Ganho de fusão: a perda dos membros não piora com o modelo fundido | **Prova**: acréscimo deste plano | 1 download por cliente testado |

O StoCFL original para na primeira pergunta. A seção 4.3 explica por que isso não basta quando existe um CFL dividindo ao lado.

## 4.2 O que o operador faz

| # | Passo | Origem | Observação |
|---|---|---|---|
| 1 | A rodada é janela de merge e existem 2 ou mais clusters | Calendário | |
| 2 | Centro de cada cluster: média de `ψ` de **todos os membros observados** | Eq. 2 do artigo | O código usa só os sorteados; a versão completa está comentada em `main` (guia 4.16) |
| 3 | Pares em ordem decrescente de cosseno | StoCFL | |
| 4 | Filtro: `cos ≥ τ`, ou um dos clusters tem menos de `n_pequeno` membros | StoCFL + novo | [Clientes](06-clientes-e-participacao.md), 6.3 |
| 5 | Cada cluster se funde no máximo uma vez por janela, até `L_FL` pares | **ISODATA** | Impede as fusões transitivas do `unite` |
| 6 | Par liberado em `nao_unir` | [Estabilidade](05-estabilidade.md) | Protege os irmãos recém-separados e limita os retestes |
| 7 | Candidato: `θ_m = (n_a θ_a + n_b θ_b) / (n_a + n_b)` | ISODATA | [Estado](07-modelos-e-estado.md), 7.4 |
| 8 | Ganho de fusão: `ΔL ≤ δ` | Novo, com precedente | 4.5 |
| 9 | Aprovado: funde, o id é o menor dos dois, e a separação fica bloqueada. Reprovado: aumenta a espera do reteste | Novo | [Estabilidade](05-estabilidade.md) |

## 4.3 Por que `ψ` sozinho não basta

**1. `ψ` é imutável.** Depois de calculado, nunca muda (invariante 4 do guia, 4.5). Se dois clusters têm `cos ≥ τ`, terão para sempre, inclusive logo depois de o CFL tê-los separado com bons motivos. Esse é o mecanismo central da [oscilação](05-estabilidade.md).

**2. Dois sinais podem discordar.** `ψ` mede a direção desde a âncora, longe do ótimo. O CFL mede o conflito perto do ponto estacionário. Em um problema com a âncora longe dos ótimos, `ψ` de grupos diferentes é quase paralelo, enquanto `ΔW` é oposto. No [toy](anexo-a-simulacao.md), o cenário B modela esse caso: cosseno cruzado de 0,86, com `τ = 0,65`.

**3. O cosseno entre centros depende da composição do cluster.** A média de `ψ` de um cluster misto cancela os componentes individuais e fica mais perto da direção comum. Com o mesmo `τ`, um cluster misto parece mais parecido com os outros:

| Composição (toy, âncora a distância 1) | Cosseno entre os centros |
|---|---|
| 1 grupo × 1 grupo | 0,50 |
| 1 grupo × 3 grupos | 0,61 |
| 2 grupos × 2 grupos | 0,67 |

Com `τ = 0,65`, os grupos puros ficam separados, mas uma bipartição `2 × 2` é refundida. Isso acontece mesmo no cenário A, em que `ψ` é um bom sinal, e explica os poucos merges que aparecem ali sem guardas.

## 4.4 Qual sinal usar

Valores do toy 10 rodadas depois de um split forçado. **Um bom sinal precisa separar a primeira coluna numérica das outras três.** A última coluna falsa existe para revelar sinais que só parecem funcionar por causa do ruído.

| Sinal | Split correto | Falso, ruído domina | Falso, desvio individual alto | Falso, quase sem ruído | Veredito |
|---|---|---|---|---|---|
| `cos ψ̄` | +0,50 | +0,99 | +0,97 | +0,98 | **Filtro.** Separa aqui, mas falha no cenário B, e nunca muda |
| `cos ΔW̄`, cada um no seu modelo | −0,93 | 0,00 | −0,05 | −0,88 | **Descartar.** Tende a 0 em todos os casos conforme os clusters convergem (−0,02 em 40 rodadas), e não separa no último caso |
| `cos ΔW̄`, os dois em `θ_m` | −0,99 | 0,00 | −0,26 | **−0,99** | **Descartar: degenerado** |
| `cos(θ_a − θ_pai, θ_b − θ_pai)` | −1,00 | 0,00 | −0,63 | **−0,98** | **Descartar: degenerado** |
| `α_cross^max`, entre clientes, em `θ_m` | −0,90 | +0,14 | +0,11 | +0,04 | **Testar.** Separa bem e não depende da idade, mas exige treinar em `θ_m` |
| `‖θ_a − θ_b‖ / ‖θ_pai − θ0‖` | +0,79 | +0,04 | +0,14 | +0,14 | **Testar** como pré-filtro gratuito. O limiar depende da idade |
| Perda cruzada `D` (FedDrift) | +0,69 | +0,00 | +0,02 | +0,02 | **Testar.** Separa bem, mas depende da escala da perda |
| **Ganho de fusão `ΔL`** | **+0,225** | **−0,000** | **−0,001** | **−0,001** | **Recomendado.** O sinal da diferença separa os casos, sem limiar a ajustar no toy |

### Dois candidatos naturais são armadilhas

"Direção média de `ΔW`" é um dos candidatos do problema 1 da especificação. Medir o deslocamento desde o modelo do pai é a variante que surge em seguida. Os dois parecem ótimos em um split correto, com cosseno perto de −1. O problema é que **dão −1 também em um split falso** quando o ruído é pequeno, e é um fato algébrico, não um detalhe do toy:

Se `θ_m` é a média ponderada, ele é quase o ponto estacionário da união. Logo, `n_a ΔW̄_a + n_b ΔW̄_b ≈ 0`, e os dois vetores são antiparalelos **por construção**, sejam os clusters congruentes ou não. O mesmo vale para os deslocamentos desde o pai. A informação sobre congruência está na **norma**, e o cosseno a joga fora.

## 4.5 Ganho de fusão

```text
ΔL(a, b) = média_{i ∈ a ∪ b} [ L_i(θ_m) − L_i(θ_c(i)) ]      funde se ΔL ≤ δ
```

`L_i` é a perda na **validação** do cliente `i`, `θ_c(i)` é o modelo atual dele e `θ_m` é o candidato.

| Propriedade | Por que importa |
|---|---|
| Testa o modelo **que será adotado** | Se a média cair em uma barreira de perda, o teste reprova. Dispensa testar a barreira à parte |
| O sinal tem significado | "Fundir não piora a perda" é o critério de negócio, e não um substituto para ele |
| É assimétrico do jeito certo | Um cluster pequeno e ruim pode ganhar com a fusão mesmo que o outro não ganhe nada. A média ponderada captura isso. A perda cruzada do FedDrift usa `max` e bloquearia o caso |
| Muda com o tempo | Dá a evidência nova que o ISODATA tinha e o StoCFL perdeu ([01](01-conceito-e-mapeamento.md), 1.4) |
| Custo baixo | 1 download de `θ_m` por cliente testado, inferência e 2 números de volta. Sem treino |

**Amostra.** Em clusters grandes, o teste pode usar `m` clientes de cada lado. O ruído da estimativa entra em `δ`.

**`δ` não pode ser zero em redes reais.** Em uma fusão boa, o ganho real é quase zero, e o ruído da validação decide no cara ou coroa: no toy, com `δ = 0` e ruído, o ARI cai de 0,94 para cerca de 0,52. Com `δ` de 2 erros padrão, estimados dos próprios valores por cliente, ele volta a 0,84. **O limite é o ganho de um split verdadeiro:** se o ruído se aproximar dele, merges errados passam, então é preciso testar mais clientes. Nesse caso, a espera entre retestes é essencial: sem ela, o ARI em B cai de 0,88 para 0,10, porque cada reteste é mais uma chance de aprovar por engano. Tabela completa em [DP-04](11-decisoes-pendentes.md#dp-04-como-provar-que-fundir-é-seguro).

**Precedente.** O FedDrift usa a perda cruzada e funde com média ponderada, o que é muito próximo disto ([anexo B](anexo-b-literatura.md)).

## 4.6 De onde vem `ψ`

| Opção | Custo | Sugestão | Justificativa |
|---|---|---|---|
| `ψ_i = −ΔW_i` da rodada 1 | **Nenhum**, se todos participam da rodada 1 | **Testar primeiro** em E0 | Na rodada 1 todos partem de `θ0`, então o treino normal **já é** a observação do StoCFL com `obep` igual às épocas locais |
| `obep` épocas a partir da âncora (código do StoCFL, padrão 10) | 1 download e 1 upload por cliente, uma vez | **Testar** em E0, com `obep` em {1, 5, 10, 20} | O sinal cresce com `obep` até saturar (guia 4.9). É o que o StoCFL usa, e o custo é pequeno |
| Gradiente normalizado na âncora (artigo) | Igual | **Adiar** | Coincide com `obep = 1` e batch cheio (guia 4.16). Só muda a escala, e o cosseno ignora a escala. A média por cluster é sensível à escala, então normalizar `ψ` é uma opção barata a testar |

## 4.7 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-MRG-1 | `ψ` imutável: o merge refaz o que o split desfez, sem limite | Ganho de fusão | No toy, cenário B: ARI 0,33 sem ele e 1,00 com ele, com 0 merges errados |
| P-MRG-2 | Centro só com os sorteados: ruidoso e dependente do sorteio (guia 4.12, item 8) | Média de todos os membros observados | É a definição da Eq. 2 do artigo. O código já tem essa versão comentada |
| P-MRG-3 | Fusões transitivas no `unite`: `A~B` e `B~C` juntam os três, mesmo com `cos(A,C) < τ` | Cada cluster uma vez por janela, até `L_FL` pares | É a regra do artigo do ISODATA, que descartou trios porque a partição mudaria "radicalmente demais" |
| P-MRG-4 | O cosseno entre centros sobe em clusters mistos (4.3) | O ganho de fusão decide; `τ` é só filtro | O efeito é de geometria, não de calibração. Mudar `τ` só troca o problema de lugar |
| P-MRG-5 | `τ` é escolhido à mão, sem regra no artigo (guia 4.15.7) | Registrar os cossenos (como `cos_rec.log`) e calibrar em E0. Com a prova, `τ` errado para baixo só custa testes, não fusões erradas | No toy, cenário B: `τ` abaixo do cosseno cruzado, partição correta |
| P-MRG-6 | `τ` alto demais bloqueia fusões necessárias | Caminho de cluster pequeno, sem `τ` | No toy, cenário E: de 24 clusters a 4, ARI de 0,00 a 1,00 |
| P-MRG-7 | A perda depende da mistura de rótulos do cliente, o que pode impedir fusões legítimas (crítica do FedCCFA) | Aceitar: é uma falha conservadora, porque mantém os clusters. Medir em C6 e C7 | Fundir de menos custa menos que fundir errado, e o ganho é medido nos próprios clientes |
| P-MRG-8 | Validação finita: `ΔL` tem ruído, e fusões boas reprovam por acaso | `δ` de 2 erros padrão, e reteste com espera | No toy com ruído: ARI de 0,52 para 0,84 em C. A espera limita as chances de aprovar por engano |
| P-MRG-9 | Testes repetidos custam comunicação | Espera crescente depois de reprovar | No toy, cenário B: de 122,7 para 20,2 testes, com a mesma partição |
| P-MRG-10 | Split muito recente: os modelos não divergiram, e `θ_m ≈ θ_pai` | A espera depois do split, que vale só para os irmãos | `W_merge`, uma idade mínima para qualquer cluster, foi testado e é prejudicial: bloqueia também quem acabou de se fundir (ARI de 0,94 para 0,12, [DP-09](11-decisoes-pendentes.md#dp-09-quanto-esperar-depois-de-cada-operação)) |
| P-MRG-11 | `ψ` ocupa memória, e `psi.pkl` é regravado toda rodada (guia 4.10) | Guardar em `float32` e salvar só os novos | 6,5 MB por cliente com `SimpleLinear` |
| P-MRG-12 | `unite` nem sempre mantém o modelo do maior (guia 4.16) | Regra explícita, ver [estado](07-modelos-e-estado.md), 7.4 | Comportamento implícito do código, não uma escolha |

## 4.8 Alternativas

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Só `cos ψ ≥ τ`** (StoCFL original) | **Descartar** como critério final | O toy mostra oscilação em todos os calendários quando `ψ` não separa. Continua como filtro |
| **Cosseno entre pesos dos modelos** ([especificação](../especificacao-isodata-fl.md), 3.3) | **Descartar** | Fica perto de 1 entre modelos de mesma origem e refunde os filhos na hora. A própria especificação registra isso |
| **Direção média de `ΔW`** (problema 1 da especificação) | **Descartar** | Degenerada (4.4) |
| **Deslocamento desde o ancestral comum** | **Descartar** | Degenerado (4.4) |
| **Deslocamento do modelo do cluster desde a âncora fixa** | **Adiar** | Não custa comunicação, mas converge para a mesma informação de `ψ̄` e não acrescenta evidência nova. Reconsiderar se `ψ` for caro demais |
| **`α_cross^max` em `θ_m`** | **Testar** em E4 | Elegante: o mesmo critério `γ_max` governaria os dois operadores. Mas exige treinar, `θ_m` pode ser um ponto ruim em redes não convexas, e no toy foi pior quando o merge era necessário (ARI 0,76 contra 0,94) |
| **Perda cruzada do FedDrift** | **Testar** em E4 | Tem precedente. Depende de uma tolerância na escala da perda: com 0, o toy reprova quase tudo (ARI 0,04), e com 0,05, funciona como o ganho de fusão. Usa `max`, que pode bloquear a fusão de um cluster pequeno com um grande |
| **Distância relativa entre modelos** (o `TC` original do ISODATA) | **Testar** em E4, como pré-filtro | Sem comunicação. Depende da idade do cluster e de um limiar |
| **Razão intra/inter do FedAC** | **Adiar** | Outra família de sinal, única para os dois operadores. Seria um algoritmo diferente do pedido |
| **Reancorar `ψ` no modelo do pai a cada split** | **Adiar** | Elimina o problema da âncora distante, mas `ψ` de âncoras diferentes não se comparam, e todos teriam de observar de novo. A prova por perda resolve o mesmo problema com menos custo |
| **Fundir só irmãos** (desfazer um split) | **Descartar** | Não permite fundir clusters de ramos diferentes, que é justamente o que o merge acrescenta a um CFL com histórico |
| **Fundir trios ou mais na mesma janela** | **Descartar** | O artigo do ISODATA testou e descartou |
| **Testar ganho em todos os pares, sem filtro** | **Descartar** | Custo quadrático no número de clusters. O filtro é a razão de usar `ψ` |

## 4.9 Critérios de aceite

- [ ] Em modo de reprodução (partida de clientes isolados, centros dos sorteados, fusões transitivas), reproduz a partição do `StoCFL-FCC+CFL.py` com os mesmos sorteios.
- [ ] Um cluster nunca se funde duas vezes na mesma janela.
- [ ] O candidato testado é exatamente o modelo adotado.
- [ ] Todo teste registra `cos ψ̄`, `ΔL` e o resultado, inclusive os reprovados.
- [ ] Depois do merge, o id é o menor dos dois, e o cluster absorvido fica sem membros e sem modelo.
