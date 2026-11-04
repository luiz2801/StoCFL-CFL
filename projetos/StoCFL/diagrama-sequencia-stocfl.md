# Diagrama de sequência: StoCFL

Troca de mensagens entre o script principal, o servidor, o trainer, os dados e os logs durante `StoCFL-FCC+CFL.py`. O servidor (`StandaloneServer`) comanda a rodada. O trainer (`RotatedMNISTTrainer`, um `SerialTrainer` do FedLab) representa todos os clientes e treina um de cada vez no mesmo processo. A flag `train` separa só o agrupamento (`train=0`) do treino em dois níveis (`train=1`). As variações entre os scripts estão na tabela de `diagrama-atividades-stocfl.md`.

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant Main as Script principal
    participant S as Server (StandaloneServer)
    participant T as Trainer (clientes simulados)
    participant D as Dados (RotatedMNIST ou CIFAR10)
    participant L as Logs (Logger, .log e .pkl)

    Note over Main,L: Preparação
    Main->>Main: ler argumentos e setup_seed(seed)
    opt process == 1
        Main->>D: pre_process(shards)
        D-->>Main: partições rotacionadas gravadas em disco
    end
    Main->>T: RotatedMNISTTrainer(model, args)
    T->>D: criar o particionador (root, save_dir)
    Main->>L: Logger("StoCFL", ...) e registrar os argumentos
    Main->>S: StandaloneServer(model, True, trainer, args)
    Note right of S: um cluster por cliente, psi vazio, gmodel e anchor = modelo inicial
    Main->>S: main()

    Note over S,L: Rodadas de comunicação (com_round)
    loop a cada rodada
        S->>S: sortear num_per_round clientes
        S->>L: "Starting round" com os ids sorteados

        Note over S,T: Observação a partir do anchor
        S->>T: observe(unobserved, anchor)
        loop para cada sorteado que ainda não tem psi
            T->>D: get_data_loader(cid, obbs)
            D-->>T: DataLoader
            T->>T: ob_train, obep épocas de SGD a partir do anchor
        end
        T-->>S: movimentos (anchor − modelo treinado)
        S->>S: psi[cid] = movimento
        S->>L: psi.pkl

        Note over S,L: Agrupamento por união
        S->>S: cluster_center, média dos psi de todos os membros de cada cluster sorteado
        opt mais de 1 cluster sorteado
            S->>S: dt_matrix (cosseno) e parse_matrix (pares do maior ao menor)
            S->>L: cos_rec.log
            loop para cada par, do maior cosseno ao menor
                alt cosseno ≥ tau
                    S->>S: unite(a, b)
                else cosseno abaixo de tau
                    Note over S: break, os pares restantes têm cosseno menor
                end
            end
        end
        S->>L: get_cluster grava cluster_rec.log e cluster.pkl

        opt train == 1
            Note over S,T: Treino em dois níveis
            S->>S: clusters sem modelo recebem deepcopy(gmodel)
            S->>T: train(cid_this_round, cluster_models, gmodel)
            loop para cada cliente sorteado
                T->>D: get_data_loader(cid, batch_size)
                D-->>T: DataLoader
                T->>T: train_alone_prox, parte do modelo do cluster com termo proximal em gmodel
            end
            loop para cada cliente sorteado
                T->>D: get_data_loader(cid, batch_size)
                D-->>T: DataLoader
                T->>T: _train_alone, parte do gmodel da rodada
            end
            T-->>S: updated_cmodels e gmodels
            S->>S: gmodel = FedAvg(gmodels)

            loop para cada cluster sorteado
                S->>S: cluster_parameters[cluster] = FedAvg dos modelos atualizados
                S->>T: get_test_dataloader(int(cid0 * k / n))
                T->>D: get_data_loader(rotação, 4096, "test")
                D-->>T: DataLoader de teste
                T-->>S: test_loader
                S->>S: evaluate do modelo do cluster e de gmodel
                S->>L: acurácia e loss do cluster
            end
            S->>L: Global acc (g_test) e accuracy.pkl
        end
    end
```

## Pontos de atenção

- **Trainer único.** Os clientes não existem como objetos. O servidor chama o trainer com uma lista de ids, e o trainer carrega os dados de cada cliente do disco quando precisa. Num sistema distribuído, as setas `observe` e `train` seriam mensagens de rede.
- **`observe` é chamado sempre.** Quando todos os sorteados já têm `psi`, a lista `unobserved` é vazia e nenhum cliente treina. Por isso o laço de observação fica vazio nas rodadas em que não aparece nenhum cliente novo.
- **Cosseno entre clusters, não entre clientes.** A matriz usa o centro de cada cluster sorteado, a média dos `psi` de todos os seus membros. Só clusters sorteados na rodada são comparados.
- **Dois laços de treino separados.** No `train`, todos os clientes treinam primeiro o modelo do cluster, e só depois o modelo global. Nos dois laços, cada cliente parte do modelo enviado pelo servidor naquela rodada.
- **Arquivos reescritos.** `cos_rec.log` e `cluster_rec.log` são apagados e recriados a cada rodada, então o disco guarda só o estado da última. O histórico completo dos clusters fica em `cluster.pkl`.
