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

Cada viagem validada gera um evento imutável, o ValidacaoRealizada, que chega ao Consumidor de Eventos de Viagem e é gravado no Armazenamento de Eventos, sem sobrescrita, só acréscimo. Esse evento é a fonte de verdade da viagem: ele não muda depois, só pode ser reinterpretado.

As regras de tarifa não vivem dentro do Núcleo de Fechamento. Cada versão de tarifa é um plugin registrado no Registro de Regras Tarifárias com uma janela de vigência (data de início e, quando aplicável, data de fim), o mesmo mecanismo de contrato e descoberta do microkernel. Quando uma tarifa nova entra no meio do mês, ela só é acrescentada como mais um plugin: o núcleo não é alterado, e as regras antigas continuam registradas.

No fechamento, o Núcleo de Fechamento não aplica "a regra de hoje" a tudo. Ele reproduz os eventos de viagem do período e, para cada evento individualmente, pede ao Registro a versão de tarifa que estava vigente na data daquele evento, não na data em que o fechamento está rodando. É esse ponto que resolve a pergunta: se a tarifa mudou no dia 15, as viagens do dia 1 ao 14 são fechadas com a regra antiga e as do dia 15 em diante com a nova, dentro do mesmo recálculo, sem precisar de nenhuma lógica especial de "meio do mês".

O resultado passa pelo pipeline de fechamento: o Filtro Consolidador por Operadora aplica a tarifa resolvida a cada evento, soma por operadora, manda para a Fila de Rejeitados qualquer evento que não conseguiu ser tarifado (com o motivo registrado), e grava o total auditável no Armazenamento de Fechamento Mensal. A partir daí, o Gerador de Arquivo de Repasse monta o arquivo de remessa enviado ao banco ou à operadora, e a API de Conciliação e Contestação expõe o resultado, incluindo qual versão de regra foi aplicada a cada viagem, para sustentar contestações dentro do prazo de 30 dias.

Se depois do fechamento uma operadora contesta e a tarifa aplicada estava errada, o mesmo mecanismo permite reprocessar exatamente o intervalo de eventos afetado com a versão correta de regra, sem tocar no restante do mês: o evento original nunca muda, apenas a interpretação aplicada a ele é reexecutada.

Os ADRs que justificam essas decisões são:

- 0004 - Separa o backend por subdomínios e estabelece o Repasse e Conciliação como serviço próprio, dono dos seus dados de fechamento.
- 0003 - Define eventos assíncronos persistentes como padrão de integração, incluindo o evento de validação de viagem que alimenta o Repasse e permite tratá-lo como fato imutável.

O diagrama que justifica essa decisão é o de nível 3, que mapeia visualmente as fronteiras de comunicação entre o Consumidor de Eventos de Viagem, o Núcleo de Fechamento, o Registro de Regras Tarifárias, o Filtro Consolidador por Operadora e o Armazenamento de Fechamento Mensal, dentro do Serviço de Repasse e Conciliação

### 5. Como o histórico de viagens de uma pessoa é apagado quando ela pede, sem quebrar a conciliação financeira?
