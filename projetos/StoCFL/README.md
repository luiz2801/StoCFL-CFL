# Stochastic-Clustered-Federated-Learning

> **Modificado neste repositório.** O código original foi corrigido para seguir o texto do artigo: modelo global por FedAvg, `Ψ` como gradiente normalizado na âncora, centro do cluster com todos os membros, modelos de cluster em `ω₀` e limiar estrito. **Com isso, os resultados ficam abaixo das tabelas publicadas**, que parecem ter vindo do código original. Os detalhes estão no [guia técnico](../../docs/guia.md), seções 4.12 e 4.16.


## Prepare

> pip install -r requirements.txt

## Run

### Stochastic federated client clusetering procedure (FCC)

```
python StoCFL-FCC.py --com_round 100 \
                     --num_per_round 20 \
                     --batch_size 50 \
                     --lr 0.1 \
                     --epochs 20 \
                     --mu 0.1 \
                     --tau 0.5 \
                     --setting fskewed \
                     --k 4 \
                     --process 1
```

### Bi-level clustered federated learning (CFL)

```
python StoCFL-FCC+CFL.py --n 200 \
                         --com_round 200 \
                         --num_per_round 20 \
                         --batch_size 50 \
                         --lr 0.1 \
                         --epochs 5 \
                         --mu 0.05 \
                         --tau 0.5 \
                         --seed 0 \
                         --dataset cifar \
                         --process 1 
```

## Testes

### Efeito da fração de clientes por rodada (m)

O notebook [teste-fracao-clientes.ipynb](teste-fracao-clientes.ipynb) roda a clusterização (`StoCFL-FCC+CFL.py --train 0`) em Rotated MNIST com `n = 200` e 50 rodadas, com `τ = 0.9`, variando `m` em 100%, 50%, 25%, 10% e 5% (200, 100, 50, 20 e 10 clientes por rodada). Ele chama o script por `subprocess`, sem alterar o código do StoCFL, lê o `cluster.pkl` de cada execução e mostra, em gráficos interativos do Plotly, por rodada, o nº de clusters, o ARI e a pureza contra os grupos reais e a fração de clientes já observados, além da rodada em que a partição para de mudar.

- Use o kernel `.venv` da raiz (ver o [README da raiz](../../README.md#ambiente)) e abra o notebook a partir desta pasta.
- Na primeira execução, o MNIST é baixado em `datasets/mnist/` e as partições rotacionadas são gravadas em `datasets/rotated_mnist_200_<seed>/` (~750 MB por seed).
- Cada execução grava `psi.pkl` (~1,3 GB com 200 clientes) a cada rodada em `logs/`. Execuções concluídas são reaproveitadas, a menos que `REEXECUTAR = True`.
- `datasets/mnist/`, `datasets/rotated_*/` e `logs/` são ignorados pelo git.

### Busca de τ

A seção 5 do mesmo notebook procura o `τ` que melhor recupera os `k = 4` grupos reais (o gabarito), para `m` = 100%, 25% e 10%. Ela roda uma varredura grossa em `τ` = 0.05, 0.25, 0.5, 0.75 e 1.0 e depois até 6 bisseções: a cada passo avalia o ponto médio do maior intervalo entre a borda do conjunto de `τ` com maior ARI final e o vizinho avaliado, parando se o intervalo ficar menor que 0.005. Mostra o intervalo ótimo, o `τ` sugerido (centro do intervalo) e gráficos de nº de clusters, ARI e pureza em função de `τ`.

- Cada `τ` é uma execução do script com `--tau` diferente (~1,3 GB em `logs/` cada; até 11 execuções por `m`). Os resultados ficam em `logs/busca-tau.json`, e reexecutar a célula reaproveita o que já foi rodado.
- Só a primeira seed (`SEEDS[0]`) é usada. A varredura e a bisseção supõem que o ARI varia de forma razoavelmente suave em `τ`, o que vale para uma seed, mas pode não valer entre seeds.

## Citation

If you find this repo helpful to your research, please cite our paper:
```
@article{zeng2023stochastic,
  title={Stochastic clustered federated learning},
  author={Zeng, Dun and Hu, Xiangjing and Liu, Shiyu and Yu, Yue and Wang, Qifan and Xu, Zenglin},
  journal={arXiv preprint arXiv:2303.00897},
  year={2023}
}
```