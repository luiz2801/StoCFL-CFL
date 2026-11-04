# Backlog

Trabalho aprovado para mais tarde, sem data. Cada item diz o que o artigo descreve, o que falta no código e o que precisa ser resolvido antes de começar. Ao concluir um item, remova-o daqui e atualize o [guia](guia.md).

## CFL: árvore de parâmetros e clientes novos

- **Artigo:** seção IV-C e Algoritmo 4. Durante o CFL, o servidor mantém uma árvore em que cada nó guarda um cluster e o modelo dele, e cada aresta guarda as atualizações pré-divisão dos clientes do filho. Um cliente novo desce a árvore pelo ramo mais similar.
- **Hoje:** `server.model_cache` é uma lista plana de `(ids, pesos, acurácias)`, sem atualizações pré-divisão e sem forma de atribuir um cliente novo.
- **Antes de começar:** o pseudocódigo impresso do Alg. 4 tem índices inconsistentes (`v0`/`v1` num lugar, `v1`/`v2` em outro), então a leitura precisa ser fixada. Nenhum cenário do notebook tem cliente novo, então é preciso criar um para testar.

## StoCFL: inferência de clientes novos

- **Artigo:** seção 4, com avaliação na seção 5.4 e na Tabela 5. O cliente novo envia `Ψ(D̂)`. O servidor calcula o maior cosseno com os centros dos clusters: se for `≥ τ`, atribui o cliente a esse cluster; senão, cria um cluster novo com o modelo do mais próximo.
- **Hoje:** não existe. Todos os clientes participam desde o início.
- **Antes de começar:** o teste exige separar 30% dos clientes, como na seção 5.4. A inferência cria um cluster sem passar pelas fusões, o que quebra a invariante 5 da seção 4.5 do guia, então ela precisa ser revista.
