# Guia Técnico: ISODATA (Classificador de Imagens)

Este guia documenta tecnicamente o subprojeto [`projetos/ISODATA-python/`](../../projetos/ISODATA-python/), explicando o algoritmo de Ball & Hall (1965), as funções implementadas, os parâmetros de linha de comando, os fluxos internos, as limitações e os bugs conhecidos.

Fluxo e troca de mensagens: [diagrama de atividades](../../projetos/ISODATA-python/diagrama-atividades-isodata.md) e [diagrama de sequência](../../projetos/ISODATA-python/diagrama-sequencia-isodata.md). Artigo original: [isodata.pdf](../../isodata.pdf). Verificado contra o código e o artigo em 2026-11-04.

---

## 1. Visão Geral do Algoritmo ISODATA

O **ISODATA** (*Iterative Self-Organizing Data Analysis Technique*) é um algoritmo de agrupamento iterativo não-supervisionado. Diferente do K-Means convencional (que mantém fixo o número de clusters $K$), o ISODATA ajusta dinamicamente a quantidade de clusters através de três operações fundamentais:
1. **Descarte:** eliminação de clusters com número de amostras inferior a um limiar ($TN$).
2. **Divisão (*Split*):** partição de clusters com dispersão interna excessiva (desvio padrão $\sigma > TS$) em dois subclusters.
3. **Fusão (*Merge*):** união de pares de clusters cujos centros estejam excessivamente próximos (distância inter-centro $< TC$).

---

## 2. Estrutura do Código e Arquivos

O subprojeto é composto por dois scripts principais:

| Arquivo | Função principal |
|---|---|
| [`main.py`](../../projetos/ISODATA-python/main.py) | Ponto de entrada CLI: parse de argumentos (`getopt`), abertura de imagem (Pillow), despacho para modo Gray/RGB e salvamento/exibição. |
| [`ISODATAKit.py`](../../projetos/ISODATA-python/ISODATAKit.py) | Núcleo do algoritmo: estruturas de dados (`Pixel`, `Cluster`, `ClusterPair`) e loops de iteração (`doISODATAGray`, `doISODATARGB`). |

---

## 3. Mapeamento de Classes e Funções

### 3.1 Classes Internas (`ISODATAKit.py`)
* **`Pixel(initX, initY, initColor)`**: Armazena as coordenadas espaciais `(x, y)` e a intensidade escalar (cinza) ou vetor de cores `[R, G, B]`.
* **`Cluster(initCenter)`**: Mantém o centro atual do cluster (`float` para cinza, `np.ndarray` 3-D para RGB) e a lista `pixelList` com os pixels atribuídos na iteração corrente.
* **`ClusterPair(initClusterAIndex, initClusterBIndex, initDistance)`**: Representa um par de clusters candidato à fusão, armazenando seus índices e a distância euclidiana entre seus centros.

### 3.2 Funções de Execução

#### `doISODATAGray(image, K, TN, TS, TC, L, I, NROWS=None)`
Executa o ISODATA para imagens em escala de cinza (canal único $L \in [0, 255]$).
1. **Inicialização:** Sorteia $K$ pixels aleatórios como centros iniciais (ou $NROWS$ se fornecido).
2. **Loop de Classificação:** Para cada pixel, calcula a distância absoluta $|x_p - c_k|$ e o associa ao cluster mais próximo.
3. **Recálculo de Centros:** Média aritmética dos tons de cinza dos pixels atribuídos.
4. **Cálculo Estatístico:** Calcula o desvio padrão $\sigma_k$ e a distância média intra-cluster $\bar{d}_k$, bem como a distância média global $\bar{D}$.
5. **Poda ($TN$):** Descarta clusters com $|pixelList| < TN$.
6. **Alternância Split/Merge:**
   * Se $N_{clusters} \le K/2$ ou (iteração ímpar e $N_{clusters} < 2K$): tenta **Split**.
   * Caso contrário: tenta **Merge**.
7. **Reconstrução:** Substitui cada pixel pelo valor arredondado do centro do seu cluster final.

#### `doISODATARGB(image, K, TN, TS, TC, L, I, NROWS=None)`
Executa o ISODATA em 3 canais (RGB).
* A distância entre cores é a distância euclidiana no espaço tridimensional:
  $$\text{dist}(c_A, c_B) = \sqrt{(R_A - R_B)^2 + (G_A - G_B)^2 + (B_A - B_B)^2}$$
* **Variação no Split:** No modo RGB, o desvio padrão $\sigma_{k, j}$ é medido separadamente para cada componente $j \in \{R, G, B\}$. A divisão ocorre apenas ao longo do eixo de maior desvio padrão ($\max_j \sigma_{k, j}$), aplicando um deslocamento de $\pm 1$ naquela componente.

---

## 4. Hiperparâmetros do ISODATA

| Parâmetro CLI | Notação do Artigo | Padrão | Descrição |
|---|---|---|---|
| `--K` | $K$ | `3` | Número de clusters desejado (meta). |
| `--TN` | $\theta_N$ | `3` | Número mínimo de amostras para manter um cluster ativo. |
| `--TS` | $\theta_S$ | `4.0` | Limiar de desvio padrão para disparar a divisão (*Split*). |
| `--TC` | $\theta_C$ | `40` | Limiar de distância inter-centro para permitir fusão (*Merge*). |
| `--L` | $L$ | `10` | Quantidade máxima de pares que podem ser fundidos por iteração. |
| `--I` | $I$ | `8` | Número máximo de iterações permitidas. |
| `--NROWS` | $k_0$ | $K$ | Número de clusters na inicialização. |
| `--rgb` | - | Flag | Processa em modo RGB (3 canais). |
| `--gray` | - | Flag | Processa em escala de cinza (padrão). |

---

## 5. Condições Lógicas de Split e Merge

### 5.1 Critério de Divisão (*Split*)
Um cluster $k$ é dividido em dois novos centros $c_k^+ = c_k + 1$ e $c_k^- = c_k - 1$ se:
1. $\sigma_k > TS$; **E**
2. Uma das duas condições for satisfeita:
   - $(\bar{d}_k > \bar{D} \quad \text{e} \quad N_k > 2(TN + 1))$
   - $N_{clusters} \le K / 2$

### 5.2 Critério de Fusão (*Merge*)
Pares de clusters $(i, j)$ com $D_{ij} = \|c_i - c_j\| < TC$ são candidatos.
1. Ordena-se os pares candidatos por ordem crescente de distância.
2. Seleciona-se no máximo os $L$ pares mais próximos.
3. Cada cluster só pode ser fundido uma vez por iteração.
4. O novo centro fundido é a média ponderada pelo número de amostras:
   $$c_{\text{novo}} = \frac{N_i c_i + N_j c_j}{N_i + N_j}$$

---

## 6. Bugs Conhecidos e Limitações Práticas

1. **Complexidade Algorítmica e Desempenho Crítico:**
   * O código implementa laços aninhados explícitos em Python puro (`for row in range... for col in range... for i in range...`) para cada iteração e pixel.
   * Não utiliza vetorização do NumPy nem aceleração GPU/multiprocessamento.
   * Complexidade por iteração: $\mathcal{O}(H \times W \times K)$, tornando o script extremamente lento para imagens maiores que $200 \times 200$ pixels.
2. **Deslocamento Fixo no Split ($\pm 1$):**
   * O código soma $+1$ e subtrai $1$ do centro para gerar os novos centros no split (no RGB, apenas da componente de maior desvio padrão). Isso **segue o artigo** de Ball & Hall (1965), que descreve exatamente esse passo e diz que a quantidade somada é arbitrária, desde que seja suficiente para produzir diferenças detectáveis na distância dos padrões aos dois centros e não seja grande a ponto de alterar outras fronteiras. Um deslocamento proporcional ao desvio padrão não faz parte do artigo nem do código.
   * Limitação real: o $\pm 1$ depende da escala dos dados. Em pixels de 8 bits é razoável, mas em variáveis com outra faixa de valores pode ser pequeno ou grande demais. Isso é relevante para qualquer adaptação a outros espaços (ver [especificação do ISODATA-FL](especificacao-isodata-fl.md)).
3. **Métrica Euclidiana no Espaço RGB:**
   * Como apontado no próprio repositório original, a distância euclidiana simples no espaço RGB não reflete a percepção de cor humana nem variações de iluminação/sombras. A conversão para espaços perceptuais (como CIELAB ou HSV/HSI) produz agrupamentos visuais muito mais homogêneos.
4. **Parada apenas por contagem de iterações:**
   * O laço termina somente quando `iterationCount >= I`. Não há teste de convergência: se os centros se estabilizam na iteração 3, as iterações 4 a 8 ainda rodam.
5. **Pixels pretos na saída:**
   * O descarte por $TN$ vem antes do `break` da última iteração. Os pixels dos clusters descartados nessa passada não pertencem a nenhum cluster e ficam com valor 0 (preto) na imagem de saída.
6. **`show()` antes de `save()`:**
   * Em `main.py`, `plot.show()` bloqueia até o usuário fechar a janela, e só depois `result.save()` grava o arquivo. Em ambiente sem interface gráfica o arquivo só é gravado se o backend do matplotlib não bloquear. O `matplotlib` é dependência obrigatória mesmo que a janela não seja desejada.
7. **Ramo de opção inválida em `main.py` é código morto e está errado:**
   * [`main.py:104`](../../projetos/ISODATA-python/main.py) usa `"...{opt}...".format(opt)`, que levantaria `KeyError` (campo nomeado com argumento posicional), além das barras invertidas antes das crases. Na prática o ramo não é alcançado, porque o `getopt` já rejeita opções desconhecidas com `GetoptError`.
8. **Divisão por zero possível com `--TN 0`:**
   * Com $TN = 0$, clusters vazios não são descartados. Se dois clusters vazios (que mantêm o centro antigo) tiverem centros a menos de $TC$, a fusão calcula $(n_A c_A + n_B c_B)/(n_A + n_B)$ com $n_A = n_B = 0$. Identificado na leitura do código; não foi executado.

> Os mesmos pontos 4 e 5 estão nos [diagramas do ISODATA](../../projetos/ISODATA-python/diagrama-sequencia-isodata.md), que seguem o código.

