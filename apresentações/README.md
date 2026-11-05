# Apresentações

Duas apresentações em LaTeX (classe Beamer), uma para cada algoritmo:

| Arquivo | Assunto | Slides |
|---|---|---|
| [apresentacao-cfl.tex](apresentacao-cfl.tex) | CFL clássico (Sattler et al., 2021), divisivo, com o cosseno entre atualizações | 17 |
| [apresentacao-stocfl.tex](apresentacao-stocfl.tex) | StoCFL (Zeng et al., 2025), aglomerativo, com participação parcial | 20 |

As apresentações resumem o que está em [docs/guia.md](../docs/guia.md) (seções 3 e 4) e nos artigos em [docs/](../docs/). Elas descrevem o estado atual do código, incluindo as correções descritas no guia.

## Compilação

É preciso `pdflatex` com os pacotes `beamer`, `tikz`, `booktabs`, `lmodern` e `amsmath`, todos do TeX Live padrão.

```
mkdir -p saida-apresentacoes
pdflatex -output-directory saida-apresentacoes apresentações/apresentacao-cfl.tex
pdflatex -output-directory saida-apresentacoes apresentações/apresentacao-cfl.tex
```

Rode a partir da raiz do repositório. O `-output-directory` junta os arquivos auxiliares e o PDF em `saida-apresentacoes/`, que está no `.gitignore` e por isso não é versionado (D-020 em [docs/decisoes.md](../docs/decisoes.md)). Compile duas vezes, para resolver as referências. O mesmo vale para `apresentacao-stocfl.tex`.

O texto está em português, mas o pacote `babel` com o idioma português não foi usado, porque ele não está instalado neste ambiente (ver D-019 em [docs/decisoes.md](../docs/decisoes.md)). A hifenização fica sem a regra do português, sem prejuízo para o conteúdo.
