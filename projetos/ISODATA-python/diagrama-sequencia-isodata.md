# Diagrama de sequência: ISODATA

Troca de mensagens entre o usuário, `main.py`, o Pillow, o `ISODATAKit.py` e o matplotlib durante uma execução de `python main.py --input ... --output ...`. O diagrama segue o caminho em tons de cinza (`doISODATAGray`), que é o padrão. O caminho RGB (`--rgb`, `doISODATARGB`) tem a mesma ordem de mensagens; as diferenças estão na tabela ao final.

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant M as main.py
    participant P as Pillow (Image)
    participant K as ISODATAKit
    participant CL as Cluster / Pixel
    participant G as matplotlib

    U->>M: python main.py --input --output [--K --TN --TS --TC --L --I --NROWS]
    M->>M: getopt, valores padrão: K=3, TN=3, TS=4.0, TC=40, L=10, I=8, NROWS=None

    alt opção inválida, sem opções ou sem --input / --output
        M-->>U: mensagem de erro e texto de ajuda
        Note over M: exit()
    else parâmetros válidos
        M->>P: Image.open(input).convert("L")
        P-->>M: image
        M->>K: doISODATAGray(image, K, TN, TS, TC, L, I, NROWS)

        Note over K,CL: Inicialização
        K->>K: numpy.array(image), sortear K (ou NROWS) posições
        K->>CL: Cluster(valor do pixel sorteado) para cada posição

        Note over K,CL: Iterações (até iteração = I, sem teste de convergência)
        loop a cada iteração
            K->>CL: pixelList.clear() em cada cluster

            loop para cada pixel da imagem
                K->>CL: centro mais próximo, |cor − centro|
                K->>CL: pixelList.append(Pixel(x, y, cor))
            end

            K->>CL: centro ← média das cores do cluster
            Note right of CL: cluster vazio mantém o centro
            K->>CL: distância média e desvio padrão de cada cluster
            CL-->>K: aveDistanceList, sdList, aveDistanceAll

            K->>K: descartar clusters com menos de TN pixels

            alt iteração ≥ I
                Note over K: sai do laço, sem dividir nem fundir
            else N ≤ K/2, ou iteração ímpar e N < 2K
                Note over K,CL: Divisão
                loop para cada cluster i
                    opt σ > TS e ((dist. média > global e n > 2·(TN+1)) ou N ≤ K/2)
                        K->>CL: substituir i por Cluster(centro + 1)
                        K->>CL: acrescentar Cluster(centro − 1)
                    end
                end
            else
                Note over K,CL: Fusão
                K->>CL: listar pares com distância entre centros < TC
                K->>K: ordenar e manter os L pares mais próximos
                loop para cada par (A, B)
                    opt nem A nem B foram fundidos nesta iteração
                        K->>CL: A ← Cluster(média dos centros ponderada por nA e nB)
                        K->>CL: marcar B para remoção
                    end
                end
                K->>CL: remover os clusters B marcados
            end
        end

        Note over K,CL: Geração da imagem
        K->>CL: ler pixelList e centro de cada cluster
        K->>K: newImgArray[x, y] ← round(centro)
        K-->>M: Image.fromarray(newImgArray, "L")

        M->>G: figure("Result"), imshow(result, cmap="gray"), show()
        G-->>U: janela com a imagem classificada
        U->>G: fechar a janela
        M->>P: result.save(output)
        P-->>U: arquivo de saída
    end
```

## Pontos de atenção

- **`show()` antes de `save()`.** `plot.show()` bloqueia até o usuário fechar a janela, e só depois `result.save(outputFilename)` grava o arquivo. Num ambiente sem interface gráfica o arquivo só sai se o backend do matplotlib não bloquear.
- **Parada só por contagem.** O laço termina quando `iterationCount >= I`. Não existe teste de convergência: se os centros se estabilizam na iteração 3, as iterações 4 a 8 ainda rodam.
- **Última iteração.** O `break` vem depois do descarte por `TN` e antes da divisão e da fusão. Os pixels de um cluster descartado nessa última passada não pertencem a nenhum cluster, e na imagem de saída ficam com valor 0.
- **Divisão e fusão alternam.** A divisão só roda com poucos clusters (N ≤ K/2) ou em iteração ímpar com N < 2K. Em iteração par, ou com N ≥ 2K, roda a fusão.
- **Tudo em Python puro.** A classificação percorre cada pixel e cada centro em laços aninhados, por isso o README do projeto avisa que a execução é muito lenta.

## Diferenças do caminho RGB

| Etapa | Tons de cinza (`doISODATAGray`) | RGB (`doISODATARGB`) |
|---|---|---|
| Abertura | `Image.open(input).convert("L")` | `Image.open(input)` |
| Centro | número (float) | vetor `[R, G, B]` |
| Distância | `abs(cor − centro)` | euclidiana nas três componentes |
| Desvio padrão | um valor por cluster | um valor por componente; vale o maior |
| Divisão | `centro + 1` e `centro − 1` | `±1` só na componente de maior desvio |
| Exibição | `imshow(result, cmap="gray")` | `imshow(result)` |
