# Mapa de Restrições → Decisões

O mapa relaciona as principais restrições do caso e do Envelope B às decisões arquiteturais adotadas pelo grupo. O objetivo é demonstrar como cada decisão responde a uma necessidade concreta do sistema.

| Restrição / característica | Decisão arquitetural | Relação |
|---|---|---|
| Os ônibus podem permanecer até 4 horas sem conexão 4G. | Permitir validação embarcada local durante períodos sem conexão. | ADR 0001 |
| Durante a desconexão, o saldo conhecido pelo ônibus pode divergir do backend e de outros canais de recarga. | Manter o saldo autoritário no serviço de Cartões e Recarga e reconciliar posteriormente as operações offline. | ADR 0002 |
| O sistema recebe cerca de 900 mil validações por dia e diferentes consumidores podem processar informações em ritmos distintos. | Utilizar eventos assíncronos persistentes para fatos de negócio que não exigem resposta imediata. | ADR 0003 |
| A telemetria pode atingir pico de 400 posições por segundo. | Processar telemetria de forma assíncrona por eventos, permitindo absorção dos picos sem competir diretamente com validação e recarga. | ADR 0003 |
| A equipe possui 40 desenvolvedores distribuídos em 5 times. | Separar o backend em serviços alinhados aos principais subdomínios de negócio, permitindo maior autonomia de desenvolvimento e implantação. | ADR 0004 |
| Validação e recarga possuem SLA de 99,9%, com multa por indisponibilidade. | Implantar os serviços críticos em células independentes e redundantes, reduzindo o raio de impacto de falhas. | ADR 0005 |
| O sistema precisa integrar banco, adquirente, operadoras e órgão gestor, que podem apresentar falhas ou indisponibilidade próprias. | Isolar integrações externas por adaptadores próprios e utilizar comunicação assíncrona quando não houver necessidade de resposta imediata. | ADR 0003 |
| A tarifa pode mudar no meio do mês e o repasse precisa considerar a regra válida no momento de cada viagem. | Versionar as regras tarifárias e registrar seu período de vigência para permitir o processamento e recálculo correto das viagens. | Decisão de domínio / Repasse e conciliação |
| Passageiros podem solicitar exclusão de seus dados pessoais conforme a LGPD. | Separar dados pessoais identificáveis dos registros financeiros que precisem ser conservados, permitindo apagar ou anonimizar o vínculo pessoal. | Decisão de dados / LGPD |
| O mesmo cartão pode ser utilizado em dois ônibus enquanto ambos estão desconectados. | Registrar cada validação com identificador único e realizar detecção e reconciliação de conflitos após o restabelecimento da comunicação. | ADR 0001 e ADR 0002 |

## Síntese

As decisões priorizam a disponibilidade dos fluxos críticos de validação e recarga, o funcionamento durante períodos sem conectividade e o isolamento de falhas. A separação por subdomínios permite que os cinco times trabalhem com maior autonomia, enquanto eventos assíncronos desacoplam capacidades com diferentes características de carga. A arquitetura também considera requisitos de consistência, integração externa, alteração de tarifas e proteção de dados pessoais.
