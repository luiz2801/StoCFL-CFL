# Diagrama de sequência: Clustered Federated Learning

Troca de mensagens entre o notebook, os clientes, o servidor e o logger durante o experimento de `clustered_federated_learning.ipynb`, com as classes `Client` e `Server` de `fl_devices.py` e o `ExperimentLogger` de `helper.py`. O notebook é quem orquestra: clientes e servidor não chamam um ao outro, só são chamados por ele ou lidos por ele.

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant NB as Notebook
    participant C as Client (x10)
    participant S as Server
    participant L as ExperimentLogger

    Note over NB,L: Preparação
    NB->>NB: carregar EMNIST, split_noniid (Dirichlet α=1.0), rotacionar 180° os clientes 0–4
    NB->>C: Client(ConvNet, SGD lr=0.1, dados, idnum)
    Note right of C: cada cliente separa 80% treino e 20% avaliação
    NB->>S: Server(ConvNet, test_data)
    NB->>L: ExperimentLogger()
    NB->>NB: cluster_indices = [todos os clientes]

    Note over NB,L: Rodadas de comunicação (c_round = 1 até 80)
    loop a cada rodada
        opt c_round == 1
            NB->>C: synchronize_with_server(server)
            C->>S: ler W
            S-->>C: W (copiado para o cliente)
        end

        NB->>S: select_clients(clients, frac=1.0)
        S-->>NB: participating_clients

        loop para cada cliente participante
            NB->>C: compute_weight_update(epochs=1)
            C->>C: W_old ← W
            C->>C: train_op, 1 época de SGD no train_loader
            C->>C: dW ← W − W_old
            C-->>NB: train_stats
            NB->>C: reset()
            C->>C: W ← W_old
        end

        NB->>S: compute_pairwise_similarities(clients)
        S->>C: ler dW de todos os clientes
        C-->>S: dW
        S-->>NB: matriz S (cosseno entre os dW)

        loop para cada cluster idc
            NB->>S: compute_max_update_norm(cluster)
            S-->>NB: max_norm
            NB->>S: compute_mean_update_norm(cluster)
            S-->>NB: mean_norm

            alt mean_norm abaixo de ε₁, max_norm acima de ε₂ e mais de 1 cliente
                NB->>S: cluster_clients(S[idc][:,idc])
                S-->>NB: c1, c2
                Note over NB: c1 e c2 são posições em idc, e os novos clusters são idc[c1] e idc[c2]
                NB->>NB: alpha_cross_max = maior cosseno entre os dois lados
                alt γ_max abaixo de √((1 − alpha_cross_max) / 2)
                    NB->>S: cache_model(idc, W, acc_clients)
                    Note right of S: guarda o modelo do cluster pai, com as acurácias da rodada anterior
                    NB->>L: log(split = c_round)
                else bipartição rejeitada
                    Note over NB: mantém idc em cluster_indices_new
                end
            else sem divisão
                Note over NB: mantém idc em cluster_indices_new
            end
        end

        NB->>S: aggregate_clusterwise(client_clusters)
        S->>C: W += média dos dW do cluster
        NB->>C: evaluate()
        C-->>NB: acurácia no eval_loader
        NB->>L: log(acc_clients, mean_norm, max_norm, rounds, clusters)
        NB->>NB: display_train_stats(...)
    end

    Note over NB,L: Pós-treino
    loop para cada cluster final
        NB->>S: cache_model(idc, W, acc_clients)
    end
    NB->>S: ler model_cache
    S-->>NB: lista de (idcs, pesos, acurácias)
    NB->>NB: montar matriz de resultados e destacar o melhor modelo de cada cliente
```

## Pontos de atenção

- **Servidor lê o cliente direto.** Em `compute_pairwise_similarities`, nas normas e em `aggregate_clusterwise`, o servidor acessa `client.dW` e `client.W` como atributos. É uma simulação em um só processo. Num sistema distribuído, essas setas seriam mensagens de rede.
- **Servidor quase não participa.** O único uso dos pesos do `Server` é a sincronização da rodada 1. Depois disso, o modelo de cada cliente evolui só pela agregação dentro do seu cluster.
- **`reset()` depois do treino.** O cliente volta a `W_old` logo após calcular `dW`. O ganho de treino só reaparece em `W` quando o servidor soma a média dos `dW` do cluster.
- **Normas por cluster.** `max_norm` e `mean_norm` são calculadas para cada `idc`, mas o `log` guarda só os valores do último cluster percorrido na rodada.
