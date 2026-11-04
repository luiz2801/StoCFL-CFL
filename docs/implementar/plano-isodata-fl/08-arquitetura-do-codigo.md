# 8. Arquitetura do código

> **Status:** proposta, nada implementado. Onde divergir da [arquitetura anterior](../arquitetura-componentes-isodata-fl.md), vale este documento, se aprovado. Responde às decisões pendentes da seção 5 daquele documento.
>
> **Depende de:** todos os módulos. **Decisões:** DP-14, DP-16, DP-17.

## 8.1 Princípios

1. **Um laço só.** Nada de uma integração com o notebook e outra com o FedLab.
2. **Lógica pura separada do treino.** Calendário, partição e agrupamento não importam `torch`, para serem testados em milissegundos.
3. **CFL e StoCFL como casos particulares.** A mesma execução, com outra configuração, reproduz cada algoritmo sozinho. Esse é o principal teste de correção.
4. **Nenhum módulo conhece os outros operadores.** O split não sabe que existe merge. As interações passam pelo estado e pela estabilidade.
5. **Os subprojetos existentes não mudam.** Continuam como referência e baseline.

## 8.2 Onde e com o quê (DP-16)

**Recomendação:** novo subprojeto `projetos/ISODATA-FL/`, em Python 3.12, com PyTorch atual, NumPy e `pytest`. Sem FedLab e sem `scikit-learn`. O ambiente tem GPU (`nvidia-smi` lista uma RTX A4000).

| Opção | Sugestão | Justificativa |
|---|---|---|
| **`projetos/ISODATA-FL/`, novo** | **Recomendada** | Segue a organização "um subprojeto por algoritmo" e fecha a lacuna da [crítica](../critica-documentacao-e-politicas.md), seção 2.2 |
| Dentro de `projetos/StoCFL/` | **Descartar** | Herdaria Python 3.8–3.10 e `fedlab==1.2.1` (guia 4.11), além de dependências desnecessárias como `spacy` e `cvxopt` |
| Dentro de `projetos/ISODATA-python/` | **Descartar** | É uma ferramenta de imagem com `Pillow`. Misturaria `torch` nela |
| Dentro de `projetos/clustered-federated-learning/` | **Descartar** | Fluxo de notebook, sem testes nem `requirements.txt` (guia 3.7) |

### Por que não usar o FedLab

Do FedLab, o StoCFL usa essencialmente serialização, média de vetores e fatiamento aleatório, além de classes base e utilitários de log (guia 4.14). Isso são poucas linhas em PyTorch puro (`parameters_to_vector`, `torch.mean`), e não justifica prender o projeto a um pacote de 2022 com incompatibilidades conhecidas.

## 8.3 Estrutura de pastas

```text
projetos/ISODATA-FL/
├── README.md
├── requirements.txt
├── diagrama-atividades-isodata-fl.md    # exigidos pela política 1
├── diagrama-sequencia-isodata-fl.md
├── isodata_fl/
│   ├── nucleo.py          # esqueleto genérico do ISODATA         (doc 01)
│   ├── calendario.py      # primos, pares, paradas, paridade etc. (doc 02)
│   ├── similaridade.py    # cosseno, normas, agrupar()            (docs 03, 04)
│   ├── split_cfl.py       # operador de split                     (doc 03)
│   ├── merge_stocfl.py    # operador de merge                     (doc 04)
│   ├── estabilidade.py    # bloqueios e espera crescente          (doc 05)
│   ├── participacao.py    # amostragem, censo, ψ                  (doc 06)
│   ├── estado.py          # partição, modelos, histórico          (doc 07)
│   ├── treino.py          # treino local sem estado entre rodadas
│   ├── dados.py           # cenários com ground truth             (doc 09)
│   └── registro.py        # eventos por rodada, em JSONL
├── adaptadores/
│   └── pixels.py          # ISODATA de pixels sobre o núcleo
├── experimentos/          # uma configuração por experimento (E0 a E9)
└── testes/
```

Cada módulo corresponde a um documento deste plano, para que implementar e consultar sigam a mesma divisão.

## 8.4 O esqueleto e o oráculo (DP-14)

**Recomendação:** um laço genérico com operadores plugáveis, e um adaptador de pixels que o usa.

```python
# nucleo.py: ilustrativo
class Operadores(Protocol):
    def coletar(self, t, estado): ...        # pixels: classifica e recalcula. FL: treina e colhe ΔW
    def estatisticas(self, t, estado): ...   # pixels: σ, d̄, D̄. FL: normas e persistência
    def podar(self, t, estado): ...          # pixels: descarta < TN. FL: marca clusters pequenos
    def dividir(self, t, estado, stats): ...
    def recalcular(self, t, estado): ...     # pixels: nada. FL: FedAvg por cluster
    def fundir(self, t, estado, stats): ...

def rodar(estado, ops, calendario, R_max):
    for t in range(1, R_max + 1):
        ops.coletar(t, estado)
        stats = ops.estatisticas(t, estado)
        ops.podar(t, estado)
        acao = calendario.acao(t, estado)     # o calendário do ISODATA é uma implementação disto
        if acao == SPLIT:
            ops.dividir(t, estado, stats)
        ops.recalcular(t, estado)
        if acao == MERGE:
            ops.fundir(t, estado, stats)
```

A ordem funciona nos dois casos. No adaptador de pixels, `coletar` já faz classificação e recálculo, e `recalcular` não faz nada, o que preserva a ordem de `ISODATAKit.py`. No FL, o split vem antes da agregação, como no CFL.

| Por quê | Detalhe |
|---|---|
| **Já foi testado** | Um protótipo com 22 linhas de esqueleto e 84 de adaptador reproduziu `ISODATAKit.py` **pixel a pixel em 300 de 300 execuções**, em cinza e RGB, cobrindo split (160), merge (155) e descarte (102). Código no [anexo A](anexo-a-simulacao.md) |
| **Teste determinístico sem GPU** | Com a mesma semente em `random.sample`, o adaptador tem que produzir **a mesma imagem** que `doISODATAGray` e `doISODATARGB` em imagens pequenas |
| **"ISODATA como base" vira uma propriedade testável** | Se o esqueleto reproduz o ISODATA original, é mesmo o ISODATA, e não só inspiração |
| **Calendário original como plugin** | `calendario_isodata(K)` implementa a linha 116 e serve de baseline |

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Laço só para FL, sem adaptador** | **Alternativa simples** | Menos código e sem abstração, mas a relação com o ISODATA fica só no texto, e perde-se o teste rápido sem `torch`. Se o usuário preferir simplicidade, é uma troca aceitável |
| **Refatorar `ISODATAKit.py` para usar o núcleo** | **Descartar** | Alteraria um código que funciona e deixaria de existir o oráculo |
| **Copiar o laço para dentro do notebook** | **Descartar** | Não é testável nem importável |

## 8.5 Interfaces principais

```python
# calendario.py
def acao(t: int, estado) -> Acao                    # SPLIT, MERGE ou NADA

# similaridade.py: sem torch
def agrupar(S: ndarray, parar_quando) -> list[list[int]]

# split_cfl.py
def avaliar_split(membros, delta_w, cfg, estab) -> Divisao | Recusa

# merge_stocfl.py
def candidatos(clusters, psi, cfg, estab) -> list[Par]
def ganho_de_fusao(a, b, theta_m, perda_val) -> float

# estabilidade.py
def pode_unir(a, b, t) -> bool
def pode_separar(c1, c2, t) -> bool
def registrar_split(c1, c2, t): ...
def registrar_merge(a, b, t): ...
```

Os nomes são ilustrativos e podem mudar na implementação.

## 8.6 Reaproveitamento e licenças

Os subprojetos não são importáveis como biblioteca, então o caminho é portar trechos curtos e manter os créditos:

| Fonte | Problema para importar | O que portar |
|---|---|---|
| `StoCFL-FCC+CFL.py` | O nome tem `-` e `+`, e o `StandaloneServer` está triplicado (guia 6) | A lógica de `bucket` e de centros por cluster |
| `trainer.py` | Importa `leaf`, que exige `spacy` (guia 4.11) | `ob_train`, adaptado |
| `datasets.py` | Depende de `fedlab` e relê do disco a cada chamada (guia 4.7) | A receita dos particionadores, com os dados em memória |
| `clustered_federated_learning.ipynb` | É notebook | Só a ideia do cenário e do laço, reescritos a partir do artigo (DP-17) |
| `fl_devices.py` | Importável, mas com pesos vivos e bugs conhecidos | Nada: as fórmulas das normas estão no artigo (DP-17) |
| `ISODATAKit.py` | Não precisa portar | Os testes o usam como oráculo |

> **Pendência de licença (DP-17).** O repositório original do CFL **não declara licença nenhuma**: não tem arquivo `LICENSE`, o README dele não menciona licença e o GitHub não reconhece nenhuma (verificado em 2026-11-04). A informação "MIT" da D-009 ainda precisa de uma fonte. Por isso, a recomendação é não copiar código de `fl_devices.py` e reescrever as fórmulas a partir do artigo, o que quase não custa nada neste plano. Os demais subprojetos têm `LICENSE`, e o aviso deve ser mantido nos trechos portados. A seção "Créditos" do [README](../../../README.md) precisa ser atualizada quando o subprojeto existir.

## 8.7 Testes

Hoje o repositório não tem testes automatizados.

| Nível | O que testa | Precisa de | Fase |
|---|---|---|---|
| Unitário | Calendário, `agrupar`, invariantes de estado, bloqueios | NumPy | 1 |
| Propriedade | Sequências aleatórias de split e merge preservam as invariantes do guia 4.5 | NumPy | 1 |
| Regressão do toy | O [anexo A](anexo-a-simulacao.md) continua reproduzindo seus resultados | NumPy | 1 |
| Oráculo | Adaptador de pixels igual a `ISODATAKit.py` | Pillow | 2 |
| Redução ao FedAvg | Sem operadores, o resultado é o FedAvg | Torch | 3 |
| Redução ao CFL | A configuração do notebook reproduz a separação | Torch | 4 |
| Redução ao StoCFL | Só merge, partida de clientes isolados: mesma partição do `StoCFL-FCC+CFL.py` | Torch | 5 |

## 8.8 Desempenho

| Ponto | Hoje | Proposta |
|---|---|---|
| Dados | StoCFL: `torch.load` do disco a cada chamada; CFL: `DataLoader` por cliente | Tensores na GPU, com índices por cliente |
| Modelos | CFL: um `nn.Module` por cliente | Um `nn.Module` e vetores 1-D |
| `ψ` | `psi.pkl` inteiro salvo a **cada rodada** (1,3 GB com 200 clientes, guia 4.10) | Salvar uma vez e só os novos |
| Cossenos | Laços em Python | Matriz normalizada, só nas janelas |

## 8.9 Problemas e soluções

| ID | Problema | Solução proposta | Justificativa |
|---|---|---|---|
| P-COD-1 | **Os testes de redução precisam dos originais rodando, em ambientes incompatíveis.** O StoCFL pede Python 3.8–3.10 e `fedlab==1.2.1`; o notebook do CFL precisa das correções de compatibilidade; o `.venv` da raiz não serve para nenhum dos dois | Um ambiente descartável para cada original, usado **só para gerar saídas de referência uma vez**. Partições e métricas ficam salvas em JSON, e os testes comparam com esse arquivo | O teste do dia a dia não pode depender de um ambiente de 2022. Guia 3.7, 4.11 e seção 6 |
| P-COD-2 | Os subprojetos não são importáveis | Portar trechos curtos (8.6) | Nome de arquivo com `+`, notebook, importações com efeitos colaterais |
| P-COD-3 | O CFL original não declara licença | Reescrever a partir do artigo, sem copiar, e confirmar a origem do "MIT" (DP-17) | 8.6 |
| P-COD-4 | O repositório não tem testes | Criar a suíte de 8.7 desde a Fase 1 | Sem isso, "reproduz o CFL" fica só na palavra |
| P-COD-5 | Determinismo na GPU não é total | Registrar a semente e a configuração, e comparar partições e tolerâncias, não pesos bit a bit | Partição é o que importa nos testes de redução |
| P-COD-6 | Se os experimentos forem longos, uma falha perde o trabalho | Salvar o estado a cada `n` rodadas, se a Fase 3 mostrar que é necessário | Não vale pagar antes de medir o custo |

## 8.10 Alternativas de arquitetura

| Alternativa | Sugestão | Justificativa |
|---|---|---|
| **Flag `--algorithm isodata_fl` nos scripts do StoCFL** (arquitetura anterior, Fase 4) | **Descartar** | A flag não existe, dois dos três scripts nem importam (guia 4.12), e o servidor está triplicado |
| **`BaseFederatedServer` com duas implementações** (arquitetura anterior) | **Descartar** | A própria arquitetura anterior registra que o código não sustenta essa classe. Um laço único elimina a necessidade |
| **Framework de FL pronto** (Flower e similares) | **Descartar** para a v1 | Tudo é simulação em um processo, e os operadores mexem no estado do servidor o tempo todo. Reconsiderar para execução distribuída real |
| **NumPy em tudo** | **Descartar** | O treino usa PyTorch, e converter vetores grandes a cada rodada custa caro |
| **PyTorch em tudo** | **Descartar** | Obrigaria a instalar `torch` para testar a lógica pura |
| **NumPy na lógica, PyTorch nos vetores** | **Recomendada** | Atende aos princípios 2 e 3. A única fronteira é `matriz_cos`, que devolve um `ndarray` |

## 8.11 Critérios de aceite

- [ ] `pytest testes/unitarios` roda sem `torch` instalado.
- [ ] Nenhum arquivo em `projetos/clustered-federated-learning`, `projetos/StoCFL` ou `projetos/ISODATA-python` foi alterado.
- [ ] O adaptador de pixels reproduz `ISODATAKit.py` em cinza e em RGB.
- [ ] A seção "Créditos" do README da raiz cita os trechos portados.
