# Anexo A. Simulação de brinquedo

> **O que isto é e o que não é.** Um modelo quadrático, feito para testar o raciocínio do plano antes de escrever qualquer código de verdade. Ele **mostra mecanismos** (quem desfaz quem, e por quê). **Não prevê** acurácia, nem valores de `τ`, `γ_max` ou `ε` em redes neurais. As tabelas foram geradas pelo código da seção A.16, sem edição.
>
> O código está neste Markdown, e não em um `.py`, porque o repositório ainda está em fase de planejamento (D-005, D-011 e D-012 em [decisoes.md](../../decisoes.md)).

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

**Pilha completa:** `γ_max = 0,72`, persistência de 3 rodadas, ganho de fusão com tolerância 0 e espera crescente de base 10. A primeira versão deste plano incluía também `W_merge = 10`, que os testes de A.11 descartaram. Salvo indicação em contrário, o calendário das tabelas é primos e interprimos. **Combinação recomendada:** a pilha, com split em primos até 70% das rodadas e merge nas pares (A.12).

**Médias de 30 sementes**, salvo indicação em contrário.

## A.2 Cenários

| Cenário | Configuração | O que testa |
|---|---|---|
| A | `K = 4`, `A = 1` | Tudo funciona: `ψ` e CFL concordam |
| B | `K = 4`, `A = 2,5` | `ψ` não separa: o merge quer desfazer todo split correto |
| C | `K = 2`, `A = 1`, `ε2 = 0,012` | `ε2` baixo: o CFL divide grupos homogêneos por ruído |
| D | `K = 1`, `A = 1`, `ε2 = 0,012` | População homogênea: não deveria dividir |
| E | `K = 4`, `A = 1`, `τ = 0,995` | `τ` alto demais: `ψ` não une nem clientes do mesmo grupo |

**Métricas.** ARI compara com o ground truth, e com `K = 1` vale 1 se houver um único cluster. "M desfaz S" conta merges que unem clientes já separados por um split. "S desfaz M" conta splits que separam clientes já unidos por um merge. Perda média é a média da perda de validação ao longo das rodadas. "Partição correta" é a rodada a partir da qual a partição fica certa, na média das execuções que terminam certas.

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
| Híbrido com a pilha, partida única | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.2 | 0.209 | 0.0004 |
| Híbrido com a pilha, partida por ψ | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.2 | 0.209 | 0.0004 |
| Híbrido com a pilha, partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.2 | 0.209 | 0.0004 |

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
| pilha completa | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.2 | 0.209 | 0.0004 |

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
| toda_rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.0 | 0.205 | 0.0004 |
| paridade | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.0 | 0.206 | 0.0004 |
| primos+naoprimos | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.0 | 0.209 | 0.0004 |
| primos+pares | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 21.0 | 0.209 | 0.0004 |
| primos+interprimos | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.0 | 20.2 | 0.209 | 0.0004 |
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
- A espera crescente reduz os testes de 122,7 para 20,2 no cenário B, e limita a oscilação no pior caso (de 45 para 7 splits). O limite teórico é `log2(R/W + 1) = 4` voltas, e o observado foi 4 merges.
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

## A.11 Testes feitos para as decisões pendentes

Cada subseção alimenta uma decisão de [11-decisoes-pendentes.md](11-decisoes-pendentes.md), que traz a interpretação. "`γ_max` mal calibrado" significa 0,68, valor que deixa splits falsos passarem: é o caso em que o merge é realmente necessário.

### DP-01: partida

**DP-01: partida única (K=4; cosseno de ψ: 0,50 entre grupos, 0,98 dentro do grupo)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| τ = 0.3 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 50.2 | 0.119 |
| τ = 0.45 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 50.2 | 0.119 |
| τ = 0.65 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| τ = 0.9 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 50.2 | 0.119 |
| τ = 0.995 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 50.2 | 0.119 |

**DP-01: partida por ψ (K=4; cosseno de ψ: 0,50 entre grupos, 0,98 dentro do grupo)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| τ = 0.3 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 50.2 | 0.119 |
| τ = 0.45 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 50.2 | 0.119 |
| τ = 0.65 | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 |
| τ = 0.9 | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 |
| τ = 0.995 | 0.00 | 24.0 | 0.0 | 0.0 | 0.0 | — | 0.031 |

**DP-01: partida por ψ, cluster pequeno < 6 (K=4; cosseno de ψ: 0,50 entre grupos, 0,98 dentro do grupo)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| τ = 0.3 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 50.2 | 0.119 |
| τ = 0.45 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 50.2 | 0.119 |
| τ = 0.65 | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 |
| τ = 0.9 | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 |
| τ = 0.995 | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 15.0 | 0.029 |

**Leitura.** A partida única não depende de `τ`. A partida por `ψ` só falha com `τ` alto, e o caminho de cluster pequeno conserta isso. Com `τ` baixo, ela cai na partida única, sem dano.

### DP-02: calendário do split

**DP-02: calendário, cenário A**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| primos+interprimos | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| primos+pares | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| periodo_4 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 49.5 | 0.118 |
| paridade | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 45.1 | 0.112 |
| toda_rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 44.1 | 0.111 |
| fases | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 50.2 | 0.119 |
| parada_50 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| parada_70 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| parada_90 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| pares_parada_50 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| pares_parada_70 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |
| pares_parada_90 | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 |

**DP-02: calendário, cenário B**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| primos+interprimos | 1.00 | 4.0 | 3.0 | 0.0 | 20.2 | 56.8 | 0.209 |
| primos+pares | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 |
| periodo_4 | 1.00 | 4.0 | 3.0 | 0.0 | 19.5 | 57.2 | 0.213 |
| paridade | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 53.6 | 0.206 |
| toda_rodada | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 52.1 | 0.205 |
| fases | 1.00 | 4.0 | 3.0 | 0.0 | 18.0 | 56.8 | 0.209 |
| parada_50 | 1.00 | 4.0 | 3.0 | 0.0 | 20.2 | 56.8 | 0.209 |
| parada_70 | 1.00 | 4.0 | 3.0 | 0.0 | 20.2 | 56.8 | 0.209 |
| parada_90 | 1.00 | 4.0 | 3.0 | 0.0 | 20.2 | 56.8 | 0.209 |
| pares_parada_50 | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 |
| pares_parada_70 | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 |
| pares_parada_90 | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 |

**DP-02: calendário, cenário C com γ_max mal calibrado (0,68)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| primos+interprimos | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 130.4 | 0.075 |
| primos+pares | 0.99 | 2.1 | 14.4 | 13.2 | 13.2 | 132.8 | 0.075 |
| periodo_4 | 0.94 | 2.5 | 19.8 | 18.3 | 18.3 | 127.1 | 0.067 |
| paridade | 0.98 | 2.3 | 21.3 | 20.0 | 20.0 | 127.8 | 0.069 |
| toda_rodada | 0.75 | 4.7 | 27.4 | 23.7 | 23.7 | 122.5 | 0.067 |
| fases | 1.00 | 2.0 | 7.1 | 6.1 | 6.1 | 86.0 | 0.075 |
| parada_50 | 1.00 | 2.0 | 5.7 | 4.7 | 4.7 | 84.2 | 0.075 |
| parada_70 | 1.00 | 2.0 | 10.8 | 9.8 | 9.8 | 126.0 | 0.075 |
| parada_90 | 0.94 | 2.3 | 13.4 | 12.1 | 12.1 | 130.4 | 0.075 |
| pares_parada_50 | 1.00 | 2.0 | 5.7 | 4.7 | 4.7 | 80.9 | 0.075 |
| pares_parada_70 | 1.00 | 2.0 | 11.0 | 10.0 | 10.0 | 122.1 | 0.075 |
| pares_parada_90 | 0.99 | 2.1 | 14.3 | 13.2 | 13.2 | 132.8 | 0.075 |

**Leitura.** Em A e B, todos acertam, e o que muda é o atraso. Com `γ_max` mal calibrado, parar os splits antes do fim, em 70% ou 50% das rodadas, é o que chega a 1,00. Toda rodada é o pior caso.

### DP-03: calendário do merge

**DP-03: merge em cada calendário, cenário C com γ_max mal calibrado (0,68), pilha completa**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| primos+interprimos | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 130.4 | 0.075 |
| primos+pares | 0.99 | 2.1 | 14.4 | 13.2 | 13.2 | 132.8 | 0.075 |
| primos+naoprimos | 0.97 | 2.3 | 14.7 | 13.4 | 13.4 | 132.2 | 0.075 |

**DP-03: merge em cada calendário, cenário E com partida por ψ, pilha completa**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| primos+interprimos | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 15.0 | 0.029 |
| primos+pares | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 12.0 | 0.029 |
| primos+naoprimos | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 10.0 | 0.029 |

**Leitura.** Mais janelas de merge corrigem um pouco mais cedo, com o mesmo número de testes, porque a espera limita os testes.

### DP-04: como verificar o merge

**DP-04: verificação, cenário B (o merge deve recusar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| só ψ, sem teste | 0.63 | 2.8 | 7.3 | 5.6 | 5.6 | 0.0 | 0.1593 |
| ganho de fusão | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| perda cruzada, tolerância 0 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| perda cruzada, tolerância 0,05 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| α_cross em θ_m | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |

**DP-04: verificação, cenário C com γ_max mal calibrado (o merge deve aceitar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| só ψ, sem teste | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 0.0 | 0.0002 |
| ganho de fusão | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 12.1 | 0.0002 |
| perda cruzada, tolerância 0 | 0.04 | 18.4 | 17.4 | 0.0 | 0.0 | 164.5 | 0.0018 |
| perda cruzada, tolerância 0,05 | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 12.1 | 0.0002 |
| α_cross em θ_m | 0.76 | 4.6 | 14.2 | 10.6 | 10.6 | 16.8 | 0.0004 |

**DP-04: verificação, cenário E com partida por ψ (o merge deve aceitar só dentro do grupo)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| só ψ, sem teste | 0.00 | 24.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0023 |
| ganho de fusão | 1.00 | 4.0 | 0.0 | 20.0 | 0.0 | 26.0 | 0.0004 |
| perda cruzada, tolerância 0 | 0.00 | 24.0 | 0.0 | 0.0 | 0.0 | 1104.0 | 0.0023 |
| perda cruzada, tolerância 0,05 | 1.00 | 4.0 | 0.0 | 20.0 | 0.0 | 26.0 | 0.0004 |
| α_cross em θ_m | 1.00 | 4.0 | 0.0 | 20.0 | 0.0 | 26.0 | 0.0004 |

**Leitura.** Sem teste, o merge desfaz splits corretos. Perda cruzada com tolerância 0 reprova quase tudo. `α_cross` é pior quando o merge é necessário.

**DP-04: ruído na validação, cenário B (o merge deve recusar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| σ_val = 0.0, δ = 0 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| σ_val = 0.0, δ = 2 erros padrão | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| σ_val = 0.0, δ = 2 erros padrão, sem espera | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 116.4 | 0.0004 |
| σ_val = 0.1, δ = 0 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| σ_val = 0.1, δ = 2 erros padrão | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| σ_val = 0.1, δ = 2 erros padrão, sem espera | 1.00 | 4.0 | 3.2 | 0.2 | 0.2 | 115.0 | 0.0004 |
| σ_val = 0.3, δ = 0 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.1 | 0.0004 |
| σ_val = 0.3, δ = 2 erros padrão | 0.88 | 3.6 | 4.9 | 2.3 | 2.3 | 15.6 | 0.0475 |
| σ_val = 0.3, δ = 2 erros padrão, sem espera | 0.10 | 1.3 | 12.9 | 12.6 | 12.6 | 17.9 | 0.3384 |
| σ_val = 1.0, δ = 0 | 0.79 | 3.4 | 5.5 | 3.2 | 3.2 | 14.9 | 0.0808 |
| σ_val = 1.0, δ = 2 erros padrão | 0.68 | 2.9 | 7.1 | 5.1 | 5.1 | 6.0 | 0.1379 |
| σ_val = 1.0, δ = 2 erros padrão, sem espera | 0.00 | 1.0 | 13.7 | 13.7 | 13.7 | 14.2 | 0.3751 |

**DP-04: ruído na validação, cenário C com γ_max mal calibrado (o merge deve aceitar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| σ_val = 0.0, δ = 0 | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 12.1 | 0.0002 |
| σ_val = 0.0, δ = 2 erros padrão | 0.94 | 2.4 | 13.5 | 12.1 | 12.1 | 12.1 | 0.0002 |
| σ_val = 0.0, δ = 2 erros padrão, sem espera | 0.99 | 2.1 | 20.1 | 19.0 | 19.0 | 19.0 | 0.0002 |
| σ_val = 0.1, δ = 0 | 0.54 | 6.4 | 19.2 | 13.8 | 13.8 | 26.7 | 0.0006 |
| σ_val = 0.1, δ = 2 erros padrão | 0.84 | 3.3 | 14.5 | 12.2 | 12.2 | 14.1 | 0.0003 |
| σ_val = 0.1, δ = 2 erros padrão, sem espera | 0.97 | 2.4 | 20.6 | 19.2 | 19.2 | 20.7 | 0.0002 |
| σ_val = 0.3, δ = 0 | 0.52 | 6.6 | 19.4 | 13.9 | 13.9 | 26.9 | 0.0006 |
| σ_val = 0.3, δ = 2 erros padrão | 0.84 | 3.3 | 14.5 | 12.2 | 12.2 | 14.1 | 0.0003 |
| σ_val = 0.3, δ = 2 erros padrão, sem espera | 0.97 | 2.4 | 20.6 | 19.2 | 19.2 | 20.7 | 0.0002 |
| σ_val = 1.0, δ = 0 | 0.51 | 6.7 | 19.6 | 13.9 | 13.9 | 27.0 | 0.0006 |
| σ_val = 1.0, δ = 2 erros padrão | 0.84 | 3.3 | 14.5 | 12.2 | 12.2 | 14.1 | 0.0003 |
| σ_val = 1.0, δ = 2 erros padrão, sem espera | 0.97 | 2.4 | 20.6 | 19.2 | 19.2 | 20.7 | 0.0002 |

**Leitura.** `σ_val` é o ruído por cliente na diferença de perda medida. Com `δ = 0`, metade das fusões boas reprova. Com `δ` de 2 erros padrão, elas passam, e os erros começam quando o ruído se aproxima do ganho verdadeiro. Sem espera, o estrago é grande, porque cada reteste é uma nova chance de aprovar por engano.

### DP-06: persistência

200 sementes para os falsos splits.

**DP-06: persistência de mean_norm abaixo de ε1**

| p | Falso split, ε2=0.026 | Falso split, ε2=0.027 | ARI no cenário A | Partição correta no cenário A | Perda média no cenário A |
|---|---|---|---|---|---|
| 1 | 0.93 | 0.54 | 1.00 | 41.6 | 0.107 |
| 2 | 0.01 | 0.00 | 1.00 | 48.7 | 0.116 |
| 3 | 0.01 | 0.00 | 1.00 | 50.2 | 0.119 |
| 5 | 0.01 | 0.00 | 1.00 | 55.4 | 0.132 |
| 8 | 0.00 | 0.00 | 1.00 | 60.4 | 0.140 |

**Leitura.** O salto está em `p = 2`. Depois disso, só aumenta o atraso.

### DP-08: como bipartir

200 sementes. "Grupos intactos" é a fração de execuções em que nenhum grupo real ficou dividido entre os dois lados.

**DP-08: bipartição forçada sob ruído (N=24)**

| σ | K | single: grupos intactos | single: menor filho | complete: grupos intactos | complete: menor filho |
|---|---|---|---|---|---|
| 0.02 | 2 | 1.00 | 12.0 | 1.00 | 12.0 |
| 0.02 | 4 | 1.00 | 7.5 | 1.00 | 9.3 |
| 0.05 | 2 | 1.00 | 12.0 | 1.00 | 12.0 |
| 0.05 | 4 | 1.00 | 7.6 | 1.00 | 9.6 |
| 0.1 | 2 | 1.00 | 12.0 | 1.00 | 12.0 |
| 0.1 | 4 | 1.00 | 7.4 | 1.00 | 9.4 |
| 0.15 | 2 | 1.00 | 12.0 | 1.00 | 12.0 |
| 0.15 | 4 | 1.00 | 7.5 | 1.00 | 9.2 |
| 0.2 | 2 | 0.94 | 11.5 | 0.96 | 12.0 |
| 0.2 | 4 | 0.94 | 7.2 | 0.88 | 9.2 |
| 0.3 | 2 | 0.07 | 2.6 | 0.31 | 10.3 |
| 0.3 | 4 | 0.03 | 1.7 | 0.10 | 8.5 |

**Leitura.** As duas ligações empatam até ruído alto. Com `σ = 0,30`, as duas falham, e *single* isola outliers.

### DP-09: espera

**DP-09: W_merge, com espera 10, cenário C com γ_max mal calibrado (o merge é necessário)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| W_merge = 0 | 0.94 | 2.4 | 19.3 | 17.9 | 17.9 | 17.9 | 0.0002 |
| W_merge = 5 | 0.38 | 9.1 | 27.3 | 19.2 | 19.2 | 19.2 | 0.0008 |
| W_merge = 10 | 0.12 | 13.8 | 33.2 | 20.4 | 20.4 | 20.4 | 0.0012 |
| W_merge = 20 | 0.10 | 14.0 | 27.3 | 14.2 | 14.2 | 14.2 | 0.0012 |
| W_merge = 40 | 0.08 | 14.3 | 21.8 | 8.6 | 8.6 | 8.6 | 0.0013 |

**DP-09: base da espera, sem W_merge, cenário C com γ_max mal calibrado (o merge é necessário)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| espera = None | 0.79 | 3.8 | 35.0 | 32.2 | 32.2 | 32.2 | 0.0003 |
| espera = 5 | 0.79 | 3.7 | 20.1 | 17.4 | 17.4 | 17.4 | 0.0003 |
| espera = 10 | 0.94 | 2.4 | 19.3 | 17.9 | 17.9 | 17.9 | 0.0002 |
| espera = 20 | 0.33 | 10.7 | 22.1 | 12.4 | 12.4 | 12.4 | 0.0009 |
| espera = 40 | 0.99 | 2.1 | 17.4 | 16.3 | 16.3 | 16.3 | 0.0002 |

**DP-09: base da espera, calendário recomendado, cenário C com γ_max mal calibrado (o merge é necessário)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| espera = None | 1.00 | 2.0 | 22.0 | 21.0 | 21.0 | 21.0 | 0.0002 |
| espera = 5 | 1.00 | 2.0 | 14.7 | 13.7 | 13.7 | 13.7 | 0.0002 |
| espera = 10 | 1.00 | 2.0 | 16.6 | 15.6 | 15.6 | 15.6 | 0.0002 |
| espera = 20 | 1.00 | 2.0 | 13.4 | 12.4 | 12.4 | 12.4 | 0.0002 |
| espera = 40 | 0.99 | 2.1 | 17.4 | 16.3 | 16.3 | 16.3 | 0.0002 |

**DP-09: W_merge, com espera 10, cenário B (o merge deve recusar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| W_merge = 0 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| W_merge = 5 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 21.0 | 0.0004 |
| W_merge = 10 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.9 | 0.0004 |
| W_merge = 20 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 18.0 | 0.0004 |
| W_merge = 40 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 18.0 | 0.0004 |

**DP-09: base da espera, sem W_merge, cenário B (o merge deve recusar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| espera = None | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 116.4 | 0.0004 |
| espera = 5 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 22.9 | 0.0004 |
| espera = 10 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 20.2 | 0.0004 |
| espera = 20 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 16.4 | 0.0004 |
| espera = 40 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 11.2 | 0.0004 |

**DP-09: base da espera, calendário recomendado, cenário B (o merge deve recusar)**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| espera = None | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 280.3 | 0.0004 |
| espera = 5 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 24.0 | 0.0004 |
| espera = 10 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 21.0 | 0.0004 |
| espera = 20 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 17.2 | 0.0004 |
| espera = 40 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 12.0 | 0.0004 |

**DP-09: W_merge, com espera 10, cenário pior caso, subgrupos com tolerância 0,1**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| W_merge = 0 | 0.47 | 4.0 | 7.0 | 4.0 | 4.0 | 4.0 | 0.0004 |
| W_merge = 5 | 0.47 | 4.0 | 7.0 | 4.0 | 4.0 | 4.0 | 0.0004 |
| W_merge = 10 | 0.47 | 4.0 | 7.0 | 4.0 | 4.0 | 4.0 | 0.0004 |
| W_merge = 20 | 0.47 | 4.0 | 7.0 | 4.0 | 4.0 | 4.0 | 0.0009 |
| W_merge = 40 | 1.00 | 2.0 | 5.0 | 4.0 | 4.0 | 4.0 | 0.0802 |

**DP-09: base da espera, sem W_merge, cenário pior caso, subgrupos com tolerância 0,1**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| espera = None | 0.47 | 4.0 | 45.0 | 42.0 | 42.0 | 42.0 | 0.0067 |
| espera = 5 | 0.47 | 4.0 | 9.0 | 6.0 | 6.0 | 6.0 | 0.0009 |
| espera = 10 | 0.47 | 4.0 | 7.0 | 4.0 | 4.0 | 4.0 | 0.0004 |
| espera = 20 | 1.00 | 2.0 | 5.0 | 4.0 | 4.0 | 4.0 | 0.0802 |
| espera = 40 | 0.47 | 4.0 | 5.0 | 2.0 | 2.0 | 2.0 | 0.0009 |

**DP-09: base da espera, calendário recomendado, cenário pior caso, subgrupos com tolerância 0,1**

| Configuração | ARI | N final | Splits | Merges | M desfaz S | Testes | Perda final |
|---|---|---|---|---|---|---|---|
| espera = None | 1.00 | 2.0 | 31.0 | 30.0 | 30.0 | 30.0 | 0.0802 |
| espera = 5 | 1.00 | 2.0 | 7.0 | 6.0 | 6.0 | 6.0 | 0.0802 |
| espera = 10 | 1.00 | 2.0 | 5.0 | 4.0 | 4.0 | 4.0 | 0.0802 |
| espera = 20 | 1.00 | 2.0 | 5.0 | 4.0 | 4.0 | 4.0 | 0.0802 |
| espera = 40 | 1.00 | 2.0 | 3.0 | 2.0 | 2.0 | 2.0 | 0.0802 |

**Leitura.** `W_merge` só atrapalha. A base da espera reduz testes e oscilação. Com os primos até o fim, o ARI em C oscila de forma irregular (0,33 com base 20), porque depende de qual operação caiu por último. Com o calendário recomendado, essa irregularidade some.

### DP-10: participação

100 clientes, 15 sementes. "Treinos" é o total de treinos de cliente na execução.

**DP-10: participação, cenário A, N=100**

| Configuração | ARI | N final | Splits | Merges | Censos | Treinos | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|---|
| total | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 15000 | 50.9 | 0.118 |
| censo, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3.0 | 7612 | 66.1 | 0.146 |
| censo, 20% por rodada | 0.34 | 2.0 | 1.0 | 0.0 | 1.0 | 3073 | 127.0 | 0.358 |
| censo, 10% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1500 | — | 0.395 |
| censo, 5% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 750 | — | 0.396 |
| censo, média corrigida, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3.0 | 7614 | 57.9 | 0.128 |
| censo, média corrigida, 20% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3.1 | 3187 | 69.3 | 0.150 |
| censo, média corrigida, 10% por rodada | 0.98 | 3.9 | 2.9 | 0.0 | 3.9 | 1752 | 80.4 | 0.173 |
| censo, média corrigida, 5% por rodada | 0.94 | 3.8 | 2.8 | 0.0 | 4.3 | 1056 | 110.3 | 0.231 |
| amostra, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 7500 | 65.1 | 0.144 |
| amostra, 20% por rodada | 0.40 | 2.2 | 1.2 | 0.0 | 0.0 | 3000 | 108.3 | 0.347 |
| amostra, 10% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1500 | — | 0.395 |
| amostra, 5% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 750 | — | 0.396 |
| amostra, média corrigida, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 7500 | 58.7 | 0.128 |
| amostra, média corrigida, 20% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 3000 | 63.9 | 0.144 |
| amostra, média corrigida, 10% por rodada | 1.00 | 4.0 | 3.1 | 0.1 | 0.0 | 1500 | 79.3 | 0.161 |
| amostra, média corrigida, 5% por rodada | 0.92 | 3.8 | 2.9 | 0.1 | 0.0 | 750 | 105.5 | 0.219 |

**DP-10: participação, cenário B, N=100**

| Configuração | ARI | N final | Splits | Merges | Censos | Treinos | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|---|
| total | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 15000 | 55.0 | 0.207 |
| censo, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3.0 | 7612 | 80.2 | 0.248 |
| censo, 20% por rodada | 0.34 | 2.0 | 1.0 | 0.0 | 1.0 | 3073 | 127.0 | 0.432 |
| censo, 10% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1500 | — | 0.469 |
| censo, 5% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 750 | — | 0.471 |
| censo, média corrigida, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3.1 | 7613 | 63.8 | 0.220 |
| censo, média corrigida, 20% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3.1 | 3182 | 75.0 | 0.242 |
| censo, média corrigida, 10% por rodada | 0.98 | 3.9 | 2.9 | 0.0 | 4.1 | 1763 | 92.3 | 0.272 |
| censo, média corrigida, 5% por rodada | 0.94 | 3.8 | 2.8 | 0.0 | 3.7 | 1009 | 111.2 | 0.313 |
| amostra, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 7500 | 78.1 | 0.245 |
| amostra, 20% por rodada | 0.40 | 2.2 | 1.2 | 0.0 | 0.0 | 3000 | 108.3 | 0.421 |
| amostra, 10% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1500 | — | 0.469 |
| amostra, 5% por rodada | 0.00 | 1.0 | 0.0 | 0.0 | 0.0 | 750 | — | 0.471 |
| amostra, média corrigida, 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 7500 | 65.8 | 0.221 |
| amostra, média corrigida, 20% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 3000 | 77.8 | 0.244 |
| amostra, média corrigida, 10% por rodada | 0.99 | 4.0 | 3.0 | 0.0 | 0.0 | 1500 | 85.4 | 0.260 |
| amostra, média corrigida, 5% por rodada | 0.93 | 3.8 | 2.8 | 0.0 | 0.0 | 750 | 115.6 | 0.302 |

**Leitura.** Sem a média corrigida, o critério do CFL praticamente não dispara abaixo de 50%. Com ela, tanto o censo quanto a amostra funcionam até 10%. A amostra não custa treino extra, mas depende de `ψ` para colocar os clientes pendentes, e no toy `ψ` sempre indica o grupo mais próximo.

### DP-11: clusters pequenos

**DP-11: TN no split, cenário C sem γ_max e sem merge (sobredivisão)**

| Configuração | ARI | N final | Splits | Merges | Testes | Perda média | Perda final |
|---|---|---|---|---|---|---|---|
| TN = 0 | 0.04 | 19.2 | 18.2 | 0.0 | 0.0 | 0.066 | 0.0018 |
| TN = 1 | 0.20 | 8.6 | 7.6 | 0.0 | 0.0 | 0.066 | 0.0008 |
| TN = 2 | 0.43 | 5.1 | 4.1 | 0.0 | 0.0 | 0.065 | 0.0005 |
| TN = 3 | 0.62 | 3.5 | 2.5 | 0.0 | 0.0 | 0.065 | 0.0003 |
| TN = 5 | 1.00 | 2.0 | 1.0 | 0.0 | 0.0 | 0.065 | 0.0002 |

**DP-11: TN no split, cenário A sem merge (K=4, 6 clientes por grupo)**

| Configuração | ARI | N final | Splits | Merges | Testes | Perda média | Perda final |
|---|---|---|---|---|---|---|---|
| TN = 0 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| TN = 1 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| TN = 2 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| TN = 3 | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 0.107 | 0.0004 |
| TN = 5 | 0.63 | 2.8 | 1.8 | 0.0 | 0.0 | 0.216 | 0.1544 |

**DP-11: caminho de cluster pequeno, cenário E com partida por ψ**

| Configuração | ARI | N final | Splits | Merges | Testes | Perda média | Perda final |
|---|---|---|---|---|---|---|---|
| n_pequeno = 0 | 0.00 | 24.0 | 0.0 | 0.0 | 0.0 | 0.031 | 0.0023 |
| n_pequeno = 2 | 0.28 | 12.0 | 0.0 | 12.0 | 12.0 | 0.030 | 0.0011 |
| n_pequeno = 3 | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 0.029 | 0.0004 |
| n_pequeno = 6 | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 0.029 | 0.0004 |
| n_pequeno = 12 | 1.00 | 4.0 | 0.0 | 20.0 | 44.0 | 0.029 | 0.0004 |
| n_pequeno = 25 | 1.00 | 4.0 | 0.0 | 20.0 | 44.0 | 0.029 | 0.0004 |

**DP-11: fusão forçada de cluster pequeno, sem teste, cenário E com partida por ψ**

| Configuração | ARI | N final | Splits | Merges | Testes | Perda média | Perda final |
|---|---|---|---|---|---|---|---|
| n_pequeno = 6, sem teste | 1.00 | 4.0 | 3.0 | 23.0 | 23.0 | 0.054 | 0.0004 |
| n_pequeno = 12, sem teste | 0.30 | 1.9 | 5.3 | 27.4 | 27.4 | 0.304 | 0.2681 |

**Leitura.** `TN_FL` limita a fragmentação, mas, alto demais, bloqueia splits legítimos. O caminho de cluster pequeno funciona a partir de `n_pequeno = 3`, e valores maiores só custam testes. Sem o teste, a fusão forçada contamina.

### DP-12: reatribuição

**DP-12: 10% dos clientes com ψ de outro grupo, partida por ψ, N=48**

| Configuração | ARI | N final | Splits | Merges | Testes | Movidos | Modelos extras | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|---|---|
| só CFL e merge | 0.86 | 7.5 | 3.5 | 0.0 | 14.3 | 0.0 | 0 | — | 0.053 |
| com cluster pequeno < 12 | 0.98 | 4.4 | 4.1 | 3.7 | 36.9 | 0.0 | 0 | 73.9 | 0.051 |
| reatribuição completa | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 5.0 | 4464 | 7.0 | 0.031 |
| reatribuição seletiva (3 × mediana) | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 5.0 | 15 | 11.0 | 0.033 |
| reatribuição completa, σ_val = 0,1 | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 5.3 | 4464 | 7.5 | 0.031 |
| reatribuição seletiva, σ_val = 0,1 | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 5.0 | 1334 | 12.5 | 0.033 |
| reatribuição completa, σ_val = 0,1, margem 0,3 | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 5.0 | 4464 | 9.4 | 0.032 |
| reatribuição seletiva, σ_val = 0,1, margem 0,3 | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 5.0 | 1334 | 12.8 | 0.033 |

**DP-12: ruído alto no treino (σ=0,15), K=2, sem γ_max, partida única**

| Configuração | ARI | N final | Splits | Merges | Testes | Movidos | Modelos extras | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|---|---|
| sem reatribuição | 0.24 | 13.8 | 42.2 | 29.4 | 29.4 | 0.0 | 0 | — | 0.066 |
| reatribuição completa | 1.00 | 2.0 | 55.2 | 0.0 | 0.0 | 79.9 | 2022 | 11.0 | 0.050 |
| reatribuição completa, σ_val = 0,1, margem 0,3 | 0.38 | 8.8 | 50.1 | 33.6 | 60.0 | 23.7 | 4842 | — | 0.060 |

**Leitura.** A reatribuição seletiva dá o mesmo resultado que a completa, com muito menos downloads. Ela resolve clientes claramente mal colocados. Com ruído na validação, não substitui o merge na limpeza de splits falsos.

### DP-13: termo proximal

**DP-13: termo proximal, cenário A, pilha completa**

| Configuração | ARI | N final | Splits | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|
| μ = 0.0 | 1.00 | 4.0 | 3.0 | 50.2 | 0.119 | 0.0004 |
| μ = 0.1 | 1.00 | 4.0 | 3.0 | 50.3 | 0.121 | 0.0035 |
| μ = 0.5 | 1.00 | 4.0 | 3.0 | 40.2 | 0.136 | 0.0419 |
| μ = 2.0 | 1.00 | 4.0 | 3.0 | 35.7 | 0.225 | 0.1669 |
| μ = 10.0 | 1.00 | 4.0 | 3.0 | 36.3 | 0.337 | 0.3101 |

**Leitura.** O critério do CFL sobrevive ao termo proximal, e o custo aparece na perda final. **O toy mostra só o custo**, porque grupos ortogonais não têm nada a compartilhar.

### DP-15: momentum

**DP-15: momentum, cenário A, pilha completa**

| Configuração | ARI | N final | Splits | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|
| β = 0 | 1.00 | 4.0 | 3.0 | 50.2 | 0.119 | 0.0004 |
| β = 0.5, ε iguais | 1.00 | 4.0 | 3.0 | 36.2 | 0.080 | 0.0006 |
| β = 0.5, ε iguais, buffers zerados | 1.00 | 4.0 | 3.0 | 36.2 | 0.081 | 0.0006 |
| β = 0.5, ε2 reescalado | 1.00 | 4.0 | 3.0 | 36.2 | 0.080 | 0.0006 |
| β = 0.9, ε iguais | 0.61 | 2.7 | 1.7 | — | 0.355 | 0.1959 |
| β = 0.9, ε iguais, buffers zerados | 1.00 | 4.0 | 3.1 | 88.6 | 0.197 | 0.0019 |
| β = 0.9, ε2 reescalado | 0.61 | 2.7 | 1.7 | — | 0.355 | 0.1959 |

**DP-15: momentum, população homogênea (não deve dividir), só CFL**

| Configuração | ARI | N final | Splits | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|
| β = 0 | 1.00 | 1.0 | 0.0 | 1.0 | 0.028 | 0.0001 |
| β = 0.5, ε iguais | 1.00 | 1.0 | 0.0 | 1.0 | 0.015 | 0.0001 |
| β = 0.5, ε iguais, buffers zerados | 1.00 | 1.0 | 0.0 | 1.0 | 0.015 | 0.0001 |
| β = 0.5, ε2 reescalado | 1.00 | 1.0 | 0.0 | 1.0 | 0.015 | 0.0001 |
| β = 0.9, ε iguais | 0.00 | 11.5 | 10.5 | — | 0.032 | 0.0056 |
| β = 0.9, ε iguais, buffers zerados | 0.00 | 10.7 | 9.7 | — | 0.031 | 0.0049 |
| β = 0.9, ε2 reescalado | 1.00 | 1.0 | 0.0 | 1.0 | 0.030 | 0.0005 |

**Leitura.** Momentum moderado acelera. Com 0,9, os mesmos limiares falham nos dois cenários, e nenhuma correção isolada resolve. O modelo é simplificado: um passo de momentum por rodada.

### DP-18: papel de `K`

**DP-18: meta de K como no ISODATA, cenário A (K real = 4)**

| Configuração | ARI | N final | Splits | Merges | Partição correta | Perda média |
|---|---|---|---|---|---|---|
| sem meta | 1.00 | 4.0 | 3.0 | 0.0 | 50.2 | 0.119 |
| K_meta = 1 | 0.34 | 2.0 | 1.0 | 0.0 | — | 0.290 |
| K_meta = 2 | 1.00 | 4.0 | 3.0 | 0.0 | 39.0 | 0.089 |
| K_meta = 4 | 1.00 | 4.0 | 3.7 | 0.7 | 24.2 | 0.061 |
| K_meta = 8 | 1.00 | 4.0 | 6.3 | 3.3 | 26.0 | 0.052 |
| K_meta = 16 | 1.00 | 4.0 | 9.5 | 6.5 | 30.0 | 0.052 |

**DP-18: K_max, cenário A (K real = 4)**

| Configuração | ARI | N final | Splits | Merges | Partição correta | Perda média |
|---|---|---|---|---|---|---|
| K_max = 2 | 0.34 | 2.0 | 1.0 | 0.0 | — | 0.290 |
| K_max = 3 | 0.75 | 3.2 | 2.2 | 0.0 | 41.0 | 0.181 |
| K_max = 4 | 1.00 | 4.0 | 3.0 | 0.0 | 50.2 | 0.119 |
| K_max = 8 | 1.00 | 4.0 | 3.0 | 0.0 | 50.2 | 0.119 |

**DP-18: K_max, cenário C sem γ_max e sem merge (sobredivisão, K real = 2)**

| Configuração | ARI | N final | Splits | Merges | Partição correta | Perda média |
|---|---|---|---|---|---|---|
| sem limite | 0.04 | 19.2 | 18.2 | 0.0 | — | 0.066 |
| K_max = 2 | 1.00 | 2.0 | 1.0 | 0.0 | 23.0 | 0.065 |
| K_max = 4 | 0.81 | 4.0 | 3.0 | 0.0 | — | 0.065 |
| K_max = 8 | 0.50 | 8.2 | 7.2 | 0.0 | — | 0.066 |

**Leitura.** Uma estimativa de `K` por cima acelera, porque permite dividir antes de convergir, e o merge limpa o excesso. Subestimar demais é grave. `K_max` limita a fragmentação, e bloqueia se ficar abaixo do real.

## A.12 A combinação recomendada

Tudo junto, para verificar que as melhorias não atrapalham umas às outras.

**Combinação recomendada, cenário A (ψ separa os grupos)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 4.0 | 3.0 | 0.0 | 0.2 | 50.2 | 0.119 | 0.0004 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 | 0.0004 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 4.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 | 0.0004 |

**Combinação recomendada, cenário B (ψ não separa os grupos)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 | 0.0004 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 | 0.0004 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 4.0 | 3.0 | 0.0 | 21.0 | 56.8 | 0.209 | 0.0004 |

**Combinação recomendada, cenário C (ε2 baixo, sobredivisão)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 2.0 | 1.0 | 0.0 | 0.0 | 28.8 | 0.075 | 0.0002 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 2.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 | 0.0002 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 2.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.029 | 0.0002 |

**Combinação recomendada, cenário D (K=1, população homogênea, ε2 baixo)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.028 | 0.0001 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.028 | 0.0001 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.028 | 0.0001 |

**Combinação recomendada, cenário E (τ alto demais)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 4.0 | 3.0 | 0.0 | 0.0 | 50.2 | 0.119 | 0.0004 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 12.0 | 0.029 | 0.0004 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 4.0 | 0.0 | 20.0 | 26.0 | 12.0 | 0.029 | 0.0004 |

**Combinação recomendada, cenário C com γ_max mal calibrado (0,68)**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 2.0 | 11.0 | 10.0 | 10.0 | 122.1 | 0.075 | 0.0002 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 2.0 | 14.8 | 14.8 | 34.2 | 114.4 | 0.029 | 0.0002 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 2.0 | 14.8 | 14.8 | 34.2 | 114.4 | 0.029 | 0.0002 |

**Combinação recomendada, cenário K=8, N=48**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 8.0 | 7.0 | 0.0 | 2.2 | 71.7 | 0.096 | 0.0004 |
| partida por ψ, cluster pequeno < 6 | 1.00 | 8.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.017 | 0.0004 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 8.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.017 | 0.0004 |

**Combinação recomendada, cenário 10% dos clientes com ψ de outro grupo, N=48**

| Configuração | ARI | N final | Splits | Merges | Testes | Partição correta | Perda média | Perda final |
|---|---|---|---|---|---|---|---|---|
| partida única | 1.00 | 4.0 | 3.0 | 0.0 | 3.6 | 50.5 | 0.118 | 0.0002 |
| partida por ψ, cluster pequeno < 6 | 0.98 | 4.3 | 4.3 | 3.9 | 15.5 | 48.5 | 0.050 | 0.0037 |
| partida por ψ, cluster pequeno < 6, reatribuição seletiva | 1.00 | 4.0 | 0.0 | 0.0 | 2.3 | 11.0 | 0.033 | 0.0002 |

**Combinação recomendada com participação parcial, só com amostra e média corrigida, cenário A, N=100**

| Configuração | ARI | N final | Splits | Merges | Treinos | Partição correta | Perda média |
|---|---|---|---|---|---|---|---|
| 100% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 15000 | 50.9 | 0.118 |
| 50% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 7500 | 58.7 | 0.128 |
| 20% por rodada | 1.00 | 4.0 | 3.0 | 0.0 | 3000 | 63.9 | 0.144 |
| 10% por rodada | 0.98 | 3.9 | 3.1 | 0.1 | 1500 | 77.1 | 0.161 |
| 5% por rodada | 0.74 | 3.2 | 2.2 | 0.0 | 750 | 83.0 | 0.233 |

**Leitura.** A partida única acerta em todos os cenários. A partida por `ψ`, com cluster pequeno e reatribuição seletiva, também acerta, e agrupa muito mais cedo quando `ψ` é bom. Com 5% de participação, a parada em 70% chega antes de os splits terminarem, e o ARI cai.

## A.13 Protótipo do esqueleto

Testa a recomendação de [DP-14](11-decisoes-pendentes.md#dp-14-o-que-é-a-base-no-código): o laço genérico de [08](08-arquitetura-do-codigo.md), 8.4, com um adaptador de pixels, reproduz `ISODATAKit.py`? Foram 300 execuções, em cinza e RGB, com imagens sintéticas de 6 a 21 pixels de lado e parâmetros sorteados, comparando a imagem de saída com a do original, usando a mesma semente.

```text
300/300 execuções iguais (300 com imagens comparadas pixel a pixel, 0 em que os dois falham com o mesmo erro); com split: 160, com merge: 155, com descarte: 102
```

O esqueleto tem 22 linhas, incluindo o calendário do ISODATA, e o adaptador tem 84. Com `TN = 0`, o original pode dividir por zero (item 8 do [guia do ISODATA](../guia-tecnico-isodata.md)), então esse valor foi trocado por 1 nos sorteios. O código está na seção A.17.

## A.14 Limites deste modelo

| O toy assume | Em redes reais | Consequência |
|---|---|---|
| Perda quadrática, um ótimo por grupo | Não convexa, com muitos mínimos | Não testa barreira de perda: a regra de modelo no merge (média, maior) não pode ser avaliada aqui |
| `ψ` é a direção até o ótimo | Empírico, sem teoria (guia 4.15.5) | A concordância entre `ψ` e `ΔW` é a pergunta de E0. Os resultados favoráveis à amostra dependem disso |
| Ruído isotrópico | Estruturado, e clientes congruentes costumam ter cosseno positivo | Os valores de `γ_max` não se transferem |
| Perda de validação sem ruído, salvo em DP-04 e DP-12 | Validação finita | `δ = 0` é otimista. O ruído foi modelado de forma simples, sem relação com o tamanho real da validação |
| Cliente isolado aprende bem | Com poucos dados, generaliza mal | Perda média otimista para clientes isolados |
| Grupos ortogonais | Distribuições relacionadas | Não modela o benefício do modelo global, só o custo |
| Momentum como um passo por rodada | Vários passos locais | Os resultados de DP-15 são só indicativos |
| Convergência em dezenas de rodadas | Depende de lr, épocas e arquitetura | As rodadas não se comparam com as de redes reais |

## A.15 Como rodar

Requer Python 3.12 e NumPy, além de Pillow para o protótipo (usados aqui: Python 3.12.3, NumPy 2.5.4 e Pillow 13.0.0). O `.venv` da raiz tem esses pacotes desde 2026-11-05 (versões mais novas do que as citadas), mas o comando abaixo usa um ambiente descartável.

```bash
python3 -m venv /tmp/toy && /tmp/toy/bin/pip install numpy pillow
# copie o código da seção A.16 para simulacao_isodata_fl.py, e o da A.17 para poc_esqueleto.py
/tmp/toy/bin/python simulacao_isodata_fl.py baselines
/tmp/toy/bin/python poc_esqueleto.py projetos/ISODATA-python
```

As seções são `baselines`, `sinais`, `calendarios`, `guardas`, `falsos`, `dispersao`, `janela`, `limites`, `d01`, `d02`, `d03`, `d04`, `d04b`, `d06`, `d08`, `d09`, `d10`, `d11`, `d12`, `d13`, `d15`, `d18` e `recomendada`, ou `tudo`. A maioria leva menos de alguns minutos. `janela` e `d10` são as mais demoradas, e vale rodar as seções em paralelo, com `OMP_NUM_THREADS=1`.

As seções antigas continuaram **idênticas, byte a byte,** depois de acrescentar os testes novos e de reescrever a bipartição para ficar mais rápida, exceto onde a pilha mudou de propósito (sem `W_merge`).

## A.16 Código da simulação

```python
#!/usr/bin/env python3
"""Simulacao de brinquedo do calendario e das guardas do ISODATA-FL.

Clientes quadraticos: o treino local do cliente i puxa o modelo para
theta*_i = grupo + subgrupo + within * u_i. A perda de validacao mede a distancia
ate grupo + subgrupo: o desvio individual u_i nao generaliza (imita dados finitos).
Nao e rede neural: nao mede acuracia, barreira de perda nem o psi real.

Uso: python simulacao_isodata_fl.py [secao|tudo]
Secoes: baselines, sinais, calendarios, guardas, falsos, dispersao, janela, limites, d01 a d18 (decisoes pendentes), recomendada.
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
    if nome == "fases":             # primeiro so split, depois so merge
        return {t for t in S if t <= R // 2}, {t for t in inter if R // 2 < t <= fim}
    if nome.startswith("parada_"):  # primos e interprimos, mas o split para antes: parada_70 = ate 70% de R
        return {t for t in S if t <= int(nome[7:]) * R // 100}, {t for t in inter if t <= fim}
    if nome.startswith("pares_parada_"):    # primos e pares, com o split parando antes
        return {t for t in S if t <= int(nome[13:]) * R // 100}, {t for t in todos if t % 2 == 0}
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
    M = (S + S.T) / 2
    np.fill_diagonal(M, -np.inf)
    grupos = {i: [i] for i in range(len(S))}
    while len(grupos) > 2:
        a, b = np.unravel_index(np.argmax(M), M.shape)     # como M e simetrica, a < b
        novo = np.maximum(M[a], M[b]) if ligacao == "single" else np.minimum(M[a], M[b])
        M[a], M[:, a] = novo, novo
        M[a, a] = -np.inf
        M[b], M[:, b] = -np.inf, -np.inf
        grupos[a] += grupos.pop(b)
    return [grupos[k] for k in sorted(grupos)]


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
          sigma=0.02, w_sub=0.0, persiste=1, partida="unico", pequeno=0, TN=0, verif="ganho", frac=1.0, modo="censo",
          reatribuir=None, K_meta=None, K_max=None, mu=0.0, beta=0.0, zerar_beta=False, psi_troca=0.0, ruido_val=0.0,
          seletiva=None, media_corrigida=False):
    """gamma: teste de gamma_max no split. ganho: tolerancia do ganho de fusao no merge.
    W_*: idade minima. tabu: bloqueio fixo de reuniao apos split. espera: base da espera crescente nos dois sentidos.
    persiste: rodadas seguidas com mean_norm < eps1 exigidas para o split (1 = regra instantanea do CFL).
    partida: "unico" = 1 cluster com todos (CFL); "psi" = componentes do grafo cos(psi) >= tau na rodada 1.
    pequeno: cluster com menos membros que isso testa fusao mesmo abaixo de tau (exige ganho).
    Os demais existem para os testes das decisoes pendentes. TN: porte minimo do split e dos filhos.
    verif: teste do merge, "ganho", "cruzada" ou "alfa". frac, modo: participacao parcial, com "censo" ou "amostra".
    reatribuir: margem de perda para um cliente trocar de cluster nas janelas de split. K_meta: meta de K como no ISODATA.
    K_max: limite de clusters. mu: termo proximal. beta: momentum por cliente; zerar_beta zera os buffers em split e merge.
    psi_troca: fracao de clientes com o psi de outro grupo. ruido_val: ruido da perda de validacao medida, por cliente.
    seletiva: na reatribuicao, so testa outros modelos quem tem perda acima disso vezes a mediana do cluster.
    media_corrigida: desconta da media amostral a variancia que vem de sortear poucos clientes."""
    p = Problema(seed, N, K, A, within, sigma, w_sub)
    am = np.random.default_rng(seed + 10 ** 6)     # gerador separado: nao altera o ruido das demais secoes
    if psi_troca:
        for i in am.choice(N, int(round(psi_troca * N)), replace=False):
            j = am.choice(np.flatnonzero(p.g != p.g[i]))
            p.psi[i] = C * (p.theta0 - p.alvo[j]) + p.ruido(1)[0]
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
    observado = np.zeros(N, dtype=bool)          # clientes cujo psi o servidor ja recebeu
    v = np.zeros((N, D)) if beta else None       # buffers de momentum
    omega = p.theta0.copy()                      # modelo global, so usado com mu > 0
    H = dict(splits=0, merges=0, m_desfaz_s=0, s_desfaz_m=0, testes=0, menor_filho=[], t_correta=np.nan, recusados=0,
             t_primeiro_split=np.nan, treinos=0, censos=0, movidos=0, modelos_extra=0)
    curva = []

    def treinar(theta, membros):
        d = p.delta(theta, membros)
        if mu:
            d = d + C * mu * (omega - theta)
        if beta:
            d = d + beta * v[membros]
            v[membros] = d
        return d

    for t in range(1, R + 1):
        if mu:
            omega = omega + p.delta(omega, np.arange(N)).mean(0)
        sorteados = None
        if frac < 1:
            sorteados = np.zeros(N, dtype=bool)
            sorteados[am.choice(N, max(1, int(round(frac * N))), replace=False)] = True
        travado = (K_max is not None and len(cl) >= K_max) or (K_meta is not None and len(cl) >= 2 * K_meta)
        relaxado = K_meta is not None and len(cl) <= K_meta / 2
        novos = []
        for c in cl:
            ativos = c.membros if sorteados is None else c.membros[sorteados[c.membros]]
            if len(ativos) == 0:                     # cluster sem ninguem sorteado fica parado nesta rodada
                novos.append(c)
                continue
            observado[ativos] = True
            d = treinar(c.theta, ativos)
            H["treinos"] += len(ativos)
            media, maximo = np.linalg.norm(d.mean(0)), np.linalg.norm(d, axis=1).max()
            if media_corrigida and 1 < len(ativos) < len(c.membros):
                s2 = ((d - d.mean(0)) ** 2).sum() / (len(ativos) - 1)
                media = np.sqrt(max(media ** 2 - s2 / len(ativos) * (1 - len(ativos) / len(c.membros)), 0.0))
            c.abaixo = c.abaixo + 1 if media < eps1 else 0
            filhos = None
            if (t in S_cal and (c.abaixo >= persiste or relaxado) and maximo > eps2 and len(c.membros) > 2 * (TN + 1)
                    and t - c.nasc >= W_split and not travado):
                if sorteados is not None and modo == "censo" and len(ativos) < len(c.membros):
                    H["censos"] += 1
                    H["treinos"] += len(c.membros) - len(ativos)
                    ativos = c.membros
                    observado[ativos] = True
                    d = treinar(c.theta, ativos)
                    media, maximo = np.linalg.norm(d.mean(0)), np.linalg.norm(d, axis=1).max()
                if len(ativos) > 2 and (sorteados is None or modo != "censo" or (media < eps1 and maximo > eps2)):
                    Sm = matriz_cos(d)
                    i1, i2 = bipartir(Sm, ligacao)
                    alfa = Sm[np.ix_(i1, i2)].max()
                    m1, m2 = ativos[i1], ativos[i2]
                    if len(ativos) < len(c.membros):     # modo amostra: os demais seguem o filho de psi mais proximo
                        c1, c2 = p.psi[m1].mean(0), p.psi[m2].mean(0)
                        pend = np.setdiff1d(c.membros, ativos)
                        perto = np.array([cos(p.psi[i], c1) >= cos(p.psi[i], c2) for i in pend], dtype=bool)
                        m1, m2 = np.concatenate([m1, pend[perto]]), np.concatenate([m2, pend[~perto]])
                    if gamma is not None and not relaxado and not gamma < np.sqrt((1 - alfa) / 2):
                        H["recusados"] += 1
                    elif min(len(m1), len(m2)) < TN + 1:
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
                if beta and zerar_beta:
                    v[c.membros] = 0.0
                novos.append(Cluster(m1, c.theta + d[i1].mean(0), t))
                novos.append(Cluster(m2, c.theta + d[i2].mean(0), t))
            else:
                c.theta = c.theta + d.mean(0)
                novos.append(c)
        cl = novos

        if t in M_cal and len(cl) > 1:
            vivos = [k for k, c in enumerate(cl) if observado[c.membros].any()]
            centros = {k: p.psi[cl[k].membros[observado[cl[k].membros]]].mean(0) for k in vivos}
            pares = sorted(((cos(centros[i], centros[j]), i, j) for x, i in enumerate(vivos)
                            for j in vivos[x + 1:]), reverse=True)
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
                    if verif == "ganho":
                        ruido = am.normal(0, ruido_val / np.sqrt(len(uniao))) if ruido_val else 0.0
                        reprova = p.perda_val(th, uniao).mean() + ruido > atual + ganho
                    elif verif == "cruzada":
                        Laa, Lbb = p.perda_val(a.theta, a.membros).mean(), p.perda_val(b.theta, b.membros).mean()
                        Lab, Lba = p.perda_val(b.theta, a.membros).mean(), p.perda_val(a.theta, b.membros).mean()
                        reprova = max(Lab - Laa, Lba - Lbb, 0.0) > ganho
                    else:                            # alfa: o split seria aprovado na uniao?
                        Sm = matriz_cos(np.vstack([p.delta(th, a.membros), p.delta(th, b.membros)]))
                        reprova = np.sqrt((1 - Sm[:na, na:].max()) / 2) > (0.72 if gamma is None else gamma)
                    if reprova:
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
                if beta and zerar_beta:
                    v[a.membros], v[b.membros] = 0.0, 0.0
                usados |= {i, j}
                fora.add(j)
                cl[i] = Cluster(np.concatenate([a.membros, b.membros]), th, t)
            cl = [c for k, c in enumerate(cl) if k not in fora]

        if reatribuir is not None and t in S_cal and len(cl) > 1:     # como a classificacao do ISODATA
            L = np.stack([0.5 * ((p.val_alvo - c.theta) ** 2).sum(1) for c in cl], axis=1)
            if ruido_val:
                L = L + am.normal(0, ruido_val, L.shape)
            atual = np.zeros(N, dtype=int)
            for k, c in enumerate(cl):
                atual[c.membros] = k
            propria = L[np.arange(N), atual]
            suspeito = np.ones(N, dtype=bool)
            if seletiva is not None:     # cada cliente ja conhece a perda no proprio modelo: nao custa download
                mediana = np.array([np.median(propria[c.membros]) for c in cl])
                suspeito = propria > seletiva * np.maximum(mediana[atual], 1e-12)
            H["modelos_extra"] += int(suspeito.sum()) * (len(cl) - 1)
            melhor = L.argmin(1)
            mudar = suspeito & (L[np.arange(N), melhor] < propria - reatribuir)
            if mudar.any():
                H["movidos"] += int(mudar.sum())
                atual[mudar] = melhor[mudar]
                for k, c in enumerate(cl):
                    c.membros, c.abaixo = np.flatnonzero(atual == k), 0
                cl = [c for c in cl if len(c.membros)]

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
PILHA = dict(gamma=0.72, persiste=3, ganho=0.0, espera=10)


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


FMT = {"ARI": ("ari", "{:.2f}"), "N final": ("N_final", "{:.1f}"), "Splits": ("splits", "{:.1f}"), "Merges": ("merges", "{:.1f}"),
       "M desfaz S": ("m_desfaz_s", "{:.1f}"), "Testes": ("testes", "{:.1f}"), "Censos": ("censos", "{:.1f}"),
       "Treinos": ("treinos", "{:.0f}"), "Movidos": ("movidos", "{:.1f}"), "Modelos extras": ("modelos_extra", "{:.0f}"),
       "Partição correta": ("t_correta", "{:.1f}"), "Perda média": ("perda_media", "{:.3f}"), "Perda final": ("perda_final", "{:.4f}")}


def tabela(titulo, colunas, linhas, sementes=30):
    print(f"\n**{titulo}**\n")
    print("| Configuração | " + " | ".join(colunas) + " |")
    print("|---" * (len(colunas) + 1) + "|")
    for nome, cfg in linhas:
        m = media_config(sementes, **cfg)
        campos = ["—" if np.isnan(m[FMT[c][0]]) else FMT[c][1].format(m[FMT[c][0]]) for c in colunas]
        print(f"| {nome} | " + " | ".join(campos) + " |", flush=True)


C_MAL = dict(K=2, A=1.0, eps2=0.012, gamma=0.68, ganho=0.0)      # cenario C com gamma_max mal calibrado: o merge e necessario
E_PSI = dict(K=4, A=1.0, tau=0.995, partida="psi", pequeno=6)    # cenario E com partida por psi: o merge e necessario


def d01():
    """Partida: efeito de tau nas duas ordens."""
    cols = ["ARI", "N final", "Splits", "Merges", "Testes", "Partição correta", "Perda média"]
    for nome, extra in (("partida única", {}), ("partida por ψ", dict(partida="psi")),
                        ("partida por ψ, cluster pequeno < 6", dict(partida="psi", pequeno=6))):
        tabela(f"DP-01: {nome} (K=4; cosseno de ψ: 0,50 entre grupos, 0,98 dentro do grupo)", cols,
               [(f"τ = {x}", {**PILHA, "K": 4, "A": 1.0, "tau": x, **extra}) for x in (0.30, 0.45, 0.65, 0.90, 0.995)])


def d02():
    """Calendario do split, com a pilha completa."""
    cols = ["ARI", "N final", "Splits", "Merges", "Testes", "Partição correta", "Perda média"]
    nomes = ("primos+interprimos", "primos+pares", "periodo_4", "paridade", "toda_rodada", "fases", "parada_50", "parada_70", "parada_90",
             "pares_parada_50", "pares_parada_70", "pares_parada_90")
    for cen, kw in (("A", dict(K=4, A=1.0, **PILHA)), ("B", dict(K=4, A=2.5, **PILHA)),
                    ("C com γ_max mal calibrado (0,68)", {**PILHA, **C_MAL})):
        tabela(f"DP-02: calendário, cenário {cen}", cols, [(n, {**kw, "cal": n}) for n in nomes])


def d03():
    """Calendario do merge, em cenarios onde o merge e necessario."""
    cols = ["ARI", "N final", "Splits", "Merges", "Testes", "Partição correta", "Perda média"]
    nomes = ("primos+interprimos", "primos+pares", "primos+naoprimos")
    for cen, kw in (("C com γ_max mal calibrado (0,68), pilha completa", {**PILHA, **C_MAL}),
                    ("E com partida por ψ, pilha completa", {**PILHA, **E_PSI})):
        tabela(f"DP-03: merge em cada calendário, cenário {cen}", cols, [(n, {**kw, "cal": n}) for n in nomes])


def d04():
    """Como verificar o merge, dentro do laco completo."""
    cols = ["ARI", "N final", "Splits", "Merges", "M desfaz S", "Testes", "Perda final"]
    V = (("só ψ, sem teste", dict(ganho=None)), ("ganho de fusão", dict(ganho=0.0)),
         ("perda cruzada, tolerância 0", dict(ganho=0.0, verif="cruzada")),
         ("perda cruzada, tolerância 0,05", dict(ganho=0.05, verif="cruzada")),
         ("α_cross em θ_m", dict(ganho=0.0, verif="alfa")))
    for cen, kw in (("B (o merge deve recusar)", dict(K=4, A=2.5, **PILHA)),
                    ("C com γ_max mal calibrado (o merge deve aceitar)", {**PILHA, **C_MAL}),
                    ("E com partida por ψ (o merge deve aceitar só dentro do grupo)", {**PILHA, **E_PSI})):
        tabela(f"DP-04: verificação, cenário {cen}", cols, [(n, {**kw, **v}) for n, v in V])


def d04b():
    """Ruido na validacao: tolerancia do ganho de fusao e tempo de espera."""
    cols = ["ARI", "N final", "Splits", "Merges", "M desfaz S", "Testes", "Perda final"]
    for cen, kw in (("B (o merge deve recusar)", dict(K=4, A=2.5, **PILHA)),
                    ("C com γ_max mal calibrado (o merge deve aceitar)", {**PILHA, **C_MAL})):
        linhas = []
        for rv in (0.0, 0.1, 0.3, 1.0):
            ep = rv / np.sqrt(24)
            linhas += [(f"σ_val = {rv}, δ = 0", {**kw, "ruido_val": rv, "ganho": 0.0}),
                       (f"σ_val = {rv}, δ = 2 erros padrão", {**kw, "ruido_val": rv, "ganho": 2 * ep}),
                       (f"σ_val = {rv}, δ = 2 erros padrão, sem espera", {**kw, "ruido_val": rv, "ganho": 2 * ep, "espera": None})]
        tabela(f"DP-04: ruído na validação, cenário {cen}", cols, linhas)


def d06(sementes=200):
    """Persistencia: falso split contra atraso."""
    print("\n**DP-06: persistência de mean_norm abaixo de ε1**\n")
    print("| p | Falso split, ε2=0.026 | Falso split, ε2=0.027 | ARI no cenário A | Partição correta no cenário A | Perda média no cenário A |")
    print("|---|---|---|---|---|---|")
    for q in (1, 2, 3, 5, 8):
        f = [np.mean([rodar(s, K=1, A=1.0, eps2=e, tau=2.0, persiste=q)["splits"] > 0 for s in range(sementes)]) for e in (0.026, 0.027)]
        m = media_config(30, K=4, A=1.0, **{**PILHA, "persiste": q})
        print(f"| {q} | {f[0]:.2f} | {f[1]:.2f} | {m['ari']:.2f} | {m['t_correta']:.1f} | {m['perda_media']:.3f} |", flush=True)


def d08(sementes=200):
    """Bipartir sob ruido: single contra complete, no ponto estacionario do FL."""
    print("\n**DP-08: bipartição forçada sob ruído (N=24)**\n")
    print("| σ | K | single: grupos intactos | single: menor filho | complete: grupos intactos | complete: menor filho |")
    print("|---|---|---|---|---|---|")
    for sg in (0.02, 0.05, 0.10, 0.15, 0.20, 0.30):
        for K_ in (2, 4):
            lin = {"single": [], "complete": []}
            for s in range(sementes):
                p = Problema(s, 24, K_, 1.0, 0.05, sg)
                todos = np.arange(24)
                th = p.theta0.copy()
                for _ in range(60):
                    th = th + p.delta(th, todos).mean(0)
                Sm = matriz_cos(p.delta(th, todos))
                for lig in lin:
                    i1, i2 = bipartir(Sm, lig)
                    lado = np.zeros(24, dtype=int)
                    lado[i2] = 1
                    intacto = all(len(set(lado[p.g == g])) == 1 for g in range(K_))
                    lin[lig].append((intacto, min(len(i1), len(i2))))
            a, b = np.mean(lin["single"], axis=0), np.mean(lin["complete"], axis=0)
            print(f"| {sg} | {K_} | {a[0]:.2f} | {a[1]:.1f} | {b[0]:.2f} | {b[1]:.1f} |", flush=True)


def d09():
    """W_merge e base da espera."""
    cols = ["ARI", "N final", "Splits", "Merges", "M desfaz S", "Testes", "Perda final"]
    cen = (("C com γ_max mal calibrado (o merge é necessário)", C_MAL),
           ("B (o merge deve recusar)", dict(K=4, A=2.5, gamma=0.72, persiste=3, ganho=0.0)),
           ("pior caso, subgrupos com tolerância 0,1", dict(K=2, A=1.0, w_sub=0.4, eps2=0.03, gamma=0.72, ganho=0.1)))
    for nome, kw in cen:
        tabela(f"DP-09: W_merge, com espera 10, cenário {nome}", cols, [(f"W_merge = {w}", {**kw, "W_merge": w, "espera": 10}) for w in (0, 5, 10, 20, 40)])
        tabela(f"DP-09: base da espera, sem W_merge, cenário {nome}", cols, [(f"espera = {e}", {**kw, "espera": e}) for e in (None, 5, 10, 20, 40)])
        tabela(f"DP-09: base da espera, calendário recomendado, cenário {nome}", cols,
               [(f"espera = {e}", {**kw, "espera": e, "cal": "pares_parada_70"}) for e in (None, 5, 10, 20, 40)])


def d10():
    """Participacao parcial, com 100 clientes."""
    cols = ["ARI", "N final", "Splits", "Merges", "Censos", "Treinos", "Partição correta", "Perda média"]
    for cen, kw in (("A", dict(N=100, K=4, A=1.0, **PILHA)), ("B", dict(N=100, K=4, A=2.5, **PILHA))):
        linhas = [("total", kw)]
        for rot, cfg in (("censo", dict(modo="censo")), ("censo, média corrigida", dict(modo="censo", media_corrigida=True)),
                         ("amostra", dict(modo="amostra")), ("amostra, média corrigida", dict(modo="amostra", media_corrigida=True))):
            linhas += [(f"{rot}, {int(f * 100)}% por rodada", {**kw, **cfg, "frac": f}) for f in (0.5, 0.2, 0.1, 0.05)]
        tabela(f"DP-10: participação, cenário {cen}, N=100", cols, linhas, sementes=15)


def d11():
    """Clusters pequenos: TN no split e caminho de fusao sem tau."""
    cols = ["ARI", "N final", "Splits", "Merges", "Testes", "Perda média", "Perda final"]
    tabela("DP-11: TN no split, cenário C sem γ_max e sem merge (sobredivisão)", cols,
           [(f"TN = {x}", dict(K=2, A=1.0, eps2=0.012, tau=2.0, TN=x)) for x in (0, 1, 2, 3, 5)])
    tabela("DP-11: TN no split, cenário A sem merge (K=4, 6 clientes por grupo)", cols,
           [(f"TN = {x}", dict(K=4, A=1.0, tau=2.0, TN=x)) for x in (0, 1, 2, 3, 5)])
    tabela("DP-11: caminho de cluster pequeno, cenário E com partida por ψ", cols,
           [(f"n_pequeno = {x}", {**PILHA, **E_PSI, "pequeno": x}) for x in (0, 2, 3, 6, 12, 25)])
    tabela("DP-11: fusão forçada de cluster pequeno, sem teste, cenário E com partida por ψ", cols,
           [(f"n_pequeno = {x}, sem teste", {**PILHA, **E_PSI, "pequeno": x, "ganho": 10.0}) for x in (6, 12)])


def d12():
    """Reatribuicao: clientes presos no cluster errado."""
    cols = ["ARI", "N final", "Splits", "Merges", "Testes", "Movidos", "Modelos extras", "Partição correta", "Perda média"]
    base = {**PILHA, "N": 48, "K": 4, "A": 1.0, "partida": "psi", "psi_troca": 0.1}
    tabela("DP-12: 10% dos clientes com ψ de outro grupo, partida por ψ, N=48", cols,
           [("só CFL e merge", base), ("com cluster pequeno < 12", {**base, "pequeno": 12}),
            ("reatribuição completa", {**base, "reatribuir": 0.0}),
            ("reatribuição seletiva (3 × mediana)", {**base, "reatribuir": 0.0, "seletiva": 3.0}),
            ("reatribuição completa, σ_val = 0,1", {**base, "reatribuir": 0.0, "ruido_val": 0.1}),
            ("reatribuição seletiva, σ_val = 0,1", {**base, "reatribuir": 0.0, "seletiva": 3.0, "ruido_val": 0.1}),
            ("reatribuição completa, σ_val = 0,1, margem 0,3", {**base, "reatribuir": 0.3, "ruido_val": 0.1}),
            ("reatribuição seletiva, σ_val = 0,1, margem 0,3", {**base, "reatribuir": 0.3, "seletiva": 3.0, "ruido_val": 0.1})])
    base = dict(K=2, A=1.0, sigma=0.15, eps1=0.06, eps2=0.05, ganho=0.0)
    tabela("DP-12: ruído alto no treino (σ=0,15), K=2, sem γ_max, partida única", cols,
           [("sem reatribuição", base), ("reatribuição completa", {**base, "reatribuir": 0.0}),
            ("reatribuição completa, σ_val = 0,1, margem 0,3", {**base, "reatribuir": 0.3, "ruido_val": 0.1})])


def d13():
    """Modelo global: o termo proximal muda o criterio do CFL?"""
    cols = ["ARI", "N final", "Splits", "Partição correta", "Perda média", "Perda final"]
    tabela("DP-13: termo proximal, cenário A, pilha completa", cols,
           [(f"μ = {x}", {**PILHA, "K": 4, "A": 1.0, "mu": x}) for x in (0.0, 0.1, 0.5, 2.0, 10.0)])


def d15():
    """Momentum por cliente, como no notebook."""
    cols = ["ARI", "N final", "Splits", "Partição correta", "Perda média", "Perda final"]
    casos = [("β = 0", dict(beta=0.0))]
    for b in (0.5, 0.9):
        casos += [(f"β = {b}, ε iguais", dict(beta=b)), (f"β = {b}, ε iguais, buffers zerados", dict(beta=b, zerar_beta=True)),
                  (f"β = {b}, ε2 reescalado", dict(beta=b, eps2=0.05 / (1 - b)))]
    tabela("DP-15: momentum, cenário A, pilha completa", cols, [(n, {**PILHA, "K": 4, "A": 1.0, **c}) for n, c in casos])
    tabela("DP-15: momentum, população homogênea (não deve dividir), só CFL", cols,
           [(n, dict(K=1, A=1.0, tau=2.0, **c)) for n, c in casos])


def d18():
    """Papel de K."""
    cols = ["ARI", "N final", "Splits", "Merges", "Partição correta", "Perda média"]
    base = {**PILHA, "K": 4, "A": 1.0}
    tabela("DP-18: meta de K como no ISODATA, cenário A (K real = 4)", cols,
           [("sem meta", base)] + [(f"K_meta = {x}", {**base, "K_meta": x}) for x in (1, 2, 4, 8, 16)])
    tabela("DP-18: K_max, cenário A (K real = 4)", cols, [(f"K_max = {x}", {**base, "K_max": x}) for x in (2, 3, 4, 8)])
    tabela("DP-18: K_max, cenário C sem γ_max e sem merge (sobredivisão, K real = 2)", cols,
           [("sem limite", dict(K=2, A=1.0, eps2=0.012, tau=2.0))] +
           [(f"K_max = {x}", dict(K=2, A=1.0, eps2=0.012, tau=2.0, K_max=x)) for x in (2, 4, 8)])


def recomendada():
    """A combinacao recomendada, rodada junta em todos os cenarios."""
    R_ = {**PILHA, "cal": "pares_parada_70"}
    cols = ["ARI", "N final", "Splits", "Merges", "Testes", "Partição correta", "Perda média", "Perda final"]
    cen = (("A (ψ separa os grupos)", dict(K=4, A=1.0)), ("B (ψ não separa os grupos)", dict(K=4, A=2.5)),
           ("C (ε2 baixo, sobredivisão)", dict(K=2, A=1.0, eps2=0.012)), ("D (K=1, população homogênea, ε2 baixo)", dict(K=1, A=1.0, eps2=0.012)),
           ("E (τ alto demais)", dict(K=4, A=1.0, tau=0.995)), ("C com γ_max mal calibrado (0,68)", dict(K=2, A=1.0, eps2=0.012, gamma=0.68)),
           ("K=8, N=48", dict(N=48, K=8, A=1.0, R=250)), ("10% dos clientes com ψ de outro grupo, N=48", dict(N=48, K=4, A=1.0, psi_troca=0.1)))
    for nome, kw in cen:
        tabela(f"Combinação recomendada, cenário {nome}", cols,
               [("partida única", {**R_, **kw}), ("partida por ψ, cluster pequeno < 6", {**R_, **kw, "partida": "psi", "pequeno": 6}),
                ("partida por ψ, cluster pequeno < 6, reatribuição seletiva", {**R_, **kw, "partida": "psi", "pequeno": 6, "reatribuir": 0.0, "seletiva": 3.0})])
    cols = ["ARI", "N final", "Splits", "Merges", "Treinos", "Partição correta", "Perda média"]
    tabela("Combinação recomendada com participação parcial, só com amostra e média corrigida, cenário A, N=100", cols,
           [(f"{int(f * 100)}% por rodada", {**R_, "N": 100, "K": 4, "A": 1.0, "frac": f, "modo": "amostra", "media_corrigida": True}) for f in (1.0, 0.5, 0.2, 0.1, 0.05)],
           sementes=15)


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    for nome, f in [("baselines", baselines), ("sinais", sinais), ("calendarios", calendarios), ("guardas", guardas),
                    ("falsos", falsos), ("dispersao", dispersao), ("janela", janela_gamma), ("limites", limites),
                    ("d01", d01), ("d02", d02), ("d03", d03), ("d04", d04), ("d04b", d04b), ("d06", d06), ("d08", d08), ("d09", d09),
                    ("d10", d10), ("d11", d11), ("d12", d12), ("d13", d13), ("d15", d15), ("d18", d18), ("recomendada", recomendada)]:
        if alvo in (nome, "tudo"):
            f()
```

## A.17 Código do protótipo

```python
#!/usr/bin/env python3
"""Prova de conceito da DP-14: o esqueleto generico reproduz o ISODATAKit.py?

Uso: python poc_esqueleto.py caminho/para/projetos/ISODATA-python
"""
import contextlib
import io
import math
import random
import sys

import numpy as np
from PIL import Image

SPLIT, MERGE, NADA = "split", "merge", "nada"


# ---------- esqueleto: nao sabe nada de pixels nem de FL ----------
def rodar_esqueleto(estado, ops, calendario, R_max):
    for t in range(1, R_max + 1):
        ops.coletar(t, estado)
        stats = ops.estatisticas(t, estado)
        ops.podar(t, estado, stats)
        acao = calendario(t, estado)
        if acao == SPLIT:
            ops.dividir(t, estado, stats)
        ops.recalcular(t, estado)
        if acao == MERGE:
            ops.fundir(t, estado, stats)
    return estado


def calendario_isodata(K, I):
    """A linha 116 de ISODATAKit.py, com a parada da linha 112."""
    def acao(t, estado):
        N = len(estado.centros)
        if t >= I:
            return NADA
        return SPLIT if (N <= K / 2) or not (t % 2 == 0 or N >= K * 2) else MERGE
    return acao


# ---------- adaptador de pixels ----------
class Estado:
    def __init__(self, pixels, centros):
        self.pixels, self.centros = pixels, centros       # pixels: M x canais, em ordem de varredura
        self.membros = [np.empty(0, dtype=int) for _ in centros]


class OperadoresPixels:
    def __init__(self, K, TN, TS, TC, L):
        self.K, self.TN, self.TS, self.TC, self.L = K, TN, TS, TC, L

    @staticmethod
    def _dist(a, b):
        return np.sqrt(((a.astype(float) - b) ** 2).sum(-1))

    def coletar(self, t, e):
        C = np.array(e.centros)
        rot = np.stack([self._dist(e.pixels, c) for c in C], axis=1).argmin(1)
        e.membros = [np.flatnonzero(rot == k) for k in range(len(C))]
        for k, m in enumerate(e.membros):
            if len(m):
                e.centros[k] = e.pixels[m].astype(float).sum(0) / len(m)

    def estatisticas(self, t, e):
        ave, sd, total = [], [], 0.0
        for c, m in zip(e.centros, e.membros):
            if len(m) == 0:
                ave.append(0.0)
                sd.append([0.0] * e.pixels.shape[1])
                continue
            soma = float(np.cumsum(self._dist(e.pixels[m], c))[-1])     # soma em ordem, como no original
            quad = np.cumsum((e.pixels[m].astype(float) - c) ** 2, axis=0)[-1]
            ave.append(soma / len(m))
            sd.append([math.sqrt(x / len(m)) for x in quad])
            total += soma
        return dict(ave=ave, sd=sd, total=total / len(e.pixels))

    def podar(self, t, e, s):
        fica = [len(m) >= self.TN for m in e.membros]
        for nome, lista in (("centros", e.centros), ("membros", e.membros), ("ave", s["ave"]), ("sd", s["sd"])):
            novo = [x for x, f in zip(lista, fica) if f]
            if nome in s:
                s[nome] = novo
            else:
                setattr(e, nome, novo)

    def dividir(self, t, e, s):
        N = len(e.centros)
        for i in range(N):
            maior = max(s["sd"][i])
            k = s["sd"][i].index(maior)
            if maior > self.TS and ((s["ave"][i] > s["total"] and len(e.membros[i]) > 2 * (self.TN + 1)) or N <= self.K / 2):
                mais, menos = e.centros[i].copy(), e.centros[i].copy()
                mais[k] += 1
                menos[k] -= 1
                e.centros[i] = mais
                e.membros[i] = np.empty(0, dtype=int)
                e.centros.append(menos)
                e.membros.append(np.empty(0, dtype=int))

    def recalcular(self, t, e):
        pass      # no pixel, coletar ja recalculou; no FL, aqui entra o FedAvg por cluster

    def fundir(self, t, e, s):
        N = len(e.centros)
        pares = [(float(self._dist(e.centros[i], e.centros[j])), i, j) for i in range(N) for j in range(i + 1, N)]
        pares = sorted([p for p in pares if p[0] < self.TC], key=lambda p: p[0])[: self.L]
        usados, apagar = [], []
        for _, i, j in pares:
            if i in usados or j in usados:
                continue
            ni, nj = len(e.membros[i]), len(e.membros[j])
            e.centros[i] = (ni * e.centros[i] + nj * e.centros[j]) / (ni + nj)
            e.membros[i] = np.empty(0, dtype=int)
            usados += [i, j]
            apagar.append(j)
        for j in sorted(apagar, reverse=True):
            e.centros.pop(j)
            e.membros.pop(j)


def isodata_por_esqueleto(img, K, TN, TS, TC, L, I, NROWS=None):
    arr = np.array(img)
    cinza = arr.ndim == 2
    pix = arr.reshape(-1, 1) if cinza else arr[..., :3].reshape(-1, 3)
    linhas, colunas = arr.shape[:2]
    pos = random.sample(range(linhas * colunas), K if NROWS is None else NROWS)
    estado = Estado(pix, [pix[p].astype(float) for p in pos])
    rodar_esqueleto(estado, OperadoresPixels(K, TN, TS, TC, L), calendario_isodata(K, I), I)
    saida = np.zeros((linhas * colunas, pix.shape[1]), dtype=np.uint8)
    for c, m in zip(estado.centros, estado.membros):
        for x in m:
            saida[x] = [round(v) for v in c]
    return saida.reshape(arr.shape if cinza else (linhas, colunas, 3))


def imagem(seed, h, w, rgb):
    """Blobs de cor com ruido: varios grupos, para exercitar split, merge e descarte."""
    r = np.random.default_rng(seed)
    k = r.integers(2, 7)
    cores = r.integers(0, 256, size=(k, 3 if rgb else 1))
    xx, yy = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    cx, cy = r.integers(0, h, k), r.integers(0, w, k)
    rot = np.argmin([(xx - a) ** 2 + (yy - b) ** 2 for a, b in zip(cx, cy)], axis=0)
    a = cores[rot] + r.normal(0, r.uniform(1, 25), size=(h, w, 3 if rgb else 1))
    a = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(a if rgb else a[..., 0])


def main():
    sys.path.insert(0, sys.argv[1])
    import ISODATAKit as kit
    casos = iguais = comparadas = 0
    houve = dict(split=0, merge=0, descarte=0)
    r = np.random.default_rng(0)
    for caso in range(300):
        rgb = bool(caso % 2)
        h, w = int(r.integers(6, 22)), int(r.integers(6, 22))
        img = imagem(caso, h, w, rgb)
        K, TN = int(r.integers(1, 8)), int(r.integers(0, 12))
        TS, TC = float(r.uniform(0.5, 30)), float(r.uniform(1, 120))
        L, I = int(r.integers(1, 6)), int(r.integers(1, 10))
        NROWS = None if r.random() < 0.5 else int(r.integers(1, 10))
        if TN == 0:
            TN = 1        # com TN=0 o original pode dividir por zero (guia do ISODATA, item 8)
        log = io.StringIO()
        random.seed(caso)
        try:
            with contextlib.redirect_stdout(log):
                f = kit.doISODATARGB if rgb else kit.doISODATAGray
                a = np.array(f(img, K, TN, TS, TC, L, I, NROWS))
            erro_a = None
        except (IndexError, ZeroDivisionError, ValueError) as e:
            a, erro_a = None, type(e).__name__
        texto = log.getvalue()
        houve["split"] += any("Split:" in x and not x.endswith(" 0") and x.split()[-3] != x.split()[-1] for x in texto.splitlines())
        houve["merge"] += any("Merge:" in x and x.split()[-3] != x.split()[-1] for x in texto.splitlines())
        houve["descarte"] += any("TN checking" in x and " 0 clusters" not in x for x in texto.splitlines())
        random.seed(caso)
        try:
            b = isodata_por_esqueleto(img, K, TN, TS, TC, L, I, NROWS)
            erro_b = None
        except (IndexError, ZeroDivisionError, ValueError) as e:
            b, erro_b = None, type(e).__name__
        casos += 1
        if erro_a or erro_b:
            ok = erro_a == erro_b        # os dois falham, com o mesmo erro, em entradas sem nenhum cluster restante
        else:
            ok = a.shape == b.shape and bool((a == b).all())
            comparadas += 1
        iguais += ok
        if not ok:
            print("DIFERENTE", caso, "rgb" if rgb else "cinza", (h, w), dict(K=K, TN=TN, TS=TS, TC=TC, L=L, I=I, NROWS=NROWS), erro_a, erro_b)
    print(f"{iguais}/{casos} execuções iguais ({comparadas} com imagens comparadas pixel a pixel, {casos - comparadas} em que os dois falham "
          f"com o mesmo erro); com split: {houve['split']}, com merge: {houve['merge']}, com descarte: {houve['descarte']}")


if __name__ == "__main__":
    main()
```
