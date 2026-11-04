# Anexo B. Trabalhos relacionados

> **Como ler.** Levantamento rápido, feito em 2026-11-04 por busca na web, para atender ao problema 9 da [especificação](../especificacao-isodata-fl.md). As descrições vêm de resumos e trechos dos artigos, **não de leitura integral**, e nenhum resultado foi reproduzido. Confira a fonte antes de citar. Não é uma revisão sistemática.

## B.1 O que o levantamento sugere

1. **A lacuna é reconhecida.** O FedDAG afirma, como motivação, que Sattler et al. divide mas não funde quando necessário, e que Zeng et al. funde mas não divide. É a mesma observação da seção 1 da especificação.
2. **Dividir e fundir no mesmo método já existe.** FedAC, SR-FCA, FedDrift e DPMM-CFL fazem isso de formas diferentes. O plano não é inédito nessa ideia.
3. **Fusão por perda tem precedente direto.** O FedDrift usa exatamente a perda cruzada e funde modelos com média ponderada, o que dá base para a [verificação no merge](04-merge-stocfl.md). O SR-FCA usa uma métrica parecida para redes neurais.
4. **O que parece novo aqui**, com a ressalva de que a busca foi curta: combinar o critério de normas do CFL com o `ψ` do StoCFL em um mesmo laço, e o calendário por primos. Nenhum resultado da busca propõe isso. "Não encontrei" não é "não existe".

## B.2 Divisão e fusão de clusters em FL

| Trabalho | O que faz | Relação com o plano | Fonte |
|---|---|---|---|
| **FedAC** (Zhang et al., 2024) | Módulo de ajuste do número de clusters: mede as distâncias dentro e entre clusters e divide ou funde mantendo a razão `Dist_intra / Dist_inter` em uma faixa. Reatribui clientes com um passo semelhante ao EM | Alternativa de sinal único para os dois operadores. Sinal baseado em distância de modelos, a ser comparado com E4 | [arXiv:2403.16460](https://arxiv.org/abs/2403.16460) |
| **SR-FCA** (Vardhan, Ghosh, Mazumdar; TMLR 2024) | Parte de clientes isolados e chama `REFINE` repetidamente, que reagrupa (`RECLUSTER`) e funde (`MERGE`). Para redes neurais, usa uma **perda cruzada**: a perda de um cliente no modelo do outro. Não precisa conhecer `K` nem de boa inicialização | Próximo da partida por `ψ`, mas com perda em vez de `ψ`. Traz garantia teórica | [arXiv:2210.11538](https://arxiv.org/abs/2210.11538) |
| **FedDrift** (Jothimurugesan et al.; AISTATS 2023) | Para deriva de conceito. Cria modelos ao detectar deriva e funde clusters por agrupamento hierárquico, com `D(i,j) = max(L_ij − L_ii, L_ji − L_jj, 0)`. A fusão é a média ponderada pelo tamanho dos dados | **Precedente direto** da verificação e da regra de modelo do merge | [arXiv:2206.00799](https://arxiv.org/abs/2206.00799), [código](https://github.com/microsoft/FedDrift) |
| **FedCCFA** (2024) | Critica métricas por perda: diferenças na distribuição de rótulos aumentam a distância estimada e impedem fusões, além do custo de medir | **Risco** da verificação: no plano é P-MRG-7, com falha conservadora | [arXiv:2410.18478](https://arxiv.org/abs/2410.18478) |
| **DPMM-CFL** (2025) | Abordagem bayesiana: modelo de mistura com processo de Dirichlet e MCMC com propostas de divisão e fusão. O número de clusters é reestimado a cada rodada | Mostra outra forma de eliminar `K`. Mais caro e com outra base teórica. Fora do escopo | [arXiv:2510.07132](https://arxiv.org/abs/2510.07132) |
| **FedDAG** (2026) | Cita, na motivação, a lacuna entre CFL (só divide) e StoCFL (só funde) | Confirma que a lacuna é reconhecida | [arXiv:2602.23504](https://arxiv.org/abs/2602.23504) |
| **IFCA** (Ghosh et al.; 2020) | Alterna entre estimar a identidade do cluster de cada cliente e otimizar os modelos. Precisa do número de clusters | Referência para a [reatribuição](06-clientes-e-participacao.md). O artigo do StoCFL critica o custo de vários modelos por rodada e o "domínio" de um modelo (guia 4.15) | [arXiv:2006.04088](https://arxiv.org/abs/2006.04088) |

## B.3 Apoio para decisões específicas

| Trabalho | O que diz | Onde é usado |
|---|---|---|
| **Frankle et al.**, *Linear Mode Connectivity and the Lottery Ticket Hypothesis* (ICML 2020) | Duas cópias de uma rede, treinadas do mesmo ponto com ruído de SGD diferente, ficam sem barreira de erro na reta entre elas quando a rede já está estável. Isso ocorre na inicialização em problemas pequenos e cedo no treino nos grandes. **Mesmos dados**, não distribuições diferentes. [arXiv:1912.05671](https://arxiv.org/abs/1912.05671) | Por que a média de modelos é razoável só em clusters que merecem fundir ([07](07-modelos-e-estado.md)) |
| **Hsu, Qi, Brown**, *Measuring the Effects of Non-Identical Data Distribution for Federated Visual Classification* (2019) | Propõe o FedAvgM, FedAvg com momentum no servidor. Relata grande ganho em CIFAR-10 nos cenários mais heterogêneos, e alerta que o ajuste fica mais difícil, por haver um hiperparâmetro a mais. [arXiv:1909.06335](https://arxiv.org/abs/1909.06335) | Alternativa ao momentum por cliente ([DP-15](11-decisoes-pendentes.md#dp-15-otimizador)) |
| **Código sem licença** | Em geral, código publicado sem licença explícita tem todos os direitos reservados ao autor. Informação geral, de fontes jornalísticas, e não parecer jurídico. [InfoWorld](https://www.infoworld.com/article/2615869/github-needs-to-take-open-source-seriously.html) | Situação do CFL original ([DP-17](11-decisoes-pendentes.md#dp-17-a-licença-do-cfl)) |
| **RFC 2439**, *BGP Route Flap Damping* (1998) | Roteadores penalizam rotas instáveis, suprimem a rota quando a penalidade passa de um limiar e a reabilitam quando ela decai. Trabalhos posteriores relatam supressão excessiva de rotas estáveis | Analogia para a espera crescente ([05](05-estabilidade.md)). É inspiração, e o mecanismo não é idêntico: aqui a espera cresce, não há penalidade que decai. [Texto](https://www.rfc-editor.org/rfc/rfc2439) |

## B.4 O artigo do ISODATA

Ball & Hall (1965), [isodata.pdf](../../../isodata.pdf). Trechos usados neste plano, conferidos com `pdftotext` em uma cópia com ruído de OCR:

| Assunto | O que o artigo diz | Uso |
|---|---|---|
| Alternância | Figura 1: vai para o divisor em iteração ímpar; para o fundidor em iteração par, na última iteração ou com clusters em excesso | [01](01-conceito-e-mapeamento.md), [02](02-calendario.md) |
| Só pares | Fundir trios "parecia mudar a partição radicalmente demais para o procedimento iterativo convergir de forma satisfatória" | [04](04-merge-stocfl.md) |
| Dividir em mais de 2 | "Perigoso" sem calcular a matriz de covariância | [03](03-split-cfl.md) |
| Consolidação | "Nenhuma divisão ou fusão é permitida nesta iteração final, que serve principalmente para consolidação" | [02](02-calendario.md) |
| Modelo fundido | Média ponderada pelo número de padrões, "o verdadeiro ponto médio do subconjunto combinado" | [07](07-modelos-e-estado.md) |
| Deslocamento `±1` | "Arbitrário", desde que produza diferenças detectáveis | [03](03-split-cfl.md) |
