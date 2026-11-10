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

### Dropout com retorno (opcional)

O `StoCFL-FCC+CFL.py` aceita `--drop` e `--drop_rounds`, que tornam os clientes **indisponíveis por algumas rodadas**: a cada rodada, um cliente disponível cai com probabilidade `--drop` e fica fora de 1 a `--drop_rounds` rodadas (duração sorteada uniformemente), e depois volta. Quem está fora não é sorteado, e os `--num_per_round` clientes são sorteados só entre os disponíveis (se houver menos, participam todos; se não houver nenhum, a rodada é pulada). Com `--drop 0` (padrão), o comportamento é o de sempre. Os outros dois scripts ainda não têm essas flags. Detalhes no [guia técnico](../../docs/guia.md) (seções 4.1, 4.8 e 4.11) e no [plano](../../docs/plano-dropout-stocfl.md).

```
python StoCFL-FCC+CFL.py --n 240 \
                         --k 4 \
                         --dataset mnist \
                         --com_round 50 \
                         --num_per_round 120 \
                         --train 0 \
                         --tau 0.9 \
                         --seed 0 \
                         --process 1 \
                         --drop 0.1 \
                         --drop_rounds 10
```

A execução grava, além dos arquivos de sempre, o `availability.pkl` (indisponíveis por rodada) e a linha `unavailable` no log, e a pasta de logs ganha `-drop0.1-r10` no nome.

## Testes

### Módulo de disponibilidade (`--drop`)

Os testes unitários do [availability.py](availability.py) rodam sem GPU, a partir desta pasta e com o `.venv` da raiz:

```
../../.venv/bin/python -m unittest tests/test_availability.py -v
```

### Efeito do dropout na clusterização

O notebook [teste-dropout.ipynb](teste-dropout.ipynb) compara a clusterização (`StoCFL-FCC+CFL.py --train 0`) **sem dropout** e **com dropout** (`--drop` = 0.05 e 0.1, `--drop_rounds 10`, ou seja, ausências de 1 a 10 rodadas) em Rotated MNIST com `n = 240`, 50 rodadas, `τ = 0.75` e 10 seeds (0 a 9), para `m` = 100% e 50% e `k` = 8 e 16 grupos reais (D-035). Ele chama o script por `subprocess`, sem alterar o código do StoCFL, lê o `cluster.pkl`, o `availability.pkl` e o log de cada execução e mostra, em gráficos interativos do Plotly: o nº de clusters, o ARI, a cobertura e os participantes por rodada (média e faixa mín–máx entre as seeds), a distribuição do resultado final por seed, **matrizes de confusão** (grupo real × grupo previsto somada nas seeds, e cluster × grupo real por seed) e a diferença dropout − sem dropout por seed com o teste de Wilcoxon.

- Use o kernel `.venv` da raiz (ver o [README da raiz](../../README.md#ambiente)) e abra o notebook a partir desta pasta.
- A grade completa são **120 execuções** (2 `k` × 2 `m` × 3 cenários × 10 seeds): cada uma grava `psi.pkl` (~1,6 GB) a cada rodada em `logs/` (~190 GB no total), e as partições de dados ocupam ~1,8 GB (`k = 8`) e ~3,6 GB (`k = 16`) por seed (~54 GB). A célula de execução confere o espaço livre antes de começar, e `APAGAR_PSI = True` apaga o `psi.pkl` de cada execução concluída (a análise não o usa). Reduza `SEEDS`, `KS`, `FRACOES` ou `DROPS` para uma grade menor.
- Execuções concluídas com os mesmos parâmetros, **inclusive `τ`** (lido da linha de argumentos do log, já que o nome da pasta não o traz), são reaproveitadas, a menos que `REEXECUTAR = True`. As execuções sem dropout do notebook de `m` (`τ = 0.9`) não são reaproveitadas.
- `τ = 0.75` fica na borda inferior da janela de `k = 16` no [relatório de m, k e τ](../../docs/relatorio-m-k-tau.md): algumas seeds poderiam fundir grupos vizinhos, com e sem dropout. O notebook mostra isso (`seeds_colapso`, matrizes de confusão). Na execução de 2026-11-09, nenhuma das 10 seeds colapsou.
- **Resultado da execução de 2026-11-09** (120 execuções, 205 min): o ARI final foi 1,0 e o nº de clusters foi `k` em todas, com e sem dropout, então o dropout só **atrasou** a rodada estável (que é a 1ª rodada com cobertura de 100%): de 1 para ~11 com `m` = 100% e de ~10 para ~14 com `m` = 50%. A grade não mostra se o dropout piora a partição final, porque em 50 rodadas todo cliente foi observado. Números e limites no [guia](../../docs/guia.md), seção 4.11 (D-037).
- A última célula grava `logs/resultados-dropout.json` com os parâmetros, as métricas finais e por rodada de cada execução (com a partição final), as tabelas de resumo e as matrizes de confusão somadas nas seeds. Como `logs/` é ignorado pelo git, o JSON não é versionado.
- `datasets/rotated_*/` e `logs/` são ignorados pelo git. O notebook é versionado **sem saídas de execução**.

### Efeito da fração de clientes por rodada (m)

O notebook [teste-fracao-clientes.ipynb](teste-fracao-clientes.ipynb) roda a clusterização (`StoCFL-FCC+CFL.py --train 0`) em Rotated MNIST com `n = 240` e 50 rodadas, com `τ = 0.9`, variando `m` em 100%, 50%, 25%, 10% e 5% (240, 120, 60, 24 e 12 clientes por rodada) e o nº de grupos reais `k` em `KS = [4, 8, 16]` (D-029). Ele chama o script por `subprocess`, sem alterar o código do StoCFL, lê o `cluster.pkl` de cada execução e mostra, em gráficos interativos do Plotly, por rodada, o nº de clusters, o ARI e a pureza contra os grupos reais e a fração de clientes já observados, além da rodada em que a partição para de mudar.

- Use o kernel `.venv` da raiz (ver o [README da raiz](../../README.md#ambiente)) e abra o notebook a partir desta pasta.
- Na primeira execução, o MNIST é baixado em `datasets/mnist/` e as partições rotacionadas são gravadas em `datasets/rotated_mnist_240_<seed>/` (`k = 4`) e `datasets/rotated_mnist_240_<seed>_k<k>/` (outros `k`) (~900 MB por seed e por `k`).
- Cada execução grava `psi.pkl` (~1,6 GB com 240 clientes) a cada rodada em `logs/`. Execuções concluídas são reaproveitadas, a menos que `REEXECUTAR = True`.
- `datasets/mnist/`, `datasets/rotated_*/` e `logs/` são ignorados pelo git.

### Busca de τ

A seção 5 do mesmo notebook procura o `τ` que melhor recupera os `k` grupos reais (o gabarito), para cada `k` de `TAU_KS` (por padrão, `KS`) e `m` = 100%, 25% e 10%. Ela roda uma varredura grossa em `τ` = 0.05, 0.25, 0.5, 0.75 e 1.0 e depois até 6 bisseções: a cada passo avalia o ponto médio do maior intervalo entre a borda do conjunto de `τ` com maior ARI final e o vizinho avaliado, parando se o intervalo ficar menor que 0.005. Mostra o intervalo ótimo, o `τ` sugerido (centro do intervalo) e gráficos de nº de clusters (escala log, porque vai de 1 a 200), ARI e pureza em função de `τ`, com uma faixa de fundo no intervalo ótimo de cada `m` (D-028).

- Cada `τ` é uma execução do script com `--tau` diferente (~1,6 GB em `logs/` cada; até 11 execuções por par `k`, `m`, ou seja, até 99 execuções e ~160 GB com `KS = [4, 8, 16]`: reduza `TAU_KS` ou `TAU_FRACOES` se faltar espaço). Os resultados ficam em `logs/busca-tau.json`, e reexecutar a célula reaproveita o que já foi rodado.
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