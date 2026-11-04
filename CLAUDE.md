# CLAUDE.md

Instruções para o Claude Code neste repositório. Valem para a raiz e para todos os subprojetos em `projetos/`.

## Políticas obrigatórias

### 1. Consultar a documentação antes de alterar algo

Antes de editar qualquer arquivo de código, configuração ou documentação, leia a documentação relevante:

- O `README.md` da raiz e o `README.md` do subprojeto afetado.
- O [guia técnico](docs/guia.md), nas seções que descrevem a função, o módulo ou o fluxo que será alterado. Os bugs conhecidos (seções 3.7 e 4.12) devem ser lidos antes de mexer no CFL ou no StoCFL. Para o ISODATA, consulte o [guia técnico do ISODATA](docs/implementar/guia-tecnico-isodata.md).
- Os diagramas do algoritmo afetado, que descrevem o fluxo e a troca de mensagens do código:
  - CFL: [diagrama-atividades-cfl.md](projetos/clustered-federated-learning/diagrama-atividades-cfl.md) e [diagrama-sequencia-cfl.md](projetos/clustered-federated-learning/diagrama-sequencia-cfl.md)
  - StoCFL: [diagrama-atividades-stocfl.md](projetos/StoCFL/diagrama-atividades-stocfl.md) e [diagrama-sequencia-stocfl.md](projetos/StoCFL/diagrama-sequencia-stocfl.md)
  - ISODATA: [diagrama-atividades-isodata.md](projetos/ISODATA-python/diagrama-atividades-isodata.md) e [diagrama-sequencia-isodata.md](projetos/ISODATA-python/diagrama-sequencia-isodata.md)
- O README de [docs/](docs/README.md) e de [projetos/](projetos/README.md), quando a mudança afetar a organização do repositório.

Se o código e um diagrama divergirem, a divergência deve ser apontada antes de qualquer alteração.

Se a documentação estiver em conflito com o código, diga isso explicitamente antes de alterar o código e registre a divergência no guia.

### 2. Atualizar a documentação assim que uma nova implementação for feita

Toda implementação nova (função, módulo, script, flag de CLI, notebook, dependência, correção de bug ou mudança de comportamento) deve ser refletida na documentação na mesma tarefa, sem esperar um pedido separado. Isso inclui:

- Atualizar o [guia técnico](docs/guia.md) quando a mudança afetar funções, fluxo de execução, variáveis, bugs conhecidos, como rodar ou a correspondência entre código e artigo.
- Atualizar o `README.md` do subprojeto e, se necessário, o `README.md` da raiz (tabela de projetos, situação, ambiente).
- Atualizar os diagramas de atividades e de sequência do algoritmo afetado quando o fluxo, as etapas, as trocas de mensagem ou as decisões mudarem. Os diagramas são arquivos Mermaid, então confira a sintaxe depois de editar.
- Remover ou corrigir a documentação que ficou obsoleta por causa da mudança. Não deixe duas descrições contraditórias.
- Quando um bug listado em "bugs conhecidos" for corrigido, atualize ou remova a entrada correspondente e a linha de situação no README da raiz.

Uma tarefa só está concluída depois que a documentação foi atualizada.

### 3. Relatar o que foi feito na documentação

Na mensagem final, diga quais arquivos de documentação foram lidos antes da mudança e quais foram atualizados depois dela.

### 4. Perguntar antes de decidir

Quando uma decisão precisar ser tomada, pergunte ao usuário antes de implementar. Isso vale para escolhas de design, de biblioteca, de estrutura de arquivos, de comportamento do algoritmo, de versão de dependência e para qualquer caso que o pedido não cubra. Use a ferramenta de pergunta com as opções possíveis, marcando a recomendada.

Só decida sozinho quando a escolha for trivial e reversível e não afetar o comportamento dos algoritmos, e então diga na mensagem final que a escolha foi feita.

### 5. Registrar cada decisão em `docs/decisoes.md`

Toda decisão tomada, seja pelo usuário em resposta a uma pergunta, seja por você em um caso trivial, deve ser registrada em [docs/decisoes.md](docs/decisoes.md) no mesmo momento. O registro inclui:

- A decisão tomada e quem a tomou.
- O contexto e o motivo.
- As alternativas consideradas, inclusive as que foram descartadas, com o motivo de cada descarte.
- A data.

Não apague decisões antigas. Se uma decisão for revista, registre a nova decisão e marque a anterior como substituída.

### 6. Fazer commits atômicos ao concluir cada tarefa

Ao terminar uma tarefa que alterou arquivos, faça os commits no repositório da raiz sem esperar um pedido separado. Isso vale para código, documentação e configuração.

- **Atômico:** cada commit contém uma única mudança lógica que pode ser entendida e revertida sozinha. Não misture mudanças sem relação, e separe, por exemplo, uma correção de bug, uma nova funcionalidade e uma reorganização de arquivos.
- **Código e documentação juntos:** a mudança e a atualização da documentação que ela exige (política 2) e o registro em `docs/decisoes.md` (política 5) entram no mesmo commit, para que cada commit deixe o repositório consistente.
- **Mensagem:** em português, com título curto no imperativo e um corpo que explique o quê e por quê. Termine com a linha de coautoria indicada pelo ambiente.
- **Antes de commitar:** rode `git status` e `git diff`. Adicione os arquivos por nome, não use `git add -A`, e não commite alterações que você não fez sem antes perguntar ao usuário. Não commite saídas de execução, como o output de células de notebook com erro, nem o `.venv/`.
- **Limites:** o commit é local. **Não faça `git push`**, não reescreva o histórico (`reset`, `rebase`, `amend`, `push --force`) e não descarte alterações (`checkout`, `restore`, `clean`) sem pedido do usuário.
- **Relato:** na mensagem final (política 3), liste os commits criados.

## Estrutura de referência

- `docs/`: artigos (PDF) e o guia técnico `guia.md`.
- `projetos/clustered-federated-learning/`: CFL (notebook Jupyter).
- `projetos/StoCFL/`: StoCFL (scripts CLI, FedLab).
- `projetos/ISODATA-python/`: ISODATA em linha de comando.

O repositório git é **um só, na raiz** (`cfl_stocfl/`). Os subprojetos não têm `.git` próprio: o histórico original deles foi removido (D-008 em [docs/decisoes.md](docs/decisoes.md)). Commits e `git status` valem para o repositório inteiro, inclusive `docs/` e `projetos/`. A branch é `main` e não há remote configurado.
