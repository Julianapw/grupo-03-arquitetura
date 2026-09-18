# ADR 0005: implantar os serviços críticos em células independentes e redundantes

**Status:** aceita

**Contexto:** O contrato estabelece SLA de 99,9% para validação e recarga, com multa por indisponibilidade. O ambiente dispõe de nuvem pública, orçamento robusto e equipe própria de operação, permitindo assumir maior complexidade operacional em troca de isolamento de falhas. Uma falha que atinja toda a base de cartões ou todo o backend de validação teria impacto incompatível com essa restrição.

**Decisão:** Implantar os serviços críticos de Cartões e Recarga e o backend de Validação em células independentes e redundantes na nuvem pública, distribuindo cartões entre células por uma chave de roteamento estável. Componentes compartilhados deverão ser reduzidos ao mínimo necessário para evitar que uma falha comum torne todas as células indisponíveis.

**Alternativas consideradas:**

* Executar uma única implantação central dos serviços críticos com escalabilidade horizontal: descartada porque, apesar de aumentar capacidade, mantém um domínio de falha amplo e permite que determinados incidentes afetem toda a base.
* Replicar toda a aplicação sem particionar a base em células: descartada porque melhora redundância de instâncias, mas não limita suficientemente o raio de impacto de falhas de dados, configuração ou implantação.
* Aplicar arquitetura celular a todos os subdomínios: descartada porque atendimento, informação ao passageiro e processamento mensal de repasse não possuem o mesmo requisito de disponibilidade dos fluxos críticos e não justificam inicialmente o custo operacional adicional.

**Consequências:**

* **Positivas:** uma falha em uma célula afeta somente uma parcela dos cartões e operações; capacidade pode ser acrescentada por célula; implantações podem ser realizadas progressivamente, reduzindo o raio de impacto de versões defeituosas; a estratégia contribui para atender ao SLA de 99,9% dos serviços críticos.
* **Negativas:** infraestrutura, observabilidade, configuração e implantação tornam-se mais complexas; componentes precisam ser replicados entre células; o roteamento precisa localizar de forma consistente a célula responsável por cada cartão; operações que atravessem células exigem tratamento explícito; o custo de nuvem e de operação aumenta.
