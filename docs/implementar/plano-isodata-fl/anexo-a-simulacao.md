# Anexo A. Simulação de brinquedo

> **O que isto é e o que não é.** Um modelo quadrático de 450 linhas, feito para testar o raciocínio do plano antes de escrever qualquer código de verdade. Ele **mostra mecanismos** (quem desfaz quem, e por quê). **Não prevê** acurácia, nem valores de `τ`, `γ_max` ou `ε` em redes neurais. As tabelas foram geradas pelo código da seção A.13, sem edição.
>
> O código está neste Markdown, e não em um `.py`, porque o repositório ainda está em fase de planejamento (D-005 e D-011 em [decisoes.md](../../decisoes.md)).

## A.1 O modelo

Cada cliente `i` tem um ótimo próprio, e uma rodada de treino local move o modelo em direção a ele:

```text
θ*_i     = grupo(g_i) + subgrupo + within · u_i     ótimo local; u_i é um vetor unitário aleatório
ΔW_i(θ)  = c · (θ*_i − θ) + ruído                   ‖ruído‖ ≈ σ, novo a cada rodada
ψ_i      = c · (θ0 − θ*_i) + ruído                  medido uma vez, a partir da âncora θ0
L_i(θ)   = ½ ‖θ − (grupo + subgrupo)‖²              perda de validação
```

| Parâmetro | Valor | Papel |
|---|---|---|
| `D` | 200 | Dimensão (em A.8, até 20.000) |
| `c` | 0,1 | Passo efetivo de uma rodada |
| Raio dos ótimos | 1 | Ótimos dos grupos são ortonormais |
| `σ` | 0,02 | Ruído por rodada |
| `within` | 0,05 | Desvio individual, que **não generaliza** (imita dados finitos): fica fora da perda de validação |
| `N`, `R` | 24, 150 | Clientes e rodadas (10 últimas sem operadores) |
| `ε1`, `ε2`, `τ` | 0,015; 0,05; 0,65 | Limiares |
| `A` | 1 ou 2,5 | Distância da âncora: controla se `ψ` separa os grupos |

**Como `A` controla `ψ`.** O cosseno entre `ψ` de grupos diferentes é `A² / (A² + 1)`: 0,50 com `A = 1` e 0,86 com `A = 2,5`. Com `τ = 0,65`, o primeiro caso separa, e o segundo não. É o modo mais simples de modelar um `ψ` que discorda do CFL.

**Pilha completa:** `γ_max = 0,72`, persistência de 3 rodadas, ganho de fusão com tolerância 0, `W_merge = 10`, espera crescente de base 10.

**Médias de 30 sementes**, salvo indicação em contrário.

## A.2 Cenários

| Cenário | Configuração | O que testa |
|---|---|---|
| A | `K = 4`, `A = 1` | Tudo funciona: `ψ` e CFL concordam |
| B | `K = 4`, `A = 2,5` | `ψ` não separa: o merge quer desfazer todo split correto |
| C | `K = 2`, `A = 1`, `ε2 = 0,012` | `ε2` baixo: o CFL divide grupos homogêneos por ruído |
| D | `K = 1`, `A = 1`, `ε2 = 0,012` | População homogênea: não deveria dividir |
| E | `K = 4`, `A = 1`, `τ = 0,995` | `τ` alto demais: `ψ` não une nem clientes do mesmo grupo |

**Métricas.** ARI compara com o ground truth, e com `K = 1` vale 1 se houver um único cluster. "M desfaz S" conta merges que unem clientes já separados por um split. "S desfaz M" conta splits que separam clientes já unidos por um merge. Perda média é a média da perda de validação ao longo das rodadas.

## A.3 Cada algoritmo sozinho contra o híbrido

**Cenário A (ψ separa os grupos)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| FedAvg | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.393 | 0.3751 |
| CFL puro | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.101 | 0.0004 |
| StoCFL puro | 1.00 | 4.0 | 0.0 | 20.0 | 0.0 | 0.0 | 0.0 | 0.029 | 0.0004 |
| Híbrido sem guardas | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.112 | 0.0004 |
| Híbrido com a pilha, partida única | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.119 | 0.0004 |
| Híbrido com a pilha, partida por ψ | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.029 | 0.0004 |
| Híbrido com a pilha, partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.029 | 0.0004 |

**Cenário B (ψ não separa os grupos)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| FedAvg | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.467 | 0.3751 |
| CFL puro | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.196 | 0.0004 |
| StoCFL puro | 0.00 | 1.0 | 0.0 | 23.0 | 0.0 | 0.0 | 0.0 | 0.465 | 0.3751 |
| Híbrido sem guardas | 0.33 | 2.0 | 25.0 | 24.0 | 24.0 | 24.0 | 0.0 | 0.446 | 0.2601 |
| Híbrido com a pilha, partida única | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.9 | 0.209 | 0.0004 |
| Híbrido com a pilha, partida por ψ | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.9 | 0.209 | 0.0004 |
| Híbrido com a pilha, partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.9 | 0.209 | 0.0004 |

**Cenário C (ε2 baixo, sobredivisão)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| FedAvg | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.271 | 0.2501 |
| CFL puro | 0.03 | 19.7 | 18.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.065 | 0.0019 |
| StoCFL puro | 1.00 | 2.0 | 0.0 | 22.0 | 0.0 | 0.0 | 0.0 | 0.029 | 0.0002 |
| Híbrido sem guardas | 0.77 | 4.0 | 45.0 | 42.0 | 42.0 | 42.0 | 0.0 | 0.065 | 0.0003 |
| Híbrido com a pilha, partida única | 1.00 | 2.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.075 | 0.0002 |
| Híbrido com a pilha, partida por ψ | 1.00 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.029 | 0.0002 |
| Híbrido com a pilha, partida por ψ, cluster pequeno < 6 | 1.00 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.029 | 0.0002 |

**Cenário D (K=1, população homogênea, ε2 baixo)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| FedAvg | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.028 | 0.0001 |
| CFL puro | 0.00 | 20.0 | 19.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.030 | 0.0019 |
| StoCFL puro | 1.00 | 1.0 | 0.0 | 23.0 | 0.0 | 0.0 | 0.0 | 0.028 | 0.0001 |
| Híbrido sem guardas | 0.00 | 2.0 | 25.9 | 24.9 | 24.9 | 24.9 | 0.0 | 0.029 | 0.0002 |
| Híbrido com a pilha, partida única | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.028 | 0.0001 |
| Híbrido com a pilha, partida por ψ | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.028 | 0.0001 |
| Híbrido com a pilha, partida por ψ, cluster pequeno < 6 | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.028 | 0.0001 |

**Cenário E (τ alto demais: ψ não une nem o mesmo grupo)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| FedAvg | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.393 | 0.3751 |
| CFL puro | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.101 | 0.0004 |
| StoCFL puro | 0.00 | 24.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.031 | 0.0023 |
| Híbrido sem guardas | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| Híbrido com a pilha, partida única | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.119 | 0.0004 |
| Híbrido com a pilha, partida por ψ | 0.00 | 24.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.031 | 0.0023 |
| Híbrido com a pilha, partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 0.0 | 20.0 | 0.0 | 0.0 | 26.0 | 0.029 | 0.0004 |

**Leitura.**

- O CFL puro erra em C e D, por sobredivisão. O StoCFL puro erra em B, onde funde tudo, e em E, onde não funde nada.
- Híbrido com a pilha e partida única: partição correta em todos os cenários, com perda média próxima à do CFL puro.
- Quando `ψ` é bom (A e C), a partida por `ψ` tem perda média muito menor, porque agrupa desde a rodada 1. Em E ela falha, e o caminho de cluster pequeno a recupera.
- **Ressalva:** nas linhas com clientes isolados, a perda média é otimista. No toy, um cliente isolado aprende quase tão bem quanto um cluster, o que não é realista em redes com poucos dados.

## A.4 Candidatos a métrica de merge

Valores médios `W` rodadas depois de um split forçado no ponto estacionário do FL (100 sementes). `dist. relativa` é `‖θ_a − θ_b‖ / ‖θ_pai − θ0‖`. `perda cruzada D` é `max(L_ab − L_aa, L_ba − L_bb, 0)`. `ganho de fusão` é `ΔL`.

**split correto (K=2)**

| W | cos ψ | cos ΔW̄ próprio | cos ΔW̄ em θ_m | cos deslocamento | α_cross em θ_m | dist. relativa | perda cruzada D | ganho de fusão |
|---|---|---|---|---|---|---|---|---|
| 1 | +0.499 | -0.989 | -0.993 | -0.996 | -0.901 | +0.220 | +0.190 | +0.086 |
| 5 | +0.499 | -0.976 | -0.993 | -0.998 | -0.901 | +0.542 | +0.469 | +0.179 |
| 10 | +0.499 | -0.934 | -0.993 | -0.999 | -0.900 | +0.794 | +0.687 | +0.225 |
| 20 | +0.499 | -0.630 | -0.993 | -0.999 | -0.900 | +1.030 | +0.891 | +0.247 |
| 40 | +0.499 | -0.023 | -0.993 | -0.999 | -0.901 | +1.141 | +0.987 | +0.250 |

**split falso, ruído domina (K=1)**

| W | cos ψ | cos ΔW̄ próprio | cos ΔW̄ em θ_m | cos deslocamento | α_cross em θ_m | dist. relativa | perda cruzada D | ganho de fusão |
|---|---|---|---|---|---|---|---|---|
| 1 | +0.990 | -0.004 | +0.005 | -0.049 | +0.142 | +0.020 | +0.000 | -0.000 |
| 5 | +0.990 | +0.008 | -0.004 | -0.012 | +0.138 | +0.031 | +0.001 | -0.000 |
| 10 | +0.990 | +0.002 | -0.002 | -0.001 | +0.142 | +0.038 | +0.001 | -0.000 |
| 20 | +0.990 | +0.007 | +0.005 | +0.003 | +0.140 | +0.044 | +0.002 | -0.000 |
| 40 | +0.990 | -0.010 | -0.007 | -0.021 | +0.137 | +0.046 | +0.002 | -0.000 |

**split falso, desvio individual alto (K=1)**

| W | cos ψ | cos ΔW̄ próprio | cos ΔW̄ em θ_m | cos deslocamento | α_cross em θ_m | dist. relativa | perda cruzada D | ganho de fusão |
|---|---|---|---|---|---|---|---|---|
| 1 | +0.972 | -0.201 | -0.266 | -0.403 | +0.107 | +0.042 | +0.002 | -0.000 |
| 5 | +0.972 | -0.102 | -0.269 | -0.558 | +0.106 | +0.098 | +0.009 | -0.000 |
| 10 | +0.972 | -0.054 | -0.262 | -0.631 | +0.107 | +0.141 | +0.018 | -0.001 |
| 20 | +0.972 | -0.000 | -0.261 | -0.684 | +0.109 | +0.181 | +0.030 | -0.002 |
| 40 | +0.972 | -0.006 | -0.272 | -0.702 | +0.107 | +0.200 | +0.037 | -0.002 |

**split falso, quase sem ruído (K=1, σ=0.001)**

| W | cos ψ | cos ΔW̄ próprio | cos ΔW̄ em θ_m | cos deslocamento | α_cross em θ_m | dist. relativa | perda cruzada D | ganho de fusão |
|---|---|---|---|---|---|---|---|---|
| 1 | +0.980 | -0.966 | -0.977 | -0.977 | +0.043 | +0.038 | +0.001 | -0.000 |
| 5 | +0.980 | -0.944 | -0.983 | -0.980 | +0.043 | +0.093 | +0.008 | -0.000 |
| 10 | +0.980 | -0.884 | -0.987 | -0.981 | +0.042 | +0.137 | +0.017 | -0.001 |
| 20 | +0.980 | -0.569 | -0.988 | -0.981 | +0.042 | +0.177 | +0.029 | -0.002 |
| 40 | +0.980 | -0.044 | -0.988 | -0.982 | +0.042 | +0.197 | +0.035 | -0.002 |

**Leitura.** Compare o primeiro bloco com os outros três. `cos ΔW̄ em θ_m` e `cos deslocamento` parecem bons nos dois primeiros blocos, mas, no último, com pouco ruído, **dão quase −1 em um split falso**: são degenerados. `cos ΔW̄ próprio` decai a zero em todos os casos. Separam de verdade: `α_cross`, distância relativa, perda cruzada e ganho de fusão.

## A.5 Calendários sem nenhuma guarda

**Cenário A (ψ separa os grupos), sem nenhuma guarda**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| toda_rodada | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 1.0 | 0.0 | 0.103 | 0.0004 |
| paridade | 1.00 | 4.0 | 3.5 | 0.5 | 0.5 | 1.1 | 0.0 | 0.105 | 0.0004 |
| primos+naoprimos | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.112 | 0.0004 |
| primos+pares | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.112 | 0.0004 |
| primos+interprimos | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.112 | 0.0004 |
| periodo_4 | 1.00 | 4.0 | 3.2 | 0.2 | 0.2 | 0.5 | 0.0 | 0.112 | 0.0004 |

**Cenário B (ψ não separa os grupos), sem nenhuma guarda**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| toda_rodada | 0.00 | 1.0 | 112.1 | 112.1 | 112.1 | 111.1 | 0.0 | 0.467 | 0.3751 |
| paridade | 0.00 | 1.0 | 56.0 | 56.0 | 56.0 | 55.0 | 0.0 | 0.459 | 0.3751 |
| primos+naoprimos | 0.00 | 1.0 | 25.0 | 25.0 | 25.0 | 24.0 | 0.0 | 0.463 | 0.3751 |
| primos+pares | 0.00 | 1.0 | 25.0 | 25.0 | 25.0 | 24.0 | 0.0 | 0.463 | 0.3751 |
| primos+interprimos | 0.33 | 2.0 | 25.0 | 24.0 | 24.0 | 24.0 | 0.0 | 0.446 | 0.2601 |
| periodo_4 | 0.35 | 2.0 | 28.1 | 27.1 | 27.1 | 27.1 | 0.0 | 0.449 | 0.2625 |

**Cenário C (ε2 baixo, sobredivisão), sem nenhuma guarda**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| toda_rodada | 1.00 | 2.0 | 206.8 | 205.8 | 205.8 | 203.8 | 0.0 | 0.064 | 0.0002 |
| paridade | 1.00 | 2.0 | 102.7 | 101.7 | 101.7 | 99.7 | 0.0 | 0.065 | 0.0002 |
| primos+naoprimos | 1.00 | 2.0 | 45.0 | 44.0 | 44.0 | 42.0 | 0.0 | 0.065 | 0.0002 |
| primos+pares | 1.00 | 2.0 | 45.0 | 44.0 | 44.0 | 42.0 | 0.0 | 0.065 | 0.0002 |
| primos+interprimos | 0.77 | 4.0 | 45.0 | 42.0 | 42.0 | 42.0 | 0.0 | 0.065 | 0.0003 |
| periodo_4 | 0.78 | 4.0 | 52.8 | 49.8 | 49.8 | 49.8 | 0.0 | 0.067 | 0.0003 |

**Leitura.** No cenário B, nenhum calendário preserva a partição. Os primos reduzem as oscilações de 112 para 25. O ARI só muda conforme a última operação ter sido um split ou um merge.

## A.6 Guardas

**Cenário A (ψ separa os grupos), calendário primos+interprimos**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| nenhuma | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.112 | 0.0004 |
| idade W=10 | 1.00 | 4.0 | 3.2 | 0.2 | 0.2 | 0.7 | 0.0 | 0.131 | 0.0004 |
| tabu permanente | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| tabu 20 rodadas | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| persistência | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.125 | 0.0004 |
| γ_max | 1.00 | 4.0 | 3.4 | 0.4 | 0.4 | 0.8 | 0.0 | 0.112 | 0.0004 |
| ganho | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.107 | 0.0004 |
| γ_max + ganho | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.107 | 0.0004 |
| pilha completa | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.119 | 0.0004 |

**Cenário B (ψ não separa os grupos), calendário primos+interprimos**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| nenhuma | 0.33 | 2.0 | 25.0 | 24.0 | 24.0 | 24.0 | 0.0 | 0.446 | 0.2601 |
| idade W=10 | 0.68 | 3.0 | 6.2 | 4.2 | 4.2 | 5.2 | 0.0 | 0.379 | 0.1290 |
| tabu permanente | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.199 | 0.0004 |
| tabu 20 rodadas | 0.53 | 2.3 | 13.2 | 11.9 | 11.9 | 10.3 | 0.0 | 0.356 | 0.2165 |
| persistência | 0.00 | 1.0 | 14.0 | 14.0 | 14.0 | 13.0 | 0.0 | 0.460 | 0.3751 |
| γ_max | 0.33 | 2.0 | 25.0 | 24.0 | 24.0 | 24.0 | 0.0 | 0.446 | 0.2601 |
| ganho | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 122.7 | 0.199 | 0.0004 |
| γ_max + ganho | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 122.7 | 0.199 | 0.0004 |
| pilha completa | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.9 | 0.209 | 0.0004 |

**Cenário C (ε2 baixo, sobredivisão), calendário primos+interprimos**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| nenhuma | 0.77 | 4.0 | 45.0 | 42.0 | 42.0 | 42.0 | 0.0 | 0.065 | 0.0003 |
| idade W=10 | 0.81 | 4.0 | 11.1 | 8.1 | 8.1 | 6.0 | 0.0 | 0.065 | 0.0004 |
| tabu permanente | 0.04 | 19.2 | 18.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.066 | 0.0018 |
| tabu 20 rodadas | 0.15 | 12.2 | 78.0 | 66.8 | 66.8 | 63.8 | 0.0 | 0.066 | 0.0010 |
| persistência | 1.00 | 2.0 | 24.9 | 23.9 | 23.9 | 21.9 | 0.0 | 0.075 | 0.0002 |
| γ_max | 1.00 | 2.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.065 | 0.0002 |
| ganho | 0.77 | 4.0 | 45.0 | 42.0 | 42.0 | 42.0 | 42.0 | 0.065 | 0.0003 |
| γ_max + ganho | 1.00 | 2.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.065 | 0.0002 |
| pilha completa | 1.00 | 2.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.075 | 0.0002 |

**Pilha completa em cada calendário, cenário B**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| toda_rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.8 | 0.205 | 0.0004 |
| paridade | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.8 | 0.206 | 0.0004 |
| primos+naoprimos | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.8 | 0.209 | 0.0004 |
| primos+pares | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.8 | 0.209 | 0.0004 |
| primos+interprimos | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.9 | 0.209 | 0.0004 |
| periodo_4 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 19.5 | 0.213 | 0.0004 |

**Pior caso: subgrupos reais, split e merge aprovados ao mesmo tempo (K=2, w_sub=0.4, tolerância 0.1)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| sem espera | 0.47 | 4.0 | 45.0 | 42.0 | 42.0 | 42.0 | 42.0 | 0.132 | 0.0067 |
| espera crescente (base 10) | 0.47 | 4.0 | 7.0 | 4.0 | 4.0 | 4.0 | 4.0 | 0.110 | 0.0004 |

**O merge corrige o que o split errou (cenário C, γ_max mal calibrado em 0.68)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|---|
| só split, sem merge | 0.04 | 18.6 | 17.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.066 | 0.0018 |
| com merge verificado | 0.79 | 3.8 | 35.0 | 32.2 | 32.2 | 32.0 | 32.2 | 0.065 | 0.0003 |
| com merge verificado e espera | 0.94 | 2.4 | 19.3 | 17.9 | 17.9 | 11.1 | 17.9 | 0.065 | 0.0002 |

**Leitura.**

- Nenhuma guarda isolada acerta A, B e C com poucas operações. Tabu permanente acerta B e erra C. Ganho de fusão acerta B e não evita o laço em C. `γ_max` acerta C e não ajuda em B.
- `γ_max` + ganho de fusão acertam os três. Em todos os calendários, a pilha chega à mesma partição.
- A espera crescente reduz os testes de 122,7 para 20,9 no cenário B, e limita a oscilação no pior caso (de 45 para 7 splits). O limite teórico é `log2(R/W + 1) = 4` voltas, e o observado foi 4 merges.
- A última tabela mostra o merge corrigindo um split mal calibrado.

## A.7 Falsos splits em população homogênea

200 sementes. Sem merge e sem `γ_max`.

| ε2 | Calendário | Testes de split até R=150 | Falso split, regra instantânea | Rodada do 1º falso split | Falso split, persistência de 3 rodadas |
|---|---|---|---|---|---|
| 0.026 | toda_rodada | 134 | 0.99 | 23.1 | 0.38 |
| 0.026 | paridade | 67 | 0.95 | 23.0 | 0.29 |
| 0.026 | primos+interprimos | 31 | 0.93 | 23.0 | 0.01 |
| 0.026 | periodo_4 | 34 | 0.74 | 24.0 | 0.00 |
| 0.027 | toda_rodada | 134 | 0.58 | 23.1 | 0.02 |
| 0.027 | paridade | 67 | 0.54 | 23.0 | 0.02 |
| 0.027 | primos+interprimos | 31 | 0.54 | 23.0 | 0.00 |
| 0.027 | periodo_4 | 34 | 0.14 | 24.0 | 0.00 |
| 0.028 | toda_rodada | 134 | 0.10 | 23.2 | 0.00 |
| 0.028 | paridade | 67 | 0.07 | 23.0 | 0.00 |
| 0.028 | primos+interprimos | 31 | 0.07 | 23.0 | 0.00 |
| 0.028 | periodo_4 | 34 | 0.03 | 24.0 | 0.00 |

**Leitura.** O número de testes quase não importa com a regra instantânea, porque os falsos splits se concentram no cruzamento de `ε1` (rodada 23). Com persistência, o efeito do número de testes aparece. Período 4 tem menos falsos positivos que os primos com a regra instantânea, provavelmente por uma coincidência de fase: seu 1º falso split ocorre na rodada 24, e não na 23, um pouco mais longe do cruzamento. Isso não foi testado à parte.

## A.8 Faixa de `γ_max`

**α_cross^max medido na bipartição, no ponto estacionário do FL (N=48)**

| Caso | D=200 | √((1−α)/2) | D=20000 | √((1−α)/2) |
|---|---|---|---|---|
| K=2 | -0.896 | 0.974 | -0.919 | 0.980 |
| K=4 | -0.264 | 0.795 | -0.310 | 0.809 |
| K=8 | -0.093 | 0.739 | -0.132 | 0.752 |
| K=12 | -0.046 | 0.723 | -0.083 | 0.736 |
| K=1 (só ruído) | +0.095 | 0.673 | +0.010 | 0.704 |

**Efeito de γ_max por dimensão: cenário C (falso split) e K=8 (split correto), 8 sementes**

| D | γ_max | C: ARI | C: N final | K=8: ARI | K=8: N final |
|---|---|---|---|---|---|
| 200 | 0.68 | 0.79 | 3.9 | 1.00 | 8.0 |
| 200 | 0.7 | 0.97 | 2.2 | 1.00 | 8.0 |
| 200 | 0.72 | 1.00 | 2.0 | 1.00 | 8.0 |
| 200 | 0.74 | 1.00 | 2.0 | 1.00 | 8.0 |
| 200 | 0.76 | 1.00 | 2.0 | 0.00 | 1.0 |
| 2000 | 0.68 | 0.79 | 4.0 | 1.00 | 8.0 |
| 2000 | 0.7 | 0.86 | 3.5 | 1.00 | 8.0 |
| 2000 | 0.72 | 1.00 | 2.0 | 1.00 | 8.0 |
| 2000 | 0.74 | 1.00 | 2.0 | 1.00 | 8.0 |
| 2000 | 0.76 | 1.00 | 2.0 | 0.00 | 1.0 |
| 20000 | 0.68 | 0.83 | 4.0 | 1.00 | 8.0 |
| 20000 | 0.7 | 0.83 | 4.0 | 1.00 | 8.0 |
| 20000 | 0.72 | 1.00 | 2.0 | 1.00 | 8.0 |
| 20000 | 0.74 | 1.00 | 2.0 | 1.00 | 8.0 |
| 20000 | 0.76 | 1.00 | 2.0 | 0.00 | 1.0 |

**Leitura.** `γ_max` precisa ficar entre a linha do ruído e a linha de `K`. Se for alto demais, nunca há split (`K = 8` com `γ_max = 0,76`: ARI 0,00, N = 1). Se for baixo demais, o ruído passa. A linha do ruído sobe para 0,707 quando `D` cresce, estreitando a faixa. A cerca de 0,72 a 0,74, o toy funciona em todas as dimensões testadas.

## A.9 Dispersão angular

O `σ_θ` proposto na [especificação](../especificacao-isodata-fl.md), seção 2, medido no ponto estacionário do FL.

| Caso | σ_θ (graus) | ‖ΔW̄‖ / média ‖ΔW_i‖ | max_norm | α_cross^max |
|---|---|---|---|---|
| K=1, só ruído | 78.6 | 0.200 | 0.023 | +0.075 |
| K=1, desvio individual alto | 83.4 | 0.116 | 0.038 | +0.050 |
| K=2 | 86.8 | 0.057 | 0.076 | -0.899 |
| K=4 | 87.4 | 0.047 | 0.092 | -0.274 |

**Leitura.** `σ_θ` varia pouco entre os casos e não separa ruído de grupos opostos. `α_cross^max` separa com clareza.

## A.10 Composição, atraso e ligação

**Cosseno entre centros de ψ (A=1, K=4): efeito da composição do cluster**

| Composição | Teórico | Medido |
|---|---|---|
| 1 grupo x 1 grupo | 0.500 | 0.499 |
| 1 grupo x 3 grupos | 0.612 | 0.611 |
| 2 grupos x 2 grupos | 0.667 | 0.665 |

**Atraso até a partição correta, cenário A, pilha completa**

| Calendário | t_min | Testes de split | Rodada da partição correta | Perda média |
|---|---|---|---|---|
| toda_rodada | 7 | 134 | 44.1 | 0.111 |
| toda_rodada | 21 | 120 | 44.1 | 0.111 |
| paridade | 7 | 67 | 45.1 | 0.112 |
| primos+interprimos | 7 | 31 | 50.2 | 0.119 |
| primos+interprimos | 23 | 26 | 50.2 | 0.119 |
| periodo_4 | 8 | 34 | 49.5 | 0.118 |

**Ligação da bipartição (cenários A e C, sem γ_max nem merge)**

| Cenário | Ligação | ARI | N final | Splits | Menor filho (média) |
|---|---|---|---|---|---|
| A | single | 1.00 | 4.0 | 3.0 | 6.5 |
| A | complete | 1.00 | 4.0 | 3.0 | 7.3 |
| C | single | 0.04 | 19.2 | 18.2 | 1.8 |
| C | complete | 0.07 | 14.9 | 13.9 | 2.7 |

**Leitura.**

- O cosseno entre centros sobe em clusters mistos, e o valor medido coincide com o teórico.
- Os primos atrasam a partição correta em cerca de 6 rodadas, com 4,3 vezes menos testes, empatando com o período 4. `t_min` não faz diferença aqui, porque é `ε1` quem decide.
- *Complete* produz filhos um pouco maiores, sem mudar o quadro.

## A.11 Limites deste modelo

| O toy assume | Em redes reais | Consequência |
|---|---|---|
| Perda quadrática, um ótimo por grupo | Não convexa, com muitos mínimos | Não testa barreira de perda: a regra de modelo no merge (média, maior) não pode ser avaliada aqui |
| `ψ` é a direção até o ótimo | Empírico, sem teoria (guia 4.15.5) | A concordância entre `ψ` e `ΔW` é a pergunta de E0 |
| Ruído isotrópico | Estruturado, e clientes congruentes costumam ter cosseno positivo | Os valores de `γ_max` não se transferem |
| Perda de validação sem ruído | Validação finita | `δ = 0` é otimista, e `W_merge` não mostra ganho |
| Cliente isolado aprende bem | Com poucos dados, generaliza mal | Perda média otimista para clientes isolados |
| Participação total | Parcial é o caso interessante do StoCFL | Censo e clientes pendentes não foram testados |
| Convergência em dezenas de rodadas | Depende de lr, épocas e arquitetura | As rodadas não se comparam com as de redes reais |

## A.12 Como rodar

Requer Python 3.12 e NumPy (usados aqui: Python 3.12.3 e NumPy 2.5.4). O `.venv` da raiz não tem NumPy.

```bash
python3 -m venv /tmp/toy && /tmp/toy/bin/pip install numpy
# copie o código da seção A.13 para simulacao_isodata_fl.py
/tmp/toy/bin/python simulacao_isodata_fl.py tudo
```

As seções são `baselines`, `sinais`, `calendarios`, `guardas`, `falsos`, `dispersao`, `janela` e `limites`. A execução completa leva menos de 30 minutos em CPU, e as seções `janela` e `limites` são as mais demoradas. Rodar de novo `sinais` e `guardas` com o mesmo código reproduziu as saídas byte a byte.

## A.13 Código

```python
#!/usr/bin/env python3
"""Simulacao de brinquedo do calendario e das guardas do ISODATA-FL.

Clientes quadraticos: o treino local do cliente i puxa o modelo para
theta*_i = grupo + subgrupo + within * u_i. A perda de validacao mede a distancia
ate grupo + subgrupo: o desvio individual u_i nao generaliza (imita dados finitos).
Nao e rede neural: nao mede acuracia, barreira de perda nem o psi real.

Uso: python simulacao_isodata_fl.py [baselines|sinais|calendarios|guardas|falsos|dispersao|janela|limites|tudo]
"""
import sys
import numpy as np

D, C, RAIO = 200, 0.1, 1.0     # dimensao, passo efetivo do treino local, raio dos otimos


def eh_primo(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def calendario(nome, R, t_min=7, congelar=10):
    """Devolve (rodadas de split, rodadas de merge). As ultimas rodadas nao tem operadores."""
    fim = R - congelar
    todos = range(t_min, fim + 1)
    P = [t for t in range(t_min, 2 * R) if eh_primo(t)]
    inter = [(a + b) // 2 for a, b in zip(P, P[1:])]
    S = {t for t in P if t <= fim}
    if nome == "fedavg":
        return set(), set()
    if nome == "cfl_puro":          # como o notebook: toda rodada, depois da rodada 20
        return {t for t in range(21, fim + 1)}, set()
    if nome == "stocfl_puro":       # como os scripts: toda rodada, desde a primeira
        return set(), set(range(1, fim + 1))
    if nome == "toda_rodada":
        return set(todos), set(todos)
    if nome == "paridade":
        return {t for t in todos if t % 2}, {t for t in todos if t % 2 == 0}
    if nome == "primos+naoprimos":
        return S, {t for t in todos if not eh_primo(t)}
    if nome == "primos+pares":
        return S, {t for t in todos if t % 2 == 0}
    if nome == "primos+interprimos":
        return S, {t for t in inter if t <= fim}
    if nome == "periodo_4":
        return {t for t in todos if t % 4 == 0}, {t for t in todos if t % 4 == 2}
    raise ValueError(nome)


def ari(a, b):
    _, ia = np.unique(a, return_inverse=True)
    _, ib = np.unique(b, return_inverse=True)
    M = np.zeros((ia.max() + 1, ib.max() + 1))
    np.add.at(M, (ia, ib), 1)
    c2 = lambda x: x * (x - 1) / 2
    A, B, T = c2(M.sum(1)).sum(), c2(M.sum(0)).sum(), c2(len(a))
    esperado = A * B / T
    maximo = (A + B) / 2
    return 1.0 if maximo == esperado else (c2(M).sum() - esperado) / (maximo - esperado)


class Problema:
    def __init__(self, seed, N, K, A, within, sigma=0.02, w_sub=0.0):
        self.rng = np.random.default_rng(seed)
        Q, _ = np.linalg.qr(self.rng.normal(size=(D, 2 * K + 1)))
        self.sigma, self.N = sigma, N
        self.g = np.array([i * K // N for i in range(N)])
        sub = np.array([1 if (i * 2 * K // N) % 2 else -1 for i in range(N)])
        self.val_alvo = RAIO * Q[:, self.g].T + w_sub * sub[:, None] * Q[:, K + self.g].T
        u = self.rng.normal(size=(N, D))
        self.alvo = self.val_alvo + within * u / np.linalg.norm(u, axis=1, keepdims=True)
        self.theta0 = A * Q[:, 2 * K]
        self.psi = C * (self.theta0 - self.alvo) + self.ruido(N)   # medido uma vez, da ancora fixa

    def ruido(self, n):
        return self.sigma * self.rng.normal(size=(n, D)) / np.sqrt(D)

    def delta(self, theta, membros):
        return C * (self.alvo[membros] - theta) + self.ruido(len(membros))

    def perda_val(self, theta, membros):
        return 0.5 * ((self.val_alvo[membros] - theta) ** 2).sum(1)


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def matriz_cos(X):
    Y = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    return Y @ Y.T


def bipartir(S, ligacao="single"):
    """Aglomera ate restarem 2 grupos. Com single, e o Algoritmo 1 do artigo do CFL."""
    grupos = [[i] for i in range(len(S))]
    while len(grupos) > 2:
        melhor, par = -np.inf, None
        for a in range(len(grupos)):
            for b in range(a + 1, len(grupos)):
                sim = S[np.ix_(grupos[a], grupos[b])]
                v = sim.max() if ligacao == "single" else sim.min()
                if v > melhor:
                    melhor, par = v, (a, b)
        grupos[par[0]] += grupos.pop(par[1])
    return grupos


def componentes(A):
    """Componentes conexas de uma matriz de adjacencia (single linkage com corte)."""
    n, vistos, saida = len(A), set(), []
    for i in range(n):
        if i in vistos:
            continue
        pilha, grupo = [i], []
        while pilha:
            x = pilha.pop()
            if x not in vistos:
                vistos.add(x)
                grupo.append(x)
                pilha.extend(np.flatnonzero(A[x]).tolist())
        saida.append(grupo)
    return saida


class Cluster:
    def __init__(self, membros, theta, nasc):
        self.membros, self.theta, self.nasc = np.array(sorted(membros)), theta.copy(), nasc
        self.abaixo = 0      # rodadas seguidas com mean_norm < eps1


def rodar(seed, N=24, K=4, A=1.0, within=0.05, R=150, tau=0.65, eps1=0.015, eps2=0.05, cal="primos+interprimos",
          gamma=None, ganho=None, W_merge=0, W_split=0, tabu=None, espera=None, t_min=7, ligacao="single",
          sigma=0.02, w_sub=0.0, persiste=1, partida="unico", pequeno=0):
    """gamma: teste de gamma_max no split. ganho: tolerancia do ganho de fusao no merge.
    W_*: idade minima. tabu: bloqueio fixo de reuniao apos split. espera: base da espera crescente nos dois sentidos.
    persiste: rodadas seguidas com mean_norm < eps1 exigidas para o split (1 = regra instantanea do CFL).
    partida: "unico" = 1 cluster com todos (CFL); "psi" = componentes do grafo cos(psi) >= tau na rodada 1.
    pequeno: cluster com menos membros que isso testa fusao mesmo abaixo de tau (exige ganho)."""
    p = Problema(seed, N, K, A, within, sigma, w_sub)
    S_cal, M_cal = calendario(cal, R, t_min)
    if cal == "stocfl_puro":
        cl = [Cluster([i], p.theta0, 1) for i in range(N)]
    elif partida == "psi":
        cl = [Cluster(g, p.theta0, 1) for g in componentes(matriz_cos(p.psi) >= tau)]
    else:
        cl = [Cluster(range(N), p.theta0, 1)]
    separados = np.zeros((N, N), dtype=int)      # vezes que o par foi separado por split
    unidos = np.zeros((N, N), dtype=int)         # vezes que o par foi unido por merge
    nao_unir = np.zeros((N, N), dtype=int)       # rodada ate a qual o par nao pode ser unido
    nao_separar = np.zeros((N, N), dtype=int)    # rodada ate a qual o par nao pode ser separado
    reprovados = np.zeros((N, N), dtype=int)     # vezes que o par foi reprovado no teste de ganho
    H = dict(splits=0, merges=0, m_desfaz_s=0, s_desfaz_m=0, testes=0, menor_filho=[], t_correta=np.nan, recusados=0,
             t_primeiro_split=np.nan)
    curva = []
    for t in range(1, R + 1):
        novos = []
        for c in cl:
            d = p.delta(c.theta, c.membros)
            media, maximo = np.linalg.norm(d.mean(0)), np.linalg.norm(d, axis=1).max()
            c.abaixo = c.abaixo + 1 if media < eps1 else 0
            filhos = None
            if (t in S_cal and c.abaixo >= persiste and maximo > eps2 and len(c.membros) > 2 and t - c.nasc >= W_split):
                Sm = matriz_cos(d)
                i1, i2 = bipartir(Sm, ligacao)
                alfa = Sm[np.ix_(i1, i2)].max()
                m1, m2 = c.membros[i1], c.membros[i2]
                if gamma is not None and not gamma < np.sqrt((1 - alfa) / 2):
                    H["recusados"] += 1
                elif (nao_separar[np.ix_(m1, m2)] > t).any():
                    H["recusados"] += 1
                else:
                    filhos = (i1, i2, m1, m2)
            if filhos:
                i1, i2, m1, m2 = filhos
                H["splits"] += 1
                if np.isnan(H["t_primeiro_split"]):
                    H["t_primeiro_split"] = t
                H["menor_filho"].append(min(len(m1), len(m2)))
                if unidos[np.ix_(m1, m2)].any():
                    H["s_desfaz_m"] += 1
                separados[np.ix_(m1, m2)] += 1
                separados[np.ix_(m2, m1)] += 1
                bloqueio = 0
                if tabu is not None:
                    bloqueio = tabu
                if espera is not None:
                    bloqueio = espera * 2 ** (int(separados[np.ix_(m1, m2)].max()) - 1)
                nao_unir[np.ix_(m1, m2)] = np.maximum(nao_unir[np.ix_(m1, m2)], t + bloqueio)
                nao_unir[np.ix_(m2, m1)] = np.maximum(nao_unir[np.ix_(m2, m1)], t + bloqueio)
                novos.append(Cluster(m1, c.theta + d[i1].mean(0), t))
                novos.append(Cluster(m2, c.theta + d[i2].mean(0), t))
            else:
                c.theta = c.theta + d.mean(0)
                novos.append(c)
        cl = novos

        if t in M_cal and len(cl) > 1:
            centros = [p.psi[c.membros].mean(0) for c in cl]
            pares = sorted(((cos(centros[i], centros[j]), i, j) for i in range(len(cl))
                            for j in range(i + 1, len(cl))), reverse=True)
            usados, fora = set(), set()
            for sim, i, j in pares:
                if i in usados or j in usados:       # regra do ISODATA: cada cluster se funde uma vez por janela
                    continue
                a, b = cl[i], cl[j]
                if sim < tau and not (ganho is not None and min(len(a.membros), len(b.membros)) < pequeno):
                    continue
                if t - a.nasc < W_merge or t - b.nasc < W_merge:
                    continue
                if (nao_unir[np.ix_(a.membros, b.membros)] > t).any():
                    continue
                na, nb = len(a.membros), len(b.membros)
                th = (na * a.theta + nb * b.theta) / (na + nb)
                if ganho is not None:
                    H["testes"] += 1
                    uniao = np.concatenate([a.membros, b.membros])
                    atual = np.concatenate([p.perda_val(a.theta, a.membros), p.perda_val(b.theta, b.membros)]).mean()
                    if p.perda_val(th, uniao).mean() > atual + ganho:
                        reprovados[np.ix_(a.membros, b.membros)] += 1
                        reprovados[np.ix_(b.membros, a.membros)] += 1
                        if espera is not None:       # adia o reteste do par reprovado, com espera crescente
                            fim = t + espera * 2 ** (int(reprovados[np.ix_(a.membros, b.membros)].max()) - 1)
                            nao_unir[np.ix_(a.membros, b.membros)] = fim
                            nao_unir[np.ix_(b.membros, a.membros)] = fim
                        continue
                if separados[np.ix_(a.membros, b.membros)].any():
                    H["m_desfaz_s"] += 1
                unidos[np.ix_(a.membros, b.membros)] += 1
                unidos[np.ix_(b.membros, a.membros)] += 1
                if espera is not None:
                    fim = t + espera * 2 ** (int(unidos[np.ix_(a.membros, b.membros)].max()) - 1)
                    nao_separar[np.ix_(a.membros, b.membros)] = np.maximum(nao_separar[np.ix_(a.membros, b.membros)], fim)
                    nao_separar[np.ix_(b.membros, a.membros)] = np.maximum(nao_separar[np.ix_(b.membros, a.membros)], fim)
                H["merges"] += 1
                usados |= {i, j}
                fora.add(j)
                cl[i] = Cluster(np.concatenate([a.membros, b.membros]), th, t)
            cl = [c for k, c in enumerate(cl) if k not in fora]

        curva.append(sum(p.perda_val(c.theta, c.membros).sum() for c in cl) / N)
        rot = np.zeros(N, dtype=int)
        for k, c in enumerate(cl):
            rot[c.membros] = k
        qualidade = ari(rot, p.g) if K > 1 else float(len(cl) == 1)
        if qualidade == 1.0 and np.isnan(H["t_correta"]):
            H["t_correta"] = t
        elif qualidade < 1.0:
            H["t_correta"] = np.nan
    H.update(ari=qualidade, N_final=len(cl), perda_final=curva[-1], perda_media=float(np.mean(curva)),
             menor_filho=float(np.mean(H["menor_filho"])) if H["menor_filho"] else np.nan)
    return H


def media_config(sementes=30, **cfg):
    r = [rodar(s, **cfg) for s in range(sementes)]
    return {k: float(np.nanmean([x[k] for x in r])) if not all(np.isnan(x[k]) for x in r) else np.nan for k in r[0]}


CAB = ("| Configuração | ARI | N final | Splits | Merges | M desfaz S | S desfaz M | Testes de fusão | Perda média | Perda final |\n"
       "|---|---|---|---|---|---|---|---|---|---|")


def imprimir(nome, m):
    print(f"| {nome} | {m['ari']:.2f} | {m['N_final']:.1f} | {m['splits']:.1f} | {m['merges']:.1f} | "
          f"{m['m_desfaz_s']:.1f} | {m['s_desfaz_m']:.1f} | {m['testes']:.1f} | {m['perda_media']:.3f} | {m['perda_final']:.4f} |")


CENARIOS = {
    "A (ψ separa os grupos)": dict(K=4, A=1.0),                 # cruzado ~0.50 < tau
    "B (ψ não separa os grupos)": dict(K=4, A=2.5),             # cruzado ~0.86 >= tau
    "C (ε2 baixo, sobredivisão)": dict(K=2, A=1.0, eps2=0.012),
}
PILHA = dict(gamma=0.72, persiste=3, ganho=0.0, W_merge=10, espera=10)


def baselines(sementes=30):
    """Cada algoritmo sozinho contra o hibrido."""
    C_ = {**CENARIOS, "D (K=1, população homogênea, ε2 baixo)": dict(K=1, A=1.0, eps2=0.012),
          "E (τ alto demais: ψ não une nem o mesmo grupo)": dict(K=4, A=1.0, tau=0.995)}
    for cen, kw in C_.items():
        print(f"\n**Cenário {cen}**\n\n{CAB}")
        imprimir("FedAvg", media_config(sementes, cal="fedavg", **kw))
        imprimir("CFL puro", media_config(sementes, cal="cfl_puro", **kw))
        imprimir("StoCFL puro", media_config(sementes, cal="stocfl_puro", **kw))
        imprimir("Híbrido sem guardas", media_config(sementes, **kw))
        imprimir("Híbrido com a pilha, partida única", media_config(sementes, **{**kw, **PILHA}))
        imprimir("Híbrido com a pilha, partida por ψ", media_config(sementes, partida="psi", **{**kw, **PILHA}))
        imprimir("Híbrido com a pilha, partida por ψ, cluster pequeno < 6", media_config(sementes, partida="psi", pequeno=6, **{**kw, **PILHA}))


def sinais(sementes=100, W=(1, 5, 10, 20, 40)):
    """Candidatos a metrica de merge, W rodadas depois de um split forcado."""
    casos = {"split correto (K=2)": dict(K=2, within=0.05), "split falso, ruído domina (K=1)": dict(K=1, within=0.05),
             "split falso, desvio individual alto (K=1)": dict(K=1, within=0.3),
             "split falso, quase sem ruído (K=1, σ=0.001)": dict(K=1, within=0.3, sigma=0.001)}
    for nome, kw in casos.items():
        print(f"\n**{nome}**\n")
        print("| W | cos ψ | cos ΔW̄ próprio | cos ΔW̄ em θ_m | cos deslocamento | α_cross em θ_m | dist. relativa | perda cruzada D | ganho de fusão |")
        print("|---|---|---|---|---|---|---|---|---|")
        for w in W:
            lin = []
            for s in range(sementes):
                p = Problema(s, 24, kw["K"], 1.0, kw["within"], kw.get("sigma", 0.02))
                todos = np.arange(24)
                th = p.theta0.copy()
                for _ in range(60):
                    th = th + p.delta(th, todos).mean(0)
                dp = p.delta(th, todos)
                i1, i2 = bipartir(matriz_cos(dp))
                a, b = todos[i1], todos[i2]
                ta, tb = th + dp[i1].mean(0), th + dp[i2].mean(0)
                for _ in range(w):
                    ta = ta + p.delta(ta, a).mean(0)
                    tb = tb + p.delta(tb, b).mean(0)
                tm = (len(a) * ta + len(b) * tb) / 24
                da, db = p.delta(tm, a), p.delta(tm, b)
                Sm = matriz_cos(np.vstack([da, db]))
                Laa, Lbb = p.perda_val(ta, a).mean(), p.perda_val(tb, b).mean()
                Lab, Lba = p.perda_val(tb, a).mean(), p.perda_val(ta, b).mean()
                atual = (len(a) * Laa + len(b) * Lbb) / 24
                lin.append([cos(p.psi[a].mean(0), p.psi[b].mean(0)), cos(p.delta(ta, a).mean(0), p.delta(tb, b).mean(0)),
                            cos(da.mean(0), db.mean(0)), cos(ta - th, tb - th), Sm[:len(a), len(a):].max(),
                            np.linalg.norm(ta - tb) / np.linalg.norm(th - p.theta0), max(Lab - Laa, Lba - Lbb, 0.0),
                            p.perda_val(tm, todos).mean() - atual])
            x = np.array(lin)
            print(f"| {w} | " + " | ".join(f"{m:+.3f}" for m in x.mean(0)) + " |")


def calendarios(sementes=30):
    nomes = ["toda_rodada", "paridade", "primos+naoprimos", "primos+pares", "primos+interprimos", "periodo_4"]
    for cen, kw in CENARIOS.items():
        print(f"\n**Cenário {cen}, sem nenhuma guarda**\n\n{CAB}")
        for n in nomes:
            imprimir(n, media_config(sementes, cal=n, **kw))


def guardas(sementes=30):
    G = {"nenhuma": {}, "idade W=10": dict(W_merge=10, W_split=10), "tabu permanente": dict(tabu=10 ** 6),
         "tabu 20 rodadas": dict(tabu=20), "persistência": dict(persiste=3), "γ_max": dict(gamma=0.72),
         "ganho": dict(ganho=0.0), "γ_max + ganho": dict(gamma=0.72, ganho=0.0), "pilha completa": PILHA}
    for cen, kw in CENARIOS.items():
        print(f"\n**Cenário {cen}, calendário primos+interprimos**\n\n{CAB}")
        for n, g in G.items():
            imprimir(n, media_config(sementes, **{**kw, **g}))
    print(f"\n**Pilha completa em cada calendário, cenário B**\n\n{CAB}")
    for n in ["toda_rodada", "paridade", "primos+naoprimos", "primos+pares", "primos+interprimos", "periodo_4"]:
        imprimir(n, media_config(sementes, cal=n, **{**CENARIOS["B (ψ não separa os grupos)"], **PILHA}))
    print("\n**Pior caso: subgrupos reais, split e merge aprovados ao mesmo tempo (K=2, w_sub=0.4, tolerância 0.1)**\n")
    print(CAB)
    base = dict(K=2, A=1.0, w_sub=0.4, eps2=0.03, gamma=0.72, ganho=0.1)
    imprimir("sem espera", media_config(sementes, **base))
    imprimir("espera crescente (base 10)", media_config(sementes, espera=10, **base))
    print(f"\n**O merge corrige o que o split errou (cenário C, γ_max mal calibrado em 0.68)**\n\n{CAB}")
    base = dict(K=2, A=1.0, eps2=0.012, gamma=0.68)
    imprimir("só split, sem merge", media_config(sementes, tau=2.0, **base))
    imprimir("com merge verificado", media_config(sementes, ganho=0.0, **base))
    imprimir("com merge verificado e espera", media_config(sementes, ganho=0.0, espera=10, **base))


def falsos(sementes=200):
    """Populacao homogenea, sem merge e sem gamma: efeito do numero de testes e da persistencia."""
    print("| ε2 | Calendário | Testes de split até R=150 | Falso split, regra instantânea | Rodada do 1º falso split | "
          "Falso split, persistência de 3 rodadas |")
    print("|---|---|---|---|---|---|")
    for e2 in (0.026, 0.027, 0.028):
        for n in ["toda_rodada", "paridade", "primos+interprimos", "periodo_4"]:
            r = [rodar(s, K=1, A=1.0, eps2=e2, cal=n, tau=2.0) for s in range(sementes)]
            q = [rodar(s, K=1, A=1.0, eps2=e2, cal=n, tau=2.0, persiste=3) for s in range(sementes)]
            prim = [x["t_primeiro_split"] for x in r if x["splits"] > 0]
            print(f"| {e2} | {n} | {len(calendario(n, 150)[0])} | {np.mean([x['splits'] > 0 for x in r]):.2f} | "
                  f"{np.mean(prim) if prim else float('nan'):.1f} | {np.mean([x['splits'] > 0 for x in q]):.2f} |")


def dispersao(sementes=30):
    """O desvio angular da especificacao (sigma_theta) separa ruido de grupos opostos?"""
    print("| Caso | σ_θ (graus) | ‖ΔW̄‖ / média ‖ΔW_i‖ | max_norm | α_cross^max |\n|---|---|---|---|---|")
    for nome, K_, wi in (("K=1, só ruído", 1, 0.05), ("K=1, desvio individual alto", 1, 0.3), ("K=2", 2, 0.05), ("K=4", 4, 0.05)):
        lin = []
        for s in range(sementes):
            p = Problema(s, 24, K_, 1.0, wi)
            todos = np.arange(24)
            th = p.theta0.copy()
            for _ in range(60):
                th = th + p.delta(th, todos).mean(0)
            d = p.delta(th, todos)
            m = d.mean(0)
            ang = np.degrees(np.arccos(np.clip([cos(x, m) for x in d], -1, 1)))
            Sm = matriz_cos(d)
            i1, i2 = bipartir(Sm)
            lin.append([np.sqrt((ang ** 2).mean()), np.linalg.norm(m) / np.linalg.norm(d, axis=1).mean(),
                        np.linalg.norm(d, axis=1).max(), Sm[np.ix_(i1, i2)].max()])
        x = np.array(lin).mean(0)
        print(f"| {nome} | {x[0]:.1f} | {x[1]:.3f} | {x[2]:.3f} | {x[3]:+.3f} |")


def janela_gamma():
    """A faixa util de gamma_max depende da dimensao D e do numero de grupos K."""
    global D
    print("\n**α_cross^max medido na bipartição, no ponto estacionário do FL (N=48)**\n")
    print("| Caso | D=200 | √((1−α)/2) | D=20000 | √((1−α)/2) |\n|---|---|---|---|---|")
    for nome, K_ in (("K=2", 2), ("K=4", 4), ("K=8", 8), ("K=12", 12), ("K=1 (só ruído)", 1)):
        lin = []
        for D in (200, 20000):
            al = []
            for s in range(20):
                p = Problema(s, 48, K_, 1.0, 0.05)
                todos = np.arange(48)
                th = p.theta0.copy()
                for _ in range(60):
                    th = th + p.delta(th, todos).mean(0)
                Sm = matriz_cos(p.delta(th, todos))
                i1, i2 = bipartir(Sm)
                al.append(Sm[np.ix_(i1, i2)].max())
            lin.append(float(np.mean(al)))
        print(f"| {nome} | {lin[0]:+.3f} | {np.sqrt((1 - lin[0]) / 2):.3f} | {lin[1]:+.3f} | {np.sqrt((1 - lin[1]) / 2):.3f} |")
    print("\n**Efeito de γ_max por dimensão: cenário C (falso split) e K=8 (split correto), 8 sementes**\n")
    print("| D | γ_max | C: ARI | C: N final | K=8: ARI | K=8: N final |\n|---|---|---|---|---|---|")
    for D in (200, 2000, 20000):
        for g in (0.68, 0.70, 0.72, 0.74, 0.76):
            c = media_config(8, K=2, A=1.0, eps2=0.012, gamma=g, ganho=0.0)
            k = media_config(8, N=48, K=8, A=1.0, R=250, gamma=g, ganho=0.0)
            print(f"| {D} | {g} | {c['ari']:.2f} | {c['N_final']:.1f} | {k['ari']:.2f} | {k['N_final']:.1f} |", flush=True)
    D = 200


def limites(sementes=30):
    print("\n**Cosseno entre centros de ψ (A=1, K=4): efeito da composição do cluster**\n")
    print("| Composição | Teórico | Medido |\n|---|---|---|")
    casos = {"1 grupo x 1 grupo": ([0], [1]), "1 grupo x 3 grupos": ([0], [1, 2, 3]), "2 grupos x 2 grupos": ([0, 1], [2, 3])}
    for nome, (x, y) in casos.items():
        A2, r2 = 1.0, RAIO ** 2
        teor = A2 / np.sqrt((A2 + r2 / len(x)) * (A2 + r2 / len(y)))
        med = []
        for s in range(sementes):
            p = Problema(s, 24, 4, 1.0, 0.05)
            med.append(cos(p.psi[np.isin(p.g, x)].mean(0), p.psi[np.isin(p.g, y)].mean(0)))
        print(f"| {nome} | {teor:.3f} | {np.mean(med):.3f} |")
    print("\n**Atraso até a partição correta, cenário A, pilha completa**\n")
    print("| Calendário | t_min | Testes de split | Rodada da partição correta | Perda média |\n|---|---|---|---|---|")
    for n, tm in [("toda_rodada", 7), ("toda_rodada", 21), ("paridade", 7), ("primos+interprimos", 7),
                  ("primos+interprimos", 23), ("periodo_4", 8)]:
        m = media_config(sementes, cal=n, t_min=tm, **{**CENARIOS["A (ψ separa os grupos)"], **PILHA})
        print(f"| {n} | {tm} | {len(calendario(n, 150, tm)[0])} | {m['t_correta']:.1f} | {m['perda_media']:.3f} |")
    print("\n**Ligação da bipartição (cenários A e C, sem γ_max nem merge)**\n")
    print("| Cenário | Ligação | ARI | N final | Splits | Menor filho (média) |\n|---|---|---|---|---|---|")
    for cen, kw in [("A", dict(K=4, A=1.0)), ("C", dict(K=2, A=1.0, eps2=0.012))]:
        for lig in ("single", "complete"):
            m = media_config(sementes, ligacao=lig, tau=2.0, **kw)
            print(f"| {cen} | {lig} | {m['ari']:.2f} | {m['N_final']:.1f} | {m['splits']:.1f} | {m['menor_filho']:.1f} |")


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    for nome, f in [("baselines", baselines), ("sinais", sinais), ("calendarios", calendarios), ("guardas", guardas),
                    ("falsos", falsos), ("dispersao", dispersao), ("janela", janela_gamma), ("limites", limites)]:
        if alvo in (nome, "tudo"):
            f()
```
