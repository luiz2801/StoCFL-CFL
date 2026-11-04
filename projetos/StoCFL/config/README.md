# config

Partições pré-calculadas dos dados (MNIST e CIFAR-10) entre clientes simulados, salvas como pickle, e os scripts que as geram.

> **Status: legado.** Os scripts principais (`StoCFL-FCC+CFL.py`, `StoCFL-FCC.py`) não usam estes arquivos. Eles só são lidos por `settings.mnist()` e `settings.cifar10()`, que são importadas mas não chamadas. Veja a seção 4.13 do [guia](../../../docs/guia.md).

## Arquivos

| Arquivo | Dataset | Distribuição | Gerado por |
|---|---|---|---|
| `mnist_iid.pkl`, `mnist_iid_10.pkl`, `mnist_iid_100.pkl`, `mnist_iid_1000.pkl` | MNIST | IID, com o número de clientes no nome | `mnist_partition.py` (`random_slicing`) |
| `mnist_noniid.pkl`, `mnist_noniid_200_10.pkl`, `mnist_noniid_200_100.pkl`, `mnist_noniid_1000_1000.pkl` | MNIST | não-IID por *shards*, no formato `noniid_{shards}_{clientes}` | `mnist_partition.py` (`noniid_slicing`) |
| `cifar10_iid.pkl`, `cifar10_iid_100.pkl` | CIFAR-10 | IID, com o número de clientes no nome | `cifar_partition.py` (`random_slicing`) |
| `cifar10_noniid.pkl`, `cifar10_noniid_100_200.pkl` | CIFAR-10 | não-IID por *shards*, no formato `noniid_{clientes}_{shards}` | `cifar_partition.py` (`noniid_slicing`) |

Atenção: a ordem dos números no nome não é a mesma nos dois datasets. Para MNIST é `{shards}_{clientes}`, e para CIFAR-10 é `{clientes}_{shards}`.

Os arquivos sem sufixo numérico no nome (`mnist_iid.pkl`, `mnist_noniid.pkl`, `cifar10_iid.pkl`, `cifar10_noniid.pkl`) não têm os parâmetros de origem no nome, e não há script que confirme como foram gerados.

## Scripts

- `mnist_partition.py`: lê o MNIST de `../datasets/mnist` (sem download), gera 1000 clientes com `noniid_slicing` (1000 *shards*) e `random_slicing`, e salva com `fedlab.utils.functional.save_dict`. Execute a partir desta pasta, porque o caminho é relativo.
- `cifar_partition.py`: lê o CIFAR-10 de `../datasets/cifar10` (sem download), gera 100 clientes com `noniid_slicing` (200 *shards*) e `random_slicing`, e salva do mesmo jeito.

## Formato

Cada pickle é um dicionário `{id_do_cliente: lista_de_índices}`, com os índices das amostras do dataset completo. Para carregar, use `fedlab.utils.functional.load_dict`.

## Dependências

`fedlab` (para `noniid_slicing`, `random_slicing` e `save_dict`/`load_dict`) e `torchvision` (para carregar o MNIST).
