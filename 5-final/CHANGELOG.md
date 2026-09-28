### Mudanças Realizadas a partir das objeções recebidas:

1. Para a objeção 3: A arquitetura celular do ADR 0005 não aparece na arquitetura executável.

O ADR 0005 já definia que Cartões e Recarga e o backend de Validação seriam implantados em células independentes, com os cartões distribuídos por uma chave de roteamento estável, sendo assim a mudança não contradiz o ADR ele se mantém o mesmo do início.
O problema era que nosso C4 mostrava esses serviços e o banco apenas uma vez. Então corrigimos o diagrama para representar explicitamente múltiplas células, cada uma com seus serviços críticos e seu armazenamento, mantendo os demais subdomínios fora das células.
Portando, a principal diferença é que os três elementos críticos que antes apareciam uma vez agora aparecem por célula.

2. Para a objeção 5: O evento chamado de fonte de verdade só é persistido por um consumidor posterior.

Ajustamos o C4 para representar o Log Persistente de Eventos como um EventStore / Outbox antes do Kafka. Os Serviços de Sincronização A e B gravam o evento Validacao Realizada nesse log antes da confirmação definitiva da sincronização. Depois, o evento persistido é publicado no Barramento de Eventos. A resposta da Pergunta 4 também foi atualizada para diferenciar o log persistente anterior ao Kafka do armazenamento append-only usado pelo Serviço de Repasse e Conciliação para suas projeções e resultados de fechamento.

3. Para a objeção 1: O texto original da Pergunta 2 continha uma premissa incorreta sobre a gravação do saldo diretamente no chip do cartão físico durante a validação no ônibus. Para corrigir esse ponto, removemos a explicação de gravação de saldo no chip do cartão na Pergunta 2. O texto foi reescrito para deixar clara a operação offline utilizando o último saldo e a reconciliação assíncrona, conforme determina o ADR 0002. A principal diferença estrutural é que a resposta agora assume corretamente o modelo de consistência eventual, onde o validador embarcado opera com uma visão local e versionada durante a falta de rede, delegando a responsabilidade do saldo autoritário e da conciliação idempotente exclusivamente para o backend (Serviço de Cartões e Recarga) quando a conectividade é restabelecida.