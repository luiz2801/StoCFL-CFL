# Diagramas de Atividades e Sequência: Framework ISODATA-FL

Este documento apresenta os diagramas que descrevem o fluxo operacional e o protocolo de comunicação entre Servidor e Clientes para a execução do algoritmo híbrido **ISODATA-FL**.

> **Status: proposta, nada implementado.** Os diagramas seguem a [especificação](especificacao-isodata-fl.md) e herdam seus problemas em aberto (seção 5 dela), em especial a métrica do merge, o papel de $K_{\text{alvo}}$ e a participação parcial. Os diagramas devem ser revisados quando esses pontos forem decididos. Os diagramas do código existente estão em [`projetos/ISODATA-python/`](../../projetos/ISODATA-python/).
>
> **Diagramas mais recentes:** [plano modular, módulo 12](plano-isodata-fl/12-diagramas.md). Eles trocam a paridade por um calendário, acrescentam a verificação no merge e fazem o split **antes** da agregação, como o CFL do notebook. Os diagramas abaixo agregam antes de decidir o split, o que diverge do CFL.

---

## 1. Diagrama de Atividades: Ciclo de uma Rodada Federada

O diagrama abaixo detalha a lógica de decisão executada a cada rodada de comunicação federada, incorporando as etapas adaptativas de *Split* e *Merge*.

```mermaid
flowchart TD
    classDef init fill:#16232a,stroke:#16232a,color:#ffffff
    classDef client fill:#eef2f7,stroke:#5b7083,color:#16232a
    classDef server fill:#e1effd,stroke:#2e6fb7,color:#16232a
    classDef split fill:#d6efeb,stroke:#09766e,stroke-width:2px,color:#16232a
    classDef merge fill:#fff1d6,stroke:#b9770e,stroke-width:2px,color:#16232a
    classDef cond fill:#ffffff,stroke:#5b7083,color:#16232a

    Start(("Início da Rodada t")):::init
    
    subgraph LocalTraining["Fase Local nos Clientes"]
        S1["Servidor distribui pesos dos clusters W_k aos respectivos clientes"]:::server
        C1["Clientes amostrados executam E épocas de SGD local"]:::client
        C2["Clientes calculam ΔW_i = W_local - W_cluster e enviam ao Servidor"]:::client
    end

    subgraph Aggregation["Agregação de Pesos"]
        A1["Servidor calcula dW_médio e norma máxima por cluster"]:::server
        A2["Agregação FedAvg: W_k = W_k + média(ΔW_i)"]:::server
    end

    subgraph Dynamics["Dinâmica Adaptativa ISODATA-FL"]
        D1{"Rodada t é par ou ímpar?"}:::cond
        
        %% Ramo de Split (Iteração Ímpar)
        subgraph SplitBranch["Verificação de Split (Rodadas Ímpares)"]
            S_C1{"Cluster k atende:<br/>norma_média < EPS_1 e<br/>(norma_max > EPS_2 ou σ > TS) e<br/>|C_k| > 2·(TN + 1)?"}:::cond
            SP1["Bipartição dos membros do cluster via afinidade angular"]:::split
            SP2["Criar dois clusters filhos:<br/>C_k1 e C_k2 herdando W_k"]:::split
            SP3["Manter cluster inalterado"]:::split
        end

        %% Ramo de Merge (Iteração Par)
        subgraph MergeBranch["Verificação de Merge (Rodadas Pares)"]
            M_C1["Calcular a similaridade entre todos os pares de clusters (j, k)<br/>métrica EM ABERTO: ver especificação, seção 5"]:::server
            M_C2{"Existe par com similaridade #ge; τ_FL?<br/>(equivale a distância angular < TC_FL)"}:::cond
            MG1["Ordenar pares candidatos e selecionar até L_FL pares"]:::merge
            MG2["Fundir modelos:<br/>W_novo = (N_j·W_j + N_k·W_k)/(N_j + N_k)<br/>Unificar membros dos clusters"]:::merge
            MG3["Nenhuma fusão realizada"]:::merge
        end
    end

    CheckEnd{"t #ge; R_max?"}:::cond
    End(("Fim do Treinamento")):::init

    Start --> S1 --> C1 --> C2 --> A1 --> A2 --> D1
    D1 -->|"Ímpar (Split)"| S_C1
    S_C1 -->|"Sim"| SP1 --> SP2 --> CheckEnd
    S_C1 -->|"Não"| SP3 --> CheckEnd
    
    D1 -->|"Par (Merge)"| M_C1 --> M_C2
    M_C2 -->|"Sim"| MG1 --> MG2 --> CheckEnd
    M_C2 -->|"Não"| MG3 --> CheckEnd

    CheckEnd -->|"Não: t = t + 1"| Start
    CheckEnd -->|"Sim"| End
```

---

## 2. Diagrama de Sequência: Troca de Mensagens (Downlink / Uplink)

O diagrama a seguir exibe as interações de rede (simuladas) entre a entidade coordenadora (`Servidor`) e os dispositivos descentralizados (`Clientes`).

```mermaid
sequenceDiagram
    autonumber
    actor S as Servidor Central (ISODATA-FL)
    actor C1 as Clientes Grupo A (Cluster 1)
    actor C2 as Clientes Grupo B (Cluster 2)

    Note over S: Inicialização com 1 ou K modelos W_k
    
    loop A cada rodada federada t
        S->>C1: Downlink: Envia W_1 corrente
        S->>C2: Downlink: Envia W_2 corrente
        
        activate C1
        Note over C1: Treinamento SGD local (E épocas)
        C1->>S: Uplink: Envia vetor de atualização ΔW_A
        deactivate C1

        activate C2
        Note over C2: Treinamento SGD local (E épocas)
        C2->>S: Uplink: Envia vetor de atualização ΔW_B
        deactivate C2

        Note over S: 1. Agrega pesos locais (FedAvg por cluster)
        Note over S: 2. Avalia critério de alternância (Split vs Merge)
        
        Note over S: Na rodada ímpar só o Split é avaliado e na par só o Merge (alternância por paridade)
        alt Condição de Split atendida em Cluster 1
            Note over S: Particiona membros de Cluster 1 em 1a e 1b
            Note over S: Duplica W_1 para W_1a e W_1b
        else Condição de Merge atendida entre Cluster 1 e Cluster 2
            Note over S: Calcula W_fusão = média ponderada(W_1, W_2)
            Note over S: Unifica clusters em único conjunto de clientes
        end
        
        Note over S: Avalia acurácia de validação e estacionariedade
    end
```

---

## 3. Invariantes e Regras de Estabilidade

Para evitar oscilações numéricas e divergências estocásticas durante o treinamento de redes neurais profundas, o agente implementador deve assegurar os seguintes invariantes:

1. **Histerese e Alternância Rígida:** Não executar *Split* e *Merge* na mesma rodada de comunicação. O `ISODATAKit.py` alterna por paridade da iteração, mas com exceções: split forçado quando $N \le K/2$ e merge forçado quando $N \ge 2K$. Esses desvios não estão nos diagramas acima (problema 2 da [especificação](especificacao-isodata-fl.md), seção 5).
2. **Período de Carência (*Warm-up*):** Não disparar operações de *Split* antes de um número mínimo de rodadas (valor ilustrativo, ex.: $t > 15$; o notebook do CFL usa 20 e `ε1`/`ε2` precisam ser calibrados junto, ver [guia, seção 3.5](../guia.md)). Clientes no início do treinamento possuem gradientes ruidosos com magnitude elevada que simulam falsas incongruências.
3. **Id do Cluster Normalizado:** Seguir a convenção do StoCFL, onde o identificador de um cluster unificado é sempre indexado pelo menor ID de cliente membro, preservando a coerência na serialização e nos logs.
4. **Invariantes do StoCFL a revisar:** o [guia, seção 4.5](../guia.md) estabelece que o número de clusters é não crescente e que `unite` só trata fusões. Um split viola o primeiro e exige tratar o id dos clusters filhos. Isso não está resolvido nos diagramas (problema 7 da especificação).

