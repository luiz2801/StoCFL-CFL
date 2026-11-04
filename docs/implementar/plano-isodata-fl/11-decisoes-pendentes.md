# 11. Decisões pendentes

> **Nenhuma destas decisões foi tomada.** Cada linha traz uma recomendação, não uma escolha (política 4 do [CLAUDE.md](../../../CLAUDE.md)). Quando uma for resolvida, registre em [decisoes.md](../../decisoes.md) e atualize o módulo correspondente.

## 11.1 O que já foi decidido pelo usuário

Registrado em D-011, em [decisoes.md](../../decisoes.md).

- O ISODATA é a base.
- O CFL separa os clientes, e o StoCFL os agrupa quando necessário.
- Nenhum dos dois roda em toda rodada.

A regra "CFL em rodadas primas a partir da 7" foi apresentada como hipótese ("acho que"). Por isso, ela é o ponto de partida do plano, mas está em DP-02.

## 11.2 Decisões

"Bloqueia" indica a fase que não pode começar sem a decisão. Decisões "por experimento" podem começar com o valor recomendado, e o experimento citado confirma ou troca.

### Algoritmo

| ID | Decisão | Opções | Recomendação | Bloqueia | Detalhes |
|---|---|---|---|---|---|
| DP-01 | Partida | Única (pedido) / por `ψ` / as duas | **As duas**, com a única como referência. E5 decide | Fase 8, por experimento | [01](01-conceito-e-mapeamento.md), 1.6 |
| DP-02 | Calendário do CFL | Primos a partir de 7 / período fixo / paridade / evento | **Primos a partir de 7**, sem usá-los como garantia contra a oscilação. E6 decide | Fase 8, por experimento | [02](02-calendario.md) |
| DP-03 | Calendário do StoCFL | Interprimos / não primos / pares | **Interprimos** | Fase 6 | [02](02-calendario.md) |
| DP-04 | Verificação do merge | Ganho de fusão / perda cruzada / `α_cross` em `θ_m` / só `ψ` | **Ganho de fusão**. E4 compara | Fase 7 | [04](04-merge-stocfl.md) |
| DP-05 | `γ_max` no split | Incluir / manter como no notebook | **Incluir**, calibrado em E0 | Fase 4 | [03](03-split-cfl.md) |
| DP-06 | Persistência em `mean_norm` | `p = 3` / `p = 1` (CFL) | **`p = 3`**. E6 confirma | Fase 4, por experimento | [03](03-split-cfl.md) |
| DP-07 | Modelo depois do merge | Média ponderada / o maior vence / melhor na validação | **Média ponderada, testada antes de adotar** | Fase 7 | [07](07-modelos-e-estado.md) |
| DP-08 | Bipartição | *Single* (artigo) / *complete* (notebook) | ***Single***, com *complete* de reserva. E3 compara | Fase 4, por experimento | [03](03-split-cfl.md) |
| DP-09 | Parâmetros de estabilidade | `W_merge` e base da espera | **10 e 10** como início, a calibrar | Fase 7, por experimento | [05](05-estabilidade.md) |

### Participação e clientes

| ID | Decisão | Opções | Recomendação | Bloqueia | Detalhes |
|---|---|---|---|---|---|
| DP-10 | Participação | Total → censo → só amostra | **Total na v1, censo em seguida** | Fase 3 | [06](06-clientes-e-participacao.md) |
| DP-11 | Clusters pequenos (`TN`) | Sem tratamento / caminho de fusão sem `τ` / fusão forçada | **`TN_FL = 0` na v1**; caminho verificado com a partida por `ψ` | Fase 8 | [06](06-clientes-e-participacao.md) |
| DP-12 | Reatribuição | Nenhuma / periódica / toda rodada | **Nenhuma na v1**; só se o ARI mostrar clientes presos | Fase 9 | [06](06-clientes-e-participacao.md) |

### Modelos

| ID | Decisão | Opções | Recomendação | Bloqueia | Detalhes |
|---|---|---|---|---|---|
| DP-13 | Modelo global e `μ` | Fora da v1 / desde o início | **Fora da v1**. E7 decide | Fase 10 | [07](07-modelos-e-estado.md) |
| DP-15 | Otimizador | SGD sem momentum / como o notebook | **Sem momentum**, com o modo de reprodução do notebook configurável | Fase 3 | [07](07-modelos-e-estado.md) |
| DP-18 | Papel de `K` | Sem `K` / `K_max` opcional / meta como no ISODATA | **`K_max` opcional, desligado** | Fase 1 | [01](01-conceito-e-mapeamento.md) |

### Código e projeto

| ID | Decisão | Opções | Recomendação | Bloqueia | Detalhes |
|---|---|---|---|---|---|
| DP-14 | Forma da "base" | Esqueleto genérico com adaptador de pixels / laço só para FL | **Esqueleto com adaptador**, porque torna a base testável. Laço só para FL é uma troca aceitável | Fase 1 | [08](08-arquitetura-do-codigo.md) |
| DP-16 | Local e dependências | `projetos/ISODATA-FL/`, sem FedLab / dentro de um subprojeto | **Novo subprojeto, sem FedLab e sem `scikit-learn`** | Fase 1 | [08](08-arquitetura-do-codigo.md) |
| DP-17 | Licença do CFL | Obter o aviso original / reescrever sem copiar | **Obter o aviso**, que também fecha a pendência de D-009 | Fase 4 | [08](08-arquitetura-do-codigo.md) |
| DP-19 | Cenários e ordem | Lista de [09](09-experimentos.md) / outra | **A lista proposta** | Fase 3 | [09](09-experimentos.md) |

**Bloqueiam a Fase 1:** DP-14, DP-16 e DP-18.

## 11.3 Problemas em aberto da especificação

Como cada um dos 9 problemas da [especificação](../especificacao-isodata-fl.md), seção 5, é tratado neste plano. **Todos continuam em aberto até que as decisões sejam tomadas.**

| # | Problema | Encaminhamento proposto | Módulo | Decisões |
|---|---|---|---|---|
| 1 | Métrica do merge | `ψ` como filtro e ganho de fusão como prova. "Direção média de `ΔW`" e "deslocamento" são degenerados | [04](04-merge-stocfl.md) | DP-04 |
| 2 | Papel de `K` e da alternância | Sem meta de `K`; a alternância passa a ser o calendário | [01](01-conceito-e-mapeamento.md), [02](02-calendario.md) | DP-02, DP-03, DP-18 |
| 3 | Destino de clusters pequenos | Sem descarte; caminho de fusão sem `τ`, verificado | [06](06-clientes-e-participacao.md) | DP-11 |
| 4 | Participação parcial | Total, depois censo | [06](06-clientes-e-participacao.md) | DP-10 |
| 5 | Sensibilidade dos limiares | Calibração do artigo, **e** em vez de **ou**, persistência | [03](03-split-cfl.md) | DP-05, DP-06 |
| 6 | Garantia teórica | Incluir `γ_max`. A espera crescente dá limite para a oscilação, mas a convergência do conjunto continua sem prova | [03](03-split-cfl.md), [05](05-estabilidade.md) | DP-05 |
| 7 | Invariantes do StoCFL | Só a de "não crescente" cai; os ids continuam válidos | [07](07-modelos-e-estado.md) | — |
| 8 | Deslocamento de escala | Sem `±1`; bipartição explícita | [03](03-split-cfl.md) | — |
| 9 | Motivação sem evidência | Revisão de literatura, toy e experimentos com critério de refutação | [anexo A](anexo-a-simulacao.md), [anexo B](anexo-b-literatura.md), [09](09-experimentos.md) | DP-19 |
