### Entrega 4B — Respostas às objeções recebidas

1. A estratégia de recarga offline contradiz a fonte autoritativa de saldo.
-> Aceitamos a objeção.

A resposta da pergunta 2 ficou inconsistente com o ADR 0002. O ADR define que o saldo autoritário permanece no Serviço de Cartões e Recarga e que o validador trabalha apenas com uma visão local limitada, assinada e versionada. Já perguntas.md acrescentou um mecanismo de ordem de recarga enviada aos validadores e gravação de crédito no cartão que não foi definido no ADR nem demonstrado no spike.
Por isso, vamos corrigir a documentação para manter a decisão já registrada no ADR 0002: durante a falta de conexão, o validador trabalha com o último estado conhecido e uma recarga feita no aplicativo pode não estar disponível imediatamente naquele ônibus. Quando a conexão retorna, as operações são sincronizadas e reconciliadas com o saldo autoritário do backend.
Essa escolha preserva uma única fonte autoritativa e assume explicitamente o trade-off já registrado no ADR: ganhamos funcionamento offline, mas aceitamos atraso temporário na disponibilidade de uma recarga durante a desconexão. Não manteremos na documentação atual a afirmação de que qualquer validador pode escrever uma recarga pendente no cartão, pois esse mecanismo não foi especificado nem validado pelo grupo.

- Mudança prevista: corrigir a pergunta 2 de perguntas.md para ficar consistente com o ADR 0002.

2. O identificador usado pelo spike não sustenta a idempotência em produção.
-> Aceitamos a objeção.
O spike usa identificadores no formato onibus-id + posição no log, suficientes para demonstrar em pequena escala que uma mesma mensagem reenviada pode ser reconhecida e ignorada. Porém, esse formato não garante substituições ou perda do armazenamento local do equipamento.
O livro deixa claro que exemplos executáveis demonstram o mecanismo que distingue a decisão, e não um sistema completo de produção.     
Portanto, o spike mostrou a necessidade de idempotência, mas não provou que o algoritmo de geração de identificadores utilizado seja adequado ao ciclo de vida real de 1.200 validadores.
Vamos manter a decisão dos ADRs 0002 e 0003 de utilizar identificadores únicos e consumidores idempotentes, mas corrigir a documentação para declarar que a geração do identificador em produção precisa ser persistente e não pode depender apenas da posição atual do log local. 
O spike será descrito como uma simplificação experimental.

- Mudança prevista: registrar no README do spike essa limitação e substituir, em uma evolução do experimento, o contador reiniciável por uma identificação persistente do dispositivo combinada com um contador monotônico persistido.

3. A arquitetura celular do ADR 0005 não aparece na arquitetura executável.
-> Aceitamos a objeção.
O ADR 0005 define que Cartões e Recarga e o backend de Validação seriam implantados em células independentes e redundantes, mas o C4 atual mostra esses elementos apenas uma vez. Assim, o diagrama não torna visível a fronteira entre células nem qual dado pertence a cada uma.
Essa objeção é relevante porque, segundo o livro, arquitetura celular existe para limitar o raio de impacto de uma falha. Se a configuração desenhada continua mostrando banco e serviços como compartilhados, o diagrama não sustenta visualmente a decisão.
Não entendemos que isso invalide a decisão do ADR 0005, mas a representação está incompleta. 
Vamos ajustar o C4 para mostrar que cada célula crítica possui sua própria instância do Serviço de Cartões e Recarga, backend de Validação e armazenamento correspondente, com uma chave estável usada para encaminhar cada cartão à célula responsável.
Também deixaremos explícito que componentes globais compartilhados devem ser mínimos, pois um componente compartilhado em excesso ampliaria novamente o domínio de falha e contrariaria a finalidade da arquitetura celular.

- Mudança prevista: atualizar o C4 de nível 2 para representar as células e o roteamento para a célula responsável.

4. Tópicos separados no mesmo Kafka não isolam a telemetria dos fluxos críticos.
-> Aceitamos a objeção.

A expressão usada em perguntas.md, dizendo que os tópicos seriam “fisicamente separados”, está incorreta para o desenho atual.
O C4 mostra um único barramento Kafka; ou seja, tópicos diferentes oferecem separação lógica, mas podem compartilhar infraestrutura.
O livro diferencia componentes, conectores e configuração e ressalta que a infraestrutura intermediária também constitui uma dependência de disponibilidade.
Além disso, a arquitetura orientada a eventos reduz o acoplamento temporal entre produtor e consumidor, mas isso não significa que o broker deixe de ser um recurso operacional compartilhado.     
Manteremos a decisão do ADR 0003 de usar processamento assíncrono para absorver o pico de telemetria, mas corrigiremos a afirmação de isolamento físico. 
A documentação passará a dizer que a telemetria é logicamente separada e possui escala independente no serviço, enquanto o isolamento de infraestrutura precisa ser dimensionado e verificado.
Como validação e recarga têm SLA de 99,9% com multa, a configuração deve impedir que telemetria consuma recursos capazes de derrubar esses fluxos. Se um barramento compartilhado não garantir isso, o desenho deve separar também os recursos de mensageria da telemetria.

- Mudança prevista: corrigir perguntas.md e deixar explícito no C4/documentação que isolamento lógico não equivale a isolamento físico.

5. O evento chamado de fonte de verdade só é persistido por um consumidor posterior

-> Aceitamos a objeção.
A pergunta 4 chamou ValidacaoRealizada de fonte imutável da viagem, mas o C4 atual mostra o armazenamento permanente ocorrendo somente depois do Kafka, pelo Serviço de Repasse. Isso cria uma diferença entre o que o texto afirma e o que a arquitetura desenhada demonstra.
O livro define Event Sourcing como o estilo que preserva o histórico completo como fonte da verdade.
Portanto, se quisermos chamar o armazenamento de eventos de fonte de verdade, precisamos definir em que ponto o fato passa a estar duravelmente registrado.
Vamos corrigir essa parte da arquitetura. 
O Serviço de Sincronização deverá persistir a validação aceita antes de considerá-la confirmada para o ônibus. A publicação para o barramento passa a ocorrer a partir desse registro persistido, e o Serviço de Repasse consome o evento para gerar suas projeções e resultados de fechamento.
Essa correção também deixa mais clara a diferença entre o barramento de eventos, usado para integração, e o armazenamento durável usado como histórico.

- Mudança prevista: ajustar o fluxo no C4 e a resposta da pergunta 4 para que o log persistente exista antes da confirmação definitiva da sincronização.

6. A regra de cinco minutos produz suspeita, não prova reutilização da mesma passagem

-> Aceitamos a objeção.
O limite de cinco minutos do spike foi criado apenas para demonstrar que eventos produzidos offline em ônibus diferentes podem ser comparados depois da reconexão. Ele não é uma regra suficiente para afirmar fraude ou reutilização da mesma passagem.
O próprio material de nosso grupo já reconhecia essa limitação: horários próximos podem levantar suspeita, mas precisam considerar regras de integração e outros dados antes de caracterizar conflito.
Assim, a arquitetura será descrita da seguinte forma: proximidade temporal entre usos em ônibus diferentes é um sinal de possível conflito, não uma prova. A decisão arquitetural que continua válida é que dois validadores desconectados não conseguem coordenar entre si naquele instante e, portanto, a análise precisa acontecer posteriormente.
O spike continuará sendo útil para provar a possibilidade de reconciliar eventos depois da reconexão, mas não será usado como evidência de que a regra de cinco minutos seja uma regra definitiva de negócio.

- Mudança prevista: alterar o README e os textos do spike de “duplicidade física” para “suspeita de conflito” ou equivalente, deixando explícito que a regra é apenas demonstrativa.

7. Remover a tabela de vínculo não garante anonimização dos eventos de viagem
-> Aceitamos a objeção.

A frase em perguntas.md que afirma que, após remover o vínculo, o identificador passa a ficar “sem possibilidade de reidentificação” é forte demais. A arquitetura garante separação entre identificadores pessoais diretos e os fatos financeiros, mas isso, por si só, demonstra pseudonimização, não anonimização garantida.
Os eventos continuam contendo informações como horário, veículo e histórico de utilização. Portanto, mesmo sem nome ou CPF, ainda pode existir risco de correlação com outras fontes.
Vamos corrigir a resposta da pergunta 5 para não afirmar anonimização automática. A solução continuará separando dados pessoais identificáveis dos registros necessários à conciliação financeira, mas passaremos a tratar a pseudonimização como uma medida de redução de exposição, acompanhada por retenção e minimização dos dados mantidos.
Após o período em que o dado individual for necessário para contestação e auditoria, devem permanecer apenas os atributos necessários à finalidade financeira prevista no caso.

- Mudança prevista: substituir a afirmação de “impossibilidade de reidentificação” por uma descrição de pseudonimização, minimização e retenção limitada conforme a finalidade.

8. A reconciliação termina com saldo negativo sem definir a compensação de negócio
-> Aceitamos parcialmente a objeção.

O spike realmente termina o cartão A com saldo negativo, mas isso foi usado para tornar visível a divergência produzida pelas duas validações offline. O objetivo do experimento era provar que o sistema consegue detectar a divergência depois da reconexão e evitar reprocessamento duplicado; ele não definiu uma política financeira completa para resolver o prejuízo.
Portanto, concordamos que o texto não deveria tratar detecção como se fosse reconciliação completa.
A decisão arquitetural do ADR 0002 permanece: o backend mantém o saldo autoritário, as operações offline são reaplicadas de forma idempotente e divergências precisam ser tratadas posteriormente. Porém, vamos registrar que o tratamento de um saldo negativo exige uma regra de negócio explícita, separada do mecanismo técnico de sincronização.
Essa regra deverá definir pelo menos quais validações são confirmadas, como o bloqueio posterior funciona e como uma divergência fica registrada para auditoria e contestação. Não vamos inventar nesta entrega uma política financeira específica que não tenha sido definida no enunciado. O importante é deixar claro que o spike demonstra detecção e reconciliação técnica das operações, não a decisão econômica final sobre quem absorve o valor divergente.

- Mudança prevista: corrigir o README do spike e a documentação para distinguir “detectar e registrar a divergência” de “resolver financeiramente a divergência”.

### Síntese das mudanças
A leitura cruzada mostrou inconsistências entre decisões já registradas e alguns textos ou simplificações do spike.
Não vamos alterar os princípios centrais da arquitetura — validação local durante perda de rede, saldo autoritário no backend, eventos assíncronos, separação por subdomínios e células nos serviços críticos, mas vamos corrigir a documentação e os diagramas onde eles afirmaram garantias maiores do que aquilo que os ADRs e experimentos realmente sustentam.

As principais correções serão: 
alinhar a recarga offline ao ADR 0002; explicitar que o identificador do spike é simplificado;
representar as células no C4;
retirar a afirmação de isolamento físico apenas por tópicos Kafka;
definir com clareza onde a validação passa a ser persistentemente registrada;
tratar a janela de cinco minutos apenas como sinal de conflito;
não confundir pseudonimização com anonimização;e
separar reconciliação técnica de política de compensação financeira.