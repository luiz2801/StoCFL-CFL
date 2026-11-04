# utils

Utilitários do FedScale: carregadores de dados, arquiteturas de modelo, transformações de áudio e texto e otimizadores. Os módulos são independentes, e a maioria não é usada pelo StoCFL.

## Principais grupos

| Grupo | Arquivos |
|---|---|
| Carregamento e divisão de dados | `dataloaders.py`, `utils_data.py`, `divide_data.py`, `voice_data_loader.py` |
| Datasets específicos | `femnist.py`, `openimage.py`, `inaturalist.py`, `amazon.py`, `reddit.py`, `stackoverflow.py` |
| Texto | `nlp.py`, `word2vec.py` |
| Áudio e fala | `speech.py`, `transforms_wav.py`, `transforms_stft.py`, `spec_augment.py`, `decoder.py`, `voice_model.py`, `resnet_speech.py` |
| Modelos de visão | `models.py`, `mobilenet.py`, `inception.py`, `sparse_image_warp.py`, `utils_model.py` |
| Otimização e aprendizado por reforço | `yogi.py` (otimizador Yogi), `dqn.py` |
| Detecção de objetos | `rcnn/`: Faster R-CNN, com a sua própria [documentação](rcnn/README.md) |

`__init__.py` está vazio.
