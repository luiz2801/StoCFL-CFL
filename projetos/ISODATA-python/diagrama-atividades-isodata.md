# Diagrama de atividades: ISODATA

Fluxo de `ISODATA-python/`, a partir de `main.py` e de `doISODATAGray` / `doISODATARGB` em `ISODATAKit.py`. O algoritmo classifica os pixels de uma imagem em clusters, dividindo clusters dispersos e fundindo clusters próximos, até atingir o número máximo de iterações `I`.

## Diagrama

```mermaid
flowchart TD
    classDef cli fill:#eef2f7,stroke:#5b7083,color:#16232a
    classDef core fill:#e1effd,stroke:#2e6fb7,color:#16232a
    classDef split fill:#d6efeb,stroke:#09766e,stroke-width:2px,color:#16232a
    classDef merge fill:#fff1d6,stroke:#b9770e,stroke-width:2px,color:#16232a
    classDef ctl fill:#ffffff,stroke:#5b7083,color:#16232a
    classDef err fill:#fde2e2,stroke:#b42318,color:#16232a
    classDef node0 fill:#16232a,stroke:#16232a,color:#ffffff

    Ini(("Início")):::node0

    %% ---------- Entrada ----------
    A1["Ler argumentos com getopt<br/>padrões: K=3, TN=3, TS=4.0, TC=40, L=10, I=8, NROWS=None"]:::cli
    D0{"opções válidas e<br/>--input e --output definidos?"}:::ctl
    E1["Mostrar erro e ajuda<br/>exit()"]:::err
    D1{"--rgb?"}:::ctl
    A2["Image.open(input)"]:::cli
    A3["Image.open(input).convert('L')"]:::cli

    %% ---------- Inicialização ----------
    B1["Sortear K pixels (ou NROWS, se informado)<br/>como centros iniciais"]:::core

    %% ---------- Iteração ----------
    subgraph IT["a cada iteração"]
        C1["iteração += 1<br/>esvaziar a lista de pixels de cada cluster"]:::core
        C2["Classificar cada pixel no cluster de centro mais próximo<br/>(cinza: |Δ|; RGB: distância euclidiana)"]:::core
        C3["Recalcular cada centro como a média dos seus pixels<br/>(cluster vazio mantém o centro)"]:::core
        C4["Calcular distância média e desvio padrão σ de cada cluster<br/>e a distância média global"]:::core
        C5["Descartar clusters com menos de TN pixels"]:::core
        D2{"iteração #ge; I?"}:::ctl
        D3{"N #le; K/2, ou<br/>(iteração ímpar e N #lt; 2K)?"}:::ctl

        subgraph SP["Divisão, para cada cluster"]
            D4{"σ #gt; TS e<br/>((dist. média #gt; global e n #gt; 2·(TN+1))<br/>ou N #le; K/2)?"}:::split
            S1["Trocar o cluster por dois:<br/>centro + 1 e centro − 1<br/>(RGB: só na componente de maior σ)"]:::split
            S2["Manter o cluster"]:::split
        end

        subgraph MG["Fusão"]
            M1["Listar pares de clusters com<br/>distância entre centros #lt; TC"]:::merge
            M2["Ordenar por distância<br/>e manter os L pares mais próximos"]:::merge
            D5{"A ou B já foi<br/>fundido nesta iteração?"}:::merge
            M3["Pular o par"]:::merge
            M4["Novo centro = média ponderada pelos tamanhos<br/>A recebe o centro, B é removido"]:::merge
        end
    end

    %% ---------- Saída ----------
    F1["Cada pixel recebe o centro arredondado<br/>do seu cluster na imagem de saída"]:::core
    F2["Montar a imagem (L ou RGB)<br/>e exibir com matplotlib"]:::cli
    F3["result.save(output)"]:::cli
    Fim((("Fim"))):::node0

    Ini --> A1 --> D0
    D0 -->|"não"| E1 --> Fim
    D0 -->|"sim"| D1
    D1 -->|"sim"| A2 --> B1
    D1 -->|"não"| A3 --> B1
    B1 --> C1 --> C2 --> C3 --> C4 --> C5 --> D2
    D2 -->|"não"| D3
    D2 -->|"sim"| F1
    D3 -->|"sim"| D4
    D4 -->|"sim"| S1 --> C1
    D4 -->|"não"| S2 --> C1
    D3 -->|"não"| M1 --> M2 --> D5
    D5 -->|"sim"| M3 --> C1
    D5 -->|"não"| M4 --> C1
    F1 --> F2 --> F3 --> Fim

    style IT fill:none,stroke:#586a71,stroke-dasharray:6 4
    style SP fill:none,stroke:#09766e,stroke-dasharray:3 3
    style MG fill:none,stroke:#b9770e,stroke-dasharray:3 3
```

### Legenda

```mermaid
flowchart LR
    classDef cli fill:#eef2f7,stroke:#5b7083,color:#16232a
    classDef core fill:#e1effd,stroke:#2e6fb7,color:#16232a
    classDef split fill:#d6efeb,stroke:#09766e,stroke-width:2px,color:#16232a
    classDef merge fill:#fff1d6,stroke:#b9770e,stroke-width:2px,color:#16232a

    L1["Linha de comando e imagem (main.py, Pillow, matplotlib)"]:::cli
    L2["Núcleo do algoritmo (ISODATAKit)"]:::core
    L3["Divisão de clusters"]:::split
    L4["Fusão de clusters"]:::merge
```

Os retângulos tracejados são repetições (UML: região de expansão): o externo é a iteração, e os internos percorrem os clusters (divisão) ou os pares (fusão). Losangos são decisões. A cor indica a etapa, no lugar das raias, porque o Mermaid não desenha raias de verdade.

## Como o fluxo funciona

- **Parâmetros.** `K` é o número de clusters esperado, `TN` o mínimo de pixels por cluster, `TS` o desvio padrão a partir do qual um cluster pode ser dividido, `TC` a distância abaixo da qual dois clusters podem ser fundidos, `L` o máximo de pares fundidos por iteração e `I` o máximo de iterações.
- **Divisão ou fusão, nunca as duas.** Em cada iteração só um dos dois ramos roda. A divisão acontece quando há poucos clusters (N ≤ K/2) ou em iteração ímpar com N < 2K. Caso contrário roda a fusão.
- **Divisão.** O cluster é substituído por dois centros deslocados em ±1. Na imagem RGB o deslocamento é só na componente de maior desvio padrão. Os pixels voltam a ser distribuídos na classificação da iteração seguinte.
- **Fusão.** Só os `L` pares mais próximos com distância menor que `TC` entram. Um cluster que já participou de uma fusão na iteração não é fundido de novo.
- **Parada.** O laço só termina por `iteração ≥ I`, depois do descarte por `TN` e antes da divisão e da fusão. Não há teste de convergência. Os pixels dos clusters descartados nessa última passada ficam com valor 0 na saída.
- **Saída.** Cada pixel vira o centro arredondado do seu cluster. A janela do matplotlib precisa ser fechada antes de o arquivo ser gravado.
