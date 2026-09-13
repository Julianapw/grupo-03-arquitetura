# Entrega 1 - Matriz de estilos aplicada
Ana Beatriz Maranho;
Julia Kimura;
Juliana Prado;
Kaue Farias;
Matias Amma;
Ruan 
## Identificação

- **Grupo:** 03
- **Caso:** Ônibus - bilhetagem e mobilidade urbana
- **Envelope:** B - consórcio de empresas de tecnologia
- **Equipe:** 40 desenvolvedores distribuídos em 5 times
- **Infraestrutura:** nuvem pública e equipe própria de operação
- **Restrição dominante:** SLA de 99,9%, com multa por indisponibilidade da validação e da recarga

## Critérios da análise

A avaliação considera os números e as restrições do caso: 1.200 validadores, 900 mil validações por dia, pico de 120 validações por segundo, funcionamento por até quatro horas sem 4G, 150 mil recargas diárias, 2,5 milhões de cartões ativos e telemetria com pico de 400 posições por segundo. Também considera o envelope B: 40 desenvolvedores em cinco times, nuvem pública, operação própria e SLA de 99,9% com multa, aplicado à validação e à recarga.
Conforme o Apêndice A.1 do livro, as classificações dos atributos indicam tendências arquiteturais, e não medições garantidas. Assim, cada estilo foi relacionado diretamente aos subdomínios e às restrições deste sistema de ônibus.

## Matriz

| Estilo arquitetural | Serve para o caso e envelope? | Subdomínio em que entraria | Por quê? | Atributo de qualidade no contexto |
|---|---|---|---|---|
| **Monolito em camadas** (cap. 5) | ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |
| **Monolito modular** (cap. 6) | **Em parte.** | Atendimento ou organização interna do serviço de cartões e recarga. | Módulos separados para saldo, recarga, bloqueio e gratuidades ajudariam a proteger as regras transacionais sobre os 2,5 milhões de cartões com transação local, sem introduzir consistência distribuída dentro desse serviço. Mas não serve como arquitetura do sistema inteiro: os cinco times precisam publicar em ritmos diferentes, e validação, telemetria e recarga têm escalas e exigências de disponibilidade muito distintas entre si — uma implantação única para tudo continuaria sendo ponto de contenção, e uma falha em qualquer módulo derrubaria o sistema todo. O livro também recomenda o estilo para sistemas novos, cujo domínio ainda está sendo descoberto, o que reforça adotá-lo já no início dentro do serviço de cartões, e não retroagir essa lógica ao sistema completo (**Livro, §§ 6.5-6.7**). | **Melhora:** testabilidade, ao isolar regras por módulo e permitir teste rápido e determinístico. **Piora:** implantabilidade e disponibilidade independente, pois uma alteração exigiria publicar a unidade inteira, e uma falha em um módulo afetaria os demais. |
| **Hexagonal (Ports and Adapters)** (cap. 7) | **Em parte.** | Validação embarcada; cartões e recarga; integração externa. | Visto que a regra de tarifa e saldo precisa funcionar por diferentes entradas: validador no ônibus, aplicativo, loja, totem, arquivo e fila, além de integrar banco. Portas e adaptadores permitem testar a decisão de passagem sem 4G e trocar protocolos externos sem acoplar o núcleo de negócio, embora não garantam sozinhos o SLA ou a escala (**Livro, §§ 7.5-7.7 e Apêndice A.1**). | **Melhora:** testabilidade, pois a regra de validação pode ser testada sem rede ou banco real. **Piora:** custo, devido aos adaptadores e mapeamentos adicionais. |
| **Microkernel (núcleo e plugins)** (cap. 8) | ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |
| **Microsserviços** (cap. 9) | ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |
| **SOA e barramento de serviços (ESB)** (cap. 10) || ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |
| **Arquitetura orientada a eventos** (cap. 11) | **Sim.** | Sincronização da validação embarcada, telemetria da frota, cartões e recarga (propagação de saldo), informação ao passageiro e repasse/conciliação. | A decisão de aceitar a passagem continua local e síncrona no validador — eventos não servem para decisões que exigem resposta imediata. O que muda é que, assim que a rede volta, o resultado dessa decisão vira evento, permitindo detectar depois se o mesmo cartão foi usado em dois ônibus; a duplicidade é resolvida pelo consumidor (por identificador único), não pelo sistema de mensageria, que só garante entrega "ao menos uma vez". A telemetria usa o mesmo canal como amortecedor de pico sem propagar pressão à validação. Já o repasse e a conciliação, por terem fluxo de negócio mais longo (recálculo de tarifa, contestação em 30 dias), pedem mais coordenação do que apenas reações soltas entre serviços (**Livro, §§ 11.5-11.7**). | **Melhora:** escalabilidade e desacoplamento temporal, pois picos de telemetria e validação são absorvidos pelo canal sem derrubar consumidores mais lentos. **Piora:** testabilidade e depuração, pois o fluxo emerge da soma de reações independentes e exige rastreamento distribuído e identificador de correlação para investigar incidentes. |
|**Arquitetura celular (cell-based)** (cap. 13) | ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |
| **CQRS** (cap. 14) | ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |
| **Event Sourcing** (cap. 15) | **Em parte.** | Repasse e conciliação; histórico financeiro e investigação de fraude. | Eventos imutáveis de validação, débito, recarga, estorno e mudança tarifária permitem recalcular o fechamento mensal com a regra vigente na data de cada uma das 900 mil viagens diárias e responder a contestações por 30 dias. Como o histórico identificado é dado pessoal, o fluxo deve guardar apenas referência pseudonimizada, ou seja, mascarada e manter os dados identificadores em armazenamento apagável separado (**Livro, §§ 15.5-15.7**). | **Melhora:** testabilidade, permitindo reconstruir e conferir o resultado do repasse. **Piora:** custo, pelo crescimento do armazenamento, versionamento e reprocessamento. |
| **Pipes and Filters (dutos e filtros)** (cap. 16) | ??? | ??? | ??? | **Melhora:** ???. **Piora:** ???. |

## Síntese da análise

Os estilos com maior aderência à estrutura geral são:
Porque:

Os demais estilos aceitos podem ser aplicados localmente: hexagonal dentro dos serviços críticos; event sourcing no repasse auditável; 
#Adicionar aqui se tiver mais estilos aceitos que podem ser aplicados localmente !!!

Os estilos (X) foram descartados como arquitetura geral, pois:

## Relação preliminar com as perguntas obrigatórias

1. **Validação sem rede e uso em dois ônibus**: o validador mantém dados mínimos locais e registra cada uso com identificador único, horário, cartão e veículo; ao voltar a conexão, publica eventos idempotentes, sem alterar o resultado obtido após a primeira aplicação e um processo de reconciliação detecta usos conflitantes. A prevenção  entre dois ônibus simultaneamente desconectados não é garantível sem coordenação; nesse período, o sistema aceita um risco controlado e detecta/compensa a duplicidade posteriormente.
2. **Saldo entre recarga e ônibus:** o serviço de cartões mantém o saldo autoritário, enquanto o validador opera com uma visão limitada, assinada, versionada e sincronizada. Recargas e débitos possuem identificadores idempotentes, e divergências são tratadas por reconciliação, sem usar uma projeção CQRS atrasada para autorizar novas operações.
3. **Pico de telemetria:** posições entram por um canal de eventos particionado e são consumidas independentemente; a fila absorve o pico e impede que telemetria concorra diretamente com validação e recarga;
4. **Mudança de tarifa no meio do mês:** regras são versionadas e possuem período de vigência; o pipeline de repasse reproduz os eventos de viagem e aplica a versão válida na data de cada evento
5. **Histórico e LGPD:** informações financeiras necessárias à conciliação permanecem mascaradas e separadas dos dados identificadores; o pedido de eliminação remove ou anonimiza o vínculo pessoal sem apagar os fatos financeiros que possuam informação legal de conservação.

## Referência

ABREU, Douglas H. S. *Estilos Arquiteturais de Software: guia de consulta*. Versão de 8 set. 2026.