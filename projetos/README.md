# projetos

Os três subprojetos do repositório. Cada um tem a sua própria pasta, e o README de cada um descreve como instalar e executar. Eles não têm repositório git próprio: o git é o da raiz. A coluna "Origem" mostra a autoria original; os detalhes e as licenças estão nos [créditos](../README.md#créditos).

| Subprojeto | Tema | Linguagem e stack | Origem |
|---|---|---|---|
| [clustered-federated-learning](clustered-federated-learning/) | CFL: clusterização divisiva de clientes em FL | Python, PyTorch, Jupyter | Felix Sattler et al. |
| [StoCFL](StoCFL/) | StoCFL: clusterização estocástica e aglomerativa de clientes, com participação parcial | Python, PyTorch, FedLab 1.2.1 | Dun Zeng et al. |
| [ISODATA-python](ISODATA-python/) | ISODATA: classificação de pixels de imagens por linha de comando | Python, Pillow, NumPy, matplotlib | Lucka |

**Fora da tabela:** `ISODATA-GNR602/` (`isodata.py` e `readme_isodata.md`) veio do histórico do remoto no merge de 2026-11-05 (D-025). É um ISODATA de terceiros, de um trabalho do curso GNR-602 (grupo 68, Indian Pines), sem autor nem licença identificados. Ele não está integrado, não é citado no guia e não foi testado.

## Relação entre os projetos

- `clustered-federated-learning` e `StoCFL` implementam dois algoritmos de aprendizado federado com clusterização. O guia em [../docs/guia.md](../docs/guia.md) compara os dois (seção 5).
- `ISODATA-python` implementa o ISODATA para classificação de pixels de imagens, o mesmo algoritmo descrito no artigo de Ball & Hall em [../isodata.pdf](../isodata.pdf).
