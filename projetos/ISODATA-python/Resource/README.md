# Resource

Imagens usadas no README principal do [ISODATA-python](../README.md): exemplos de entrada e saída do classificador e fórmulas renderizadas.

## Exemplos de entrada e saída

| Entrada | Saída | Parâmetros | Resultado |
|---|---|---|---|
| `T.png` | `T1.png` | `K=4`, `TN=3`, `TS=4.0`, `TC=40`, `L=10`, `I=8` | 4 iterações, 4 classes |
| `TC.png` | `TC1.png` | `K=4`, `TN=3`, `TS=2.0`, `TC=100`, `L=10`, `I=8` | 6 iterações, 4 classes |

Os nomes com `TC` são o segundo teste, com parâmetros diferentes.

## Imagem de sensoriamento remoto

| Arquivo | Descrição |
|---|---|
| `ETM.jpg`, `ETM.png` | Imagem de satélite de sensor ETM, usada no teste com dados reais. O objetivo era 4 classes, e o resultado teve 5, com erro de classificação no centro do rio, a jusante. A imagem vem de um mestrado em sensoriamento remoto da UCL, citado no README principal. |

## Fórmulas (SVG)

Renderizações em LaTeX, usadas no README para mostrar parâmetros e a fórmula da distância de cor:

| Arquivo | Conteúdo |
|---|---|
| `LaTeX_K_=_4,_L_=_10,_I_=_8.svg` | Parâmetros `K`, `L` e `I` do primeiro teste |
| `LaTeX_theta_N_=_3,_theta_S_=_4.0,_theta_C_=_40.svg` | Parâmetros `θN`, `θS` e `θC` do primeiro teste |
| `LaTeX_theta_N_=_3,_theta_S_=_2.0,_theta_C_=_100.svg` | Parâmetros `θN`, `θS` e `θC` do segundo teste |
| `LaTeX_Color_Distance.svg` | Fórmula da distância de cor no RGB usada pelo programa |
