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

## D-026: Busca de τ no notebook de teste de m

- **Data:** 2026-11-06
- **Decidido por:** o usuário, em resposta a perguntas, escolheu o local, as frações `m`, o critério e o orçamento. Claude decidiu os detalhes triviais e reversíveis, listados abaixo.
- **Situação:** vigente
- **Contexto:** o usuário quis testar vários valores de `τ` para ver como os clientes se agrupam, começando em 1.0 e 0.05 e depois fazendo uma busca binária com os melhores resultados.
- **Decisão:**
  - Nova seção 5 em `teste-fracao-clientes.ipynb`, com `m` em 100%, 25% e 10% (`TAU_FRACOES`).
  - O critério é um cenário ideal como gabarito: os `k = 4` grupos reais. O melhor `τ` é o de maior ARI final contra o gabarito.
  - Varredura grossa em `TAU_GRADE = [0.05, 0.25, 0.5, 0.75, 1.0]` e até 6 bisseções.
  - Claude decidiu, por serem triviais e reversíveis: bissecar o maior intervalo entre a borda do conjunto ótimo (empates em ARI formam um intervalo) e o vizinho avaliado, parando abaixo de `TAU_LARGURA_MIN = 0.005`; sugerir o centro do intervalo ótimo; cache em `logs/busca-tau.json`, porque o nome da pasta de logs do script não traz o `τ`; esperar a virada do minuto entre execuções do mesmo `m`, porque o script nomeia a pasta só até o minuto e duas execuções no mesmo minuto cairiam na mesma pasta; gráfico com nº de clusters em escala linear (D-023); uma só seed; manter os `psi.pkl` de cada execução (~1,3 GB, cerca de 43 GB no total).
  - O código do StoCFL não foi alterado.
- **Alternativas consideradas:**
  - Notebook novo: descartada pelo usuário, que pediu uma seção no notebook atual.
  - Só `m` = 100%: descartada pelo usuário, que pediu uma lista de `m`.
  - Critério pelo nº de clusters igual a `k` (monótono em `τ`) ou pelo maior intervalo com `k = 4`: descartadas pelo usuário em favor do gabarito. O nº de clusters continua nas tabelas e nos gráficos.
  - Começar só em 1.0 e 0.05: descartada pelo usuário, porque os dois extremos podem dar o mesmo resultado (cada cliente num cluster, ou todos juntos) e a bisseção não teria como se orientar.
  - Apagar os `psi.pkl` depois de ler as métricas: não feita, para manter as execuções reaproveitáveis e inspecionáveis; há espaço em disco.
  - Instalar `nbconvert` para executar o notebook: não feita; a verificação rodou as mesmas células como script.

## D-027: Comentários do notebook de teste de m

- **Data:** 2026-11-06
- **Decidido por:** Claude, por ser trivial e reversível. O usuário pediu "melhora os comentários no notebook", sem dizer quais células.
- **Situação:** vigente
- **Contexto:** os comentários de `teste-fracao-clientes.ipynb` eram poucos e curtos, principalmente nas funções de métricas e na busca de τ.
- **Decisão:** comentários melhorados em todas as células de código (parâmetros, execução, métricas, gráficos e busca de τ). Nenhuma linha de código mudou; conferido comparando o código sem comentários antes e depois. As saídas das células foram preservadas, editando o JSON do notebook em vez de usar o `NotebookEdit`, que as apagaria.
- **Alternativas consideradas:**
  - Só a seção 5 (a busca de τ): descartada, porque o pedido não a restringia e as seções 1 a 3 também tinham pouco comentário.
  - Comentar linha a linha: descartada, para manter a densidade parecida com a do resto do repositório.

## D-028: Gráficos da busca de τ com escala log no nº de clusters

- **Data:** 2026-11-06
- **Decidido por:** o usuário, que pediu para consertar o gráfico da busca de τ ("está muito ruim") e, perguntado como resolver o eixo do nº de clusters, escolheu a escala log. As demais melhorias (limites dos eixos, faixas do `τ` ótimo, marcadores) foram de Claude, por serem triviais e reversíveis.
- **Situação:** vigente. Substitui, só para o gráfico da seção 5, a escolha de escala linear registrada na D-026 (que seguia a D-023, sobre o gráfico por rodada).
- **Contexto:** em função de `τ`, o nº de clusters vai de 1 a 200 (`τ = 1.0`: cada cliente é um cluster). Em escala linear, esse ponto achatava os valores de 1 a 11 numa linha colada no zero. Além disso, as curvas de `m` = 100% e 25% coincidem em ARI e pureza e uma escondia a outra.
- **Decisão:**
  - Painel de nº de clusters em escala log, com marcas em 1, 2, 4, 10, 20, 50, 100 e 200. A D-023 continua valendo para o gráfico por rodada (seção 3), que tem faixa de 4 a 10 clusters.
  - Eixo x de 0 a 1.04; ARI de -0.05 a 1.05; pureza de 0.2 a 1.05.
  - Faixa colorida de fundo com o intervalo de `τ` de maior ARI de cada `m`; marcadores de tamanhos diferentes por `m`.
  - Só o código de plotagem mudou. Os dados e a busca não foram alterados, e o gráfico não foi executado no notebook (as saídas antigas ficam no arquivo do usuário até ele reexecutar a célula); o código foi testado com os dados da tabela do guia.
- **Alternativas consideradas:**
  - Linear cortado em ~12 clusters, com anotação do ponto de 200: descartada pelo usuário, que preferiu a escala log; esconderia o ponto extremo.
  - Linear sem o `τ = 1.0` na plotagem: descartada pelo usuário, porque perderia a referência de "cada cliente é um cluster".

## D-029: Gabarito com mais grupos (`--k`) e lista `KS` no notebook de teste de m

- **Data:** 2026-11-06
- **Decidido por:** o usuário pediu "um gabarito com mais clusters em vez de só 4, em uma lista iterável, como nos casos anteriores" e, perguntado, escolheu parametrizar o script, a lista `[4, 8, 16]` e `n = 240`. Claude decidiu, por serem triviais e reversíveis, os nomes e os detalhes abaixo.
- **Situação:** vigente. Altera o cenário da D-022 (`n = 200`, `k = 4`) e o código do `StoCFL-FCC+CFL.py`.
- **Contexto:** o script fixava `k = 4` (rotações 0°, 90°, 180°, 270°) no código, então o notebook só testava 4 grupos reais.
- **Decisão:**
  - `StoCFL-FCC+CFL.py` ganhou `--k`. No MNIST, `k` ângulos igualmente espaçados (`360·i/k`) e `shards = n / k`. O default continua 4 (MNIST) e 2 (CIFAR), então o comportamento sem `--k` não muda; no CIFAR só vale 2. Exige `n % k == 0`.
  - Para `k` diferente do padrão, a pasta de dados ganha `_k{k}` e a de logs `-k{k}` (`rotated_mnist_240_0_k8`), para dados e logs de `k` diferentes não se misturarem. Com o `k` padrão os nomes antigos ficam iguais.
  - O notebook passa a ter `KS = [4, 8, 16]` e `N = 240` (divisível por 4, 8 e 16), com `TAU_KS = list(KS)` para a busca de τ, como já havia `FRACOES` e `TAU_FRACOES`. O gabarito virou a função `verdade(k)`, e as seções 1 a 3 e 5 iteram sobre `k`, com uma figura por `k`. A chave do cache de `busca-tau.json` ganhou `n` e `k`.
  - As saídas antigas do notebook (n = 200) ficam no arquivo do usuário até ele reexecutar; o commit leva o notebook sem saídas (política 6).
  - Com `n = 240`, os logs e dados de `n = 200` não são reaproveitados, nem para `k = 4`.
- **Alternativas consideradas:**
  - Notebook gerando as partições, sem mudar o StoCFL: descartada pelo usuário; a pasta de dados só é identificada por `n` e `seed`, então `k` diferentes colidiriam.
  - Misturar rotação e rótulos (como a ablação de 8 clusters do artigo): descartada pelo usuário; muda o cenário, não só o nº de grupos.
  - `K = [4, 5, 8, 10]` e `[2, 4, 8]`: descartadas pelo usuário em favor de `[4, 8, 16]`.
  - `n = 200` com `K = [4, 8, 10]` e `n` proporcional a `k` (200, 400, 800): descartadas pelo usuário; a segunda custaria ~5 GB por rodada no `n = 800`.
  - Sempre incluir `k` nos nomes de logs e dados: descartada por Claude, porque invalidaria o reaproveitamento das execuções existentes com o nome antigo.

## D-030: Relatório de m, k e τ em `docs/relatorio-m-k-tau.md`

- **Data:** 2026-11-06
- **Decidido por:** Claude, por serem escolhas triviais e reversíveis (o pedido do usuário foi "gera um relatório explicando a relação de m, k e τ" no notebook de teste de `m`, sem formato nem local).
- **Situação:** vigente.
- **Contexto:** o notebook `teste-fracao-clientes.ipynb` tinha resultados de 15 execuções (`k` = 4, 8, 16 × 5 valores de `m`) e a busca de `τ`, mas a análise estava só nas saídas, e o guia dizia que esses resultados não estavam registrados.
- **Decisão:** relatório em Markdown em `docs/`, escrito em português, com base só nas saídas já existentes no notebook (nenhuma execução nova, nenhum código alterado). Separa fatos medidos de hipóteses (por exemplo, os cossenos entre grupos não foram medidos). O guia (4.11) e o README de `docs/` passam a apontar para ele.
- **Alternativas consideradas:**
  - Documento no Claude Docs ou artefato publicado: descartada, porque o pedido não pediu um documento externo e a política do repositório mantém a documentação em `docs/`.
  - Copiar os resultados para dentro do guia: descartada, porque o guia ficaria longo; o guia só referencia o relatório.
  - Rodar novas execuções (outras seeds, `m` = 50% e 5% na busca de `τ`): descartada, porque custa ~1,6 GB por execução e não foi pedida; fica listada como limite do relatório.

## D-031: Branch `dropout-stocfl` e plano do dropout com retorno no StoCFL

- **Data:** 2026-11-09
- **Decidido por:** o usuário definiu a ideia (um sorteio de dropout separado do sorteio de `m`, com o cliente voltando ao treinamento depois) e pediu a branch e o documento. Claude decidiu, por serem triviais e reversíveis, o nome da branch, o nome e o local do plano, o uso de `unittest` nos testes e a forma do processo de disponibilidade (rodada de retorno sem sorteio, para limitar a ausência).
- **Situação:** vigente, com uma parte substituída por [D-032](#d-032-escolhas-de-design-do-dropout-com-retorno-no-stocfl): o sorteio de `m` deixa de ser independente do `drop` e passa a ser feito só entre os clientes disponíveis. Implementação em andamento: módulo e integração no `StoCFL-FCC+CFL.py` feitos (ver D-033 e D-034).
- **Contexto:** o usuário quis testar o efeito do dropout do MimiC no StoCFL. A análise mostrou que o terceiro padrão do MimiC (pesos aleatórios novos a cada rodada) tem a mesma distribuição que o `random.sample` do StoCFL, então não muda nenhum resultado. Um dropout sem retorno e sem memória no tempo também equivale a um `m` menor. A simulação de 2026-11-09 mostrou que só a queda **por grupo de rotação, com retorno**, produz um regime que variar `m` não reproduz (algum grupo sem sobrevivente em ~80% das rodadas). Os números do plano vêm do processo especificado, com rodada de retorno sem sorteio; uma primeira simulação, sem essa garantia, deu 0,643 de disponibilidade e 83,1% de rodadas com grupo vazio.
- **Decisão:**
  - Trabalhar na branch `dropout-stocfl`, criada a partir de `main`.
  - O `drop` é um processo de disponibilidade independente do sorteio de `m`, com gerador próprio, e o cliente que cai volta depois de até `L` rodadas.
  - O plano está em [plano-dropout-stocfl.md](plano-dropout-stocfl.md). Com `--drop 0` (padrão) o comportamento atual não muda.
- **Alternativas consideradas:**
  - Implementar o terceiro padrão do MimiC ao pé da letra: descartada, porque equivale ao sorteio uniforme atual (verificado por simulação) e não muda resultados.
  - Dropout sem retorno ou sorteado de novo a cada rodada, sem memória: descartada pelo usuário (o cliente deve voltar) e por ser equivalente a um `m` menor.
  - Copiar o código de `mimic_codes/`: descartada, porque o diretório não tem arquivo de licença e o processo deste plano é diferente dos três padrões do MimiC.
  - Trabalhar direto na `main`: descartada, porque o usuário pediu uma branch e a mudança altera o código do algoritmo.
  - Plano em Claude Docs ou artefato publicado: descartada, porque a documentação do repositório fica em `docs/` (D-030).
  - `pytest` nos testes: descartada, porque não está instalado no `.venv` e `unittest` basta.

## D-032: Escolhas de design do dropout com retorno no StoCFL

- **Data:** 2026-11-09
- **Decidido por:** o usuário respondeu as pendências P1 a P7 do plano e, depois de ver a simulação do desenho escolhido, confirmou "manter como decidido" e o escopo "só `StoCFL-FCC+CFL.py` primeiro". Claude interpretou as respostas ambíguas e decidiu os detalhes triviais listados abaixo.
- **Situação:** vigente. Substitui em parte a D-031 (o sorteio de `m` passa a ser entre os disponíveis). Implementação em andamento: módulo e integração no `StoCFL-FCC+CFL.py` feitos (ver D-033 e D-034); o notebook foi feito (D-035); faltam os outros dois scripts e as execuções completas.
- **Contexto:** o plano ([plano-dropout-stocfl.md](plano-dropout-stocfl.md)) deixava sete escolhas abertas. As respostas do usuário combinam disponibilidade conhecida (quem caiu não é sorteado e outro entra no lugar) com queda por cliente. Claude simulou esse desenho antes de implementar e avisou que o efeito esperado é pequeno: o `drop` atrasa a observação dos clientes em poucas rodadas (some por volta da rodada 25), e só com `m` grande o nº de participantes cai de fato (157,5 em vez de 240 com `m = 100%`, `d = 0,1` e `L ~ U[1,10]`). Só presença e cobertura foram medidas, não o ARI.
- **Decisão:**
  - **P1:** o `drop` age na seleção. O cliente que cai não pode ser sorteado, e outro entra no lugar. A fase `train` (cliente observado mas sem treinar) saiu do escopo, e o `gmodel` não é tocado.
  - **P2:** cada cliente cai sozinho. A lei por grupo de rotação saiu do escopo (o grupo de rotação é o gabarito dos dados, não o cluster que o algoritmo descobre).
  - **P3:** a duração `L` da ausência é sorteada com distribuição uniforme, um sorteio por queda. Interpretação de Claude: inteiro em `{1, …, L_max}`, com `L_max` em `--drop_rounds`.
  - **P4:** qualquer cliente pode cair, não só os sorteados em `m`. O processo de disponibilidade roda para os `N` clientes.
  - **P5:** reformulada, porque o usuário não entendeu a pergunta original. Com P1 e P4, só faltam clientes se houver menos de `m` disponíveis. Claude decidiu usar todos os disponíveis e pular a rodada se nenhum estiver disponível.
  - **P6:** `StoCFL-FCC+CFL.py` primeiro. Os outros dois scripts ficam para depois, só com a lei por cliente.
  - **P7:** notebook novo, `teste-dropout.ipynb`.
  - Claude decidiu, por serem triviais e reversíveis: os nomes das flags (`--drop`, `--drop_rounds`), o estado inicial com todos disponíveis, o formato do log e do `availability.pkl`.
- **Alternativas consideradas:**
  - Fase `train` do `drop` (cliente na matriz que não treina): descartada, porque o cliente que cai nem é sorteado.
  - Lei por grupo de rotação: descartada pelo usuário em favor da queda por cliente. Fica como extensão possível (mapear cliente → grupo no módulo de disponibilidade).
  - Duração fixa `L`: descartada pelo usuário em favor do sorteio uniforme.
  - Só os sorteados em `m` podem cair, sem reposição: descartada pelo usuário (qualquer cliente pode cair). Também foi oferecida de novo depois da simulação, e ele manteve a reposição.
  - Mínimo de sobreviventes (o MimiC usa 2) e promoção de clientes extras: não se aplica, porque `m` é completado entre os disponíveis.
  - Os três scripts de uma vez: adiada pelo usuário; segue o precedente do `--k` (D-029).
  - Seção nova no `teste-fracao-clientes.ipynb`: descartada pelo usuário, que tem alterações pendentes nesse notebook, e ele é a referência reproduzível dos resultados de `m`.

## D-033: Detalhes de implementação do módulo `availability.py` e dos seus testes

- **Data:** 2026-11-09
- **Decidido por:** Claude, por serem escolhas triviais e reversíveis que não alteram o comportamento do algoritmo (a especificação do processo está em D-032 e no plano, seção 5.2).
- **Situação:** vigente.
- **Contexto:** o plano fixa a classe `Availability(n, drop, rounds, seed)`, o método `step()` e os testes T1 a T5, mas deixa em aberto a forma do retorno, a organização dos testes e a verificação de que o teste detecta defeitos.
- **Decisão:**
  - `step()` devolve uma `list` de `bool` de tamanho `n` (`up[c]`). O estado fica em `down_left` e `grace`, listas de tamanho `n`, como na especificação.
  - Os testes ficam em `projetos/StoCFL/tests/test_availability.py`, sem `__init__.py`, e importam `availability` a partir da pasta do StoCFL (`../../.venv/bin/python -m unittest tests/test_availability.py -v`, como no plano).
  - T3 foi dividido em dois testes. O primeiro confere a ausência máxima e a cobertura de `1..L_max`. O segundo usa `drop = 0,99`, em que, sem a rodada de retorno, as ausências se emendariam e passariam de `L_max`, e então a garantia "há uma rodada disponível entre duas ausências" é de fato testada.
  - Foi acrescentado um teste fora da lista T1 a T5: o `step()` não consome o gerador global (`random.getstate()` igual antes e depois), porque o plano exige gerador próprio.
  - Verificação do teste: um mutante do módulo sem a rodada de retorno (`grace` sempre falso) foi rodado contra os testes e falhou em 3 deles (os dois T3 e o T4), então os testes detectam a falta da rodada de retorno. O mutante foi descartado e não está no repositório.
  - Comentários do módulo em inglês e curtos, como o resto do código do StoCFL.
- **Alternativas consideradas:**
  - Devolver um `set` dos indisponíveis ou um array numpy: descartada, porque o módulo não depende de `numpy` e a lista indexada por cliente é o que o laço de `main` usa (`up[c]`).
  - `pytest`: já descartado em D-031 (não está no `.venv`).
  - Um só teste T3: descartada, porque, com `drop` baixo, o teste de ausência máxima passaria mesmo sem a rodada de retorno.

## D-034: Detalhes da integração do dropout no `StoCFL-FCC+CFL.py`

- **Data:** 2026-11-09
- **Decidido por:** Claude, por serem escolhas triviais e reversíveis que não alteram o comportamento do algoritmo com `--drop 0` (o desenho está em D-032 e no plano, seção 5). Nenhuma escolha de design precisou ser perguntada.
- **Situação:** vigente.
- **Contexto:** o plano fixa as flags, o sorteio entre os disponíveis, a rodada vazia, a linha `unavailable`, o `availability.pkl` e o sufixo da pasta de logs, mas deixa em aberto a validação das flags, a posição da linha de log e a forma de pular o treino.
- **Decisão:**
  - **Validação.** Com `assert` no `__main__`, no estilo das validações de `--k`: `0 <= drop < 1` e `drop_rounds >= 1`, e, **só com `drop > 0`**, `num_per_round <= n`. A última existe porque `min(m, disponíveis)` esconderia um `m > n`. Sem `--drop`, o `random.sample` continua levantando `ValueError` para `m > n`, e esse caminho não foi tocado.
  - **`self.availability`** é criado sempre em `__init__`, como no plano, mas `step()` só é chamado com `drop > 0`.
  - **Log.** No ramo `drop > 0`, a linha `Round {r}/{T}, unavailable [...]` sai antes da linha `Starting round`, e `availability.pkl` é regravado a cada rodada, como o `cluster.pkl`, com listas ordenadas de `int`.
  - **Rodada vazia.** `if self.args.train and not cid_this_round: ... elif self.args.train:`, equivalente ao `if self.args.train and cid_this_round` do plano, sem reindentar o bloco de treino. Efeito colateral aceito: com `--drop 0`, `--num_per_round 0` e `--train 1`, que antes quebrava em `fedavg_aggregate([])`, a rodada passa a ser tratada como vazia. Essa configuração não era suportada.
  - **Pasta de logs.** `-drop{d}-r{L_max}` depois do `-k{k}` e antes de `-time-`, com `d` no formato de `str(float)` (`0.1`).
  - **Documentação.** Os números de linha do script no guia (4.3, 4.4 e 4.16) foram atualizados, inclusive a referência `:213` da 4.16, que já estava errada por uma linha (era 214) antes desta mudança. O plano mantém os números de linha antigos, com um aviso no topo. Em D-031 e D-032, só o campo "Situação" foi atualizado; o conteúdo não foi alterado.
  - **Verificação dos testes I1 a I4** (resultados no guia, 4.11). O I4 do plano, com `n = 40` e seed 0, **não gerou nenhuma rodada vazia**, então não exercitou o ramo novo; o teste foi repetido com `n = 8` e `m = 4`, em que 4 de 15 rodadas ficaram vazias. O I5 (leitura pelo notebook) fica para o passo 4.
  - **Mermaid.** A sintaxe dos dois diagramas foi conferida só por uma checagem estrutural em Python (nós definidos, `subgraph`/`end`, `alt`/`else`/`end`, aspas e `#gt;`), que passa nas versões novas e antigas e falha em versões quebradas de propósito. O `mermaid.js` não foi executado: não há `node` nem `mmdc` no ambiente, e a tentativa de renderizar com o `mermaid.js` 10.9.1 baixado no Firefox foi bloqueada pelo classificador de permissões, então o arquivo baixado foi apagado.
- **Alternativas consideradas:**
  - `ValueError` no lugar de `assert`: descartada, porque o script já valida `--k` com `assert`, e a validação antecipada evita preparar os dados antes de falhar.
  - `num_per_round <= n` também com `--drop 0`: descartada, para não tocar o caminho com `--drop 0` (só mudaria o tipo do erro).
  - Reindentar o bloco de treino com `if self.args.train and cid_this_round`: descartada, porque o diff ficaria maior sem mudar o comportamento.
  - Criar `Availability` só com `drop > 0`: descartada, porque o plano a cria em `__init__` e assim valores inválidos falham sempre.
  - Gravar a linha `unavailable` depois da `Starting round`: descartada, porque a disponibilidade é decidida antes do sorteio e a linha fica dentro do mesmo ramo `drop > 0`.

## D-035: Notebook `teste-dropout.ipynb`: cenários, matrizes de confusão e smoke test

- **Data:** 2026-11-09
- **Decidido por:** o usuário escolheu os cenários (pedido e respostas a duas perguntas); Claude decidiu, por serem triviais e reversíveis, os detalhes de implementação listados abaixo.
- **Situação:** vigente. Cumpre o passo 4 do plano e a P7 de [D-032](#d-032-escolhas-de-design-do-dropout-com-retorno-no-stocfl). Substitui a grade sugerida na seção 9 do plano.
- **Contexto:** o usuário pediu que o notebook rodasse os cenários com 10 seeds e 50 rodadas, com e sem dropout, e plotasse matriz de confusão e gráficos em Plotly. O pedido deixava em aberto `m`, `d`, `L`, `k` e `τ`, e Claude perguntou.
- **Decisão (do usuário):**
  - `m` = 100% e 50% (240 e 120 clientes por rodada), `n = 240`, 50 rodadas, 10 seeds, `--train 0` (Claude seguiu o plano nesse último).
  - Duração da ausência uniforme em 1 a 10 rodadas (`--drop_rounds 10`; o mínimo de 1 é o desenho de D-032, não há flag para ele).
  - `d` = 0,05 e 0,1, além de `d = 0` (StoCFL sem dropout). O usuário perguntou o que era `d` (probabilidade de um cliente disponível cair em cada rodada), e Claude explicou antes de ele escolher.
  - `k` = 8 e 16, com `τ = 0,75`. Claude recomendou `k = 4` com `τ = 0,625`, o centro da janela do [relatório de m, k e τ](relatorio-m-k-tau.md), e avisou que o `τ = 0,75` é o menor `τ` que recuperou os grupos para `k = 16` (em 0,7188 tudo colapsou em 1 cluster). O usuário manteve `τ = 0,75`, então algumas seeds podem colapsar, com e sem dropout; o notebook mostra isso (coluna `seeds_colapso`, matrizes de confusão) e a leitura avisa.
  - Só criar o notebook e rodar o smoke test, sem executar a grade completa (120 execuções).
- **Decisão (de Claude, trivial e reversível):**
  - Notebook novo `projetos/StoCFL/teste-dropout.ipynb`, versionado sem saídas, com as funções de métricas copiadas do `teste-fracao-clientes.ipynb` (que não foi editado). As seeds são 0 a 9.
  - **Reaproveitamento de execuções** pela linha `Namespace(...)` do log (`n`, `m`, `seed`, `k`, `μ`, `τ`, `train`, `drop`, `drop_rounds`), porque o nome da pasta de logs não traz o `τ`. Logs de antes da flag `--drop` valem como `drop = 0`. Das 120 execuções, 2 já existem (seed 0, `m` = 100%, `k` = 8 e 16, sem dropout, da busca de `τ`).
  - **Disco:** a célula de execução estima o espaço (`psi.pkl` de ~1,6 GB por execução e ~0,23 GB de dados por `k` e seed) e para se faltar. Opção `APAGAR_PSI` (padrão `False`) apaga o `psi.pkl` de cada execução concluída, porque a análise não o usa. Os dados de `k = 8` e `k = 16` ocupam 1,8 GB e 3,6 GB por seed (~54 GB para 10 seeds), e a grade completa usa ~190 GB de `psi.pkl`.
  - **Gráficos (Plotly):** por `k`, painéis de nº de clusters, ARI, cobertura e participantes por rodada, com uma coluna por `m`, uma linha por cenário (média entre as seeds e faixa mín–máx); caixas com um ponto por seed para ARI, nº de clusters e rodada estável finais; tabela dropout − sem dropout por seed com Wilcoxon (24 testes, sem correção para comparações múltiplas; diferenças todas zero dão `p = 1`).
  - **Matrizes de confusão** da partição final, um painel por cenário: (1) grupo real × grupo previsto (o grupo previsto de um cluster é o grupo real dominante), somada nas seeds e normalizada por linha; (2) cluster × grupo real de uma seed, com menu para trocar de seed. A matriz de pares (mesmo cluster × mesmo grupo, do scikit-learn) entra na tabela de resumo como pares misturados e separados, sem heatmap. A matriz (1) esconde fragmentação e clientes nunca sorteados (ficam na diagonal), e o notebook avisa disso.
  - **Smoke test** com uma cópia reduzida (`n = 48`, 6 rodadas, seeds 0 e 1, `k` = 8 e 16, `m` = 100% e 50%, 3 cenários: 24 execuções, ~10 min com a geração dos dados): 15 células sem erro, 12 figuras, I5 do plano (cobertura do log = chaves de `psi.pkl`) em 24 de 24, e segunda execução reaproveitando as 24. Os gráficos foram conferidos só pela estrutura, não visualmente (sem `kaleido`). Os artefatos do teste (dados e logs de `n` = 8, 40 e 48) foram apagados, e os de `n = 240` não foram tocados.
  - **Verificação feita antes de escrever o notebook:** `--process 0` e `--process 1` dão a mesma sequência de clientes sorteados (conferido com `n = 40`), então gerar os dados só quando faltam, como no notebook de `m`, não altera o sorteio.
- **Alternativas consideradas:**
  - Executar a grade completa agora: descartada pelo usuário ("rode o smoke test").
  - Grade do plano (`m` = 100%, 50% e 10% × `d` = 0,1 e 0,2) ou só `m = 50%`: descartadas pelo usuário em favor de `m` = 100% e 50% e `d` = 0,05 e 0,1.
  - `k = 4` com `τ = 0,625` (centro da janela) e `τ = 0,9`: recomendada por Claude a primeira e descartadas as duas pelo usuário em favor de `k` = 8 e 16 com `τ = 0,75`.
  - Gerar os dados com uma execução de `--com_round 0`: descartada, porque `--process` não altera o sorteio.
  - Apagar o `psi.pkl` por padrão: descartada, para não mudar o que o usuário vê em disco sem pedir.
  - Heatmap da matriz de pares 2×2: descartada, porque a tabela de resumo já traz os pares misturados e separados.
  - Reaproveitar sem checar o `τ`, como o notebook de `m`: descartada, porque esse notebook usa um `τ` por vez, e aqui o mesmo nome de pasta já abriga execuções de `τ` diferentes (0,9 e 0,75).

## D-036: Célula do `teste-dropout.ipynb` que grava os resultados em JSON

- **Data:** 2026-11-09
- **Decidido por:** o usuário pediu "quando acabar salva os resultados em um json", sem dizer onde nem o quê. Claude decidiu, por serem escolhas triviais e reversíveis, o local, o conteúdo e a forma.
- **Situação:** vigente. Acrescenta uma seção ao notebook de [D-035](#d-035-notebook-teste-dropoutipynb-cenários-matrizes-de-confusão-e-smoke-test), sem mudar os cenários.
- **Contexto:** a grade completa (120 execuções, D-035) estava rodando em segundo plano, e o usuário quis os resultados num arquivo para analisar fora do notebook.
- **Decisão:**
  - Uma célula final (seção 7) grava `projetos/StoCFL/logs/resultados-dropout.json`, ao lado do `busca-tau.json`. O `logs/` é ignorado pelo git, então o JSON **não é versionado**, e o commit leva só a célula.
  - O JSON é estrito (`allow_nan=False`; `NaN` vira `null`) e tem `parametros`, `execucoes` (métricas finais, a pasta de logs e `rotulos`, o cluster de cada cliente na partição final), `por_rodada`, `resumo`, `comparacao` (dropout − sem dropout com Wilcoxon) e `matrizes_grupo_real_x_previsto` (somadas nas seeds). Com os `rotulos` e as seeds dá para recalcular as matrizes e o ARI sem os logs.
  - Para isso, o notebook passou a guardar a tabela de Wilcoxon em `comparacao` e as matrizes somadas em `matrizes_soma`. Nada mais nas células anteriores mudou.
  - A célula foi testada fora do notebook sobre 3 execuções reais já concluídas (seed 0, `k = 8`, `m = 100%`), enquanto a grade rodava, e depois vai rodar sobre a grade completa, reaproveitando as execuções. Editar o arquivo do notebook não afetou a grade em andamento, que usa a cópia carregada na memória do `nbclient`.
- **Alternativas consideradas:**
  - Script avulso fora do repositório: descartada, porque o resultado não seria reproduzível pelo usuário.
  - Versionar o JSON (por exemplo em `docs/`): descartada por ora, porque não foi pedido e é um resultado de execução; pode ser feito depois se o usuário quiser.
  - Um CSV por tabela: descartada, porque o usuário pediu um JSON e as tabelas têm formatos diferentes.
  - Gravar só o resumo: descartada, porque sem as métricas por rodada e os rótulos finais não dá para refazer os gráficos nem as matrizes.
