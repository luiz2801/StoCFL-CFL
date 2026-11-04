# 11. Decisões pendentes

> **Nenhuma destas decisões foi tomada.** Cada seção explica o dilema, como cada opção ajuda, o que ela custa e o que os testes mostraram. A recomendação é uma proposta, não uma escolha (política 4 do [CLAUDE.md](../../../CLAUDE.md)). Quando uma decisão for resolvida, registre em [decisoes.md](../../decisoes.md) e atualize o módulo correspondente. Neste documento, "você" é quem decide: a pessoa responsável pelo repositório.
>
> **Os números vêm do [toy](anexo-a-simulacao.md)**, um modelo quadrático com 30 sementes, salvo indicação em contrário. Eles mostram mecanismos: quem desfaz quem e por quê. Não preveem acurácia em redes neurais. "ARI" mede a partição: 1,00 é a partição correta, e 0,00 equivale ao acaso. "Rodada correta" é quando a partição certa é atingida, e "perda média" resume a qualidade ao longo do treino (menor é melhor).

## 11.1 Por onde começar

São 19 decisões, mas a maioria não precisa de resposta agora.

| Tipo | Decisões | O que é preciso |
|---|---|---|
| **Só você pode responder:** dependem do seu objetivo ou de informação que só você tem | DP-01, DP-02, DP-10, DP-17, DP-18, DP-19 | Uma resposta (lista abaixo) |
| **Escolha de projeto:** nenhum experimento decide, e a recomendação é clara | DP-14, DP-16 | Um "de acordo", ou uma objeção |
| **O experimento decide:** começa-se pela recomendação, e um experimento confirma ou troca | DP-03 a DP-09, DP-11 a DP-13, DP-15 | Nada agora |

### As perguntas que só você pode responder

| Pergunta | Por que muda o plano | Decisão |
|---|---|---|
| "CFL primeiro" é um requisito seu ou uma suposição? | Se for suposição, a ordem inversa vira uma candidata real, e no toy ela agrupa muito mais cedo | [DP-01](#dp-01-quem-age-primeiro) |
| Os primos são um requisito ou uma hipótese a testar? | Se for hipótese e um período fixo empatar, qual você prefere? | [DP-02](#dp-02-quando-o-cfl-pode-agir) |
| Seu objetivo final precisa de participação parcial? | Define se a Fase 9 é essencial ou opcional. É a principal razão de existir do StoCFL | [DP-10](#dp-10-quantos-clientes-participam) |
| De onde veio a informação de que o CFL é MIT? | O repositório original não declara licença nenhuma | [DP-17](#dp-17-a-licença-do-cfl) |
| Nos seus cenários dá para estimar `K`, mesmo por cima? | Uma estimativa acelerou bastante no toy | [DP-18](#dp-18-o-papel-de-k) |
| Qual é o objetivo do trabalho, e que dados importam? | Define os cenários, e o que se pode concluir no fim | [DP-19](#dp-19-cenários-e-ordem-dos-experimentos) |

## 11.2 Resumo

| ID | O dilema em uma frase | Recomendação | Quem decide | Bloqueia |
|---|---|---|---|---|
| [DP-01](#dp-01-quem-age-primeiro) | Agrupar cedo com `ψ`, arriscando errar, ou tarde com o CFL, de forma robusta? | As duas, com a partida única como referência | Você e E5 | Fase 8 |
| [DP-02](#dp-02-quando-o-cfl-pode-agir) | Poucas janelas custam menos, mas atrasam. E quando o split deve parar? | Primos a partir de 7, parando em 70% das rodadas | Você e E6 | Fase 8 |
| [DP-03](#dp-03-quando-o-stocfl-pode-agir) | Merge frequente corrige mais cedo, mas seria desperdício? | **Rodadas pares** | E6 | Fase 6 |
| [DP-04](#dp-04-como-provar-que-fundir-é-seguro) | `ψ` é grátis e congelado; um teste custa e também erra | Ganho de fusão, com `δ` de 2 erros padrão | E4 | Fase 7 |
| [DP-05](#dp-05-γ_max-no-split) | Sem `γ_max`, o CFL divide por ruído; com ele mal calibrado, nunca divide | Incluir, com alarme | E0 | Fase 4 |
| [DP-06](#dp-06-persistência-antes-do-split) | Agir no primeiro sinal ou esperar para confirmar? | `p = 3` | E6 | Fase 4 |
| [DP-07](#dp-07-o-modelo-depois-do-merge) | Média aproveita o treino de todos, mas pode cair em uma barreira | Média ponderada, testada antes de adotar | E4 | Fase 7 |
| [DP-08](#dp-08-como-bipartir) | *Single* tem garantia e isola outliers; *complete* é equilibrada e não tem | *Single*, com *complete* de reserva | E3 | Fase 4 |
| [DP-09](#dp-09-quanto-esperar-depois-de-cada-operação) | Esperar pouco deixa errar; esperar muito atrasa a correção | **Só espera crescente, sem `W_merge`** | E4 | Fase 7 |
| [DP-10](#dp-10-quantos-clientes-participam) | O CFL exige todos, e o StoCFL existe para não exigir | Total na v1; depois, **sempre com a média corrigida** | Você e E8 | Fase 3 |
| [DP-11](#dp-11-clusters-pequenos) | Em FL não se descarta cliente. Fundir à força ou deixar sozinho? | `TN_FL = 0`; caminho de fusão testada | E5 | Fase 8 |
| [DP-12](#dp-12-reatribuir-clientes) | Sem reatribuir, um cliente fica preso; reatribuir custa caro | Nenhuma na partida única; **seletiva** na partida por `ψ` | E5 e E8 | Fase 9 |
| [DP-13](#dp-13-modelo-global-e-termo-proximal) | O modelo global transfere conhecimento, mas dobra o custo e puxa os clusters | Fora da v1 | E7 | Fase 10 |
| [DP-14](#dp-14-o-que-é-a-base-no-código) | Base verificável custa abstração; laço simples perde a prova | Esqueleto genérico com adaptador de pixels | **Você** | Fase 1 |
| [DP-15](#dp-15-otimizador) | Reproduzir o CFL pede momentum, e o momentum atrapalha o híbrido | SGD puro, com modo de reprodução | Medição na Fase 3 | Fase 3 |
| [DP-16](#dp-16-onde-fica-o-código-e-com-o-quê) | Reaproveitar pronto ou evitar limitações herdadas? | `projetos/ISODATA-FL/`, sem FedLab | **Você** | Fase 1 |
| [DP-17](#dp-17-a-licença-do-cfl) | O CFL original não declara licença | Reescrever sem copiar e confirmar a origem do "MIT" | **Você** | Qualquer publicação |
| [DP-18](#dp-18-o-papel-de-k) | `K` acelera, mas CFL e StoCFL existem para não precisar dele | Sem meta; `K_max` opcional; testar estimativa por cima | **Você** e E6 | Fase 1 |
| [DP-19](#dp-19-cenários-e-ordem-dos-experimentos) | Mais cenários dão mais evidência e custam mais | A lista de [09](09-experimentos.md), reduzida conforme o orçamento | **Você** | Fase 3 |

### A combinação recomendada, rodada junta

Melhorias testadas separadamente podem não funcionar juntas, então a combinação foi testada inteira: `γ_max` de 0,72, persistência de 3 rodadas, ganho de fusão, espera de base 10, CFL em primos a partir de 7 até 70% das rodadas e StoCFL em rodadas pares.

| Cenário | Partida única: ARI, rodada correta, perda média | Partida por `ψ`, com cluster pequeno e reatribuição seletiva |
|---|---|---|
| A: `ψ` separa os grupos | 1,00, rodada 50, 0,119 | 1,00, rodada 1, 0,029 |
| B: `ψ` não separa | 1,00, rodada 57, 0,209 | 1,00, rodada 57, 0,209 |
| C: `ε2` baixo | 1,00, rodada 29, 0,075 | 1,00, rodada 1, 0,029 |
| D: população homogênea | 1,00, rodada 1, 0,028 | 1,00, rodada 1, 0,028 |
| E: `τ` alto demais | 1,00, rodada 50, 0,119 | 1,00, rodada 12, 0,029 |
| C com `γ_max` mal calibrado | 1,00, rodada 122, 0,075 | 1,00, rodada 114, 0,029 |
| `K = 8`, 48 clientes | 1,00, rodada 72, 0,096 | 1,00, rodada 1, 0,017 |
| 10% dos clientes com `ψ` errado | 1,00, rodada 51, 0,118 | 1,00, rodada 11, 0,033 |

### O que mudou em relação à primeira versão deste documento

Os testes mudaram quatro recomendações e corrigiram duas afirmações da primeira versão:

| Decisão | Antes | Agora | Por quê |
|---|---|---|---|
| DP-03 | Interprimos | Rodadas pares | Nenhuma métrica favorece os interprimos, e janelas de merge quase não custam |
| DP-02 | Primos até o fim | Parar os splits em 70% | O merge precisa de tempo para limpar: ARI de 0,94 para 1,00 com `γ_max` errado |
| DP-09 | `W_merge = 10` | Sem `W_merge` | É redundante com a espera, e derruba o ARI de 0,94 para 0,12 |
| DP-10 | Censo primeiro; só amostra adiada | As duas, sempre com média corrigida | Sem a correção o CFL não divide com amostra; com ela, a amostra funcionou tão bem quanto o censo |
| DP-13 | "O termo proximal invalida os limiares do CFL" | Não invalida no toy | A afirmação estava errada: o custo real é outro |
| DP-17 | "Obter o aviso de copyright" | Reescrever sem copiar | O aviso não existe no repositório original |

## 11.3 Como as decisões se ligam

- **DP-01, DP-11 e DP-12** andam juntas. A partida por `ψ` só é segura com o caminho de cluster pequeno e, se `ψ` errar em alguns clientes, com reatribuição seletiva.
- **DP-04 e DP-09** se completam. Com ruído, cada reteste é uma nova chance de aprovar um merge errado, e a espera limita os retestes.
- **DP-05 e DP-02** se cobrem. Se o `γ_max` errar e deixar splits falsos passarem, parar os splits antes do fim dá ao merge tempo para limpar.
- **DP-05 ameaça o merge.** Com `γ_max` bem calibrado, o merge quase não age. Se isso se repetir em redes reais, a versão só com split pode bastar ([01](01-conceito-e-mapeamento.md), P-CON-5).
- **DP-10 enfraquece um argumento de DP-02.** O principal motivo prático para poucas janelas era o custo do censo. Se a amostra corrigida bastar, esse motivo some.
- **DP-15 vem antes de DP-05 e DP-06.** O momentum muda a escala das normas, então os limiares só podem ser calibrados depois de fixar o otimizador.
- **DP-18 limita DP-05.** Quanto mais grupos, menos negativo fica o cosseno entre eles, e menor precisa ser o `γ_max`.

---

## Algoritmo

### DP-01: quem age primeiro

**O dilema.** O CFL só divide depois que o modelo conjunto converge. Até lá, clientes com distribuições diferentes treinam o mesmo modelo, que fica medíocre para todos. O StoCFL pode agrupar desde a primeira rodada, mas só se `ψ` e `τ` estiverem bons. Se não estiverem, o treino começa com a partição errada. É uma troca entre **velocidade e robustez**, e a ordem que você pediu escolhe a robustez.

**Os dois erros não têm o mesmo peso.** Juntar demais é corrigível, porque o CFL separa depois. Separar demais não é, porque o CFL só divide. Isso explica a tabela abaixo.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Partida única** (o pedido): 1 cluster com todos | É imune a `τ`. Começa do modelo FL, que serve de referência ("pelo menos tão bom quanto o FL") | Agrupa tarde. Até lá, todos treinam um modelo de compromisso |
| **Partida por `ψ`:** clientes com `cos(ψ) ≥ τ` começam juntos | Agrupa na rodada 1. Se `ψ` é bom, o CFL nem precisa agir | Depende de `τ` e exige `ψ` de todos antes de começar. Com `τ` alto, os clientes ficam presos sozinhos |
| **Partida por `ψ` + cluster pequeno** ([DP-11](#dp-11-clusters-pequenos)) | Conserta o erro irreversível: cluster pequeno testa fusão mesmo abaixo de `τ` | Mais testes de fusão, e uma regra a mais |

ARI, rodada correta e perda média, conforme `τ`. No cenário, o cosseno de `ψ` é 0,50 entre grupos e 0,98 dentro do grupo:

| `τ` | Partida única | Partida por `ψ` | Partida por `ψ` + cluster pequeno |
|---|---|---|---|
| 0,30 e 0,45: baixo demais | 1,00, rodada 50, 0,119 | 1,00, rodada 50, 0,119 (vira partida única) | Igual |
| 0,65 e 0,90: no vão | 1,00, rodada 50, 0,119 | **1,00, rodada 1, 0,029** | **1,00, rodada 1, 0,029** |
| 0,995: alto demais | 1,00, rodada 50, 0,119 | **0,00**, 24 clusters | 1,00, rodada 15, 0,029 |

**Duas ressalvas.** No toy, um cliente sozinho aprende quase tão bem quanto um cluster, o que favorece a partida por `ψ`: em redes com poucos dados, ele generalizaria mal. E a tabela supõe um `ψ` que separa os grupos, algo que o experimento E0 ainda precisa confirmar em dados reais.

**Recomendação.** Implementar as duas, porque a diferença é uma configuração, e manter a partida única como referência. E5 compara com dados reais.

**Se errar:** custo baixo, é uma troca de configuração. **O que preciso de você:** saber se "CFL primeiro" é um requisito. Se for, o plano não muda, e E5 fica só como comparação.

### DP-02: quando o CFL pode agir

**O dilema tem duas partes.**

*Com que frequência?* Menos janelas custam menos e testam menos, mas atrasam os splits. A hipótese era que os primos também evitariam que um desfizesse o outro. Isso **não se confirmou**: no toy, sem guardas, quase todo split é desfeito em qualquer calendário ([05](05-estabilidade.md), 5.1). Sobra a pergunta: a regra dos primos vale pelo custo, ou um período fixo faz o mesmo?

*Até quando?* Se o split pode agir até o fim, a última operação pode ser um split falso, sem tempo de correção. Se ele para cedo, um split necessário e tardio se perde.

| Calendário | Como ajuda | O que custa | Testes até `R = 150` | Rodada correta (A) | Falso split, com persistência |
|---|---|---|---|---|---|
| **Primos a partir de 7** (hipótese) | Sem parâmetro, é subconjunto das ímpares do ISODATA, e fica mais raro com o tempo | Lacuna irregular, que chega a 2 rodadas | 31 | 50,2 | 0,01 |
| **Período fixo de 4** | Fácil de explicar, com lacuna constante | É preciso escolher o período | 34 | 49,5 | 0,00 |
| **Paridade** (ISODATA original) | A mais fiel ao artigo, e mais rápida | Teste em metade das rodadas | 67 | 45,1 | 0,29 |
| **Toda rodada, ou "evento"** | A mais rápida e a mais simples, se as guardas bastarem | Mais testes e censo inviável | 134 | 44,1 | 0,38 |

Falso split medido em população homogênea, com `ε2 = 0,026`.

**Parar antes do fim** foi o achado mais útil desta rodada de testes. Com `γ_max` mal calibrado, deixando splits falsos passarem:

| Regra de parada do split | ARI | Splits e merges | Rodada correta |
|---|---|---|---|
| Até o fim | 0,94 | 13,5 e 12,1 | 130 |
| Para em 90% | 0,94 | 13,4 e 12,1 | 130 |
| **Para em 70%** | **1,00** | 10,8 e 9,8 | 126 |
| **Para em 50%** | **1,00** | 5,7 e 4,7 | 84 |
| Fases: só split até 50%, e depois só merge | **1,00** | 7,1 e 6,1 | 86 |

A explicação é simples: o merge tem prova, e o split falso, não. Se o merge tem a última palavra, ele limpa os erros, e os splits corretos sobrevivem, porque o teste recusa desfazê-los. É uma extensão da iteração de consolidação do artigo do ISODATA. Nos cenários A e B, parar não custa nada, porque os splits terminam antes de 50% das rodadas.

**O risco:** com treino lento, um split necessário pode cair depois do limite. O CFL do artigo dividiu nas rodadas 50, 100 e 150, então `R` precisa ser dimensionado pensando nisso.

**Recomendação.** Primos a partir de 7, parando em 70% das rodadas. E6 compara com período fixo e paridade, e testa `t_min` em {7, 11, 23}. No toy, `t_min` não faz diferença, porque `ε1` é quem decide, mas o toy não pune um split cedo demais.

**Se errar:** custo baixo, o calendário é um módulo isolado. **O que preciso de você:** saber se os primos são um requisito. Se empatarem com o período fixo em E6, qual você prefere?

### DP-03: quando o StoCFL pode agir

**O dilema.** Sua regra define as rodadas do CFL, mas não as do StoCFL. Merge frequente corrige excesso de divisão mais cedo. Parece desperdício, e também parece arriscado testar logo depois de um split, antes de os filhos divergirem.

**O que os testes mostraram:** os dois receios não se confirmam. Uma janela de merge quase não custa, porque calcular cossenos é só no servidor, e a espera crescente limita os testes. O risco de testar cedo é coberto pela própria espera.

| Opção | Como ajuda | O que custa | Janelas até 200 | ARI, `γ_max` errado | Rodada correta, cenário E | Testes, cenário B |
|---|---|---|---|---|---|---|
| **Rodadas pares** | Simples, e é a iteração de merge do ISODATA. Primos a partir de 3 são ímpares, então nunca colide | Merge na rodada seguinte a um split, coberto pela espera | 97 | **0,99** | 12 | 21,0 |
| **Interprimos** (ponto médio entre primos) | Alternância exata: um merge entre dois splits | Mais difícil de explicar. Nenhuma métrica a favor | 42 | 0,94 | 15 | 20,2 |
| **Todas as não primas** | Corrige mais cedo | Sem ganho claro sobre as pares | 151 | 0,97 | 10 | 21,0 |

**Recomendação.** Rodadas pares. A primeira versão propunha os interprimos, pela elegância da alternância exata, mas ela não trouxe benefício medido. Fica também a formulação simples: **o CFL age nas rodadas primas, e o StoCFL, nas pares.**

**Se errar:** custo mínimo.

### DP-04: como provar que fundir é seguro

**O dilema.** `ψ` é de graça, mas nunca muda. Sozinho, ele refaz o que o CFL separou, indefinidamente. Um teste custa comunicação e também erra, para os dois lados: reprovar uma fusão boa deixa o cluster fragmentado, e aprovar uma ruim desfaz um split correto.

| Opção | Como ajuda | O que custa | B: deve recusar | C com `γ_max` errado: deve aceitar | E: só dentro do grupo |
|---|---|---|---|---|---|
| **Só `ψ`** (StoCFL original) | Sem comunicação extra | Desfaz splits corretos quando `ψ` não separa | 0,63 | 0,94 | 0,00 |
| **Ganho de fusão:** a perda dos membros não piora no modelo fundido | Testa o modelo que será adotado, e o sinal da diferença tem significado direto | 1 download por cliente testado | **1,00** | **0,94** | **1,00** |
| **Perda cruzada** (FedDrift), tolerância 0 | Precedente na literatura | Reprova quase tudo: 1.104 testes inúteis em E | 1,00 | 0,04 | 0,00 |
| **Perda cruzada**, tolerância 0,05 | Funciona, com a tolerância certa | Depende da escala da perda: mais um número a calibrar | 1,00 | 0,94 | 1,00 |
| **`α_cross` em `θ_m`:** o CFL dividiria a união? | Um único critério para os dois operadores | Exige treinar em `θ_m`, e foi pior quando o merge era necessário | 1,00 | 0,76 | 1,00 |

Valores de ARI, com as demais guardas ligadas. Sem teste, o caminho de cluster pequeno não existe, daí o 0,00 em E. Duas outras métricas candidatas foram descartadas por serem **degeneradas**, ver [04](04-merge-stocfl.md), 4.4.

**O ruído na validação cria outro dilema: qual tolerância `δ`?** O toy original media a perda sem ruído, o que era a sua maior limitação. Com ruído `σ_val` por cliente:

| `σ_val` | B, `δ = 0` | B, `δ` = 2 erros padrão | B, idem, **sem espera** | C errado, `δ = 0` | C errado, `δ` = 2 erros padrão |
|---|---|---|---|---|---|
| 0,1 | 1,00 | 1,00 | 1,00 | 0,54 | 0,84 |
| 0,3 | 1,00 | 0,88 | **0,10** | 0,52 | 0,84 |
| 1,0 | 0,79 | 0,68 | **0,00** | 0,51 | 0,84 |

- **`δ = 0` é seguro contra merges errados, mas reprova metade das fusões boas**, porque em uma fusão boa o ganho real é quase zero e o ruído decide no cara ou coroa.
- **`δ` = 2 erros padrão aceita as boas**, e começa a errar quando o ruído se aproxima do ganho real. Em B, o ganho real é de cerca de 0,25, e com `σ_val = 0,3` o `δ` já é 0,12.
- **Sem espera, o estrago é grande:** cada reteste é uma nova chance de o ruído aprovar por engano. A espera é uma proteção estatística, além de economia.

**Regra prática:** o teste só é confiável se o erro padrão de `ΔL` for bem menor que o ganho de um split verdadeiro. Se não for, é preciso testar mais clientes.

**Recomendação.** Ganho de fusão, com `δ` de 2 erros padrão estimados dos próprios valores por cliente, sempre com espera. E4 compara com as alternativas em redes reais.

**Riscos em redes reais:** clientes com mistura de rótulos diferente podem ter perda maior sem que a fusão seja ruim (crítica do FedCCFA, [anexo B](anexo-b-literatura.md)). O erro é conservador: mantém os clusters separados.

**Se errar:** médio. Uma verificação frouxa volta a oscilar; uma rígida deixa os clusters fragmentados. As duas situações aparecem nas métricas.

### DP-05: `γ_max` no split

**O dilema.** O artigo do CFL inclui esse teste no Algoritmo 5, e o notebook não. Ele verifica se a bipartição é significativa: se os dois lados realmente apontam para direções opostas. Os dois erros possíveis são muito diferentes:

- **Sem o teste:** o CFL divide por ruído. No toy, com `ε2` baixo, são 20 clusters em uma população de 2 grupos (ARI 0,03).
- **Com `γ_max` alto demais:** o algoritmo **nunca divide, e não dá erro nenhum**. Parece que a população é homogênea, mas é só FedAvg.

A faixa útil é estreita, fica acima da linha do ruído e abaixo da linha de `K`. Com `D = 20.000`:

| `γ_max` | Cenário C: split falso (deveria recusar) | `K = 8`: split correto (deveria aprovar) |
|---|---|---|
| 0,68 e 0,70 | ARI 0,83: deixa passar | 1,00 |
| **0,72 e 0,74** | **1,00** | **1,00** |
| 0,76 | 1,00 | **0,00: nunca divide** |

A linha de `K` é cerca de `√((1 + 1/(K−1)) / 2)`, e a do ruído tende a 0,707 quando a dimensão cresce.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Não incluir** (como o notebook) | Sem falha silenciosa e sem calibração | Sem proteção contra splits falsos, exceto `ε2` e o merge |
| **Incluir com valor fixo** | É a proteção do artigo, e não custa comunicação | Se errar para cima, falha em silêncio |
| **Incluir, com alarme e calibração** | Mantém a proteção e torna visível a falha: recusas seguidas com `ε` satisfeitos disparam um alarme | Mais telemetria, e um passo de calibração em E0 |

**Recomendação.** Incluir, com alarme. A faixa do toy não vale para redes reais, porque `ΔW` real não é ruído isotrópico. E0 mede a faixa real.

**Se errar:** o erro para cima é o perigoso, por ser invisível sem o alarme. O erro para baixo é coberto pelo merge e pela parada do split: com `γ_max = 0,68`, a combinação recomendada ainda chega a ARI 1,00.

### DP-06: persistência antes do split

**O dilema.** O CFL decide com o valor instantâneo de `mean_norm`. Na primeira rodada abaixo de `ε1`, `max_norm` ainda contém o resíduo comum a todos, e isso faz parecer que algum cliente está longe do ótimo. O resultado é um falso split, sempre no mesmo momento (por volta da rodada 23). Exigir várias rodadas seguidas abaixo de `ε1` evita isso, mas atrasa os splits verdadeiros.

| `p` | Falso split, `ε2 = 0,026` | Falso split, `ε2 = 0,027` | Rodada correta (A) | Perda média (A) |
|---|---|---|---|---|
| 1 (como o CFL) | 0,93 | 0,54 | 41,6 | 0,107 |
| 2 | **0,01** | **0,00** | 48,7 | 0,116 |
| 3 | 0,01 | 0,00 | 50,2 | 0,119 |
| 5 | 0,01 | 0,00 | 55,4 | 0,132 |
| 8 | 0,00 | 0,00 | 60,4 | 0,140 |

Falso split em 200 sementes.

**Como ajuda:** o monitoramento é gratuito, porque usa os `ΔW` que o FedAvg já envia. **O que custa:** cerca de 7 rodadas de atraso de `p = 1` para `p = 2`, e pouco mais depois disso.

**Recomendação.** `p = 3`. No toy, `p = 2` já resolve, mas redes reais são mais ruidosas, e a margem custa só 1,5 rodada. E6 confirma. Com `p = 1`, reproduz-se o CFL.

**Se errar:** baixo. É um número.

### DP-07: o modelo depois do merge

**O dilema.** Dois clusters viram um, e sobra uma pergunta: qual modelo? A média aproveita o treino dos dois, mas em redes não convexas ela pode cair em uma **barreira de perda**, um ponto ruim entre dois pontos bons. Manter o modelo do maior é seguro, mas joga fora o treino do menor. **O toy não responde a isso**, porque um modelo quadrático não tem barreira.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Média ponderada** (ISODATA, FedDrift) | Aproveita o treino dos dois. Equivale a uma rodada de FedAvg | Pode cair em barreira |
| **O maior vence** (`unite` do StoCFL) | Sem barreira, e sem custo | Descarta o treino do menor. No código nem é sempre o maior (guia 4.16) |
| **O melhor na validação da união** | O mais seguro | Um download a mais por cliente testado |
| **Voltar ao ancestral comum** (cache do CFL) | Modelo já validado | Perde o treino desde o split |

**Por que a média é defensável aqui.** Redes treinadas a partir do mesmo ponto, depois de estáveis, tendem a não ter barreira entre elas (Frankle et al., [anexo B](anexo-b-literatura.md)). Dois clusters que merecem fundir têm dados parecidos e um ancestral comum, que é o caso favorável. Além disso, o ganho de fusão **testa exatamente a média**: se ela cair em uma barreira, o teste reprova, e o erro vira uma fusão recusada, não um modelo ruim.

**Recomendação.** Média ponderada, testada antes de adotar. E4 mede com que frequência ela é reprovada e se o segundo candidato (o maior) resolveria esses casos.

**Se errar:** baixo, por causa do teste.

### DP-08: como bipartir

**O dilema.** A garantia do artigo do CFL (Corolário 1) vale para o Algoritmo 1, equivalente a *single linkage*. Mas *single* tende a isolar outliers, gerando filhos de um cliente só. O notebook usa *complete*, com filhos equilibrados e sem a garantia, e é o que seria preciso para reproduzi-lo.

| `σ` | `K` | *Single*: grupos intactos | *Single*: menor filho | *Complete*: grupos intactos | *Complete*: menor filho |
|---|---|---|---|---|---|
| 0,02 a 0,15 | 2 | 1,00 | 12,0 | 1,00 | 12,0 |
| 0,02 a 0,15 | 4 | 1,00 | 7,5 | 1,00 | 9,4 |
| 0,20 | 2 | 0,94 | 11,5 | 0,96 | 12,0 |
| 0,20 | 4 | 0,94 | 7,2 | 0,88 | 9,2 |
| 0,30 | 2 | 0,07 | 2,6 | 0,31 | 10,3 |
| 0,30 | 4 | 0,03 | 1,7 | 0,10 | 8,5 |

Bipartição forçada no ponto estacionário, 200 sementes. O ruído `σ` vai de 0,02, o padrão do toy, até mais de 4 vezes o sinal.

**Leitura:** as duas empatam em quase toda a faixa. Com ruído muito alto, as duas falham, e *complete* degrada de forma mais gradual. Nesse caso, um `γ_max` calibrado deveria recusar o split de qualquer forma.

**Recomendação.** *Single*, que é o que tem garantia e dispensa o `scikit-learn`, com *complete* de reserva quando um filho sair pequeno demais. E3 compara.

**Se errar:** baixo, é uma função trocável.

### DP-09: quanto esperar depois de cada operação

**O dilema.** Depois de um split, quanto tempo até permitir reunir os filhos? Pouco: os modelos ainda não divergiram, e o teste não tem o que medir. Muito: um split falso demora a ser corrigido. Havia duas ferramentas candidatas.

**`W_merge` (idade mínima do cluster) é prejudicial.** A primeira versão recomendava `W_merge = 10`, e estava errada:

| `W_merge` | ARI, C com `γ_max` errado | N final | ARI, B |
|---|---|---|---|
| **0** | **0,94** | 2,4 | 1,00 |
| 5 | 0,38 | 9,1 | 1,00 |
| 10 | 0,12 | 13,8 | 1,00 |
| 20 | 0,10 | 14,0 | 1,00 |
| 40 | 0,08 | 14,3 | 1,00 |

O motivo é claro: todo cluster recém-criado fica bloqueado, inclusive os que acabaram de se fundir, então fusões em sequência ficam presas. Além disso, `W_merge` é **redundante**: a espera já bloqueia os irmãos depois de um split, que era o único caso que importava.

**A espera crescente ajuda em três frentes:** depois de um split, reunir os irmãos espera `W`, depois `2W`, `4W`; depois de um merge, o mesmo para separar; depois de um teste reprovado, o reteste também espera mais.

| Base da espera | ARI, `γ_max` errado, primos até o fim | ARI, `γ_max` errado, calendário recomendado | Testes, B | Splits, pior caso |
|---|---|---|---|---|
| Nenhuma | 0,79 | 1,00 | 116,4 | 45,0 |
| 5 | 0,79 | 1,00 | 22,9 | 9,0 |
| **10** | **0,94** | **1,00** | **20,2** | **7,0** |
| 20 | 0,33 | 1,00 | 16,4 | 5,0 |
| 40 | 0,99 | 0,99 | 11,2 | 5,0 |

**Como ajuda:** a espera limita a oscilação a `log2(R/W + 1)` voltas por par, corta os testes em cerca de 6 vezes e protege contra o ruído da validação ([DP-04](#dp-04-como-provar-que-fundir-é-seguro)). **O que custa:** atrasa correções legítimas. A coluna "até o fim" oscila de forma irregular (0,33 com base 20), porque o resultado depende de qual operação caiu por último. O calendário recomendado elimina essa loteria.

**Recomendação.** Só a espera crescente, com base 10, sem `W_merge`. E4 calibra a base em redes reais.

**Se errar:** baixo. É um número, e a métrica de oscilação mostra o efeito.

---

## Participação e clientes

### DP-10: quantos clientes participam

**O dilema.** O CFL pressupõe todos os membros em toda rodada. O StoCFL existe para não exigir isso. Um híbrido que só funcione com todos perde metade do motivo de combiná-los. Mas participação parcial mistura riscos, e não há baseline do CFL nesse modo.

**O teste revelou um problema inesperado.** O obstáculo previsto era a bipartição com dados incompletos. Na verdade, **o critério do CFL nem dispara**: em um cluster com grupos opostos, a média de uma amostra não se cancela, e `mean_norm` fica alto justamente quando o cluster é incongruente.

```text
‖média da amostra‖²  ≈  ‖média real‖²  +  variância / m
```

Com `‖ΔW‖ ≈ 0,087` e `ε1 = 0,015`, seriam necessários mais de 34 clientes amostrados por cluster para o critério passar. Por isso, o censo sozinho não resolve: ele nunca é chamado.

**A correção** é descontar da média o que vem de sortear poucos clientes, e é um estimador padrão, sem custo de comunicação:

```text
mean_norm² corrigido = ‖ΔW̄‖² − (s² / m) · (1 − m / n)      s²: variância amostral dos ΔW; n: membros; m: amostrados
```

Cenário A com 100 clientes, 15 sementes. O cenário B dá o mesmo quadro:

| Participação | Sem correção: censo / amostra | **Corrigida: censo** (ARI, rodada, treino extra) | **Corrigida: só amostra** (ARI, rodada) |
|---|---|---|---|
| 100% | 1,00 | 1,00, rodada 51 | 1,00, rodada 51 |
| 50% | 1,00 / 1,00 | 1,00, rodada 58, +1,5% | 1,00, rodada 59 |
| 20% | **0,34 / 0,40** | 1,00, rodada 69, +6% | **1,00, rodada 64** |
| 10% | **0,00 / 0,00** | 0,98, rodada 80, +17% | **1,00, rodada 79** |
| 5% | **0,00 / 0,00** | 0,94, rodada 110, +41% | 0,92, rodada 106 |

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Total** (M1) | Exata, reproduz o CFL e isola os demais problemas | Irrealista, e custa `N` treinos por rodada |
| **Censo com média corrigida** (M2) | Bipartição exata, com todos os membros do candidato | Treino extra e clientes disponíveis sob demanda, o que nem sempre é possível |
| **Só amostra com média corrigida** (M3) | Nenhum treino extra e nenhum pedido especial, o que combina com o espírito do StoCFL | Bipartição parcial. Os demais seguem o filho de `ψ` mais próximo, **o que depende de `ψ` ser informativo** |

**Por que o resultado favorável à amostra pode não se repetir.** No toy, `ψ` sempre diz qual grupo é o mais próximo, mesmo quando não separa pelo limiar `τ`. Em redes reais isso precisa ser verificado, e por isso o censo continua na comparação.

**Interação com a parada do split.** Com poucos clientes, tudo fica mais lento. Com a parada em 70% das rodadas, a amostra corrigida mantém ARI 1,00 até 20% de participação, cai para 0,98 com 10% e para 0,74 com 5%, porque os splits não terminam a tempo. Em participação baixa, a parada precisa vir mais tarde.

**Recomendação.** Participação total na v1. Depois, **sempre com a média corrigida**, comparando censo e amostra em E8.

**Se errar:** médio. Com a correção, o custo de testar é baixo. **O que preciso de você:** saber se o seu objetivo exige participação parcial. Se exigir, a Fase 9 é central e deve vir antes da Fase 8.

### DP-11: clusters pequenos

**O dilema.** O ISODATA descarta clusters com menos de `TN` pontos. Em FL isso não existe, porque o cliente continua lá e precisa de um modelo. Um cluster pequeno tem poucos dados e um modelo ruim. Fundi-lo à força pode contaminar o vizinho, e deixá-lo sozinho prejudica seus membros. Há duas perguntas separadas.

**Antes: limitar o tamanho dos filhos (`TN_FL`)?** Isso evita fragmentação, mas exige saber o tamanho do menor grupo real:

| `TN_FL` | Só divide cluster com mais de | Sobredivisão: ARI, N final | Sem sobredivisão, 6 clientes por grupo: ARI |
|---|---|---|---|
| 0 (como o CFL) | 2 | 0,04, 19,2 | 1,00 |
| 1 | 4 | 0,20, 8,6 | 1,00 |
| 2 | 6 | 0,43, 5,1 | 1,00 |
| 3 | 8 | 0,62, 3,5 | 1,00 |
| 5 | 12 | 1,00, 2,0 | **0,63: bloqueia split legítimo** |

Um `TN_FL` alto também impede isolar um cliente com distribuição realmente única, o que pode ser o certo a fazer.

**Depois: o que fazer com um cluster que ficou pequeno?**

| Opção | Como ajuda | O que custa | Cenário E, partida por `ψ`: ARI, N final, testes |
|---|---|---|---|
| **Nada** | Simples, como o CFL | Clientes presos com pouca informação | 0,00, 24, 0 |
| **Fusão testada, sem `τ`** (`n_pequeno = 3` ou mais) | Une o que `ψ` não une, sem risco de contaminar, porque o ganho de fusão filtra | Mais testes | 1,00, 4, 26 a 44 |
| `n_pequeno = 2` | Menos testes | Para em pares | 0,28, 12, 12 |
| **Fusão forçada, sem teste**, `n_pequeno = 12` | Sempre resolve o tamanho | **Contamina**: junta grupos diferentes | 0,30, 1,9 |

**Recomendação.** `TN_FL = 0` na v1, que reproduz o CFL, e fusão testada para clusters pequenos, com `n_pequeno` entre 3 e 6, se a partida por `ψ` for usada. Com a partida única, quase não entra em ação. E5 confirma.

**Se errar:** baixo, se a fusão for sempre testada. Forçar é o único erro grave.

### DP-12: reatribuir clientes

**O dilema.** A "classificação" do ISODATA, que permite cada ponto trocar de grupo a cada iteração, é o que lhe dá autocorreção. CFL e StoCFL só movem clientes em blocos: um cliente no cluster errado fica preso. Mas reatribuir exige que cada cliente avalie vários modelos, é sensível a ruído, e foi criticado no IFCA pelo custo e pelo "domínio" de um modelo (guia 4.15).

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Nenhuma** | Simples, sem comunicação | Cliente mal colocado depende de um split seguido de fusão |
| **Completa, nas janelas de split** | É a classificação do ISODATA. Todo cliente avalia todos os modelos | `N × (clusters − 1)` downloads por janela |
| **Seletiva** | Cada cliente já sabe a perda no próprio modelo. Só quem está muito acima da mediana do cluster testa os demais | Um limiar a mais |
| **Em toda rodada** (IFCA) | A mais reativa | Custo proibitivo, e precisa de `K` fixo |

Quando `ψ` erra em 10% dos clientes, com partida por `ψ` e 48 clientes:

| Configuração | ARI | N final | Modelos extras | Rodada correta | Perda média |
|---|---|---|---|---|---|
| Só CFL e merge | 0,86 | 7,5 | 0 | Nunca | 0,053 |
| Com cluster pequeno | 0,98 | 4,4 | 0 | 74 | 0,051 |
| Reatribuição completa | 1,00 | 4,0 | 4.464 | 7 | 0,031 |
| **Reatribuição seletiva** | **1,00** | **4,0** | **15** | **11** | **0,033** |
| Seletiva, com ruído `σ_val = 0,1` | 1,00 | 4,0 | 1.334 | 12,5 | 0,033 |

**A seletiva dá o mesmo resultado com 300 vezes menos downloads**, embora o ruído reduza essa vantagem. Ela é eficaz para clientes claramente mal colocados.

**Ela não é a cura para splits falsos.** Com ruído alto no treino (`σ = 0,15`) e sem `γ_max`, a reatribuição completa chega a ARI 1,00 sem nenhum merge, porque o filho errado esvazia e some, como no ISODATA original. Mas esse resultado depende de uma validação sem ruído: com `σ_val = 0,1` e margem de 0,3, o ARI só sobe de 0,24 para 0,38.

**Recomendação.** Nenhuma com a partida única, em que não apareceram clientes presos (ARI 1,00, mesmo com `ψ` errado). Seletiva, se a partida por `ψ` for usada. E5 e E8 confirmam.

**Se errar:** baixo, é um módulo opcional.

---

## Modelos

### DP-13: modelo global e termo proximal

**O dilema.** O StoCFL treina também um modelo global e puxa cada cluster em direção a ele. Isso transfere conhecimento entre clusters, o que é essencial quando cada cluster só vê parte das classes: na Tabela 4 do artigo, a acurácia no cenário patológico vai de 24–38% (`λ ≤ 0,05`) a 89% (`λ = 10`). Mas dobra o treino, acrescenta um hiperparâmetro, e a tração impede cada cluster de chegar ao próprio ótimo.

**Correção da primeira versão.** Ela dizia que o termo proximal invalida os limiares do CFL. No toy, isso não acontece: no ponto estacionário, a tração se cancela com o desvio médio do cluster, e os `ΔW` individuais ficam como eram.

| `μ` | ARI | Rodada correta | Perda final |
|---|---|---|---|
| 0 | 1,00 | 50,2 | 0,0004 |
| 0,1 | 1,00 | 50,3 | 0,0035 |
| 0,5 | 1,00 | 40,2 | 0,0419 |
| 2 | 1,00 | 35,7 | 0,1669 |
| 10 | 1,00 | 36,3 | 0,3101 |

O split continua funcionando, e até antes. O custo aparece no fim: o modelo fica preso entre o ótimo do cluster e o global. **O toy mostra só o lado do custo**, porque não modela transferência de conhecimento: grupos ortogonais não têm nada a compartilhar.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Sem modelo global** (`μ = 0`) | Metade do custo e um hiperparâmetro a menos | Sem transferência. Cluster pequeno ou com poucas classes sofre |
| **Com modelo global** | Transferência entre clusters, e um modelo para clientes novos | Dobra o treino, e o melhor `μ` varia muito por cenário, de 0,05 a 10 |
| **Só na fase final** | Combina os dois | Não testado, e acrescenta o momento de ligar |

**Atenção ao portar:** o `gmodel` do código do StoCFL não é FedAvg, é treino encadeado (guia 4.12, item 12). Uma reimplementação fiel ao artigo não reproduz o código, e vice-versa.

**Recomendação.** Fora da v1, para isolar o efeito do split e do merge. E7 decide. **Se o seu cenário tiver rótulos muito desbalanceados entre clientes, esta decisão sobe de prioridade.**

**Se errar:** médio. Acrescentar depois é simples, porque o treino é um módulo isolado.

### DP-15: otimizador

**O dilema.** Para reproduzir o CFL é preciso o otimizador do notebook: momentum de 0,9 por cliente e lr × 0,99 a cada rodada. Mas o momentum é um estado no cliente: depois de um split ou merge, o buffer aponta para o ótimo do cluster anterior. E um cliente em participação parcial nem sempre guarda estado. Além disso, o momentum muda a escala das normas, então os limiares `ε` deixam de valer.

| `β` (momentum) | Cenário A: ARI, rodada correta | População homogênea: N final (deveria ser 1) |
|---|---|---|
| 0 | 1,00, rodada 50 | 1,0 |
| 0,5 | 1,00, **rodada 36** | 1,0 |
| 0,9, mesmos `ε` | **0,61** | **11,5** |
| 0,9, buffers zerados em split e merge | 1,00, rodada 89 | **10,7** |
| 0,9, `ε2` reescalado | **0,61** | 1,0 |

**Leitura:** momentum moderado acelera. Com 0,9, nenhuma correção isolada resolve: zerar os buffers conserta um cenário, e reescalar `ε2` conserta o outro. O modelo de momentum do toy é simplificado (um passo por rodada), então os números são só indicativos.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **SGD puro**, sem decaimento | Cliente sem estado, normas com significado estável | Pode treinar mais devagar, e não reproduz o notebook diretamente |
| **Como o notebook** | Reprodução direta | Buffers contaminados, e `ε` precisam de calibração própria |
| **Momentum com buffers zerados** e `ε` recalibrados | Mantém a aceleração | Mais calibração, e ainda exige estado no cliente |
| **Momentum no servidor** (FedAvgM, por cluster) | Acelera sem estado no cliente, e é natural zerar em split e merge | Hiperparâmetro a mais, e o artigo original alerta para o ajuste mais difícil. Não testado aqui |

**Recomendação.** SGD puro no híbrido, com o otimizador do notebook configurável, só para o teste de reprodução da Fase 4. Considerar o FedAvgM depois, se a velocidade pesar. Fixar isso **antes** de calibrar `ε`.

**Se errar:** médio, porque obriga a recalibrar os limiares.

### DP-18: o papel de `K`

**O dilema.** No ISODATA, `K` guia o algoritmo: com poucos clusters ele relaxa a divisão e com muitos ele para de dividir. CFL e StoCFL existem justamente para não precisar saber `K`. Mas, sem nenhum limite, um `γ_max` errado pode fragmentar sem controle. E há uma surpresa: **uma estimativa de `K` acelerou bastante.**

Meta como no ISODATA. Com `N ≤ K/2`, o split dispensa a estacionariedade e o `γ_max`, e com `N ≥ 2K`, não há split. `K` real = 4:

| `K_meta` | ARI | Splits e merges | Rodada correta | Perda média |
|---|---|---|---|---|
| Sem meta | 1,00 | 3,0 e 0,0 | 50,2 | 0,119 |
| 1: muito abaixo | **0,34** | 1,0 e 0,0 | Nunca | 0,290 |
| 2: metade | 1,00 | 3,0 e 0,0 | 39,0 | 0,089 |
| **4: exato** | 1,00 | 3,7 e 0,7 | **24,2** | 0,061 |
| 8: o dobro | 1,00 | 6,3 e 3,3 | 26,0 | 0,052 |
| 16: quatro vezes | 1,00 | 9,5 e 6,5 | 30,0 | 0,052 |

**Superestimar é barato**, porque o merge verificado limpa o excesso, e **subestimar demais é grave.** O ganho vem de dividir mais cedo, sem esperar a convergência. Isso funciona no toy porque `ΔW` já separa os grupos cedo. O artigo do CFL mostra separação depois de cerca de 10 rodadas em um experimento (guia 3.9.7), mas isso precisa ser verificado.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Sem `K`** | Mantém a propriedade que motiva CFL e StoCFL | Mais lento, sem limite de segurança |
| **`K_max` como limite** | Cinto de segurança contra fragmentação: com `γ_max` e merge desligados, N final cai de 19 para 8 com `K_max = 8` | Abaixo do real, bloqueia: com `K_max = 2` e `K = 4`, o ARI é 0,34 |
| **Estimativa de `K`, de preferência por cima** | Divide mais cedo, com o merge limpando o excesso | Exige alguma informação prévia, e a garantia do CFL não vale fora da estacionariedade |

**Recomendação.** Sem meta na referência, `K_max` opcional e desligado, e testar a estimativa por cima em E6.

**Se errar:** baixo, se `K_max` ficar folgado. **O que preciso de você:** saber se dá para estimar `K` nos seus cenários. Se der, esta opção sobe de prioridade.

---

## Código e projeto

### DP-14: o que é a "base" no código

**O dilema.** Você pediu o ISODATA como base, mas `ISODATAKit.py` não é reaproveitável: trabalha com `Pixel`, `pixelList` e imagem. Se a base for só inspiração, a frase não pode ser verificada, e o código pode se afastar do ISODATA sem ninguém notar. Se for um esqueleto genérico, há abstração em um projeto cujo único uso real é FL, e abstração prematura tem custo real.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Esqueleto genérico + adaptador de pixels** | "É mesmo o ISODATA" vira um teste. Permite testar sem GPU e sem `torch`. O calendário original vira um plugin | Cerca de 100 linhas a mais. O laço precisa servir a dois mundos |
| **Laço só para FL** | Menos código e leitura direta | A relação com o ISODATA fica só no texto, e perde-se o teste rápido |
| **Refatorar `ISODATAKit.py`** | Um só código | Mexe em algo que funciona, e deixa de existir o oráculo |

**A dúvida sobre o custo foi resolvida com um protótipo:** 22 linhas de esqueleto e 84 de adaptador reproduziram `ISODATAKit.py` **pixel a pixel em 300 de 300 execuções**, em cinza e RGB, com parâmetros aleatórios, cobrindo split (160 execuções), merge (155) e descarte (102). O código está no [anexo A](anexo-a-simulacao.md).

**Recomendação.** Esqueleto com adaptador. O custo é pequeno, e o protótipo já mostra que funciona. O laço só para FL continua sendo uma troca aceitável, se você preferir o mínimo.

**Se errar:** baixo. O adaptador pode sair sem tocar no FL.

### DP-16: onde fica o código e com o quê

**O dilema.** Reaproveitar um subprojeto dá uma base pronta, mas herda as limitações dele. Começar um novo evita isso, mas exige portar o que for usado.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **`projetos/ISODATA-FL/`, novo, sem FedLab** | Ambiente atual (Python 3.12, PyTorch recente), sem dependências desnecessárias. Segue "um subprojeto por algoritmo" | Portar particionadores e treino, e gerar as referências dos originais em ambientes próprios |
| Dentro de `projetos/StoCFL/` | Dados e treino prontos | Prende a Python 3.8–3.10 e `fedlab==1.2.1`, com `spacy` e `cvxopt` obrigatórios |
| Dentro de `projetos/clustered-federated-learning/` | Cenário pronto | Fluxo de notebook, sem testes, sem licença declarada ([DP-17](#dp-17-a-licença-do-cfl)) |
| Dentro de `projetos/ISODATA-python/` | Fica junto da base | Mistura `torch` em uma ferramenta de imagens |
| Framework pronto (Flower e similares) | Infraestrutura pronta e caminho para execução real | Dependência pesada para uma simulação, e os operadores mexem no estado do servidor o tempo todo |

**`scikit-learn` também sai:** `agrupar` substitui o `AgglomerativeClustering` com poucas linhas, e elimina a incompatibilidade de `affinity`.

**Recomendação.** Novo subprojeto, sem FedLab e sem `scikit-learn`.

**Se errar:** médio. Mudar de lugar é fácil; mudar de pilha, não.

### DP-17: a licença do CFL

**O dilema.** A D-009 registra o CFL como MIT, a partir da sua informação. **Mas o repositório original não declara licença nenhuma:** em 2026-11-04, não havia arquivo `LICENSE`, o README não mencionava licença, nenhum commit falava disso, e o GitHub não reconhecia nenhuma (`license: null`). Em geral, código sem licença explícita tem todos os direitos reservados ao autor, o que restringe copiar e redistribuir. **Isto não é parecer jurídico.**

A questão é separada em duas:

- **O ISODATA-FL futuro:** dá para evitar por completo.
- **A cópia que já está em `projetos/clustered-federated-learning/`:** hoje não há remote, então nada foi distribuído. A questão aparece se o repositório for publicado.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **Confirmar a origem do "MIT"** | Se veio do autor ou de outra fonte, basta registrar, e a questão se resolve | Só depende de você lembrar de onde veio |
| **Pedir ao autor uma licença ou permissão** | Resolve de vez, inclusive para a cópia existente, e permite criar o `LICENSE` que falta | Depende de resposta. O repositório não é atualizado desde 2021 |
| **Reescrever a partir do artigo, sem copiar** | Resolve para o ISODATA-FL. Quase não custa, porque o plano já reimplementa tudo, e as fórmulas estão no artigo | Não resolve a cópia existente |
| **Tirar o subprojeto antes de publicar** | Resolve a cópia, e o artigo continua citado | Perde o baseline local |
| **Seguir como está** | Sem esforço agora | Risco se publicar |

**Recomendação.** Reescrever o que o ISODATA-FL precisar, sem copiar, e confirmar de onde veio o "MIT". Se a origem não se confirmar, pedir ao autor antes de qualquer publicação.

**Se errar:** não afeta o algoritmo. O risco só existe em caso de publicação, e é evitável antes dela.

### DP-19: cenários e ordem dos experimentos

**O dilema.** Os cenários definem o que se pode concluir. Muitos dão mais evidência, mas o custo por execução ainda não foi medido. O cenário do notebook (2 grupos) nem exercita o merge. FEMNIST é o mais convincente, mas não tem ground truth, então não há ARI, e a execução é cara.

| Opção | Como ajuda | O que custa |
|---|---|---|
| **A lista de [09](09-experimentos.md), em sequência** | Cobre não dividir, dividir, sobredividir, hierarquia e dados reais. Cada etapa pode interromper o projeto | É longa, e pode precisar de corte depois da Fase 3 |
| **Só reproduzir os artigos** | Comparação direta com a literatura | Não exercita o merge nem o caso de `γ_max` errado, que é onde o híbrido se justifica |
| **Começar por dados reais** | Resultado convincente mais cedo | Sem ground truth, um resultado ruim não diz o que deu errado |
| **Um cenário-alvo seu** | Foco no que importa para você | Só faz sentido se existir um cenário-alvo |

**Recomendação.** A lista proposta, cortando conforme o custo medido na Fase 3. O corte mínimo é C1 (não dividir), C3 (dividir), C4 (sobredividir) e um cenário real.

**Se errar:** médio: dá para acrescentar cenários, mas conclusões em cenários errados custam caro. **O que preciso de você:** o objetivo do trabalho (artigo, comparação, aplicação) e se há dados específicos. Isso pode mudar a lista inteira.

---

## 11.4 O que já foi decidido pelo usuário

Registrado em D-011, em [decisoes.md](../../decisoes.md).

- O ISODATA é a base.
- O CFL separa os clientes, e o StoCFL os agrupa quando necessário.
- Nenhum dos dois roda em toda rodada.

A regra "CFL em rodadas primas a partir da 7" foi apresentada como hipótese ("acho que"). Por isso, ela é o ponto de partida do plano, mas está em DP-02.

**Bloqueiam a Fase 1:** DP-14, DP-16 e DP-18.

## 11.5 Problemas em aberto da especificação

Como cada um dos 9 problemas da [especificação](../especificacao-isodata-fl.md), seção 5, é tratado neste plano. **Todos continuam em aberto até que as decisões sejam tomadas.**

| # | Problema | Encaminhamento proposto | Módulo | Decisões |
|---|---|---|---|---|
| 1 | Métrica do merge | `ψ` como filtro e ganho de fusão como prova. "Direção média de `ΔW`" e "deslocamento" são degenerados | [04](04-merge-stocfl.md) | DP-04 |
| 2 | Papel de `K` e da alternância | Sem meta de `K`; a alternância passa a ser o calendário | [01](01-conceito-e-mapeamento.md), [02](02-calendario.md) | DP-02, DP-03, DP-18 |
| 3 | Destino de clusters pequenos | Sem descarte; caminho de fusão sem `τ`, verificado | [06](06-clientes-e-participacao.md) | DP-11 |
| 4 | Participação parcial | Total, depois amostra ou censo, sempre com média corrigida | [06](06-clientes-e-participacao.md) | DP-10 |
| 5 | Sensibilidade dos limiares | Calibração do artigo, **e** em vez de **ou**, persistência | [03](03-split-cfl.md) | DP-05, DP-06 |
| 6 | Garantia teórica | Incluir `γ_max`. A espera crescente dá limite para a oscilação, mas a convergência do conjunto continua sem prova | [03](03-split-cfl.md), [05](05-estabilidade.md) | DP-05 |
| 7 | Invariantes do StoCFL | Só a de "não crescente" cai; os ids continuam válidos | [07](07-modelos-e-estado.md) | — |
| 8 | Deslocamento de escala | Sem `±1`; bipartição explícita | [03](03-split-cfl.md) | — |
| 9 | Motivação sem evidência | Revisão de literatura, toy e experimentos com critério de refutação | [anexo A](anexo-a-simulacao.md), [anexo B](anexo-b-literatura.md), [09](09-experimentos.md) | DP-19 |
