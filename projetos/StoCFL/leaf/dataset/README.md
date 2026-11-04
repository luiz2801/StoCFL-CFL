# dataset

Classes de `torch.utils.data.Dataset` para os datasets do benchmark LEAF.

## Arquivos

| Arquivo | Dataset LEAF | Tarefa |
|---|---|---|
| `femnist_dataset.py` | FEMNIST | Classificação de 62 caracteres manuscritos |
| `shakespeare_dataset.py` | Shakespeare | Previsão do próximo caractere |
| `celeba_dataset.py` | CelebA | Classificação binária (sorriso ou não) |
| `sent140_dataset.py` | Sent140 | Análise de sentimento em tweets |
| `reddit_dataset.py` | Reddit | Texto de comentários |

## Importação

O `__init__.py` tem as importações comentadas, então `from leaf.dataset import ...` não traz nada. Importe o módulo direto, por exemplo `from leaf.dataset.femnist_dataset import FemnistDataset`.

No StoCFL, só o FEMNIST é usado, pelo `StoCFL-FEMNIST.py`, por meio de `leaf/dataloader.py`.
