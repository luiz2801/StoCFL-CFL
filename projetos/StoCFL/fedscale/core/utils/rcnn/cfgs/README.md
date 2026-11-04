# cfgs

Arquivos de configuração YAML do Faster R-CNN, usados pelo módulo `rcnn/` do FedScale.

| Arquivo | Backbone |
|---|---|
| `vgg16.yml` | VGG-16 |
| `res50.yml` | ResNet-50 |
| `res101.yml` | ResNet-101 |
| `res101_ls.yml` | ResNet-101, variante com configuração própria |

Cada arquivo define `EXP_DIR` (nome do diretório de saída) e o bloco `TRAIN`, com parâmetros do RPN e das caixas delimitadoras. O sufixo `_ls` não está explicado no código.
