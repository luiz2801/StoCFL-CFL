# resultados

Resultados das execuções do StoCFL em JSON compactado (`gzip -9 -n`), guardados depois que os logs de cada execução foram apagados para liberar disco (D-039, D-040, D-041 em [decisoes.md](../decisoes.md)). A descrição e a leitura dos números estão no [guia técnico](../guia.md), seção 4.11.

| Arquivo | Tamanho | O que tem |
|---|---|---|
| [resultados-dropout.json.gz](resultados-dropout.json.gz) | 0,8 MB (13 MB descompactado) | A grade de 120 execuções do `teste-dropout.ipynb` (2026-11-09): 2 `k` × 2 `m` × 3 cenários × 10 seeds. Por execução, as métricas, o cluster de cada cliente em cada rodada, os sorteados, os indisponíveis e os cossenos entre clusters da última rodada; mais as tabelas de resumo, o Wilcoxon e as matrizes de confusão. |
| [resultados-fracao-clientes.json.gz](resultados-fracao-clientes.json.gz) | 3,9 MB (23 MB descompactado) | As 153 execuções do `teste-fracao-clientes.ipynb` (teste de `m` e busca de `τ`, 2026-11-05 e 06): métricas, clusters e sorteados por rodada, cossenos, e a matriz de cossenos entre clientes da rodada 0 para cada `n` e `k`. |

## Como usar

Os notebooks leem `projetos/StoCFL/logs/`, que o git ignora. Para restaurar um arquivo, a partir da raiz do repositório:

```
gunzip -c docs/resultados/resultados-dropout.json.gz > projetos/StoCFL/logs/resultados-dropout.json
```

Com ele no lugar, o `teste-dropout.ipynb` replota sem nenhum log (`DADOS_JSON = True` na célula 1). O `teste-fracao-clientes.ipynb` ainda não lê o JSON. Para ler direto em Python: `json.load(gzip.open("docs/resultados/resultados-fracao-clientes.json.gz"))`.
