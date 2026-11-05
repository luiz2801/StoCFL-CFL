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

## D-013: Corrigir o guia depois de verificar o código contra os artigos

- **Data:** 2026-11-04
- **Decidido por:** usuário, quanto à correção ("corrige as imprecisões do guia"). Claude, por serem escolhas triviais, reversíveis e sem efeito sobre algoritmos (política 4): o texto das correções, manter a numeração dos itens, acrescentar a invariante 5 e não versionar os scripts de verificação.
- **Situação:** vigente
- **Contexto:** a verificação do CFL e do StoCFL contra os dois artigos, com leitura do código e execução de trechos isolados fora do repositório, achou imprecisões no guia: o item 4.12 #7 estava marcado "verificar" e se mostrou sem problema; o centro do cluster do StoCFL era descrito como ambíguo no artigo, e a dica de descomentar o bloco "reupdate center" não funciona; a divergência *complete* × Alg. 1 do CFL era descrita de forma imprecisa; faltavam divergências na tabela 4.16; e a seção 8 dizia que nada foi executado.
- **Decisão:**
  - Corrigir em [guia.md](guia.md): 3.5, 3.7 (#1 e #4), 3.10, 4.3, 4.5 (nova invariante 5), 4.12 (#7 e #8), 4.15.8, 4.16 (três linhas novas), seção 6 e seção 8 (resultado dos testes). O cabeçalho passou a dizer que trechos foram executados.
  - Os itens 4.12 #7 e #8 mantêm o número, porque outros textos citam a numeração dessa lista.
  - O código não foi alterado. As divergências continuam abertas: modelo global encadeado, centro do cluster só com sorteados, `ψ` não normalizado, *complete linkage*, bug de índices e ausência da checagem de `γ_max`. Corrigi-las é escolha de comportamento do algoritmo e cabe ao usuário.
- **Alternativas consideradas:**
  - Versionar os scripts de verificação em `docs/` ou `projetos/`: descartada. Foram verificações pontuais, o guia descreve o método e o resultado, e a D-005 mantém `projetos/` sem código novo na fase de planejamento. Pode ser revista se o usuário quiser os testes reexecutáveis.
  - Corrigir só as quatro imprecisões, sem registrar a verificação: descartada, porque a seção 8 ficaria dizendo que nada foi executado, o que deixou de ser verdade.
  - Renumerar ou remover o item 4.12 #7: descartada, para não quebrar referências.
  - Já alterar o código para seguir o artigo: descartada, fora do pedido e contra a política 4.

## D-014: Corrigir o código do CFL e do StoCFL para seguir o texto dos artigos

- **Data:** 2026-11-04
- **Decidido por:** usuário ("as correções devem levar o algoritmo ao declarado nos papers"; "não agora, mas ponha num backlog"; "sim, em commit separado"). Claude escolheu o local do backlog (`docs/backlog.md`), por ser trivial e reversível.
- **Situação:** vigente. Substitui a D-005 **só** para o código de `clustered-federated-learning` e `StoCFL`. A D-005 continua valendo para o ISODATA-FL, que segue em planejamento.
- **Contexto:** a verificação por execução mostrou que o código diverge do texto dos artigos, e que no StoCFL o texto e os números publicados apontam para direções opostas: o modelo global encadeado contradiz o texto, mas é o que chega perto das tabelas (seção 8 do [guia](guia.md)).
- **Decisão:**
  - A referência é o **texto e os algoritmos** dos artigos, mesmo que os resultados se afastem das tabelas publicadas.
  - Onde o artigo não declara uma regra (por exemplo, como fundir os modelos de dois clusters), o código fica como está, e a lacuna continua documentada.
  - O cenário de demonstração do notebook (EMNIST, Dirichlet, rotação) não é algoritmo e não muda.
  - Árvore de parâmetros, Alg. 4 e inferência de clientes novos vão para o [backlog](backlog.md).
  - O que é preciso só para rodar (imports, versões) entra em commits separados, sem mudar o algoritmo.
- **Alternativas consideradas:**
  - Manter o modelo global encadeado para reproduzir os números: descartada pelo usuário, que escolheu o declarado nos artigos.
  - Implementar já os recursos ausentes: descartada pelo usuário.
  - Corrigir só o algoritmo, deixando os scripts sem rodar: descartada pelo usuário.

## D-015: Valores de `ε1`, `ε2` e `γ_max` no notebook do CFL

- **Data:** 2026-11-04
- **Decidido por:** usuário, em resposta à pergunta com os resultados dos testes.
- **Situação:** vigente
- **Contexto:** o artigo não informa valores. Dá uma regra de bolso (`ε1 ≈ max‖Δθ_c‖/10`, `ε2 ∈ [ε1, 10·ε1]`), diz que `ε1` deve ser "tão pequeno quanto o tempo permitir" e define `γ_max ∈ [0, 1)`. Os valores anteriores (0.4 e 1.6) foram calibrados com momentum e decaimento do lr, que saem do notebook.
- **Decisão:** `EPS_1 = 0.2`, `EPS_2 = 0.8` e `GAMMA_MAX = 0.5`. Com SGD puro, Alg. 1 e 80 rodadas, em 13 seeds: todas dividem, a 1ª divisão sempre acerta, nenhum cluster mistura grupos e 11 terminam exatamente nos 2 grupos. Os valores valem para esse cenário e precisam ser recalibrados se lr, épocas, lote ou arquitetura mudarem.
- **Alternativas consideradas:**
  - `ε1 ≈ 0.04`, a regra de bolso: descartada. O ruído do SGD mantém `mean_norm` em ~0.10–0.15 mesmo depois de 200 rodadas, e o CFL nunca dividiria.
  - `ε1 = 0.15`, `ε2 = 0.6`: descartada. Em 4 seeds, 2 não dividiram em 80 rodadas.
  - `ε1 = 0.2`, `ε2 = 0.5`: descartada. Gerou de 3 a 6 divisões extras por seed, algumas nas rodadas 3 e 4, longe de um ponto estacionário.
  - `γ_max = 0`: descartada. A checagem existiria, mas nunca rejeitaria nada.
  - `γ_max = 0.7`: descartada. Fica logo abaixo do menor limite de uma divisão correta (0.712) e pode bloquear divisões corretas em outros dados.
  - Nenhum `γ_max` separa as divisões corretas das extras nesse cenário, então a checagem não elimina as divisões extras (2 de 13 seeds).

## D-016: Tamanho das camadas do `CNN_CIFAR10` com duas FC

- **Data:** 2026-11-04
- **Decidido por:** Claude, por ser uma escolha trivial e reversível, que não muda o algoritmo: é uma consequência do pedido de seguir o artigo em algo que ele não especifica.
- **Situação:** vigente
- **Contexto:** o artigo descreve o modelo de CIFAR-10 como "duas camadas convolucionais seguidas de duas totalmente conectadas", sem informar tamanhos. O código tinha três (120→84→10).
- **Decisão:** manter a primeira camada e retirar a intermediária: 120→10.
- **Alternativas consideradas:**
  - 84→10: descartada. Reduz mais o modelo sem motivo, e 120 já existia como entrada do classificador.
  - Manter as três camadas: descartada. Contradiz o artigo.

## D-017: Detalhes de implementação das correções de D-014

- **Data:** 2026-11-04
- **Decidido por:** Claude, por serem escolhas triviais e reversíveis, em pontos que o artigo não especifica e que não mudam o algoritmo declarado.
- **Situação:** vigente
- **Contexto:** seguir o texto dos artigos deixou alguns detalhes em aberto.
- **Decisão:**
  - `Ψ` é calculado em modo `eval`, para que o dropout do `CNN_FEMNIST` não torne a representação aleatória. O artigo define `Ψ` como função de `D`.
  - `--obep` foi removido, porque deixou de ter sentido. `--obbs` ficou, só para acumular o gradiente em lotes menores, sem mudar o resultado.
  - A cópia de `ω₀` para um cluster sem modelo é feita sob demanda, para não ocupar memória com `N` modelos.
  - O notebook exige `len(idc) > 1` antes de bipartir, porque a Definição 1 do artigo pede os dois lados não vazios.
  - `Server.cluster_clients` transcreve o Algoritmo 1 em vez de usar `linkage="single"` do scikit-learn. O resultado foi o mesmo em 1500 matrizes, e o CFL deixa de depender da biblioteca.
  - A regra de fusão de modelos de dois clusters fica como estava, porque o artigo não a declara (D-014).
  - As saídas das células 9 e 12 do notebook foram removidas, porque descreviam o algoritmo antigo, e a política 6 não permite commitar saídas de execução.
  - Os scripts de verificação não foram versionados, como na D-013.
- **Alternativas consideradas:**
  - `Ψ` em modo `train`: descartada. Com dropout, dois cálculos no mesmo cliente dariam resultados diferentes.
  - Inicializar os `N` modelos em `ω₀` já no início: descartada. O efeito é o mesmo, com custo de memória ou de código.
  - Reexecutar o notebook e commitar as novas saídas: descartada pela política 6.

## D-018: Apresentações em Beamer, um arquivo por algoritmo, em `apresentações/`

- **Data:** 2026-11-05
- **Decidido por:** Claude, por ser uma escolha trivial e reversível, que não afeta o comportamento dos algoritmos. O usuário pediu "um diretório novo chamado apresentaçãoes" com uma apresentação do StoCFL e outra do CFL clássico, em LaTeX.
- **Situação:** vigente
- **Contexto:** o pedido não definiu a classe LaTeX, a estrutura de arquivos nem a localização. O nome pedido tem a grafia "apresentaçãoes", que parece erro de digitação de "apresentações".
- **Decisão:**
  - Criar `apresentações/` na raiz do repositório, com o acento correto, e um `README.md` de índice.
  - Usar a classe Beamer, com `aspectratio=169` e o tema Madrid.
  - Fazer duas apresentações separadas: `apresentacao-cfl.tex` e `apresentacao-stocfl.tex`.
  - O conteúdo segue `docs/guia.md` (seções 3 e 4) e os artigos, e inclui as correções e as limitações registradas no guia.
  - Os PDFs e os arquivos auxiliares não são versionados. *(O diretório de saída fora do repositório foi substituído pela D-020.)*
- **Alternativas consideradas:**
  - Nome "apresentaçãoes", exatamente como digitado: descartada por ser provavelmente um erro de digitação. Se for intencional, o diretório pode ser renomeado.
  - Uma única apresentação com os dois algoritmos: descartada, porque o pedido separou as duas apresentações.
  - `diapositivos` ou outro documento que não seja Beamer: descartada, porque Beamer é a classe mais usada para apresentações em LaTeX e o pedido não indicou outra.
  - Diretório `projetos/apresentações/`: descartada, porque as apresentações cobrem os dois projetos e não pertencem a um só.

## D-019: Apresentações sem o pacote `babel` em português

- **Data:** 2026-11-05
- **Decidido por:** Claude, por ser uma escolha trivial e reversível, feita porque o ambiente não tem o pacote necessário. Instalar pacotes do sistema não foi feito sem pedido.
- **Situação:** vigente
- **Contexto:** `\usepackage[brazil]{babel}` falhou com "Unknown option 'brazil'": o arquivo `brazil.ldf` não existe neste ambiente. O pacote que o fornece, `texlive-lang-portuguese`, não está instalado.
- **Decisão:** remover a linha do `babel` dos dois arquivos. O texto é em português, escrito diretamente, e só a hifenização do português fica de fora. O README de `apresentações/` registra isso.
- **Alternativas consideradas:**
  - Instalar `texlive-lang-portuguese` com `apt`: descartada por exigir privilégio de administrador e uma mudança no sistema, fora do repositório. Fica como opção para o usuário, se quiser a hifenização.
  - Usar `babel` com `english`: descartada, porque deixaria a hifenização em inglês, que é pior para o texto em português.

## D-020: Saída das apresentações em `saida-apresentacoes/`, ignorada pelo git, e ajustes de conteúdo

- **Data:** 2026-11-05
- **Decidido por:** o usuário pediu compilar em `/home/luiz/cfl_stocfl/saida-apresentacoes` e corrigir o que a revisão apontou. Claude fez os ajustes de texto, por serem triviais e reversíveis.
- **Situação:** vigente. Substitui a parte da D-018 que punha a saída fora do repositório.
- **Contexto:** a saída já estava na raiz do repositório, contra o README, e aparecia como não rastreada.
- **Decisão:**
  - Compilar em `saida-apresentacoes/`, na raiz, e listá-la no `.gitignore`.
  - Slide "Dois critérios" do CFL: `mean_norm` com média simples, como em `compute_mean_update_norm` e no Algoritmo 5, com nota de que o artigo pondera por `|D_i|/|D_c|`.
  - StoCFL: SFCC expandida no roteiro, "FedAvg" qualificado como "v1 do artigo", e "Quando agrupa" do CFL reescrito como "quando as normas convergem".
- **Alternativas consideradas:**
  - Manter a saída fora do repositório: descartada pelo usuário, que indicou o diretório dentro dele.
  - Trocar o autor `luiz2801` por um nome: descartada, porque o nome real não é conhecido. Fica a pergunta ao usuário.
  - Adicionar slide de resultados e de encerramento: não feito, por alterar o conteúdo e depender de escolha do usuário.

## D-021: Notebook de clusterização ao longo do tempo em `docs/`, com Mermaid via `mermaid.js`

- **Data:** 2026-11-05
- **Decidido por:** o usuário, em resposta a perguntas, pediu um notebook com o diagrama do StoCFL e outro do CFL e escolheu o local e a renderização. Claude decidiu os detalhes triviais e reversíveis (nome, exemplos, iframe).
- **Situação:** vigente
- **Contexto:** o usuário pediu uma representação em Mermaid de como os clientes se agrupam ao longo do tempo no StoCFL, e depois que ela fosse salva num notebook, junto com a versão para o CFL.
- **Decisão:**
  - Criar `docs/clusterizacao-ao-longo-do-tempo.ipynb`, escolha do usuário. O notebook cobre os dois algoritmos, então não fica em um subprojeto só (mesmo raciocínio da D-018).
  - Renderizar com células de código que carregam `mermaid.js` (versão 10.9.1, CDN jsDelivr), escolha do usuário.
  - Claude pôs o `mermaid.js` dentro de um `iframe` com `srcdoc`, porque o Jupyter e o VS Code não executam `<script>` em saídas HTML comuns.
  - Os exemplos são ilustrativos, não execuções reais: StoCFL com 8 clientes e quatro rotações de MNIST; CFL com os 10 clientes do notebook (0 a 4 rotacionados em 180°). O número da rodada de divisão do CFL (`r*`) é arbitrário.
  - O notebook é salvo sem saídas.
  - Revisão no mesmo dia, a pedido do usuário (a primeira versão, com as rodadas lado a lado, ficou ruim de ler): as rodadas passaram a ser linhas, de cima para baixo, as uniões ganharam borda grossa, e o `iframe` ajusta a própria altura depois do desenho. Claude decidiu isso por ser só apresentação.
- **Alternativas consideradas:**
  - `projetos/` ou a raiz como local: descartadas pelo usuário, em favor de `docs/`.
  - Blocos ```` ```mermaid ```` em células Markdown: descartada pelo usuário, porque no Jupyter puro apareceriam como texto.
  - Imagem estática (mermaid.ink ou `mmdc`): descartada pelo usuário; também não há `mmdc` no ambiente.
  - Um arquivo `.md` de diagrama como os de cada projeto: descartada, porque o pedido foi um notebook.

## D-022: Ambiente único no `.venv` da raiz e notebook de teste da fração de clientes (m) do StoCFL

- **Data:** 2026-11-05
- **Decidido por:** o usuário, em resposta a perguntas, escolheu o cenário, o modo de execução, o local e o ambiente. Claude decidiu os detalhes triviais e reversíveis, listados abaixo.
- **Situação:** vigente. Substitui a descrição anterior do `.venv` da raiz como "apenas kernel Jupyter" (README da raiz e guia).
- **Contexto:** o usuário pediu um pipeline de testes em `.ipynb` com `m` em 100%, 50%, 25% e 10% e no máximo 50 rodadas. O ambiente não tinha `torch` nem `fedlab`, e o usuário quis que o `.venv` da raiz fosse o único ambiente do projeto, com tudo para rodar qualquer cenário.
- **Decisão:**
  - Notebook `projetos/StoCFL/teste-fracao-clientes.ipynb`, que chama `StoCFL-FCC+CFL.py` por `subprocess` e lê `cluster.pkl` e o log principal. O código do StoCFL não foi alterado.
  - Cenário Rotated MNIST com `n = 200` (`k = 4`), `--train 0` (só clusterização), `τ = 0.5`, no máximo 50 rodadas.
  - `.venv` da raiz como único ambiente, com `requirements.txt` na raiz que une StoCFL, CFL, ISODATA e Jupyter; torch do PyPI com CUDA (2.15.0, build `cu132`). Os `requirements.txt` dos subprojetos ficam como estavam.
  - Claude decidiu, por serem triviais e reversíveis: `SEEDS = [0]` por padrão (cada seed gera uma partição nova de ~750 MB; editável); métricas de nº de clusters, ARI, pureza, clusters mistos, cobertura e rodada de estabilização; reaproveitar execuções concluídas (`REEXECUTAR = False`); ignorar no git `projetos/StoCFL/logs/`, `datasets/mnist/` e `datasets/rotated_*/`; o nome do notebook; e atualizar três frases obsoletas sobre o `.venv` em documentos de planejamento (`docs/implementar/`).
- **Alternativas consideradas:**
  - Rotated MNIST com `n = 400` ou Rotated CIFAR-10: descartadas pelo usuário. O `n = 400` usa mais memória (cada `Ψ` tem ~6,5 MB), e o CIFAR-10 é mais pesado.
  - Rodar com `--train 1`: descartada pelo usuário; o foco é o efeito de `m` na clusterização, e o treino ficaria bem mais lento, com resultados abaixo do artigo (D-014).
  - Criar `projetos/StoCFL/.venv`: descartada pelo usuário, que quis um único ambiente na raiz.
  - Torch só para CPU: descartada pelo usuário; a máquina tem uma RTX A4000 e os scripts usam a GPU se houver.
  - Descrever as dependências só no README, sem arquivo: descartada pelo usuário, em favor do `requirements.txt` na raiz.
  - Notebook em `docs/`, ou importando o servidor: descartadas. O script não é importável (o código principal está sob `__main__`), e importar exigiria alterar o código.

## D-023: Gráficos do notebook de teste de m em Plotly

- **Data:** 2026-11-05
- **Decidido por:** o usuário pediu os gráficos em "plotpy" e, perguntado qual biblioteca era, escolheu o Plotly.
- **Situação:** vigente. Altera os gráficos da D-022, que usavam matplotlib.
- **Contexto:** o notebook `teste-fracao-clientes.ipynb` plotava com matplotlib.
- **Decisão:** trocar por Plotly (3 painéis com `make_subplots`: nº de clusters, ARI e cobertura, todos em escala linear), com a mesma paleta e com traços e marcadores distintos por `m`. `plotly` 7.1.0 e `nbformat` 5.11.1 (exigido por `fig.show()` em notebook) entram no `requirements.txt` da raiz e no `.venv`. O `matplotlib` continua nos requisitos, porque o CFL e o ISODATA o usam.
- **Alternativas consideradas:**
  - PlotPy (biblioteca científica baseada em Qt): descartada pelo usuário, em favor do Plotly. Ela abre janelas desktop, não renderiza no notebook e exige PyQt.
  - Manter o matplotlib: descartada pelo usuário, que pediu a troca.
  - Escala log no painel do nº de clusters, que Claude tinha usado por padrão para não comprimir a faixa de 4 a 10 clusters: descartada pelo usuário em 2026-11-05, que pediu escala linear.

## D-024: Notebook de teste de m com `τ = 0.9` e `m` = 5%

- **Data:** 2026-11-05
- **Decidido por:** o usuário, que editou os parâmetros do notebook `teste-fracao-clientes.ipynb`. Claude apenas registrou a mudança e atualizou a documentação.
- **Situação:** vigente. Altera os parâmetros da D-022 (`τ = 0.5` e `m` até 10%).
- **Contexto:** o usuário rodou o notebook com outros parâmetros e pediu o commit.
- **Decisão:**
  - `TAU = 0.9` (antes 0.5) e `FRACOES = [1.0, 0.5, 0.25, 0.1, 0.05]` (antes sem 0.05, ou seja, 10 clientes por rodada a mais).
  - O notebook é commitado **sem as saídas das células** (política 6 do `CLAUDE.md`). O arquivo no disco do usuário mantém as saídas; só o commit as omite.
  - A tabela de resultados do guia (4.11) continua sendo da execução com `τ = 0.5`, e o texto agora diz isso. Os resultados com `τ = 0.9` não foram registrados.
- **Alternativas consideradas:**
  - Commitar o notebook com as saídas: descartada, porque a política 6 proíbe commitar saídas de execução e o diff teria ~1.400 linhas de HTML e JSON de gráficos.
  - Limpar as saídas no arquivo do usuário: descartada, porque apagaria resultados que ele pode querer ver e o pedido foi só de commit.
  - Registrar no guia os resultados com `τ = 0.9`: não feita, porque os números só existem nas saídas do notebook e não foram conferidos.

## D-025: Merge com o histórico do remoto, mantendo a versão local

- **Data:** 2026-11-05
- **Decidido por:** o usuário pediu "resolve os conflitos com um merge e dá push", depois de ver as opções. Claude escolheu a versão de cada arquivo em conflito.
- **Situação:** vigente
- **Contexto:** o push foi rejeitado porque o `origin/main` (`006b840`, um único commit, "Add CFL and StoCFL projects with reference papers and guide") não tinha ancestral em comum com o histórico local. O merge deu conflito add/add em 22 arquivos.
- **Decisão:**
  - `git merge --allow-unrelated-histories`, com a versão **local** (`--ours`) em todos os 22 arquivos. A versão do remoto de 17 deles já está no histórico local, em commits antigos. Nos outros 5 (`docs/guia.md`, `ISODATAKit.py`, `README.md` e `main.py` do ISODATA-python e o notebook do CFL), o remoto tem uma versão anterior às correções, por exemplo um guia que ainda diz que nada foi executado.
  - Manter `projetos/ISODATA-GNR602/`, que só existe no remoto, e avisar no `projetos/README.md` que é código de terceiros, sem licença identificada e não integrado.
  - Push normal (fast-forward depois do merge), sem `--force`.
- **Alternativas consideradas:**
  - `push --force-with-lease`: descartada, porque apagaria o `006b840` e o `ISODATA-GNR602/`.
  - Push para outra branch: descartada pelo usuário, que pediu o merge.
  - Versão do remoto nos 5 arquivos que só ela tem: descartada, porque desfaria correções e a documentação atual.
  - Apagar o `ISODATA-GNR602/`: descartada, porque o arquivo não é meu nem foi citado como lixo. Fica a decisão de integrá-lo ou removê-lo para o usuário.
