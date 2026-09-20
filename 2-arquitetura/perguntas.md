# Perguntas: Caso ônibus Envelope B

### 1. Como o validador aceita a passagem sem rede, e como o sistema descobre depois que a mesma passagem foi usada em dois ônibus?

### 2. Como o saldo do cartão fica consistente entre recarga no aplicativo e uso no ônibus, com atraso de sincronização?

O saldo do cartão se mantém consistente entre recarga e aplicativo e uso no ônibus mesmo com atraso de sincronização porque, na arquitetura definida, o processo é o seguinte: o passageiro faz a recarga no aplicativo e o Serviço de Cartões e Recarga atualiza o saldo no banco de dados central, registrando uma ordem de pendente de escrita no cartão. A partir disso, a nuvem envia essa ordem de carga para a memória local dos validadores embarcados dos ônibus quando há conexão com a internet.

Quando o passageiro aproxima o cartão na maquininha do ônibus que não está conectado à internet, o validador lê o código do cartão, consulta a memória local e encontra a ordem de carga pendente de escrita. Nesse momento, o próprio validador faz a escrita dos créditos no chip do cartão do usuário e já desconta o valor da passagem, permitindo que a catraca abra sem depender da rede.

No momento em que o ônibus se conecta à internet, ele envia o lote de confirmações de escrita para o Serviço de Sincronização via barramento de eventos (Kafka), com um identificador único. A nuvem atualiza o status da transação para concluída e descarta eventuais duplicidades.

Os ADRs que justificam essas decisões são:
- 0001 — Justifica o uso de uma arquitetura baseada em eventos para desacoplar a compra no app da validação no ônibus.
- 0002 — Estabelece que o saldo real deve ficar na nuvem e que a gravação física síncrona no chip do cartão deve ser feita pelo validador embarcado.
- 0003 — Define o uso do barramento Kafka com identificador único para garantir a idempotência.

Os diagramas que justificam essa decisão são os de nível 1 e 2, que mapeiam visualmente as fronteiras de comunicação entre o validador embarcado, o API Gateway, o Serviço de Sincronização, o barramento Kafka e a base de cartões e saldos.

### 3. Como a telemetria escala no pico sem derrubar o restante do sistema?

### 4. Como o repasse mensal é recalculado se uma regra de tarifa mudou no meio do mês?

### 5. Como o histórico de viagens de uma pessoa é apagado quando ela pede, sem quebrar a conciliação financeira?
