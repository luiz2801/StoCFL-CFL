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

### Rótulos non-IID por Dirichlet (opcional)

O `StoCFL-FCC+CFL.py` aceita `--dirichlet_alpha α`, que troca a rotação por **rótulos non-IID**: o MNIST de treino, sem rotação, é dividido entre os `--n` clientes com proporções `Dir(α)` por classe (`hetero_dir_partition` do FedLab, mínimo de 50 amostras por cliente, semeado pela `--seed`), e todo cluster é avaliado no MNIST de teste inteiro. Exige `--dataset mnist` e `--k 1`. Sem a flag, nada muda. Não há grupos reais: o nº de clusters é um resultado, e o `--tau` controla a granularidade. Detalhes no [guia técnico](../../docs/guia.md) (seções 4.7, 4.9 e 4.11) e no [plano](../../docs/plano-dropout-treino-stocfl.md).

```
python StoCFL-FCC+CFL.py --n 240 \
                         --k 1 \
                         --dirichlet_alpha 0.5 \
                         --dataset mnist \
                         --com_round 50 \
                         --num_per_round 120 \
                         --train 1 \
                         --tau 0.8 \
                         --seed 0 \
                         --process 1
```

Os dados vão para `datasets/rotated_mnist_240_0_k1_a0.5/` e a pasta de logs ganha `-k1-a0.5` no nome. Com `--train 1`, o `accuracy.pkl` traz, além da acurácia de cada cluster sorteado e do modelo global, o **recall por classe** no mesmo teste (`cluster_recall` e `global_recall`), em qualquer cenário.

### Divisão pelo CFL (experimental)

O [StoCFL-FCC+CFL-split.py](StoCFL-FCC+CFL-split.py) testa a [hipótese da divisão](../../docs/hipotese-stocfl-divisao-cfl.md): dividir com o CFL de Sattler os clusters que o StoCFL encadeou (D-058). Ele reaproveita o servidor, o trainer e os dados do `StoCFL-FCC+CFL.py`, sem alterá-lo, e acrescenta um passo depois do treino de cada rodada:

1. Nos clusters com algum par de `Ψ` com cosseno ≤ `τ` (clientes que não se uniriam sozinhos), aplica o critério do CFL às atualizações `ΔW` dos membros sobre o modelo do cluster: `‖média ΔW‖ < ε1` e `max ‖ΔW_i‖ > ε2`.
2. Se o critério disparar, divide o cluster pelo Algoritmo 1 do CFL sobre o cosseno dos `ΔW`, desde que `γ_max < √((1 − α_cross^max)/2)`. As partes herdam o modelo do cluster pai.
3. Depois de uma divisão, `--after_split` escolhe o que acontece:
   - `none`: nada, e o StoCFL pode juntar as partes de novo;
   - `reanchor`: o modelo global treinado vira a nova âncora, e o `Ψ` de todos os clientes é recalculado;
   - `cannot_link`: os clientes das duas partes não podem voltar a ficar juntos.

```
python StoCFL-FCC+CFL-split.py --n 40 \
                               --k 4 \
                               --dataset mnist \
                               --com_round 40 \
                               --num_per_round 40 \
                               --train 1 \
                               --tau 0.25 \
                               --seed 0 \
                               --process 1 \
                               --split 1 \
                               --after_split reanchor \
                               --eps1 0.09 \
                               --eps2 0.146 \
                               --gamma_max 0.5
```

- **É experimental:** só rotação (sem `--dirichlet_alpha`), e a divisão exige todos os clientes em toda rodada (`--num_per_round` igual a `--n`, sem `--drop`).
- **`ε1` e `ε2` são normas absolutas** e dependem de lr, épocas, batch e modelo. Os valores acima foram calibrados para `n = 40`, `k = 4`, lr 0.1, 5 épocas e batch cheio, nas execuções com `--split 0` (D-058). A regra do artigo (`ε1` = um décimo da maior norma média) daria 0,033, abaixo do piso de ~0,049 em que a norma média estaciona.
- **`--split 0`** roda o StoCFL sem divisão, com os mesmos sorteios, partições, acurácias e log do `StoCFL-FCC+CFL.py` (conferido), mais os logs extras.
- **Saídas:** grava `cluster.pkl`, `accuracy.pkl`, `cos_rec.log` e `cluster_rec.log`, como o script principal, e mais `accuracy_clients.pkl`, `norms.pkl`, `split_events.pkl` e `psi_cos.pkl` (guia, seção 4.10). Não grava o `psi.pkl`. A pasta de logs é `logs/runs-split-...`, com `τ`, a variante e os segundos no nome.

## Testes

### Módulo de disponibilidade (`--drop`)

Os testes unitários do [availability.py](availability.py) rodam sem GPU, a partir desta pasta e com o `.venv` da raiz:

```
../../.venv/bin/python -m unittest tests/test_availability.py -v
```

### Particionador Dirichlet e recall por classe (`--dirichlet_alpha`)

Os testes do `dirichlet_partition` ([datasets.py](datasets.py)) e do `evaluate_recall` ([functional.py](functional.py)) rodam sem GPU e precisam do MNIST em `datasets/mnist/` (sem ele, os do particionador são pulados):

```
../../.venv/bin/python -m unittest tests/test_dirichlet.py -v
```

### Efeito do dropout na clusterização

O notebook [teste-dropout.ipynb](teste-dropout.ipynb) compara a clusterização (`StoCFL-FCC+CFL.py --train 0`) **sem dropout** e **com dropout** (`--drop` = 0.05 e 0.1, `--drop_rounds 10`, ou seja, ausências de 1 a 10 rodadas) em Rotated MNIST com `n = 240`, 50 rodadas, `τ = 0.75` e 10 seeds (0 a 9), para `m` = 100% e 50% e `k` = 8 e 16 grupos reais (D-035). Ele chama o script por `subprocess`, sem alterar o código do StoCFL, lê o `cluster.pkl`, o `availability.pkl` e o log de cada execução e mostra, em gráficos interativos do Plotly: o nº de clusters, o ARI, a cobertura e os participantes por rodada (média e faixa mín–máx entre as seeds), a distribuição do resultado final por seed, **matrizes de confusão** (grupo real × grupo previsto somada nas seeds, e cluster × grupo real por seed) e a diferença dropout − sem dropout por seed com o teste de Wilcoxon.

- Use o kernel `.venv` da raiz (ver o [README da raiz](../../README.md#ambiente)) e abra o notebook a partir desta pasta.
- A grade completa são **120 execuções** (2 `k` × 2 `m` × 3 cenários × 10 seeds): cada uma grava `psi.pkl` (~1,6 GB) a cada rodada em `logs/` (~190 GB no total), e as partições de dados ocupam ~1,8 GB (`k = 8`) e ~3,6 GB (`k = 16`) por seed (~54 GB). A célula de execução confere o espaço livre antes de começar, e `APAGAR_PSI = True` apaga o `psi.pkl` de cada execução concluída (a análise não o usa). Reduza `SEEDS`, `KS`, `FRACOES` ou `DROPS` para uma grade menor. **As pastas de logs da grade de 2026-11-09 já foram apagadas** (D-039): os dados importantes estão no `resultados-dropout.json`, e `DADOS_JSON = True` replota sem elas.
- Execuções concluídas com os mesmos parâmetros, **inclusive `τ`** (lido da linha de argumentos do log, já que o nome da pasta não o traz), são reaproveitadas, a menos que `REEXECUTAR = True`. As execuções sem dropout do notebook de `m` (`τ = 0.9`) não são reaproveitadas.
- `τ = 0.75` fica na borda inferior da janela de `k = 16` no [relatório de m, k e τ](../../docs/relatorio-m-k-tau.md): algumas seeds poderiam fundir grupos vizinhos, com e sem dropout. O notebook mostra isso (`seeds_colapso`, matrizes de confusão). Na execução de 2026-11-09, nenhuma das 10 seeds colapsou, mas com `k = 16` a margem é pequena: para a seed 0, a borda inferior de `τ`, calculada dos cossenos entre clientes, é 0,7397, só 0,010 abaixo de `τ` (guia, seção 4.11, e [relatório](../../docs/relatorio-m-k-tau.md)).
- **Resultado da execução de 2026-11-09** (120 execuções, 205 min): o ARI final foi 1,0 e o nº de clusters foi `k` em todas, com e sem dropout, então o dropout só **atrasou** a rodada estável (que é a 1ª rodada com cobertura de 100%): de 1 para ~11 com `m` = 100% e de ~10 para ~14 com `m` = 50%. A grade não mostra se o dropout piora a partição final, porque em 50 rodadas todo cliente foi observado. Números e limites no [guia](../../docs/guia.md), seção 4.11 (D-037), e a comparação com a grade com treino no [relatório do dropout](../../docs/relatorio-dropout.md).
- **Para ver os gráficos sem rodar a grade**, abra `logs/teste-dropout-executado.ipynb`: é uma cópia do notebook executada sobre as 120 execuções, com as 12 figuras interativas e as tabelas (ignorada pelo git, como o resto de `logs/`; só para ler, porque as células conferem que estão em `projetos/StoCFL/`). Para refazê-la, execute o notebook desta pasta com todas as células e `DADOS_JSON = True` (célula 1): ele lê o JSON, não precisa dos logs e leva segundos (D-038, D-039).
- A última célula grava `logs/resultados-dropout.json` (~13 MB) com os parâmetros, as métricas finais e por rodada de cada execução, as tabelas de resumo, as matrizes de confusão somadas nas seeds e os **dados brutos de cada execução**, que bastam para replotar sem os logs: o cluster de cada cliente em cada rodada, os clientes sorteados e os indisponíveis por rodada e os cossenos entre os clusters da última rodada. Com `DADOS_JSON = True` o notebook lê esse arquivo no lugar dos logs e não grava nada. Sem as pastas de logs e com o JSON desta grade já gravado, o notebook **para com um aviso** em vez de rodar a grade de novo (`REEXECUTAR = True` força a nova execução). Como `logs/` é ignorado pelo git, a cópia versionada é a compactada em `docs/resultados/resultados-dropout.json.gz` (D-041); para restaurá-lo, `gunzip -c docs/resultados/resultados-dropout.json.gz > projetos/StoCFL/logs/resultados-dropout.json`, a partir da raiz.
- `datasets/rotated_*/` e `logs/` são ignorados pelo git. O notebook é versionado **sem saídas de execução**.

### Cache de lotes do `RotatedMNISTTrainer`

O `RotatedMNISTTrainer` (o do `StoCFL-FCC+CFL.py`) lê o arquivo de cada cliente e de cada teste do disco uma vez por execução e guarda os lotes em memória (`get_batches`), sem mudar nenhum resultado (D-049; guia, seção 4.6). Os testes rodam sem GPU e sem dados:

```
../../.venv/bin/python -m unittest tests/test_trainer_cache.py -v
```

### Efeito do dropout no aprendizado, com rótulos non-IID (Dirichlet)

O notebook [teste-dropout-treino.ipynb](teste-dropout-treino.ipynb) roda o StoCFL completo (`StoCFL-FCC+CFL.py --train 1`) com `--dirichlet_alpha` 0.5 e 1.0, **sem dropout e com `--drop` 0.05 e 0.1** (`--drop_rounds 10`), `m` = 100% e 50%, 10 seeds, 50 rodadas, `n = 240` e `τ` = 0.84683 e 0.8 (240 execuções; D-043 a D-051). Mostra, em Plotly, o nº e o tamanho dos clusters, a acurácia do modelo do cluster e do global (no teste balanceado e ponderada pela distribuição de rótulos do cluster, a partir do recall por classe) e os participantes por rodada, as acurácias separadas entre clusters de um cliente e clusters de 2 ou mais, a distribuição final por seed, a diferença dropout − sem dropout com Wilcoxon e heatmaps cluster × classe.

- Use o kernel `.venv` da raiz e abra o notebook a partir desta pasta. `APAGAR_PSI = True` (padrão) apaga o `psi.pkl` (~1,5 GB) de cada execução concluída.
- Segue a política 7, mas sem cópia no repositório (D-053): grava `logs/resultados-dropout-treino.json.gz` (JSON compactado, fora do git) com os dados brutos; `DADOS_JSON = True` só lê o JSON e plota; sem os logs e com o JSON da grade já gravado, para com um aviso (`REEXECUTAR = True` força).
- **Grade executada de 2026-11-10 a 12** (240 execuções, 22,5 h de GPU; D-052, D-055). O dropout não muda o modelo global e muda menos de meio ponto a acurácia ponderada dos modelos de cluster; ele atrasa a convergência (2 a 7 rodadas com `m` = 100%) e, com `m` = 100%, deixa mais clusters e menores, o que derruba a acurácia do cluster no teste balanceado (até −3,7 pontos) sem mudá-la na distribuição do próprio cluster. Com `α = 0.5`, os modelos de cluster ficam 1,3 a 1,6 ponto acima do global; o ganho vem dos clusters de 2 ou mais clientes, e os singletons não ajudam. Números no [guia](../../docs/guia.md), seção 4.11, e a leitura das duas grades no [relatório do dropout](../../docs/relatorio-dropout.md).
- Os resultados estão em `logs/resultados-dropout-treino.json.gz` (45,6 MB, fora do git, D-053), e os logs da grade foram apagados: `DADOS_JSON = True` replota em segundos, e a cópia executada com as figuras está em `logs/teste-dropout-treino-executado.ipynb`.

### Escolha de τ com rótulos non-IID (Dirichlet)

O notebook [varredura-tau-dirichlet.ipynb](varredura-tau-dirichlet.ipynb) escolhe o `τ` da simulação do dropout com treino (D-046) por **Monte Carlo sobre `τ`**: 400 valores de `τ ~ U[0.3, 1.0]`, cada um na grade inteira (`--dirichlet_alpha` 0.5 e 1.0, seeds 0 a 9, `m` = 100% e 50%, `d` = 0, 0.05 e 0.1, 50 rodadas, `n = 240`). O critério é o maior ARI médio contra um **gabarito construído** (agrupamento Ward das proporções de classes dos clientes, `k` pela silhueta). As simulações usam um simulador da fusão a partir da matriz de cossenos entre os `Ψ` (calculados pelo script real), validado contra 9 execuções reais do script, idênticas em todas as rodadas.

- Use o kernel `.venv` da raiz e abra o notebook a partir desta pasta. A primeira execução gera as partições Dirichlet (`datasets/rotated_mnist_240_<seed>_k1_a<α>/`, 228 MB cada) e leva ~42 min.
- **Resultado de 2026-11-10:** `τ = 0.84683` (ARI médio 0,305), com ~110 clusters e ~82 singletons em média. O gabarito é fraco (silhueta 0,15–0,26, e com `α = 1.0` o `k` bate no limite de 40 em 5 seeds). Números no [guia](../../docs/guia.md), seção 4.11.
- **Sensibilidade ao gabarito** (seção 7, D-050): com outros três gabaritos (Ward com `k` até 80, ligação média com cosseno, `k` fixo em 10), o `τ` de maior ARI fica entre 0,830 e 0,871, e `τ = 0.84683` fica a no máximo 0,014 do ARI máximo de cada um. A seção também mostra o regime do segundo `τ` da grade, 0.8.
- **Os logs foram apagados** (D-046); com `DADOS_JSON = True` (célula 1) o notebook lê `logs/resultados-varredura-tau-dirichlet.json` e replota em segundos. Sem os logs, o modo normal para com um aviso em vez de rodar tudo de novo (`REEXECUTAR = True` força). Cópia versionada: `docs/resultados/resultados-varredura-tau-dirichlet.json.gz` (`gunzip -c ../../docs/resultados/resultados-varredura-tau-dirichlet.json.gz > logs/resultados-varredura-tau-dirichlet.json`, a partir desta pasta).

### Efeito da fração de clientes por rodada (m)

O notebook [teste-fracao-clientes.ipynb](teste-fracao-clientes.ipynb) roda a clusterização (`StoCFL-FCC+CFL.py --train 0`) em Rotated MNIST com `n = 240` e 50 rodadas, com `τ = 0.9`, variando `m` em 100%, 50%, 25%, 10% e 5% (240, 120, 60, 24 e 12 clientes por rodada) e o nº de grupos reais `k` em `KS = [4, 8, 16]` (D-029). Ele chama o script por `subprocess`, sem alterar o código do StoCFL, lê o `cluster.pkl` de cada execução e mostra, em gráficos interativos do Plotly, por rodada, o nº de clusters, o ARI e a pureza contra os grupos reais e a fração de clientes já observados, além da rodada em que a partição para de mudar.

- Use o kernel `.venv` da raiz (ver o [README da raiz](../../README.md#ambiente)) e abra o notebook a partir desta pasta.
- Na primeira execução, o MNIST é baixado em `datasets/mnist/` e as partições rotacionadas são gravadas em `datasets/rotated_mnist_240_<seed>/` (`k = 4`) e `datasets/rotated_mnist_240_<seed>_k<k>/` (outros `k`) (~900 MB por seed e por `k`).
- Cada execução grava `psi.pkl` (~1,6 GB com 240 clientes) a cada rodada em `logs/`. Execuções concluídas são reaproveitadas, a menos que `REEXECUTAR = True`.
- `datasets/mnist/`, `datasets/rotated_*/` e `logs/` são ignorados pelo git.

### Busca de τ

A seção 5 do mesmo notebook procura o `τ` que melhor recupera os `k` grupos reais (o gabarito), para cada `k` de `TAU_KS` (por padrão, `KS`) e `m` = 100%, 25% e 10%. Ela roda uma varredura grossa em `τ` = 0.05, 0.25, 0.5, 0.75 e 1.0 e depois até 6 bisseções: a cada passo avalia o ponto médio do maior intervalo entre a borda do conjunto de `τ` com maior ARI final e o vizinho avaliado, parando se o intervalo ficar menor que 0.005. Mostra o intervalo ótimo, o `τ` sugerido (centro do intervalo) e gráficos de nº de clusters (escala log, porque vai de 1 a 200), ARI e pureza em função de `τ`, com uma faixa de fundo no intervalo ótimo de cada `m` (D-028).

- Cada `τ` é uma execução do script com `--tau` diferente (~1,6 GB em `logs/` cada; até 11 execuções por par `k`, `m`, ou seja, até 99 execuções e ~160 GB com `KS = [4, 8, 16]`: reduza `TAU_KS` ou `TAU_FRACOES` se faltar espaço). Os resultados ficam em `logs/busca-tau.json`, e reexecutar a célula reaproveita o que já foi rodado.
- **Os logs do teste de `m` e da busca de `τ` foram apagados** em 2026-11-10 (153 execuções, ~222 GB; D-040). Os dados importantes estão em `logs/resultados-fracao-clientes.json` (~23 MB; cópia versionada compactada em `docs/resultados/resultados-fracao-clientes.json.gz`, D-041): por execução, os parâmetros, as métricas finais e por rodada, o cluster de cada cliente e os sorteados por rodada e os cossenos; e a matriz de cossenos entre clientes da rodada 0 para cada `n` e `k`, com a qual a janela de `τ` se calcula sem rodar nada. **O notebook ainda não lê esse JSON**, então executar suas células de execução roda tudo de novo (~25 GB o teste de `m`, até ~160 GB a busca de `τ`), e o `logs/busca-tau.json` só tem nomes de pastas que não existem mais.
- Só a primeira seed (`SEEDS[0]`) é usada. A varredura e a bisseção supõem que o ARI varia de forma razoavelmente suave em `τ`, o que vale para uma seed, mas pode não valer entre seeds.

### Smoke tests da divisão pelo CFL

Em 2026-11-12, o [StoCFL-FCC+CFL-split.py](StoCFL-FCC+CFL-split.py) rodou em Rotated MNIST com `n = 40`, `k = 4`, `m = 100%`, 40 rodadas e seeds 0 e 1, sem dropout e sem Dirichlet (D-058, D-059). Foram 20 execuções, com `ε1 = 0.09`, `ε2 = 0.146` e `γ_max = 0.5`, em três cenários: tudo fundido (`τ = 0.25`), um par encadeado (`τ` = 0.28 na seed 0 e 0.26 na seed 1) e controle (`τ = 0.6`).

- **O CFL dividiu os clusters encadeados exatamente entre as rotações.** Com `reanchor` ou `cannot_link`, chegou aos 4 grupos certos. A acurácia do modelo do cluster de cada cliente subiu de 0,655 para 0,86 (tudo fundido) e de 0,835 para 0,89 (par encadeado), contra 0,894 no controle.
- **Com `none`, os clientes separados voltaram ao mesmo cluster na rodada seguinte, todas as vezes,** quando o cosseno entre os centros das partes passava de `τ` (tudo fundido). Nesse caso, a acurácia ficou idêntica à da execução sem divisão. No par encadeado, os centros ficavam abaixo de `τ`, e as partes não voltaram.
- **Com `reanchor`, os cossenos entre rotações no `Ψ` recalculado ficaram negativos,** e as partes não voltaram. O resultado foi idêntico ao do `cannot_link`.
- **Onde estão os dados:** números e leitura na [hipótese](../../docs/hipotese-stocfl-divisao-cfl.md), seção 13. Os resultados estão em `logs/resultados-divisao-cfl-smoke.json.gz` (fora do git, política 7), e os logs foram apagados. O notebook [teste-divisao-cfl.ipynb](teste-divisao-cfl.ipynb), que roda aberto da raiz do repositório ou desta pasta, lê esse JSON (`DADOS_JSON = True`, padrão) e mostra, em Plotly: a **evolução dos clusters** (clientes × rodadas, com a cor dizendo que rotações o cluster de cada cliente contém, e linhas nas divisões do CFL e nas voltas), o nº de clusters e a acurácia por rodada, as normas do critério do CFL com `ε1` e `ε2`, os cossenos entre os `Ψ` antes e depois da reancoragem e a tabela das divisões (D-060). Com `DADOS_JSON = False` ele roda as execuções que faltarem, grava o JSON e apaga os logs; sem os logs e com o JSON gravado, para com um aviso (`REEXECUTAR = True` força). Uma cópia executada, com as 17 figuras, está em `logs/teste-divisao-cfl-executado.ipynb` (fora do git).

**MNIST sem rotação, com grupos de classes (padrão desde a D-061).** Com `--label_groups 1`, o script divide o MNIST sem rotação em 4 grupos de clientes com as classes {0,1,2}, {3,4}, {5,6} e {7,8,9}. Os smoke tests foram repetidos nesse conjunto (`τ` = −0.3, −0.22 e 0.5; `ε1 = 0.07`, `ε2 = 0.378`; 20 execuções). O CFL separou grupos inteiros; com *cannot-link* a acurácia do cenário tudo fundido subiu de 0,865 para 0,957, contra 0,978 do controle. Aqui o `reanchor` não impediu a volta numa das seeds, e no par encadeado o pré-filtro do `Ψ` nem disparou ([hipótese](../../docs/hipotese-stocfl-divisao-cfl.md), seção 14). O notebook mostra esse conjunto com `PARTICAO = "classes"` (padrão) e o Rotated MNIST com `"rotacao"`; resultados em `logs/resultados-divisao-cfl-classes.json.gz`, cópia executada em `logs/teste-divisao-cfl-classes-executado.ipynb`.

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