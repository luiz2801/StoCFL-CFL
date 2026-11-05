# docs

Material de referência do repositório: os artigos dos dois algoritmos de aprendizado federado com clusterização e o guia técnico que explica o código.

## Conteúdo

| Arquivo | Descrição |
|---|---|
| [StoCFL.pdf](StoCFL.pdf) | Artigo do StoCFL: Zeng et al., *StoCFL: A stochastically clustered federated learning framework for Non-IID data with dynamic client participation*, Neural Networks, 2025 (arXiv:2303.00897). |
| [Clustered_Federated_Learning_Model-Agnostic_Distributed_Multitask_Optimization_Under_Privacy_Constraints.pdf](Clustered_Federated_Learning_Model-Agnostic_Distributed_Multitask_Optimization_Under_Privacy_Constraints.pdf) | Artigo do CFL: Sattler, Müller e Samek, IEEE TNNLS, 2021 (arXiv:1910.01991). |
| [guia.md](guia.md) | Guia técnico do CFL e do StoCFL: o que cada função faz, fluxo de execução, variáveis, bugs conhecidos, como rodar e mapa entre artigo e código. |
| [../isodata.pdf](../isodata.pdf) | Artigo do ISODATA: Ball & Hall, *ISODATA, A Novel Method of Data Analysis and Pattern Classification*, 1965. Está na raiz do repositório, fora de `docs/`. |
| [implementar/](implementar/README.md) | Diretório de planejamento com os documentos de crítica, guia técnico do ISODATA (código existente), e as propostas ainda não implementadas de especificação, diagramas e arquitetura do ISODATA-FL. O [plano modular](implementar/plano-isodata-fl/README.md) é a proposta mais recente. |
| [clusterizacao-ao-longo-do-tempo.ipynb](clusterizacao-ao-longo-do-tempo.ipynb) | Notebook com dois diagramas Mermaid ilustrativos: o StoCFL unindo clusters (K = N diminui) e o CFL dividindo um cluster (K = 1 aumenta). Desenha com `mermaid.js` via CDN, então precisa de internet. |
| [decisoes.md](decisoes.md) | Registro das decisões tomadas sobre o repositório, com as alternativas consideradas e o motivo de cada escolha. |
| [backlog.md](backlog.md) | Trabalho aprovado para mais tarde: recursos que os artigos descrevem e o código ainda não tem. |

## Por onde começar

1. Leia a seção 1 do [guia](guia.md) para ver a estrutura do repositório.
2. Para entender os algoritmos, leia as seções 3.1 (CFL) e 4.1 (StoCFL).
3. Antes de rodar ou modificar o código, leia os bugs conhecidos: seções 3.7 (CFL) e 4.12 (StoCFL).

Os caminhos no guia são relativos a `projetos/`.
