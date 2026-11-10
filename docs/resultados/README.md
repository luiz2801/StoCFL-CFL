# resultados

Resultados das execuções do StoCFL em JSON compactado (`gzip -9 -n`), guardados depois que os logs de cada execução foram apagados para liberar disco (D-039, D-040, D-041 em [decisoes.md](../decisoes.md)). Pela política 7 do [CLAUDE.md](../../CLAUDE.md) (D-042), todo notebook de simulação deixa aqui o JSON dos seus resultados, compactado. A descrição e a leitura dos números estão no [guia técnico](../guia.md), seção 4.11.

| Arquivo | Tamanho | O que tem |
|---|---|---|
| [resultados-dropout.json.gz](resultados-dropout.json.gz) | 0,8 MB (13 MB descompactado) | A grade de 120 execuções do `teste-dropout.ipynb` (2026-11-09): 2 `k` × 2 `m` × 3 cenários × 10 seeds. Por execução, as métricas, o cluster de cada cliente em cada rodada, os sorteados, os indisponíveis e os cossenos entre clusters da última rodada; mais as tabelas de resumo, o Wilcoxon e as matrizes de confusão. |
| [resultados-varredura-tau-dirichlet.json.gz](resultados-varredura-tau-dirichlet.json.gz) | 6,6 MB (25 MB descompactado) | O Monte Carlo sobre `τ` do `varredura-tau-dirichlet.ipynb` (2026-11-10, D-046): por `(α, seed)`, a matriz de cossenos entre os 240 clientes (`G`, float64), os histogramas de rótulos e o gabarito; os sorteios e os indisponíveis por rodada de cada `(seed, m, d)`; as 48.000 linhas do Monte Carlo (400 `τ` × 120 combinações); e as 9 execuções de validação do simulador, com a partição real de cada rodada. |
| [resultados-fracao-clientes.json.gz](resultados-fracao-clientes.json.gz) | 3,9 MB (23 MB descompactado) | As 153 execuções do `teste-fracao-clientes.ipynb` (teste de `m` e busca de `τ`, 2026-11-05 e 06): métricas, clusters e sorteados por rodada, cossenos, e a matriz de cossenos entre clientes da rodada 0 para cada `n` e `k`. |

## Como usar

Os notebooks leem `projetos/StoCFL/logs/`, que o git ignora. Para restaurar um arquivo, a partir da raiz do repositório:

```
gunzip -c docs/resultados/resultados-dropout.json.gz > projetos/StoCFL/logs/resultados-dropout.json
```

Com ele no lugar, o `teste-dropout.ipynb` replota sem nenhum log (`DADOS_JSON = True` na célula 1). O `varredura-tau-dirichlet.ipynb` também (`DADOS_JSON = True`). O `teste-fracao-clientes.ipynb` ainda não lê o JSON. Para ler direto em Python: `json.load(gzip.open("docs/resultados/resultados-fracao-clientes.json.gz"))`.
