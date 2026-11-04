# Roteiro de Implementação e Críticas (implementar/)

Este diretório reúne os documentos de diagnóstico crítico da documentação e das políticas do repositório, bem como as especificações conceituais, matemáticas e arquiteturais para guiar agentes e desenvolvedores na futura aplicação do **ISODATA** sobre os frameworks **CFL** e **StoCFL**.

> **Status (2026-11-04): fase de planejamento. Nada do ISODATA-FL foi implementado.** O [guia técnico do ISODATA](guia-tecnico-isodata.md) descreve código existente e foi verificado contra ele e contra o artigo. Os demais documentos são propostas com problemas em aberto, listados na seção 5 da [especificação](especificacao-isodata-fl.md) e na seção 5 da [arquitetura](arquitetura-componentes-isodata-fl.md).
>
> **Proposta mais recente:** o [plano modular](plano-isodata-fl/README.md) (CFL como split, StoCFL como merge e calendário por rodadas) encaminha esses problemas, com recomendações ainda não aprovadas. Comece por ele.
>
> **Atenção (2026-11-04): o código do CFL e do StoCFL mudou depois deste plano.** A D-014 em [decisoes.md](../decisoes.md) corrigiu os dois para seguir o texto dos artigos. Onde este plano descreve o "notebook" ou o "código do StoCFL" (momentum, decaimento do lr, aquecimento, *complete linkage*, `obep`, modelo global encadeado), ele se refere ao código original, disponível até o commit `3159d55`. Para reproduzir aquele comportamento, use esse commit.

---

## Conteúdo do Diretório

| Arquivo | Descrição |
|---|---|
| [critica-documentacao-e-politicas.md](critica-documentacao-e-politicas.md) | Diagnóstico crítico das políticas e da documentação em relação ao escopo global do projeto. |
| [guia-tecnico-isodata.md](guia-tecnico-isodata.md) | Guia técnico do subprojeto `ISODATA-python` (classes, parâmetros, funções, condições de split/merge e limitações). |
| [especificacao-isodata-fl.md](especificacao-isodata-fl.md) | Especificação técnica e formulação matemática para transpor o ISODATA ao Aprendizado Federado (CFL + StoCFL). |
| [diagramas-isodata-fl.md](diagramas-isodata-fl.md) | Diagramas Mermaid de atividades e de sequência da rodada federada com dinâmica adaptativa de Split e Merge. |
| [arquitetura-componentes-isodata-fl.md](arquitetura-componentes-isodata-fl.md) | Design de classes, desacoplamento de software e roteiro de implementação modular em 4 fases. |
| [plano-isodata-fl/](plano-isodata-fl/README.md) | Plano passo a passo com CFL como split e StoCFL como merge: calendário, estabilidade, problemas, soluções, alternativas, experimentos e decisões pendentes. Um arquivo por módulo. |

