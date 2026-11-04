# Diagnóstico Crítico: Políticas e Documentação vs. Escopo do Projeto

Este documento apresenta a análise crítica detalhada da aderência entre as políticas de governança, a documentação existente e o escopo do repositório `cfl_stocfl`.

---

## 1. Contexto e Escopo Declarado

Conforme definido no [README.md](../../README.md), o repositório foi concebido para abranger duas frentes de pesquisa:
1. **Aprendizado Federado com Clusterização de Clientes (*Clustered Federated Learning*):** abordando dados não-IID através das implementações de CFL (Sattler et al., divisivo) e StoCFL (Zeng et al., aglomerativo).
2. **Classificação de Imagens com ISODATA:** implementação do algoritmo clássico de Ball & Hall (1965) em Python para classificação de pixels em imagens comuns e sensoriamento remoto.

**Objetivo de convergência futuro:** Utilizar a dinâmica adaptativa do algoritmo ISODATA (capacidade simultânea de divisão (*split*) e fusão (*merge*) de clusters) como base para aprimorar ou unificar os frameworks de CFL e StoCFL.

---

## 2. Crítica às Políticas Obrigatórias ([CLAUDE.md](../../CLAUDE.md))

O arquivo de instruções [`CLAUDE.md`](../../CLAUDE.md) estabelece cinco políticas obrigatórias. A avaliação de cada uma em relação ao escopo revela pontos fortes, mas também inconsistências operacionais graves.

### 2.1 Política 1: Consultar a documentação antes de alterar algo
* **Avaliação positiva:** Excelente para CFL e StoCFL, onde o [guia técnico](../../docs/guia.md) mapeia detalhadamente linhas de código, bugs conhecidos e referências dos artigos.
* **Inconsistência identificada (resolvida):** A política instruía a consultar o guia técnico (`docs/guia.md`) nas seções da função a alterar, mas **o `guia.md` não tem nenhuma seção sobre o ISODATA**. A versão atual do [CLAUDE.md](../../CLAUDE.md) já resolve isso: manda consultar o [guia técnico do ISODATA](guia-tecnico-isodata.md) e os diagramas do ISODATA.
* **Impacto residual:** Assimetria de governança. CFL e StoCFL têm suas seções no `guia.md`, e o ISODATA tem um guia separado. O `guia.md` não aponta para ele.

### 2.2 Política 2: Atualizar a documentação assim que uma nova implementação for feita
* **Avaliação positiva:** Garante que o repositório não acumule débitos técnicos documentais e mantém diagramas Mermaid sincronizados com o código.
* **Lacuna identificada:** Não prevê o processo de unificação entre subprojetos. Se um novo módulo híbrido for criado (por exemplo, `ISODATA-FL`), não há regra pré-definida sobre em qual subprojeto ele residirá ou se deve ser criado um novo subprojeto em `projetos/`.

### 2.3 Política 3: Relatar o que foi feito na documentação
* **Avaliação positiva:** Promove transparência e facilidade de auditoria para o usuário e para outros agentes.

### 2.4 Política 4: Perguntar antes de decidir
* **Avaliação positiva:** Previne refatorações destrutivas ou escolhas de bibliotecas conflitantes (como introduzir dependências incompatíveis com o `fedlab==1.2.1` no StoCFL).

### 2.5 Política 5: Registrar cada decisão em `docs/decisoes.md`
* **Avaliação positiva:** Preserva o histórico arquitetural (ADR - *Architecture Decision Records*).

---

## 3. Crítica à Documentação Existente

### 3.1 [docs/guia.md](../../docs/guia.md)
* **Pontos fortes:** Documento de excepcional qualidade técnica para CFL e StoCFL. Detalha nuances de implementação (ex.: tensores vivos em `client.W` vs serialização 1-D no FedLab; divergência de *linkage* completo vs simples).
* **Falha:** Omite completamente o ISODATA. Não há menção ao algoritmo de Ball & Hall, aos parâmetros $K, TN, TS, TC, L, I$, ou ao arquivo `ISODATAKit.py`. O conteúdo foi coberto por [guia-tecnico-isodata.md](guia-tecnico-isodata.md), mas o `guia.md` não faz referência a ele.
* **Ausência de ponte teórica:** Não há nenhuma discussão preliminar sobre como transpor conceitos de agrupamento de pixels para agrupamento de pesos em redes neurais.

### 3.2 Subprojeto [projetos/ISODATA-python/](../../projetos/ISODATA-python/)
* **`README.md` inadequado:** O [`README.md`](../../projetos/ISODATA-python/README.md) encontra-se integralmente em chinês, mantendo o texto do repositório upstream de Lucka. Não explica sua relevância para o projeto `cfl_stocfl` nem fornece instruções em português alinhadas ao restante do repositório.
* **Diagramas Mermaid:** Positivamente, os arquivos [`diagrama-atividades-isodata.md`](../../projetos/ISODATA-python/diagrama-atividades-isodata.md) e [`diagrama-sequencia-isodata.md`](../../projetos/ISODATA-python/diagrama-sequencia-isodata.md) foram criados em português e estão corretos em relação ao código de `ISODATAKit.py`.

### 3.3 Organização de Arquivos e Artigos
* **Arquivo PDF solto na raiz:** O artigo original [`isodata.pdf`](../../isodata.pdf) (Ball & Hall, 1965) está localizado na raiz do repositório, enquanto os artigos do CFL e StoCFL estão centralizados em [`docs/`](../../docs/).
* **Desatualização do índice `docs/README.md` (corrigida):** a tabela omitia o artigo do ISODATA. Agora há uma linha que aponta para `../isodata.pdf`, enquanto o arquivo continuar na raiz.

---

## 4. Matriz de Severidade das Críticas

A coluna "Situação" foi atualizada em 2026-11-04. Nenhuma das ações pendentes foi executada: o repositório está em fase de planejamento e as mudanças estruturais (mover arquivos, traduzir README) ficam para depois, conforme a decisão D-005 em [decisoes.md](../decisoes.md).

| Item | Componente afetado | Severidade | Impacto para agentes e humanos | Ação recomendada | Situação |
|---|---|---|---|---|---|
| Ausência do ISODATA no Guia | `docs/guia.md` | **Alta** | Agente não possui referências de código/bugs do ISODATA | Criar guia técnico dedicado ou seção no `guia.md` | **Atenuada.** O guia dedicado existe em [guia-tecnico-isodata.md](guia-tecnico-isodata.md) e o `CLAUDE.md` aponta para ele. O `guia.md` continua sem mencionar o ISODATA. |
| `README` em idioma incompatível | `projetos/ISODATA-python/README.md` | **Média** | Dificulta compreensão e padronização do projeto | Traduzir e adaptar para português | **Pendente.** |
| Dispersão do artigo `isodata.pdf` | Raiz do repositório | **Baixa** | Desorganização estrutural de arquivos | Mover para `docs/` e atualizar links | **Pendente.** Hoje o PDF é citado por [README.md](../../README.md) e [projetos/README.md](../../projetos/README.md), e o [docs/README.md](../README.md) aponta para ele na raiz. |
| Ambiguidade no `CLAUDE.md` | `CLAUDE.md` (Política 1) | **Média** | Agente busca seções inexistentes antes de alterar ISODATA | Atualizar política referenciando a documentação do ISODATA | **Resolvida.** A Política 1 já cita o guia técnico e os diagramas do ISODATA. |
| Falta de especificação para ISODATA-FL | Repositório global | **Crítica** | Agente não sabe como integrar ISODATA com FL | Criar guias e diagramas conceituais específicos | **Atenuada.** Os documentos existem, mas a [especificação](especificacao-isodata-fl.md) tem problemas em aberto (seção 5 dela) que precisam ser resolvidos antes de qualquer implementação. |

