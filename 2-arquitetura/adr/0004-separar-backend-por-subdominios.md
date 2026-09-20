# ADR 0004: separar o backend por subdomínios de negócio

**Status:** aceita

**Contexto:**  
O sistema possui responsabilidades com características distintas de escala e disponibilidade, incluindo validação, cartões e recarga, telemetria, informação ao passageiro, repasse e conciliação, integração externa e atendimento. Além disso, o projeto possui 40 desenvolvedores distribuídos em cinco times, enquanto validação e recarga possuem SLA de 99,9% com multa por indisponibilidade. Manter todas essas capacidades em uma única unidade de implantação aumentaria o acoplamento entre os times e dificultaria a evolução e o isolamento dos serviços críticos.

**Decisão:**  
Separar o backend em serviços alinhados aos principais subdomínios de negócio, com responsabilidades e propriedade de dados claramente definidas. Cada serviço poderá ser desenvolvido, implantado e escalado de forma independente, enquanto a integração assíncrona entre os subdomínios seguirá a estratégia definida no ADR 0003.

**Alternativas consideradas:**

* Utilizar um único monolito para todo o backend: descartada porque os cinco times teriam de coordenar alterações e implantações em uma única unidade, além de dificultar o isolamento e a escala independente dos serviços críticos.

* Dividir os serviços apenas por camadas técnicas, como apresentação, negócio e dados: descartada porque uma mesma funcionalidade de negócio atravessaria vários serviços, aumentando o acoplamento entre equipes.

* Criar serviços muito pequenos para cada operação do sistema: descartada porque aumentaria desnecessariamente a quantidade de serviços, contratos, chamadas de rede e componentes operacionais.

**Consequências:**

* **Positivas:** os cinco times possuem maior autonomia de desenvolvimento e implantação; subdomínios com cargas diferentes podem escalar independentemente; falhas podem ser melhor isoladas; alterações em uma capacidade de negócio não exigem necessariamente a implantação de todo o backend.

* **Negativas:** aumenta a complexidade operacional; são necessários contratos claros entre os serviços; observabilidade e rastreamento distribuído tornam-se necessários; operações envolvendo vários subdomínios precisam tratar explicitamente consistência e falhas distribuídas.
