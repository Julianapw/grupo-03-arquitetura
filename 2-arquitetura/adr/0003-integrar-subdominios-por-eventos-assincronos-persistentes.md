# ADR 0003: integrar os subdomínios por eventos assíncronos persistentes

**Status:** aceita

**Contexto:** O sistema recebe cerca de 900 mil validações por dia e telemetria contínua dos 1.200 ônibus, além de integrar componentes com características diferentes de disponibilidade e escala. Os validadores podem permanecer desconectados por até quatro horas, e picos de telemetria não devem consumir recursos dos fluxos críticos de validação e recarga. Também existem integrações externas com órgão gestor, operadoras, banco e adquirente, cujas indisponibilidades não podem interromper os demais subdomínios.

**Decisão:** Usar eventos assíncronos persistentes como padrão de integração para fatos de negócio que não exigem resposta imediata, incluindo validações sincronizadas, alterações de saldo e telemetria. Chamadas síncronas serão mantidas apenas quando o fluxo exigir resposta imediata, e integrações externas serão isoladas por adaptadores próprios.

**Alternativas consideradas:**

* Integrar todos os serviços por chamadas síncronas: descartada porque aumenta o acoplamento temporal e permite que indisponibilidade ou lentidão de um serviço se propague aos demais.
* Utilizar um ESB central para toda a comunicação: descartada porque concentraria grande parte das integrações em um componente que pode ampliar o impacto de uma falha e acrescentaria um salto desnecessário aos fluxos críticos.
* Compartilhar diretamente bancos de dados entre os serviços: descartada porque quebra a propriedade dos dados por subdomínio e aumenta o acoplamento entre equipes e serviços.

**Consequências:**

* **Positivas:** produtores e consumidores ficam temporalmente desacoplados; a fila absorve picos sem exigir que todos os consumidores processem na mesma velocidade; telemetria pode escalar independentemente; eventos gerados offline podem ser enviados quando a conexão retornar; falhas temporárias de consumidores ou integrações externas não precisam interromper o produtor.
* **Negativas:** os fluxos passam a trabalhar com consistência eventual; a entrega pode ocorrer mais de uma vez, exigindo consumidores idempotentes e identificadores únicos; investigação de falhas exige correlação e rastreamento distribuído; contratos e versões dos eventos precisam ser governados entre os cinco times.
