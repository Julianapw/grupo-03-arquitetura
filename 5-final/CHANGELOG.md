### Mudanças Realizadas a partir das objeções recebidas:

1. Para a objeção 1: A estratégia de recarga offline contradiz a fonte autoritativa de saldo.

O texto original da Pergunta 2 continha uma premissa incorreta sobre a gravação do saldo diretamente no chip do cartão físico durante a validação no ônibus. Para corrigir esse ponto, removemos a explicação de gravação de saldo no chip do cartão na Pergunta 2. O texto foi reescrito para deixar clara a operação offline utilizando o último saldo e a reconciliação assíncrona, conforme determina o ADR 0002. A principal diferença estrutural é que a resposta agora assume corretamente o modelo de consistência eventual, onde o validador embarcado opera com uma visão local e versionada durante a falta de rede, delegando a responsabilidade do saldo autoritário e da conciliação idempotente exclusivamente para o backend (Serviço de Cartões e Recarga) quando a conectividade é restabelecida.

2. Para a objeção 2: O identificador usado pelo spike não sustenta a idempotência em produção.

Adicionamos uma nova seção no `3-spike/README.md` chamada "Limitações do Experimento". Nela, registramos um *disclaimer* explicando que o formato do identificador gerado no código Python é puramente didático para demonstrar a matemática da idempotência em pequena escala. Deixamos claro que, em um ambiente de produção real, seria obrigatório o uso de geração de identificadores persistentes e monotônicos atrelados ao dispositivo para evitar colisões.

3. Para a objeção 3: A arquitetura celular do ADR 0005 não aparece na arquitetura executável.

O ADR 0005 já definia que Cartões e Recarga e o backend de Validação seriam implantados em células independentes, com os cartões distribuídos por uma chave de roteamento estável, sendo assim a mudança não contradiz o ADR ele se mantém o mesmo do início. O problema era que nosso C4 mostrava esses serviços e o banco apenas uma vez. Então corrigimos o diagrama para representar explicitamente múltiplas células, cada uma com seus serviços críticos e seu armazenamento, mantendo os demais subdomínios fora das células. Portanto, a principal diferença é que os três elementos críticos que antes apareciam uma vez agora aparecem por célula.

4. Para a objeção 4: Tópicos separados no mesmo Kafka não isolam a telemetria dos fluxos críticos.

Corrigimos a resposta da Pergunta 3 substituindo a expressão "fisicamente separados" por "logicamente separados". Os fluxos continuam utilizando tópicos distintos no Kafka, permitindo processamento, particionamento e consumidores independentes, porém sem assumir isolamento físico completo entre eles. A nova redação também deixa claro que esses tópicos podem compartilhar brokers, rede, disco e outros recursos do mesmo cluster. Dessa forma, mantivemos a estratégia arquitetural original e corrigimos a afirmação de separação física apontada na objeção.

5. Para a objeção 5: O evento chamado de fonte de verdade só é persistido por um consumidor posterior.

Ajustamos o C4 para representar o Log Persistente de Eventos como um EventStore / Outbox antes do Kafka. Os Serviços de Sincronização A e B gravam o evento Validacao Realizada nesse log antes da confirmação definitiva da sincronização. Depois, o evento persistido é publicado no Barramento de Eventos. A resposta da Pergunta 4 também foi atualizada para diferenciar o log persistente anterior ao Kafka do armazenamento append-only usado pelo Serviço de Repasse e Conciliação para suas projeções e resultados de fechamento.

6. Para a objeção 6: A regra de cinco minutos produz suspeita, não prova reutilização da mesma passagem.

Alteramos o arquivo `3-spike/README.md` e os logs gerados pelo próprio script `spike.py` (que alimentam o arquivo `saida-esperada.txt`). Removemos as afirmações categóricas "duplicidade física" e "uso duplicado", substituindo-as pelo termo "suspeita de conflito". Com isso, reconhecemos que a heurística de tempo alerta para uma divergência técnica, mas não configura prova definitiva de fraude de negócio sem a análise de outros fatores.

7. Para a objeção 7: Remover a tabela de vínculo não garante anonimização dos eventos de viagem.

Corrigimos a resposta da Pergunta 5 substituindo as afirmações de anonimização irreversível pelo conceito de pseudonimização. Mesmo após a remoção do vínculo direto entre o identificador e os dados pessoais do passageiro, informações como horário, veículo, trajeto e padrões de utilização ainda podem permitir correlações com outras fontes de dados. Também acrescentamos minimização e retenção limitada, estabelecendo que os registros necessários para conciliação e auditoria sejam mantidos somente durante o período necessário para suas finalidades legais e operacionais. Assim, preservamos a conciliação financeira sem afirmar que a possibilidade de reidentificação é completamente eliminada.

8. Para a objeção 8: A reconciliação termina com saldo negativo sem definir a compensação de negócio.

Adicionamos explicações no `3-spike/README.md` para separar o mecanismo de software da regra financeira. Deixamos claro que a simulação se encerra ao detectar e registrar a divergência (saldo negativo), protegendo o fluxo técnico e não cobrando repetições de mensagens. Não assumimos na arquitetura uma política sobre quem paga o prejuízo do uso simultâneo no cenário offline, visto que a resolução financeira não fazia parte do escopo técnico de sincronização proposto pelo spike.
