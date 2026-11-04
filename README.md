# cfl_stocfl

Repositório de estudos e implementações em duas linhas de pesquisa:

- **Aprendizado federado com clusterização de clientes** (*Clustered Federated Learning*): CFL (Sattler et al.) e StoCFL (Zeng et al.), para dados não-IID.
- **Classificação de imagens com ISODATA**: implementação do algoritmo ISODATA (Ball & Hall, 1965) em Python, para pixels de imagens comuns e de sensoriamento remoto.

Para a explicação detalhada dos algoritmos, das funções, dos bugs conhecidos e da correspondência entre código e artigos, veja o [guia técnico](docs/guia.md).

## Estrutura

```
cfl_stocfl/
├── docs/                               # artigos, guia técnico, decisões e planejamento (implementar/)
├── projetos/                           # um subprojeto por algoritmo/implementação
│   ├── clustered-federated-learning/   # CFL (notebook Jupyter)
│   ├── StoCFL/                         # StoCFL (scripts CLI, FedLab)
│   └── ISODATA-python/                 # ISODATA como ferramenta de linha de comando
├── isodata.pdf                         # artigo original do ISODATA (Ball & Hall, 1965)
└── .venv/                              # ambiente virtual Python 3.12 (apenas kernel Jupyter)
```

## Projetos

| Projeto | Algoritmo | Como executar | Situação |
|---|---|---|---|
| [clustered-federated-learning](projetos/clustered-federated-learning/) | CFL, divisivo, com `scikit-learn` | Notebook `clustered_federated_learning.ipynb` | Funciona com correções (ver guia, seção 3.7) |
| [StoCFL](projetos/StoCFL/) | StoCFL, aglomerativo, com FedLab 1.2.1 | `StoCFL-FCC+CFL.py` (principal) | Os três scripts rodam; `StoCFL-FCC.py` só com `--train 0` (ver guia, seção 4.12) |
| [ISODATA-python](projetos/ISODATA-python/) | ISODATA para imagens comuns (RGB ou cinza) | `python main.py --input ... --output ...` | Funcional, mas muito lento |

## Ambiente

- O `.venv/` da raiz tem só o kernel Jupyter (Python 3.12). Não tem `torch`, `numpy`, `scikit-learn` nem `fedlab`, então não serve para rodar os projetos de aprendizado federado.
- Os projetos de aprendizado federado foram testados com Python 3.12, PyTorch 2.15 em CPU e `fedlab==1.2.1` (ver [guia, seção 4.11](docs/guia.md)).
- A raiz é o único repositório git (branch `main`, sem remote). Os subprojetos `clustered-federated-learning`, `StoCFL` e `ISODATA-python` não têm `.git` próprio; o histórico original deles foi removido, e a autoria está nos créditos abaixo.

## Créditos

Este repositório parte de trabalhos de outros autores, que aqui são estudados e **modificados**. Ao unificar tudo em um só repositório, o histórico git original de cada projeto foi removido (D-008 em [docs/decisoes.md](docs/decisoes.md)). Por isso a autoria e a origem ficam registradas aqui.

| Projeto | Autoria original | Origem | Licença |
|---|---|---|---|
| `projetos/clustered-federated-learning/` (CFL) | Felix Sattler (Fraunhofer HHI; commits também como `felisat`), com Klaus-Robert Müller e Wojciech Samek, autores do artigo *Clustered Federated Learning: Model-Agnostic Distributed Multi-Task Optimization under Privacy Constraints* ([arXiv:1910.01991](https://arxiv.org/abs/1910.01991)) | Repositório [felisat/clustered-federated-learning](https://github.com/felisat/clustered-federated-learning), de 2020 | MIT, segundo o mantenedor deste repositório. **A origem dessa informação precisa ser confirmada:** o repositório original não tem arquivo de licença, e o README dele não menciona licença (verificado em 2026-11-04). Sem o texto, o aviso de copyright não pode ser acrescentado aqui. Ver a decisão [DP-17](docs/implementar/plano-isodata-fl/11-decisoes-pendentes.md). |
| `projetos/StoCFL/` | Dun Zeng, Xiangjing Hu, Shiyu Liu, Yue Yu, Qifan Wang e Zenglin Xu, autores do artigo *StoCFL* ([arXiv:2303.00897](https://arxiv.org/abs/2303.00897)). Os commits originais são de Dun Zeng e de `Zed`/`zed`. | Código publicado pelos autores (URL não registrado) | MIT, Copyright (c) 2023 Dun Zeng ([LICENSE](projetos/StoCFL/LICENSE)) |
| `projetos/ISODATA-python/` | Lucka (`lucka-me`), autor da implementação em Python | Projeto `ISODATA-python` do autor no GitHub (URL exata não registrada) | MIT, Copyright (c) 2018 Lucka ([LICENSE](projetos/ISODATA-python/LICENSE)) |
| [isodata.pdf](isodata.pdf) | Geoffrey H. Ball e David J. Hall, *ISODATA, A Novel Method of Data Analysis and Pattern Classification*, relatório técnico, abril de 1965 | Algoritmo implementado em `ISODATA-python` | Artigo de terceiros, só para consulta. |

- **Código de terceiros** incluído em `StoCFL/`: FedScale, LEAF (com o adaptador do FedLab) e o Faster R-CNN adaptado por Jianwei Yang. Os créditos e as licenças originais estão nos READMEs e cabeçalhos de cada pasta.
- **Modificações neste repositório** (feitas por `luiz2801`, a partir de 2026-11-04): documentação em `docs/`, diagramas Mermaid de cada algoritmo, `CLAUDE.md`, a opção `--NROWS` e a reescrita do núcleo em `ISODATA-python`, e as mudanças que vierem nos algoritmos. O que não está listado aqui continua sendo obra dos autores originais.

## Licença

Este repositório usa a licença **MIT** ([LICENSE](LICENSE)), Copyright (c) 2026 luiz2801. O texto do copyright pode ser ajustado pelo mantenedor, por exemplo para o nome completo.

Os subprojetos são MIT e mantêm o aviso de copyright dos autores originais: `ISODATA-python` (Lucka) e `StoCFL` (Dun Zeng) têm arquivo `LICENSE` próprio. O CFL (Felix Sattler) é MIT segundo o mantenedor, mas não tem arquivo `LICENSE` aqui nem no repositório original (ver a tabela de créditos). Os arquivos de terceiros (`StoCFL/fedscale/`, `StoCFL/leaf/`, `StoCFL/fedscale/core/utils/rcnn/`) mantêm as licenças originais. A MIT exige manter o aviso de copyright nas cópias e modificações, então não remova os arquivos `LICENSE`.

## Documentação por diretório

- [docs/](docs/README.md): artigos e guia técnico
- [projetos/](projetos/README.md): visão dos três projetos
