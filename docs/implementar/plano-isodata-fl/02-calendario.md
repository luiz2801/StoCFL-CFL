# 2. Calendário

> **Status:** proposta, nada implementado. Resolve, se aprovado, a parte de alternância do problema 2 da [especificação](../especificacao-isodata-fl.md) e substitui a paridade dos [diagramas anteriores](../diagramas-isodata-fl.md).
>
> **Futuro módulo:** `isodata_fl/calendario.py`. **Depende de:** nada. **Decisões:** DP-02, DP-03.

## 2.1 A regra

**Hipótese do usuário:** o CFL atua só em rodadas primas a partir da 7, para que ele e o StoCFL não desfaçam o trabalho um do outro.

**Proposta completa:** o CFL age nas rodadas primas a partir da 7, **até 70% das rodadas**, e o StoCFL age nas **rodadas pares**. Como todo primo a partir de 3 é ímpar, os dois nunca coincidem, e o resultado é uma versão rarefeita da alternância do ISODATA: split nas ímpares, merge nas pares.

| Operador | Rodadas até 100 |
|---|---|
| **S** (CFL) | 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 |
| **M** (StoCFL) | Todas as pares a partir da 8 |

```text
t:    1-6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
       FL  S  M  .  M  S  M  S  M  .  M  S  M  S  M  .  M  S  M  .  M  .  M  S  M  S
```

Quatro regras acompanham o calendário:

1. **O treino roda em toda rodada.** O calendário só governa os operadores.
2. **Janela é permissão, não ordem.** Em rodada prima, o CFL **avalia** seu critério. Se o critério falhar, nada acontece.
3. **Monitorar em toda rodada, agir só na janela.** Normas custam nada, porque usam os `ΔW` que o FedAvg já envia.
4. **O merge tem a última palavra.** Os splits param antes do fim, para que o merge possa limpar os erros (2.8).

## 2.2 O que a regra dos primos garante

Calculado para `t` até 300.

| Propriedade | Verificação |
|---|---|
| **É subconjunto das iterações de split do ISODATA** | Todo primo a partir de 7 é ímpar, e o artigo divide nas ímpares. A regra é uma versão rarefeita da alternância original |
| **Nunca coincide com um calendário periódico** | Um primo `p` não é múltiplo de nenhum `m ≥ 2`, exceto `p = m`. Testado para `m` em {2, 3, 4, 5, 6, 7, 10, 11} |
| **Fica mais rara com o tempo** | A densidade cai como `1/ln t`, em ritmo modesto (tabela abaixo) |
| **Não tem parâmetro além de `t_min`** | Um período fixo exigiria escolher o período |

| Até a rodada | Janelas de split | Lacuna média | Lacuna máxima | Pares de primos gêmeos |
|---|---|---|---|---|
| 50 | 12 | 3,64 | 6 | 4 |
| 80 | 19 | 4,00 | 6 | 6 |
| 100 | 22 | 4,29 | 8 | 6 |
| 200 | 43 | 4,57 | 14 | 13 |
| 300 | 59 | 4,93 | 14 | 17 |

## 2.3 O que a regra não garante

**Não impede a oscilação.** É o resultado mais importante deste módulo. No [toy](anexo-a-simulacao.md), sem guardas, quase todo split é desfeito em **qualquer** calendário. Os primos só reduzem a frequência, de 112 para 25 oscilações, com ARI final de 0,33 no melhor caso. O motivo é o sinal, não o tempo: ver [estabilidade](05-estabilidade.md).

**Não garante intervalo.** A lacuna mínima é 2 em qualquer horizonte, por causa dos primos gêmeos. Em 11, 12 e 13 acontecem split, merge e split em rodadas seguidas. O intervalo de verdade precisa vir da idade do cluster.

**A redução de falsos positivos depende de outra medida.** Sob a suposição de testes independentes, menos testes significam menos falsos splits:

| Calendário até `R = 80` | Testes | `P(≥ 1 falso)` com `p = 2%` por teste |
|---|---|---|
| Toda rodada depois da 20 | 60 | 0,70 |
| Primos a partir de 7 | 19 | 0,32 |
| Primos a partir de 23 | 14 | 0,25 |
| Período 5 a partir de 10 | 15 | 0,26 |

**O toy contradiz a suposição de independência.** Os falsos splits se concentram no momento em que `mean_norm` cruza `ε1`, porque ali `max_norm` ainda contém o resíduo comum: o 1º falso split ocorre, em média, na rodada 23 ou 24, em todos os calendários. Baixar de 134 para 31 testes quase não ajuda sozinho. Depois de exigir persistência, o efeito aparece:

| `ε2 = 0,026`, população homogênea | Testes | Falso split, regra instantânea | Falso split, persistência de 3 rodadas |
|---|---|---|---|
| Toda rodada | 134 | 0,99 | 0,38 |
| Paridade | 67 | 0,95 | 0,29 |
| Primos | 31 | 0,93 | **0,01** |
| Período 4 | 34 | 0,74 | **0,00** |

**A vantagem é do calendário esparso, e não do primo em si.**

## 2.4 Veredito sobre os primos

| Argumento | Resiste? | Evidência |
|---|---|---|
| Um não desfaz o trabalho do outro | **Não** | [Estabilidade](05-estabilidade.md), 5.1 |
| Evita colisão com o merge | Sim, mas um período fixo bem escolhido também evita | Aritmética |
| Compatível com a alternância do ISODATA | **Sim** | Primos são ímpares |
| Fica mais raro com o tempo | Sim, em ritmo modesto, e é específico dos primos | Lacuna de 3,6 para 4,9 |
| Menos falsos splits | Só com persistência, e não é específico dos primos | 2.3 |
| Reduz o custo do censo | **Sim**, e é o argumento prático mais forte, mas vale para qualquer calendário esparso | 43 janelas contra 180 até `R = 200` |
| Atrasa pouco | **Sim**, cerca de 6 rodadas, igual a um período fixo de mesma densidade | 2.6 |
| Dispensa ajuste de parâmetro | **Sim** | Só `t_min` |

**Conclusão:** a regra pode ficar, pelos motivos certos: custo baixo, atraso pequeno e nenhum parâmetro. A proteção contra a oscilação precisa vir das [guardas](05-estabilidade.md). O experimento E6 compara os primos com um período fixo. **Se empatarem, a hipótese H5 é refutada e a escolha passa a ser só de simplicidade.** O dilema está detalhado em [DP-02](11-decisoes-pendentes.md#dp-02-quando-o-cfl-pode-agir).

## 2.5 Quando o StoCFL age

A hipótese do usuário não define o calendário do StoCFL. Opções, até `R = 200`:

| Opção | Merges | Distância do split ao merge seguinte (mín/média/máx) | ARI com `γ_max` errado | Rodada correta, cenário E | Sugestão |
|---|---|---|---|---|---|
| **Pares** (paridade do ISODATA) | 97 | 1 / 1,00 / 1 | **0,99** | 12 | **Recomendada** |
| Interprimos (ponto médio entre dois primos) | 42 | 1 / 2,37 / 7 | 0,94 | 15 | **Testar** em E6: alternância exata, mas sem benefício medido |
| Não primos | 151 | 1 / 1,00 / 1 | 0,97 | 10 | **Descartar:** sem ganho claro sobre as pares |
| Múltiplos de 4 | 49 | 1 / 1,93 / 3 | — | — | **Descartar:** nada a favor |
| Múltiplos de 6 | 32 | 1 / 2,95 / 5 | — | — | **Descartar:** nada a favor |
| Só quando necessário, sem calendário | Variável | Variável | — | — | **Testar** em E6 como modo "evento" |

**Por que pares:**

- **Uma janela de merge quase não custa.** Calcular cossenos é só no servidor, e a espera crescente limita os testes: no cenário B, são 21,0 testes nas pares e 20,2 nos interprimos, com o dobro de janelas.
- **Mais fiel ao ISODATA:** as iterações pares são as de fusão no artigo.
- **Mais fácil de explicar:** primas para o CFL, pares para o StoCFL.
- **Mais janelas corrigem um pouco mais cedo**, como mostra a tabela.

**Mudança de recomendação.** A primeira versão deste plano recomendava os interprimos, porque dão exatamente um merge entre dois splits, à maior distância possível dos dois. É elegante, mas nenhuma métrica medida favoreceu essa escolha.

**Limite:** nas pares, o merge sempre cai 1 rodada depois de um split. Os filhos não terão divergido, mas isso não importa: a espera bloqueia a reunião dos irmãos ([05](05-estabilidade.md)).

## 2.6 Quanto o calendário atrasa

Cenário A do toy, com a pilha de guardas:

| Calendário | Testes de split até `R = 150` | Rodada da partição correta | Perda média |
|---|---|---|---|
| Toda rodada | 134 | 44,1 | 0,111 |
| Paridade | 67 | 45,1 | 0,112 |
| Período 4 | 34 | 49,5 | 0,118 |
| Primos a partir de 7 | 31 | 50,2 | 0,119 |

Os primos chegam à partição correta cerca de 6 rodadas depois de "toda rodada" (14%), com 4,3 vezes menos testes. O atraso é aceitável e vem quase todo de esperar a próxima janela. **O período 4 empata com os primos:** a maior densidade dos primos no início não se traduziu em vantagem.

## 2.7 Por que começar na rodada 7

| Fonte | Primeira divisão possível | Observação |
|---|---|---|
| Hipótese do usuário | 7 | |
| Notebook do CFL | 21 (`c_round > 20`) | Aquecimento fixo no código, que não está no artigo (guia 3.10) |
| Artigo do CFL, Algoritmo 5 | Qualquer rodada | O critério de normas decide |
| Experimentos do artigo do CFL | Splits em 30, 50, 60, 90, 100 e 150 | A separação correta já aparece em cerca de 10 rodadas no experimento de troca de rótulos (guia 3.9.7) |
| Toy | Mesma rodada de partição correta (50,2) com `t_min = 7` e com `t_min = 23` | `ε1` é quem decide. O toy não tem como mostrar dano de um split cedo demais |

O `t_min` baixo é seguro **enquanto `ε1` estiver bem calibrado**, porque a janela só permite. Duas ressalvas:

- **Rodadas não são uma unidade universal.** Sete rodadas de 5 épocas não equivalem a sete rodadas de 1 época. `t_min` precisa ser avaliado em cada configuração.
- **Em rodadas iniciais, os sinais são piores.** Se `ε1` estiver frouxo, um `t_min` baixo permite split em modelo pouco treinado, sem a proteção do aquecimento.

**Proposta:** `t_min = 7` como hipótese de partida, configurável. E6 testa {7, 11, 23}. Na [partida por `ψ`](01-conceito-e-mapeamento.md), o 7 ganha um sentido natural: as rodadas 1 a 6 ficam só para o StoCFL.

## 2.8 Consolidação final

O artigo do ISODATA reserva a última iteração: "nenhuma divisão ou fusão é permitida nesta iteração final, que serve principalmente para consolidação". Em FL, as últimas `F` rodadas não têm operadores, porque um split na última rodada deixa os filhos sem treino. Valor inicial: `F = 10`, ajustado à velocidade de convergência observada na Fase 3.

**Parar os splits antes dos merges.** Se os dois operadores agem até o fim, a partição final depende de qual agiu por último. O merge tem uma prova e o split falso não, então o merge deve ter a última palavra: os erros são limpos, e os splits corretos sobrevivem, porque o teste recusa desfazê-los.

| Cenário C com `γ_max` mal calibrado | ARI | Splits e merges | Rodada correta |
|---|---|---|---|
| Split até o fim | 0,94 | 13,5 e 12,1 | 130 |
| Split para em 90% | 0,94 | 13,4 e 12,1 | 130 |
| **Split para em 70%** | **1,00** | 10,8 e 9,8 | 126 |
| Split para em 50% | 1,00 | 5,7 e 4,7 | 84 |

Nos cenários A e B, parar não custa nada, porque os splits terminam antes de 50% das rodadas. O risco é um split necessário cair depois do limite, se o treino for lento: com participação de 5%, por exemplo, o ARI cai para 0,74. `R` e a parada precisam ser escolhidos juntos.

## 2.9 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-CAL-1 | O calendário não impede a oscilação | Tratar a oscilação com guardas. O calendário é só o agendador | 2.3 |
| P-CAL-2 | Primos gêmeos e rodadas pares colam as janelas: o merge pode cair 1 rodada depois de um split | Espera crescente, por par de clientes | O que importa é o tempo desde o split daquele par, não a posição no calendário. `W_merge`, por cluster, foi testado e é prejudicial (DP-09) |
| P-CAL-3 | `mean_norm` só fica abaixo de `ε1` em rodadas não primas, e a janela se perde | Persistência monitorada em toda rodada, avaliada na próxima janela | Monitorar é gratuito. O atraso fica limitado pela lacuna, de no máximo 14 até `R = 200` |
| P-CAL-4 | Janelas iniciais (7, 11, 13) podem ser cedo demais | `ε1` continua obrigatório, e `t_min` é testado em E6 | A janela só permite. Teorema 1: a separação depende de estar perto do estacionário |
| P-CAL-5 | Split muito no fim deixa filhos sem treino | `F` rodadas finais sem operadores | Regra do artigo do ISODATA |
| P-CAL-9 | Um split falso tardio não tem tempo de ser corrigido, e o resultado vira uma loteria sobre qual operador agiu por último | Parar os splits em 70% das rodadas (2.8) | No toy: ARI de 0,94 para 1,00, sem custo nos cenários A e B |
| P-CAL-6 | Splits em cascata ficam mais lentos com menos janelas | Medir em E6. Se pesar, usar um período menor ou o modo evento | No toy, o atraso é de cerca de 6 rodadas (2.6) |
| P-CAL-7 | `t` depende da configuração (épocas, lr) | Registrar `t_min` e as épocas juntos, e não comparar entre configurações | 2.7 |
| P-CAL-8 | Janela de merge sem nada a fazer | Sem custo: sem par acima do filtro, nenhuma mensagem sai | O cálculo de cossenos entre centros é só no servidor |

## 2.10 Alternativas

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Toda rodada** (como o notebook, depois do aquecimento) | **Testar** em E6, como baseline | Mais reativa e sem atraso. Mais testes, mais falsos splits sob persistência (0,38 contra 0,01), e censo inviável com participação parcial |
| **Paridade** (ISODATA e especificação) | **Testar** em E6 | A mais fiel ao artigo. Metade das rodadas com teste, sem esfriamento, e merge sempre na rodada seguinte a um split |
| **Período fixo** | **Testar** em E6 | **Concorrente direto.** No toy, empata com os primos na partição e é mais simples de explicar. Exige escolher o período |
| **Evento, sem calendário** | **Testar** em E6 | Age assim que o critério vale, com guardas por idade. Se as guardas bastam, o calendário pode ser desnecessário. É a alternativa mais simples conceitualmente |
| **Fases** (primeiro só split, depois só merge) | **Testar** em E6 | ARI 1,00 no toy, como a parada do split. Mas sem merge na primeira metade, um excesso de divisão fica mais tempo, e a partida por `ψ` perde o caminho de cluster pequeno no início |
| **Primos sem o segundo gêmeo** (lacuna mínima 4) | **Descartar** | Elimina as janelas coladas sem parâmetro novo, mas a espera já resolve o problema real |
| **Sequências mais ralas:** quadrados, Fibonacci, potências de 2 | **Descartar** | Até `R = 200` dão 12, 7 e 5 janelas, com lacunas de até 27, 55 e 64 rodadas. Atrasariam demais os splits em cascata |
| **Janelas aleatórias** | **Descartar** | Dificulta comparar execuções e não traz vantagem |
| **Split e merge na mesma rodada** | **Descartar** | O artigo do ISODATA nunca faz isso, e os dados de uma rodada não sustentam as duas decisões |
| **Forçar split ou merge por `N` versus `K`** (ISODATA, `N ≤ K/2` e `N ≥ 2K`) | **Descartar** | Exige `K`, que CFL e StoCFL dispensam. `K_max` opcional cobre o limite de segurança (DP-18) |

## 2.11 Critérios de aceite

- [ ] `acao(t)` devolve as rodadas das tabelas de 2.1.
- [ ] Nenhuma rodada tem split e merge ao mesmo tempo.
- [ ] Os splits param na fração configurada de `R`, e os merges continuam até as últimas `F` rodadas.
- [ ] Nas últimas `F` rodadas, só há `NADA`.
- [ ] A interface aceita qualquer calendário da seção 2.10 sem mudar os operadores.
- [ ] `calendario_isodata(K)` reproduz a linha 116 de `ISODATAKit.py`.
