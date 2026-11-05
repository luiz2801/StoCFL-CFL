# Apresentações

Duas apresentações em LaTeX (classe Beamer), uma para cada algoritmo:

| Arquivo | Assunto | Slides |
|---|---|---|
| [apresentacao-cfl.tex](apresentacao-cfl.tex) | CFL clássico (Sattler et al., 2021), divisivo, com o cosseno entre atualizações | 17 |
| [apresentacao-stocfl.tex](apresentacao-stocfl.tex) | StoCFL (Zeng et al., 2025), aglomerativo, com participação parcial | 18 |

As apresentações resumem o que está em [docs/guia.md](../docs/guia.md) (seções 3 e 4) e nos artigos em [docs/](../docs/). Elas descrevem o estado atual do código, incluindo as correções descritas no guia.

## Compilação

É preciso `pdflatex` com os pacotes `beamer`, `tikz`, `booktabs`, `lmodern` e `amsmath`, todos do TeX Live padrão.

```
pdflatex -output-directory ~/saida-apresentacoes apresentacao-cfl.tex
pdflatex -output-directory ~/saida-apresentacoes apresentacao-cfl.tex
```

O `-output-directory` impede que os arquivos auxiliares e o PDF sejam gravados no repositório. Compile duas vezes, para resolver as referências. O diretório de saída (aqui `~/saida-apresentacoes`) precisa existir antes e ficar fora do repositório.

O texto está em português, mas o pacote `babel` com o idioma português não foi usado, porque ele não está instalado neste ambiente (ver D-019 em [docs/decisoes.md](../docs/decisoes.md)). A hifenização fica sem a regra do português, sem prejuízo para o conteúdo.
