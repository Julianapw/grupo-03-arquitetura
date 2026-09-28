# Perguntas: Caso ônibus Envelope B

### 1\. Como o validador aceita a passagem sem rede, e como o sistema descobre depois que a mesma passagem foi usada em dois ônibus?

O validador usa uma cópia local do saldo, das regras e dos bloqueios para liberar a passagem sem depender da internet. Antes de abrir a catraca, atualiza o saldo local e salva o registro com identificador único, cartão, ônibus e horário. Isso permite continuar funcionando durante as quatro horas sem conexão previstas no caso.

Quando a conexão volta, os registros são enviados pelo API Gateway ao Serviço de Sincronização e seguem pelo Kafka. O ônibus guarda as pendências até receber a confirmação. Se um registro chegar novamente, seu identificador permite reconhecer que ele já foi processado e evitar outra cobrança.

O backend também compara os usos do mesmo cartão em ônibus diferentes para encontrar conflitos. Horários muito próximos levantam uma suspeita, mas precisam considerar as integrações permitidas; quando houver um identificador da passagem, ele permite verificar sua reutilização. Como dois ônibus sem rede não trocam informações, não é possível impedir todos esses casos na hora. A conferência acontece depois, com ajuste do saldo e envio dos bloqueios necessários, conforme o ADR 0001.

Os ADRs que justificam essas decisões são:

* 0001 — Permite a validação local sem rede e reconhece a limitação de impedir usos simultâneos em ônibus desconectados.
* 0002 — Mantém o saldo autoritário no serviço de Cartões e Recarga e define a reconciliação das operações sem cobrar novamente os registros repetidos.
* 0003 — Define o envio de eventos persistentes e o uso de identificadores únicos para tratar reenvios.

O diagrama que justifica essa decisão é o de nível 2, que mostra a comunicação entre o validador, a base local, o agente de sincronização, o API Gateway, o Serviço de Sincronização, o Kafka e o Serviço de Cartões e Recarga.

### 2\. Como o saldo do cartão fica consistente entre recarga no aplicativo e uso no ônibus, com atraso de sincronização?

O saldo do cartão não fica consistente de forma imediata: ele fica consistente de forma eventual, e a arquitetura assume isso de propósito. O saldo autoritário vive no backend, no Serviço de Cartões e Recarga. O validador embarcado nunca é a fonte da verdade. Nem o saldo guardado no validador nem o saldo guardado no cartão são considerados a referência, porque vários ônibus desconectados e vários canais de recarga poderiam manter estados diferentes ao mesmo tempo.

Durante a falta de conexão, o validador opera com uma visão local limitada, assinada e versionada, que é o último estado que ele conseguiu sincronizar. Se o passageiro recarrega pelo aplicativo, o Serviço de Cartões e Recarga atualiza o saldo autoritário e registra a recarga com um identificador único, mas um ônibus sem rede não fica sabendo disso naquele momento. Se o passageiro embarcar nesse ônibus logo depois, o validador decide com o último saldo que conhece, e a recarga pode não estar disponível ali até o próximo contato com o backend. É o trade-off registrado no ADR 0002: a passagem continua sendo validada durante as até quatro horas sem 4G, e em troca aceita-se um atraso temporário na disponibilidade da recarga.

Cada débito feito offline é registrado no ônibus com um identificador único, junto com cartão, ônibus e horário, e fica pendente. Quando a conexão volta, essas operações são enviadas pelo API Gateway ao Serviço de Sincronização, que as registra de forma persistente e as publica como eventos até o Serviço de Cartões e Recarga. Lá, recargas e débitos são reconciliados com o saldo autoritário. Como todos têm identificador único, a reconciliação é idempotente: um registro reenviado por falha de rede é reconhecido e não altera o saldo mais de uma vez. Depois disso, o ônibus recebe uma visão local atualizada na próxima sincronização.

Durante a desconexão, portanto, existe um risco controlado de divergência, por exemplo um saldo negativo quando o mesmo cartão é usado em ônibus desconectados. A arquitetura garante que essas divergências são identificadas e registradas na reconciliação. A regra de negócio sobre como resolvê-las financeiramente é separada do mecanismo técnico e não é definida neste trabalho.

Os ADRs que justificam essas decisões são:

0001 - Permite que o validador decida localmente sem rede, usando os dados mínimos armazenados no dispositivo. 0002 - Mantém o saldo autoritário no Serviço de Cartões e Recarga, define que o validador opera com uma visão local limitada, assinada e versionada, e que recargas e débitos são reconciliados de forma idempotente. 0003 - Define eventos assíncronos persistentes com identificadores únicos para levar as operações ao backend e tolerar reenvios.

Os diagramas que justificam essa decisão são os de nível 1 e 2, que mapeiam visualmente as fronteiras de comunicação entre o validador embarcado, o API Gateway, o Serviço de Sincronização, o barramento Kafka, o Serviço de Cartões e Recarga e a base de cartões e saldos.

### 3\. Como a telemetria escala no pico sem derrubar o restante do sistema?

A telemetria escala no pico sem derrubar o restante do sistema porque, na arquitetura definida, o fluxo de posições GPS é totalmente separado dos fluxos críticos de validação e recarga, tanto na entrada quanto no processamento.

Cada ônibus envia suas coordenadas GPS ao Serviço de Telemetria (visível no diagrama C4 de contêineres), que é um serviço dedicado e independente dos serviços de Cartões e Recarga e de Sincronização. O Serviço de Telemetria recebe os dados via HTTPS pelo API Gateway e os publica imediatamente no Barramento de Eventos (Apache Kafka) usando o protocolo Kafka nativo, em tópicos particionados exclusivos para telemetria. Isso significa que, mesmo no pico de 400 mensagens por segundo, a ingestão é feita de forma assíncrona: o serviço produtor apenas envia e não espera processamento de volta.

O Kafka atua como amortecedor de pico (buffer): se os consumidores de telemetria (ex.: Informação ao Passageiro para previsão de chegada, Órgão Gestor para monitoramento da frota) não conseguem consumir na mesma velocidade do pico, as mensagens ficam retidas no tópico particionado até serem processadas, sem gerar contrapressão no produtor nem no restante do sistema. Os tópicos de telemetria são fisicamente separados dos tópicos de validação e recarga no Kafka, portanto um acúmulo de mensagens de GPS não atrasa a sincronização de validações offline nem a propagação de recargas.

Além disso, como o Serviço de Telemetria é uma unidade de implantação independente (ADR 0004), ele pode escalar horizontalmente — adicionando mais instâncias — sem afetar ou exigir reimplantação dos outros serviços. Os serviços críticos de Cartões e Recarga, por sua vez, estão implantados em células independentes e redundantes (ADR 0005), com recursos de computação e banco de dados próprios, completamente isolados da infraestrutura de telemetria.

Os ADRs que justificam essas decisões são:

* 0003 — Define eventos assíncronos persistentes como padrão de integração, permitindo que telemetria use o barramento sem acoplamento temporal com validação e recarga.
* 0004 — Separa o backend por subdomínios de negócio, garantindo que o Serviço de Telemetria seja uma unidade independente com escala própria.
* 0005 — Implanta os serviços críticos em células independentes, isolando fisicamente validação e recarga de qualquer pico de carga nos demais subdomínios.

O diagrama que justifica essa decisão é o de Nível 2 (Contêineres), que mostra o Serviço de Telemetria como um contêiner separado, conectado ao Barramento de Eventos por Kafka Protocol (400 msg/s), sem nenhuma dependência direta com o Serviço de Cartões e Recarga ou com a Base de Cartões e Saldos.

### 4\. Como o repasse mensal é recalculado se uma regra de tarifa mudou no meio do mês?

Cada viagem validada gera um evento imutável, o ValidacaoRealizada. O Serviço de Sincronização grava essa validação em um log persistente antes de confirmar definitivamente a sincronização para o ônibus. A publicação no Kafka ocorre posteriormente, a partir do registro persistido. Dessa forma, uma indisponibilidade temporária no Kafka não causa perda do registro da viagem nem da confirmação já registrada. O Serviço de Repasse e Conciliação consome o evento publicado para gerar suas projeções e resultados de fechamento; o armazenamento de eventos usado para suas projeções é append-only.

As regras de tarifa não vivem dentro do Núcleo de Fechamento. Cada versão de tarifa é um plugin registrado no Registro de Regras Tarifárias com uma janela de vigência (data de início e, quando aplicável, data de fim), o mesmo mecanismo de contrato e descoberta do microkernel. Quando uma tarifa nova entra no meio do mês, ela só é acrescentada como mais um plugin: o núcleo não é alterado, e as regras antigas continuam registradas.

No fechamento, o Núcleo de Fechamento não aplica "a regra de hoje" a tudo. Ele reproduz os eventos de viagem do período e, para cada evento individualmente, pede ao Registro a versão de tarifa que estava vigente na data daquele evento, não na data em que o fechamento está rodando. É esse ponto que resolve a pergunta: se a tarifa mudou no dia 15, as viagens do dia 1 ao 14 são fechadas com a regra antiga e as do dia 15 em diante com a nova, dentro do mesmo recálculo, sem precisar de nenhuma lógica especial de "meio do mês".

O resultado passa pelo pipeline de fechamento: o Filtro Consolidador por Operadora aplica a tarifa resolvida a cada evento, soma por operadora, manda para a Fila de Rejeitados qualquer evento que não conseguiu ser tarifado (com o motivo registrado), e grava o total auditável no Armazenamento de Fechamento Mensal. A partir daí, o Gerador de Arquivo de Repasse monta o arquivo de remessa enviado ao banco ou à operadora, e a API de Conciliação e Contestação expõe o resultado, incluindo qual versão de regra foi aplicada a cada viagem, para sustentar contestações dentro do prazo de 30 dias.

Se depois do fechamento uma operadora contesta e a tarifa aplicada estava errada, o mesmo mecanismo permite reprocessar exatamente o intervalo de eventos afetado com a versão correta de regra, sem tocar no restante do mês: o evento original nunca muda, apenas a interpretação aplicada a ele é reexecutada.

Os ADRs que justificam essas decisões são:

* 0004 - Separa o backend por subdomínios e estabelece o Repasse e Conciliação como serviço próprio, dono dos seus dados de fechamento.
* 0003 - Define eventos assíncronos persistentes como padrão de integração, incluindo o evento de validação de viagem que alimenta o Repasse e permite tratá-lo como fato imutável.

O diagrama que justifica essa decisão é o de nível 3, que mapeia visualmente as fronteiras de comunicação entre o Consumidor de Eventos de Viagem, o Núcleo de Fechamento, o Registro de Regras Tarifárias, o Filtro Consolidador por Operadora e o Armazenamento de Fechamento Mensal, dentro do Serviço de Repasse e Conciliação

### 5\. Como o histórico de viagens de uma pessoa é apagado quando ela pede, sem quebrar a conciliação financeira?

O histórico de viagens de uma pessoa é apagado sem quebrar a conciliação financeira porque a arquitetura separa, desde a origem, os dados pessoais identificadores dos fatos financeiros da viagem.

Quando uma validação é registrada, o evento de viagem gravado no Armazenamento de Eventos (visível no diagrama C4 de contêineres) contém apenas um identificador pseudonimizado do passageiro — não o nome, CPF ou número do cartão diretamente. O vínculo entre esse identificador pseudonimizado e os dados pessoais reais (nome, CPF, e-mail, número do cartão) fica armazenado separadamente, no Serviço de Cartões e Recarga e na Base de Cartões e Saldos.

Essa separação segue o princípio de pseudonimização: o evento de viagem registra "o passageiro com ID abc123 embarcou no ônibus X às 07:32 do dia 15, tarifa R$4,40", mas não registra quem é abc123. Para saber quem é essa pessoa, é preciso consultar a tabela de vínculo no Serviço de Cartões.

Quando o passageiro solicita a exclusão dos seus dados pessoais (direito garantido pela LGPD), o sistema executa as seguintes etapas:

1. Remove ou anonimiza o vínculo pessoal na Base de Cartões e Saldos: o registro que liga o identificador pseudonimizado ao nome, CPF e demais dados pessoais é apagado ou substituído por dados irreversíveis (anonimização).
2. Mantém os fatos financeiros intactos no Armazenamento de Eventos: os eventos de viagem permanecem com o identificador pseudonimizado (abc123), mas esse identificador agora não leva a ninguém — é um dado órfão, sem possibilidade de reidentificação.
3. A conciliação financeira não é afetada, pois o Serviço de Repasse e Conciliação (diagrama C4 de componentes) trabalha com os eventos de viagem e as regras tarifárias, não com os dados pessoais do passageiro. O Núcleo de Fechamento reproduz eventos, aplica tarifa vigente e consolida por operadora — tudo isso usa apenas o identificador pseudonimizado, o horário, o veículo e o valor da tarifa. Nenhuma dessas informações é perdida com a exclusão dos dados pessoais.
4. Contestações dentro do prazo de 30 dias continuam possíveis: a API de Conciliação e Contestação expõe os registros financeiros com a versão de regra aplicada. Se o passageiro já pediu exclusão, o registro financeiro continua existindo para fins de auditoria — apenas não é mais possível identificar a pessoa.

Os ADRs que justificam essas decisões são:

* 0003 — Define eventos assíncronos persistentes como padrão de integração, incluindo eventos de viagem como fatos imutáveis. A imutabilidade dos eventos é compatível com a anonimização porque o evento em si não é alterado — apenas o vínculo externo é removido.
* 0004 — Separa o backend por subdomínios, garantindo que o Serviço de Cartões (dono dos dados pessoais) e o Serviço de Repasse (dono dos dados financeiros) tenham propriedade de dados independentes.

Os diagramas que justificam essa decisão são os de Nível 2 (Contêineres), que mostra a separação entre a Base de Cartões e Saldos (onde vivem os dados pessoais) e o Armazenamento de Eventos (onde ficam os fatos financeiros pseudonimizados), e o de Nível 3 (Componentes), que mostra que o Armazenamento de Eventos de Viagem armazena dados com "id pseudonimizado", confirmando que o fluxo financeiro inteiro opera sem dados pessoais diretos.

