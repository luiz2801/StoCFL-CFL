# models

Arquiteturas de rede neural usadas nos experimentos do StoCFL. Todas são `torch.nn.Module`.

## Arquivos

| Arquivo | Classes | Uso |
|---|---|---|
| `cnn.py` | `CNN_FEMNIST`, `CNN_MNIST`, `CNN_CIFAR10`, `AlexNet_CIFAR10` | Redes convolucionais para cada dataset. O cabeçalho cita Reddi et al., *Adaptive Federated Optimization* (ICML 2020). `CNN_MNIST` e `AlexNet_CIFAR10` são código legado (ver guia, seção 4.13). |
| `linear.py` | `SimpleLinear` | Rede totalmente conectada para MNIST: entrada de 784 valores, camada oculta de `h1` (padrão 2048) e saída de 10 classes. |
| `model.py` | `ConvNet` | Rede convolucional com 62 classes (EMNIST), parecida com a do CFL. **Não é usada pelo StoCFL.** |

## Qual modelo cada cenário usa

A escolha depende do script e do dataset. Consulte a seção 4.7 do [guia](../../../docs/guia.md) para o mapeamento completo entre cenário, dataset e modelo.
