# Registro de decisões

Registro das decisões tomadas sobre o repositório: o que foi decidido, por quê, e quais alternativas foram consideradas. As decisões são numeradas em ordem cronológica e não são apagadas. Quando uma decisão for revista, a nova recebe um número novo e a anterior passa a "Substituída por D-xxx".

Para cada decisão, a entrada segue este modelo:

```markdown
## D-xxx: título curto

- **Data:** AAAA-MM-DD
- **Decidido por:** usuário ou Claude (com a justificativa de por que não foi perguntado)
- **Situação:** vigente, substituída por D-yyy
- **Contexto:** o problema e o motivo da decisão.
- **Decisão:** o que foi escolhido.
- **Alternativas consideradas:**
  - Alternativa A: motivo do descarte.
  - Alternativa B: motivo do descarte.
```

---

## D-001: CLAUDE.md na raiz do repositório

- **Data:** 2026-11-04
- **Decidido por:** Claude, por ser uma escolha reversível de localização de arquivo. Pode ser mudada pelo usuário.
- **Situação:** vigente
- **Contexto:** o usuário pediu que as políticas de trabalho (consultar a documentação, atualizar a documentação, perguntar antes de decidir) valessem para o repositório.
- **Decisão:** criar `CLAUDE.md` na raiz de `cfl_stocfl/`, válido para a raiz e para os três subprojetos.
- **Alternativas consideradas:**
  - `~/.claude/CLAUDE.md` (global): valeria para todos os projetos do usuário, o que não foi pedido.
  - Um `CLAUDE.md` em cada subprojeto: duplicaria as regras e precisaria de manutenção em três lugares.

## D-002: diagramas consultados são os `.md` em Mermaid

- **Data:** 2026-11-04
- **Decidido por:** Claude, por ser uma interpretação do pedido do usuário ("os diagramas de cada algoritmo").
- **Situação:** vigente
- **Contexto:** os diagramas de atividades e de sequência de cada algoritmo estão em arquivos `diagrama-*.md` com blocos Mermaid.
- **Decisão:** a política cita esses seis arquivos. As imagens PNG e SVG em `Resource/` (ISODATA) e `fedscale/core/` (StoCFL) não entram, porque são figuras dos READMEs e não diagramas do código.
- **Alternativas consideradas:**
  - Incluir as imagens PNG e SVG: são figuras de exemplo e de resultados, não descrevem o fluxo do código, então a consulta obrigatória não as cobriria.
  - Usar só o guia técnico: o usuário pediu explicitamente os diagramas.

## D-003: Documentação modular das críticas e do roteiro ISODATA-FL

- **Data:** 2026-11-04
- **Decidido por:** usuário (ao solicitar documentação em Markdown para cada ponto de crítica e de implementação futura) e Antigravity.
- **Situação:** vigente. Os caminhos citados abaixo (`docs/<arquivo>.md`) foram alterados pela D-004: os arquivos estão em `docs/implementar/`.
- **Contexto:** o usuário solicitou uma análise crítica das políticas e documentação frente ao escopo do repositório, além de uma base conceitual para orientar agentes futuros na aplicação do ISODATA sobre CFL e StoCFL.
- **Decisão:** criar arquivos Markdown temáticos e modulares em `docs/`:
  - `docs/critica-documentacao-e-politicas.md`: diagnóstico crítico do estado atual.
  - `docs/guia-tecnico-isodata.md`: documentação técnica da implementação existente do ISODATA.
  - `docs/especificacao-isodata-fl.md`: formalização matemática e conceitual da dinâmica adaptativa em FL.
  - `docs/diagramas-isodata-fl.md`: diagramas Mermaid de atividade e sequência da rodada federada híbrida.
  - `docs/arquitetura-componentes-isodata-fl.md`: design de classes e roteiro de implementação em fases.
- **Alternativas consideradas:**
  - Concatenar tudo em um único arquivo extenso: dificultaria a leitura e navegação por agentes em tarefas especializadas.
  - Modificar diretamente o `docs/guia.md`: o guia atual possui mais de 1000 linhas focadas em CFL/StoCFL com referências de linha fixas; criar documentos modulares evita quebrar links existentes e isola o planejamento da especificação dos códigos legados.

## D-004: Centralização dos documentos de planejamento e crítica em `docs/implementar/`

- **Data:** 2026-11-04
- **Decidido por:** usuário (em resposta à pergunta sobre localização do diretório `implementar/`).
- **Situação:** vigente
- **Contexto:** o usuário solicitou que todos os novos documentos de crítica e de implementação futura fossem reunidos em um diretório chamado `implementar/`.
- **Decisão:** criar o diretório `docs/implementar/` e mover para ele os 5 documentos gerados, adicionando um `README.md` de índice próprio e atualizando as referências em `docs/README.md` e `CLAUDE.md`.
- **Alternativas consideradas:**
  - `implementar/` na raiz do repositório (`/home/luiz/cfl_stocfl/implementar/`): descartada em favor de manter a raiz limpa e todos os documentos textuais dentro do domínio de `docs/`.

## D-005: Fase de planejamento, correções só na documentação

- **Data:** 2026-11-04
- **Decidido por:** usuário (ao interromper a pergunta sobre como corrigir o merge e a estrutura, e pedir apenas correções de documentação).
- **Situação:** vigente
- **Contexto:** a revisão de `docs/implementar/` encontrou um erro factual no guia do ISODATA, itens desatualizados na crítica e problemas de design na especificação do ISODATA-FL (critério de merge, papel de `K`, participação parcial, entre outros). O usuário está na fase de planejamento.
- **Decisão:** corrigir apenas a documentação. Não alterar código, não mover arquivos e não traduzir o README do ISODATA. Os problemas de design foram registrados como **em aberto** na seção 5 da especificação e na seção 5 da arquitetura, sem escolher solução.
- **Alternativas consideradas:**
  - Corrigir já o critério de merge na especificação (deslocamento desde a âncora, como no StoCFL, ou direção média de `ΔW`): descartada, porque é escolha de comportamento do algoritmo e o usuário não quis decidir agora.
  - Mover `isodata.pdf` para `docs/` e traduzir o README do ISODATA: descartada por ser mudança estrutural, adiada. As entradas correspondentes da crítica ficam marcadas como pendentes.
  - Prototipar as Fases 1 e 2 da arquitetura: descartada, o usuário não quer implementação nesta etapa.

## D-006: Ajustes triviais de consistência na documentação de `implementar/`

- **Data:** 2026-11-04
- **Decidido por:** Claude, por serem escolhas triviais, reversíveis e sem efeito sobre algoritmos (a política 4 permite).
- **Situação:** vigente
- **Contexto:** a revisão encontrou pequenas inconsistências nos documentos de `implementar/`.
- **Decisão:**
  - Trocar os links `file:///home/luiz/cfl_stocfl/...` por caminhos relativos, como no resto da documentação, para não quebrarem fora desta máquina.
  - Padronizar a restrição de porte do split como `|C_k| > 2(TN_FL+1)` (estrita) na especificação, igual ao código do ISODATA e ao diagrama.
  - Marcar o warm-up de 15 rodadas dos diagramas como valor ilustrativo.
  - Adicionar uma linha para `isodata.pdf` em `docs/README.md` apontando para a raiz, em vez de mover o arquivo.
- **Alternativas consideradas:**
  - Manter `>=` na especificação: descartada porque contradizia o diagrama e o código do ISODATA (`>`).
  - Manter os links `file:///`: descartada por dependerem do caminho absoluto desta máquina.


## D-007: Commits locais atômicos, sem push, e docs fora do git

- **Data:** 2026-11-04
- **Decidido por:** usuário (em resposta às perguntas sobre remote, sobre o ISODATA não commitado e sobre a documentação).
- **Situação:** parcialmente substituída por D-008 (a documentação agora está no git; sem remote e sem push continuam valendo)
- **Contexto:** os três subprojetos têm repositórios git próprios, mas nenhum tem remote configurado. Havia alterações não commitadas nos três, e o ISODATA tinha uma reescrita de `ISODATAKit.py` que não foi feita nesta sessão.
- **Decisão:**
  - Commits locais e atômicos, sem push. O push fica para quando houver remote.
  - ISODATA: quatro commits (`ISODATAKit.py`; `main.py` com `--NROWS`; diagramas; `Resource/README.md`).
  - CFL e StoCFL: um commit por par de diagramas.
  - O notebook do CFL ficou de fora, porque a diferença são outputs e metadados, com um traceback de `ModuleNotFoundError`.
  - Os 9 READMEs não rastreados em `StoCFL/fedscale/` e `StoCFL/leaf/` ficaram de fora, por serem de terceiros e de origem não verificada.
  - `docs/` e a raiz continuam fora de qualquer repositório git.
- **Alternativas consideradas:**
  - Dar push: descartada, porque não há remote configurado.
  - Criar um repositório git na raiz para versionar `docs/`: descartada pelo usuário, que quer manter a documentação como está.
  - Commitar o notebook: descartada, porque o diff é ruído de execução com um erro.

## D-008: Repositório git único na raiz, sem o histórico dos subprojetos

- **Data:** 2026-11-04
- **Decidido por:** usuário ("usa o repositório que é de minha autoria, o da raiz e remove completamente os repositórios nos subdiretórios, vou modificar os algoritmos mas dê créditos no readme").
- **Situação:** vigente
- **Contexto:** o usuário quer o projeto inteiro versionado e pretende modificar os algoritmos. Os três subprojetos tinham repositórios git próprios (históricos upstream de Felix Sattler, Dun Zeng/Zed e Lucka, mais 15 commits de 2026-11-04), a raiz e `docs/` estavam fora do git, e não havia remote.
- **Decisão:**
  - `git init` na raiz, branch `main`, sem remote. `.gitignore` exclui `.venv/`, `__pycache__/`, `*.py[cod]` e `.ipynb_checkpoints/`.
  - Os diretórios `.git` de `clustered-federated-learning`, `StoCFL` e `ISODATA-python` foram apagados. O histórico deles foi **perdido**.
  - A autoria, as origens e as licenças ficam na seção "Créditos" do [README.md](../README.md). Os arquivos `LICENSE` dos subprojetos foram mantidos.
  - O notebook do CFL entrou com o output de erro (`ModuleNotFoundError`) removido, sem outras mudanças de conteúdo.
  - Os 9 READMEs não rastreados de `StoCFL/fedscale/` e `StoCFL/leaf/` entraram no repositório, porque o usuário pediu o projeto inteiro. A origem deles não foi verificada.
  - `CLAUDE.md`, o README da raiz e `projetos/README.md` foram atualizados para refletir o repositório único.
- **Alternativas consideradas:**
  - Importar os subprojetos preservando o histórico (subtree ou merge de históricos não relacionados): oferecida como a recomendada, descartada pelo usuário, que pediu a remoção completa.
  - Submódulos: exigem remote para cada subprojeto, e nenhum existe.
  - Manter os repositórios separados e criar um só para `docs/` e a raiz: não atende o pedido de ter o projeto inteiro no repositório.
- **Consequência:** commits futuros dos algoritmos ficam no mesmo histórico dos documentos. Não é possível comparar com o upstream por `git diff`; use os links dos créditos.

## D-009: Licença MIT na raiz e correção da licença do CFL

- **Data:** 2026-11-04
- **Decidido por:** usuário ("O CFL tem licença do MIT. Esse projeto terá licença MIT também"). Claude escolheu o titular `luiz2801` e o ano 2026 no `LICENSE`, por serem triviais e reversíveis.
- **Situação:** vigente, com uma ressalva factual de 2026-11-04: o repositório original do CFL não tem arquivo de licença, o README dele não menciona licença e o GitHub não reconhece nenhuma. A origem da informação "MIT" ainda precisa ser confirmada pelo usuário (DP-17 em [11-decisoes-pendentes.md](implementar/plano-isodata-fl/11-decisoes-pendentes.md)).
- **Contexto:** o README dizia que o CFL não tinha licença no original, o que o usuário corrigiu. O repositório da raiz ainda não tinha licença.
- **Decisão:**
  - Adicionar `LICENSE` (MIT) na raiz, Copyright (c) 2026 luiz2801.
  - Registrar o CFL como MIT no README. O arquivo `LICENSE` original **não** foi criado em `projetos/clustered-federated-learning/`, porque o texto de copyright dos autores não está no repositório e não deve ser inventado. Fica como pendência.
- **Alternativas consideradas:**
  - Criar `projetos/clustered-federated-learning/LICENSE` com um copyright presumido: descartada, seria fabricar o aviso de copyright de Felix Sattler.
  - Usar o nome completo do usuário no `LICENSE`: descartada, o nome não foi informado. O e-mail e o usuário git não bastam para inferi-lo.

## D-010: Política 6, commits atômicos ao concluir cada tarefa

- **Data:** 2026-11-04
- **Decidido por:** usuário ("adicione a política de sempre fazê-los"). Claude definiu os detalhes da política (limites, formato de mensagem), por serem consequência direta do pedido e reversíveis.
- **Situação:** vigente
- **Contexto:** os commits só eram feitos quando o usuário pedia, e o usuário quer que passem a ser parte do fluxo de toda tarefa.
- **Decisão:** acrescentar a política 6 ao `CLAUDE.md`. Ao concluir uma tarefa, fazer commits atômicos locais, com código e documentação juntos. A autorização cobre apenas commits: `git push`, reescrita de histórico e descarte de alterações continuam exigindo pedido.
- **Alternativas consideradas:**
  - Commitar só quando o usuário pedir (comportamento anterior): descartada, é o que o usuário quis mudar.
  - Incluir `git push` automático: descartada, não há remote e o usuário não pediu. Enviar o código para fora é uma ação que deve ser pedida.
  - Commits separados para documentação e para código: descartada, deixaria commits intermediários com código e documentação divergentes, o que a política 2 proíbe.

## D-011: Plano modular do ISODATA-FL, com o CFL como split e o StoCFL como merge

- **Data:** 2026-11-04
- **Decidido por:** usuário, quanto à direção ("utilizar o ISODATA como base", "o CFL irá separar os clientes e o StoCFL irá agrupá-los caso seja necessário", "não rodarão todo round", "crie um diretório novo [...] modular"). Claude, por serem escolhas triviais e reversíveis (política 4): o local do diretório, a divisão dos arquivos e o código da simulação dentro de um Markdown.
- **Situação:** vigente. **Esta decisão não aprova as recomendações do plano:** elas continuam pendentes em [11-decisoes-pendentes.md](implementar/plano-isodata-fl/11-decisoes-pendentes.md).
- **Contexto:** a proposta anterior (D-003) deixava em aberto o papel de cada algoritmo. O usuário definiu os papéis e sugeriu que o CFL atue só em rodadas primas a partir da 7, para que um não desfaça o trabalho do outro, e pediu um plano passo a passo com problemas, soluções, alternativas e justificativas.
- **Decisão:**
  - Criar `docs/implementar/plano-isodata-fl/`, com um arquivo por módulo, cada um correspondendo a uma parte do código futuro.
  - Tratar "CFL em rodadas primas a partir da 7" como **hipótese** do usuário ("acho que"), e não como decisão: é o ponto de partida do plano e é comparada com outros calendários no experimento E6.
  - Testar o raciocínio em uma simulação de brinquedo, rodada fora do repositório, com o código e os resultados no anexo A. O resultado principal contraria a hipótese: o calendário reduz a oscilação, mas não a elimina, e o plano propõe guardas para isso.
  - Acrescentar notas de "proposta mais recente" na especificação, nos diagramas e na arquitetura, sem reescrevê-los.
  - Nenhum código foi criado em `projetos/` (D-005 continua valendo).
- **Alternativas consideradas:**
  - Um único documento: descartada pelo pedido de modularidade e pelo motivo de D-003.
  - Reescrever a especificação, os diagramas e a arquitetura: descartada, porque são propostas e ainda não há decisão. As notas evitam a contradição sem apagar o raciocínio anterior.
  - Diretório na raiz ou em `projetos/`: descartada pela D-004, e `projetos/` é para código, que ainda não existe.
  - Simulação em um `.py` no repositório: descartada, porque o usuário pediu Markdown e a D-005 mantém o repositório sem código novo. Fica no anexo, e vira teste na Fase 1, se aprovada.
  - Escrever o plano só com argumentos, sem simular: descartada, porque a simulação derrubou várias expectativas iniciais (vantagem dos primos sobre o período fixo, efeito do número de testes, candidatos a métrica de merge).
  - Perguntar cada ponto antes de escrever: descartada, porque o pedido é justamente o levantamento das alternativas. As escolhas de algoritmo ficam como recomendações pendentes.
- **Consequência:** a próxima etapa é o usuário resolver as decisões pendentes. As três que bloqueiam a Fase 1 são DP-14, DP-16 e DP-18, e a de maior efeito no algoritmo é a DP-01 (quem age primeiro).

## D-012: Detalhar as decisões pendentes e testar cada uma antes de explicá-la

- **Data:** 2026-11-04
- **Decidido por:** usuário, quanto ao pedido ("detalhe melhor as decisões pendentes, explique o dilema e como as possíveis soluções podem ajudar"). Claude, por serem escolhas triviais e reversíveis (política 4): manter tudo em um único arquivo e ampliar a simulação antes de escrever.
- **Situação:** vigente. **As decisões pendentes continuam pendentes:** esta entrada registra só como elas são apresentadas e as recomendações que mudaram.
- **Contexto:** várias recomendações da D-011 eram justificadas só por argumento. Explicar um dilema assim seria repetir uma opinião, então a simulação foi ampliada com testes específicos, incluindo um protótipo do esqueleto, ainda fora de `projetos/`. Os testes mudaram recomendações e derrubaram afirmações do próprio plano.
- **Decisão:**
  - Reescrever `11-decisoes-pendentes.md`: para cada decisão, o dilema, como cada opção ajuda, o que custa, o que os testes mostraram, a recomendação e o custo de errar. As decisões foram separadas em "só você pode responder", "escolha de projeto" e "o experimento decide".
  - Atualizar as recomendações propostas: merge nas rodadas pares, em vez de interprimos; parar os splits em 70% das rodadas; sem `W_merge`; média corrigida em qualquer modo com amostra; comparar censo e amostra, em vez de adiar a amostra; reatribuição seletiva com a partida por `ψ`; reescrever o CFL sem copiar.
  - Corrigir a afirmação de que o termo proximal invalida os limiares do CFL, que o toy não sustenta.
  - Atualizar os módulos e os diagramas do plano, para que nenhum contradiga as novas recomendações.
- **Alternativas consideradas:**
  - Só detalhar o texto, sem novos testes: descartada, porque os testes mudaram várias recomendações, e o texto teria explicado dilemas com premissas erradas.
  - Um arquivo por decisão: descartada. Quem decide lê em sequência, e as decisões se referem umas às outras. O índice no topo do arquivo cobre a navegação.
  - Testar em rede neural real: descartada nesta etapa. Exige ambiente e dados, e é o trabalho das Fases 3 a 5. O próprio plano registra o que o toy não responde.
  - Criar o protótipo do esqueleto em `projetos/`: descartada pela D-005. O código fica no anexo A.
- **Consequência:** a recomendação combinada foi testada junta, em todos os cenários do toy. O que ainda precisa de resposta do usuário está na seção 11.1 de [11-decisoes-pendentes.md](implementar/plano-isodata-fl/11-decisoes-pendentes.md).

