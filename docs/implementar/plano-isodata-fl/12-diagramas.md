# 12. Diagramas

> **Status:** proposta, nada implementado. Descrevem a configuração recomendada, com partida configurável e participação total. Quando o subprojeto existir, os diagramas de atividades e de sequência passam para `projetos/ISODATA-FL/`, como exige a política 1 do [CLAUDE.md](../../../CLAUDE.md). Substituem, se aprovados, os da [proposta anterior](../diagramas-isodata-fl.md).

## 12.1 Atividades de uma rodada

```mermaid
flowchart TD
    classDef sv fill:#e1effd,stroke:#2e6fb7,color:#16232a
    classDef cl fill:#eef2f7,stroke:#5b7083,color:#16232a
    classDef split fill:#d6efeb,stroke:#09766e,stroke-width:2px,color:#16232a
    classDef merge fill:#fff1d6,stroke:#b9770e,stroke-width:2px,color:#16232a
    classDef ctl fill:#ffffff,stroke:#5b7083,color:#16232a
    classDef node0 fill:#16232a,stroke:#16232a,color:#ffffff

    Ini(("Início")):::node0
    P0{"partida?"}:::ctl
    P1["1 cluster com todos os clientes<br/>modelo = θ0"]:::sv
    P2["Componentes do grafo cos(ψ) #ge; τ<br/>todos com modelo = θ0"]:::sv

    subgraph RT["a cada rodada t"]
        T0["Calendário de t: SPLIT, MERGE ou NADA<br/>NADA nas últimas F rodadas"]:::sv
        A1["Definir os participantes<br/>v1: todos. Depois: censo dos candidatos"]:::sv
        A2["Cliente sem ψ: observar a partir da âncora<br/>uma vez por cliente"]:::cl
        A3["Treino local a partir do modelo do cluster<br/>cada cliente devolve ΔW"]:::cl
        A4["Monitorar por cluster, em toda rodada<br/>mean_norm, max_norm, persistência"]:::sv
        D1{"ação = SPLIT?"}:::ctl

        subgraph SP["Split, para cada cluster"]
            S1{"Porte suficiente, mean_norm #lt; ε1<br/>por p rodadas e max_norm #gt; ε2?"}:::split
            S2["Cossenos entre os ΔW<br/>agrupar até restarem 2 grupos"]:::split
            S3{"Filhos com o tamanho mínimo, γ_max aprovado<br/>e par liberado para separar?"}:::split
            S4["Trocar o cluster pelos dois filhos<br/>registrar a evidência e iniciar a espera para reunir"]:::split
            S5["Manter o cluster<br/>registrar a recusa e o motivo"]:::split
        end

        A5["Agregar: FedAvg por cluster na partição atual<br/>cada filho recebe só a média dos seus membros"]:::sv
        D2{"ação = MERGE?"}:::ctl

        subgraph MG["Merge, até L pares"]
            M1["Centros: média de ψ dos membros observados<br/>pares em ordem decrescente de cosseno"]:::merge
            M2{"Há par com cos #ge; τ, idade mínima,<br/>liberado e ainda não fundido nesta janela?"}:::merge
            M3["Candidato: θm = média ponderada dos modelos<br/>membros avaliam θm na validação: ΔL"]:::merge
            M4{"ΔL #le; δ?"}:::merge
            M5["Fundir: modelo = θm, id = menor cliente<br/>registrar e iniciar a espera para separar"]:::merge
            M6["Manter separados<br/>registrar e aumentar a espera do reteste"]:::merge
        end

        A6["Registrar a rodada"]:::sv
    end

    D3{"t #lt; R_max?"}:::ctl
    Fim((("Fim"))):::node0

    Ini --> P0
    P0 -->|"única"| P1 --> T0
    P0 -->|"por ψ"| P2 --> T0
    T0 --> A1 --> A2 --> A3 --> A4 --> D1
    D1 -->|"sim"| S1
    D1 -->|"não"| A5
    S1 -->|"sim"| S2 --> S3
    S1 -->|"não"| S5
    S3 -->|"sim"| S4 --> A5
    S3 -->|"não"| S5 --> A5
    A5 --> D2
    D2 -->|"sim"| M1 --> M2
    D2 -->|"não"| A6
    M2 -->|"sim"| M3 --> M4
    M2 -->|"não"| A6
    M4 -->|"sim"| M5 --> M2
    M4 -->|"não"| M6 --> M2
    A6 --> D3
    D3 -->|"sim: t + 1"| T0
    D3 -->|"não"| Fim

    style RT fill:none,stroke:#586a71,stroke-dasharray:6 4
    style SP fill:none,stroke:#09766e,stroke-dasharray:3 3
    style MG fill:none,stroke:#b9770e,stroke-dasharray:3 3
```

### Legenda

```mermaid
flowchart LR
    classDef sv fill:#e1effd,stroke:#2e6fb7,color:#16232a
    classDef cl fill:#eef2f7,stroke:#5b7083,color:#16232a
    classDef split fill:#d6efeb,stroke:#09766e,stroke-width:2px,color:#16232a
    classDef merge fill:#fff1d6,stroke:#b9770e,stroke-width:2px,color:#16232a

    L1["Servidor"]:::sv
    L2["Clientes"]:::cl
    L3["Operador de split (CFL)"]:::split
    L4["Operador de merge (StoCFL)"]:::merge
```

Os retângulos tracejados são repetições. Losangos são decisões. Para simplificar, o diagrama mostra uma seta entre o split e a agregação, mas o laço do split percorre todos os clusters elegíveis antes de agregar.

## 12.2 Sequência de uma rodada

```mermaid
sequenceDiagram
    autonumber
    participant Cal as Calendário
    participant S as Servidor
    participant E as Estabilidade
    participant C as Clientes
    participant R as Registro

    Note over S,C: Partida: 1 cluster ou partição por ψ

    loop a cada rodada t
        S->>Cal: acao(t, estado)
        Cal-->>S: SPLIT, MERGE ou NADA
        S->>C: modelo do cluster de cada participante
        opt cliente sem ψ
            S->>C: âncora
            C-->>S: ψ do cliente, uma vez
        end
        C->>C: treino local
        C-->>S: ΔW
        S->>S: normas e persistência por cluster

        opt ação = SPLIT
            loop cada cluster elegível
                S->>S: cossenos e bipartição (c1, c2)
                S->>E: pode_separar(c1, c2, t)
                E-->>S: resposta
                alt γ_max aprovado e par liberado
                    S->>E: registrar_split(c1, c2, t)
                    S->>R: split com normas e α_cross
                else recusa
                    S->>R: motivo da recusa
                end
            end
        end

        S->>S: FedAvg por cluster, na partição atual

        opt ação = MERGE
            S->>S: centros de ψ e pares com cos ≥ τ
            loop até L pares, cada cluster uma vez
                S->>E: pode_unir(a, b, t)
                E-->>S: resposta
                opt par liberado
                    S->>C: θm para avaliar nos membros de a e b
                    C-->>S: perda de validação em θm e no modelo atual
                    alt ΔL ≤ δ
                        S->>S: fundir, modelo = θm
                        S->>E: registrar_merge(a, b, t)
                        S->>R: merge com cos ψ e ΔL
                    else reprovado
                        S->>E: aumentar a espera do reteste
                        S->>R: reprovação com ΔL
                    end
                end
            end
        end

        S->>R: estado da rodada
    end
```

### Mensagens a mais em relação ao FedAvg

| Mensagem | Quantas vezes | Custo |
|---|---|---|
| `ψ` | Uma por cliente. Gratuita se a rodada 1 for aproveitada | 1 download e 1 upload de modelo |
| Avaliação de `θm` | Só em merges testados, limitados pela espera crescente | 1 download por cliente testado, e 2 números de upload |
| Censo (Fase 9) | Só em clusters candidatos, nas janelas de split | Treino normal, em clientes que não seriam sorteados |

O split não acrescenta nenhuma mensagem: usa os mesmos `ΔW` que o FedAvg já envia.

## 12.3 Estados de um par de grupos de clientes

O que o [módulo de estabilidade](05-estabilidade.md) controla, do ponto de vista de dois grupos que podem estar juntos ou separados:

```mermaid
stateDiagram-v2
    [*] --> Juntos
    Juntos --> EsperaParaReunir: split aprovado
    EsperaParaReunir --> Candidatos: espera e idade vencidas
    Candidatos --> EmTeste: janela de merge com cos ψ ≥ τ
    EmTeste --> EsperaParaReunir: ΔL acima de δ, espera maior
    EmTeste --> EsperaParaSeparar: ΔL até δ, fundidos
    EsperaParaSeparar --> Juntos: espera vencida
    Juntos --> [*]: fim do treino
    Candidatos --> [*]: fim do treino
```

Cada volta completa no ciclo dobra a espera, o que limita o número de voltas ([05](05-estabilidade.md), seção 5.4).

## 12.4 Como os módulos se ligam

```mermaid
flowchart TD
    N["nucleo<br/>laço do ISODATA"]
    Cal["calendario"]
    Sp["split_cfl"]
    Mg["merge_stocfl"]
    Es["estabilidade"]
    Si["similaridade"]
    Pa["participacao"]
    Et["estado"]
    Tr["treino"]
    Da["dados"]
    Re["registro"]
    Px["adaptadores/pixels"]

    N --> Cal
    N --> Sp
    N --> Mg
    N --> Pa
    N --> Re
    Px --> N
    Sp --> Si
    Mg --> Si
    Sp --> Es
    Mg --> Es
    Sp --> Et
    Mg --> Et
    Es --> Et
    Pa --> Tr
    Pa --> Et
    Tr --> Da
```

O split e o merge não se conhecem: toda interação entre eles passa por `estabilidade` e `estado`.
