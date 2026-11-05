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

O notebook [teste-fracao-clientes.ipynb](teste-fracao-clientes.ipynb) roda a clusterização (`StoCFL-FCC+CFL.py --train 0`) em Rotated MNIST com `n = 200` e 50 rodadas, variando `m` em 100%, 50%, 25% e 10% (200, 100, 50 e 20 clientes por rodada). Ele chama o script por `subprocess`, sem alterar o código do StoCFL, lê o `cluster.pkl` de cada execução e mostra, por rodada, o nº de clusters, o ARI e a pureza contra os grupos reais e a fração de clientes já observados, além da rodada em que a partição para de mudar.

- Use o kernel `.venv` da raiz (ver o [README da raiz](../../README.md#ambiente)) e abra o notebook a partir desta pasta.
- Na primeira execução, o MNIST é baixado em `datasets/mnist/` e as partições rotacionadas são gravadas em `datasets/rotated_mnist_200_<seed>/` (~750 MB por seed).
- Cada execução grava `psi.pkl` (~1,3 GB com 200 clientes) a cada rodada em `logs/`. Execuções concluídas são reaproveitadas, a menos que `REEXECUTAR = True`.
- `datasets/mnist/`, `datasets/rotated_*/` e `logs/` são ignorados pelo git.

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