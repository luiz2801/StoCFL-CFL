# 5. Estabilidade: como um não desfaz o trabalho do outro

> **Status:** proposta, nada implementado. Números do [toy](anexo-a-simulacao.md), um modelo quadrático: mostram mecanismos, não preveem resultados em redes reais.
>
> **Futuro módulo:** `isodata_fl/estabilidade.py`. **Depende de:** [estado](07-modelos-e-estado.md). **Decisões:** DP-04, DP-05, DP-09.

## 5.1 O calendário resolve?

A hipótese inicial é que, com o CFL só em rodadas primas, um algoritmo não desfaz o trabalho do outro. **O teste mostra que o calendário reduz a frequência, mas não elimina a oscilação.**

Cenário B do toy, sem guardas (`K = 4`, partição correta tem ARI 1,00):

| Calendário | ARI final | Splits | Merges | Merges que desfazem splits |
|---|---|---|---|---|
| Toda rodada | 0,00 | 112,1 | 112,1 | 112,1 |
| Paridade do ISODATA | 0,00 | 56,0 | 56,0 | 56,0 |
| Primos + não primos | 0,00 | 25,0 | 25,0 | 25,0 |
| Primos + pares | 0,00 | 25,0 | 25,0 | 25,0 |
| Primos + interprimos | 0,33 | 25,0 | 24,0 | 24,0 |
| Período 4 | 0,35 | 28,1 | 27,1 | 27,1 |

Os primos dividem por 4,5 o número de oscilações, mas **quase todo split ainda é desfeito**. A partição final só muda conforme a última operação tenha sido um split ou um merge. O calendário troca a frequência, e não o resultado.

**O motivo é o sinal, e não o tempo.** `ψ` não muda (invariante 4 do guia, 4.5). Se o merge aprova um par hoje, aprovará em qualquer rodada futura, por mais longe que ela esteja.

## 5.2 Como cada um desfaz o outro

| # | Mecanismo | Por quê | Sintoma no toy |
|---|---|---|---|
| **O1** | **Merge desfaz split correto** | `ψ` diz "juntar" e não muda | Cenário B: 24 de 25 splits desfeitos |
| **O2** | **Split desfaz merge** | A média ponderada é quase o ponto estacionário da união. Logo depois do merge, `mean_norm ≈ 0` e `max_norm` é alto, então o critério do CFL dispara na próxima janela. **Não há atraso natural** | Cenário B: 24 splits em clusters recém-fundidos |
| **O3** | **Laço falso** | O CFL divide um grupo homogêneo por ruído, o merge corrige, e o CFL divide de novo | Cenário C: 45 splits e 42 merges |
| **O4** | **Janelas coladas** | Com primos gêmeos, o merge cai 1 rodada depois do split (11 e 12, 17 e 18...). Os filhos quase não treinaram | Mesmo calendário, 13 pares gêmeos até a rodada 200 |
| **O5** | **Empate real** | Subgrupos genuínos: o split é legítimo, e o merge também é aceitável pela tolerância | Pior caso: 45 splits e 42 merges |

O1 e O3 são erros em lados opostos: em O1 o merge está errado, em O3 o split. **Nenhuma guarda em um único lado resolve os dois.**

## 5.3 Nenhuma guarda sozinha basta

Calendário de primos e interprimos, 30 sementes. Para cada cenário: ARI final e, entre parênteses, total de operações. **Em um resultado bom, o ARI é 1,00 e há poucas operações.** O mínimo é 3 operações em A e B, e 1 em C.

| Guarda | A: `ψ` separa | B: `ψ` não separa | C: `ε2` baixo |
|---|---|---|---|
| Nenhuma | 1,00 (3,8) | 0,33 (49,0) | 0,77 (87,0) |
| Idade mínima de 10 rodadas | 1,00 (3,4) | 0,68 (10,4) | 0,81 (19,2) |
| Tabu permanente depois do split | 1,00 (3,0) | **1,00 (3,0)** | **0,04 (18,2)** |
| Tabu de 20 rodadas | 1,00 (3,0) | 0,53 (25,1) | 0,15 (144,8) |
| Persistência de `mean_norm` | 1,00 (3,8) | 0,00 (28,0) | 1,00 (48,8) |
| `γ_max` | 1,00 (3,8) | 0,33 (49,0) | **1,00 (1,0)** |
| Ganho de fusão | 1,00 (3,0) | **1,00 (3,0)** | 0,77 (87,0) |
| **`γ_max` + ganho de fusão** | **1,00 (3,0)** | **1,00 (3,0)** | **1,00 (1,0)** |
| **Pilha completa** | **1,00 (3,0)** | **1,00 (3,0)** | **1,00 (1,0)** |

Como ler:

- **Tabu permanente** parece a solução óbvia, e funciona em B. Em C é desastroso, porque torna permanentes os erros do CFL: 19 clusters, onde deveriam ser 2. É a versão espelhada da "fusão irreversível" do StoCFL.
- **Tabu com prazo e idade mínima** só adiam. Quando o prazo vence, a oscilação volta.
- **Persistência em C** tem ARI 1,00 por sorte: foram 48,8 operações, e só parou na partição certa porque a última foi um merge.
- **`γ_max` e ganho de fusão são complementares:** um protege contra o erro do split, e o outro, contra o erro do merge.

**Com a pilha, o calendário deixa de importar para a partição.** Em todos os seis calendários do cenário B, o ARI é 1,00, com 3 splits e 0 merges. A diferença entre eles passa a ser só de custo e atraso ([calendário](02-calendario.md)).

## 5.4 A pilha proposta

Cada operador precisa **provar o que afirma**, usando evidência que muda com o estado. O calendário só decide quando a prova é pedida.

| Camada | Age em | Protege de | Custo | Evidência no toy | Sugestão |
|---|---|---|---|---|---|
| Calendário | Ambos | Conflito na mesma rodada | Atraso pequeno | Oscilações de 112 para 25 | Manter |
| Persistência `p = 3` | Split | Falso split no cruzamento de `ε1` | 2 rodadas de atraso | Falso split de 0,93 para 0,01 | Manter |
| `γ_max` | Split | **O3** | Nenhum, usa a mesma `S` | ARI em C de 0,77 para 1,00 | Manter e calibrar |
| Ganho de fusão | Merge | **O1** e, por consequência, **O2** | 1 download por cliente testado | ARI em B de 0,33 para 1,00 | Manter |
| Espera crescente | Ambos | **O5** e o custo de testes repetidos | Atrasa correções legítimas | Pior caso de 45 para 7 splits; testes de 122,7 para 20,9 | Manter |
| `W_merge` | Merge | **O4** | Atrasa correções | **Nenhum ganho no toy**, pois a perda não tem ruído | Manter como hipótese, E4 decide |

### Limite para a oscilação

A espera crescente dá uma garantia simples. Se a `k`-ésima espera de um par dura `W · 2^(k−1)` rodadas, o tempo gasto em `m` voltas é `W(2^m − 1)`. Dentro de `R` rodadas:

```text
número de voltas de um mesmo par ≤ log2(R/W + 1)
```

Com `R = 150` e `W = 10`, o limite é 4. No pior caso do toy, foram exatamente 4 merges. **É um limite para a oscilação, não uma prova de convergência:** o conjunto continua sem garantia teórica (problema 6 da especificação).

## 5.5 Regra de precedência

Quando os operadores discordam:

1. **Prova vence filtro.** `ψ` nunca decide sozinho contra um split aprovado.
2. **Evidência nova vence evidência velha.** O ganho de fusão é medido nos modelos atuais; `ψ` é da rodada em que foi observado.
3. **Empate mantém o que está.** Se os dois lados têm prova, a partição atual fica até a espera vencer.
4. **O CFL não tem preferência automática.** Ele tem um teorema, mas com hipóteses (guia 3.9.2), e o `ε2` errado produz splits falsos. O merge precisa poder corrigi-lo. No toy, com `γ_max` mal calibrado em 0,68, só o split dá ARI 0,04. Com merge verificado e espera, dá 0,94. **É onde o StoCFL tem função de verdade no híbrido.** Com `γ_max` bem calibrado, ele quase não age ([01](01-conceito-e-mapeamento.md), P-CON-5).

## 5.6 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-EST-1 | O1: merge por `ψ` desfaz split correto | Ganho de fusão | 5.3 |
| P-EST-2 | O2: split logo depois do merge, sem atraso natural | Resolvido na origem: merges errados não acontecem. Espera para separar, para os casos restantes | No toy, com o ganho, nenhum merge errado acontece |
| P-EST-3 | O3: laço falso | `γ_max` e persistência | 5.3 |
| P-EST-4 | O4: janelas coladas em primos gêmeos | `W_merge`, por cluster, em vez de confiar no calendário | A idade é o que importa, não a posição no calendário |
| P-EST-5 | O5: empate real | Espera crescente, nos dois sentidos | Oscilação limitada (5.4) |
| P-EST-6 | Guardas atrasam correções legítimas | Medir. No toy, cenário C com `γ_max` mal calibrado: ARI 0,79 sem espera e 0,94 com ela. Aqui a espera até ajudou, porque reduziu a oscilação | Trocas a ver em E3 |
| P-EST-7 | Oscilação pode passar despercebida | Métricas "M desfaz S" e "S desfaz M" em toda execução, e alarme se passar do limite de 5.4 | ARI final esconde a oscilação (linha da persistência em 5.3) |

## 5.7 Alternativas

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Só o calendário** (hipótese inicial) | **Descartar** como proteção única | 5.1. Fica como organizador das janelas |
| **Só idade mínima** | **Descartar** | Só adia: ARI 0,68 em B |
| **Tabu permanente** | **Descartar** | Ótimo em B, desastroso em C (ARI 0,04). Torna os erros do CFL irreversíveis, o defeito que a especificação aponta no StoCFL |
| **Tabu com prazo** | **Descartar** | Reagenda a oscilação: ARI 0,53 em B e 0,15 em C |
| **Histerese em `τ`** (limiares diferentes para unir e separar) | **Descartar** | `ψ` é fixo e o split não usa `ψ`. Não há o que separar com dois limiares |
| **Fases: primeiro só split, depois só merge** | **Testar** em E6 | Impede **O2** por construção, e é simples. **O1** continua, então o ganho de fusão ainda é necessário. Perde a capacidade de reagir mais tarde |
| **CFL calibra `τ`:** subir `τ` para acima do cosseno de um split aprovado | **Adiar** | Atacaria a falta de regra para `τ` (guia 4.15.7) e pouparia testes. Risco: um split falso sobe `τ` para todos. Reconsiderar depois de E4 |
| **Objetivo único `J`:** perda + custo por cluster, aceitando só operações que reduzem `J` | **Adiar** | É a garantia mais limpa, pois `J` estritamente decrescente impede ciclos. Mas o split só pode ser avaliado depois de treinar os filhos, o que exige o período de teste abaixo, e é preciso escolher o custo por cluster |
| **Período de teste:** manter o modelo do pai em paralelo por `W` rodadas e reverter se os filhos não melhorarem | **Adiar** | Implementaria a promessa "pelo menos tão bom quanto o FL", que o artigo do CFL faz sem descrever como (guia 3.9.3). Mas dobra o custo durante o teste |
| **Congelar depois de `n` oscilações** | **Descartar** | A espera crescente é a versão contínua disso, e não precisa escolher `n` |

## 5.8 Critérios de aceite

- [ ] Com a pilha, o número de voltas de qualquer par respeita o limite de 5.4 (teste de propriedade).
- [ ] As métricas de oscilação aparecem em toda execução.
- [ ] Toy na implementação real: a tabela de 5.3 reproduz qualitativamente.
- [ ] Desligar todas as guardas reproduz a oscilação (o teste confirma que as guardas é que causam o efeito).
