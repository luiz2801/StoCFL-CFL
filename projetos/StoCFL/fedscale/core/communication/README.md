# communication

Comunicação entre o agregador e os clientes do runtime FedScale, por gRPC.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `job_api.proto` | Definição do serviço e das mensagens gRPC. As classes Python geradas a partir dele ficam em `core/job_api_pb2.py` e `core/job_api_pb2_grpc.py`. |
| `channel_context.py` | Classe `ClientConnections`, que abre o canal gRPC com o agregador. Usa a porta base 18888 e aceita mensagens de até 1 GB. |
| `__init__.py` | Vazio. |
