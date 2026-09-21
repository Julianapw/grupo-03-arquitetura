# C4 nível 2 e pergunta 1 — referências e integração

O [diagrama unificado](c4-containers.png) reúne a parte de nuvem/APIs da Júlia Kimura com a parte de borda/Kafka do Kauê. O [Mermaid](c4-containers.mmd) é a fonte editável. A resposta está na pergunta 1 de [perguntas.md](perguntas.md).

## Referências

- **ABREU, Douglas H. S.** *Um problema, cinco realidades*. PUC-Campinas, 2026-2. Caso Ônibus, Envelope B: fonte das premissas de volume, prazo sem rede e resposta em até 300 ms.
- **ABREU, Douglas H. S.** *Estilos Arquiteturais de Software: guia de consulta*. Versão de 8 set. 2026. Base da matriz da Entrega 1. Nesta integração, as escolhas seguem os ADRs 0001, 0002, 0003 e 0005 já escritos pelo grupo.
- **BROWN, Simon.** [Container diagram](https://c4model.com/diagrams/container) e [Notation](https://c4model.com/diagrams/notation). C4 Model. Consultados em 20 set. 2026. Aplicações, armazenamentos, fronteiras e relações do nível 2.
- **APACHE SOFTWARE FOUNDATION.** [Apache Kafka — Design](https://kafka.apache.org/40/design/design/). Documentação 4.0. Consultada em 20 set. 2026. Entrega de eventos, repetição e ordem por partição; a idempotência no banco da aplicação continua necessária.
- **SQLITE.** [Atomic Commit In SQLite](https://www.sqlite.org/atomiccommit.html). Consultado em 20 set. 2026. Transações locais; a configuração e o armazenamento do equipamento precisam ser validados.
- **AMAZON WEB SERVICES.** [Transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html). Consultado em 20 set. 2026. Gravação da operação e da pendência de publicação na mesma transação. A referência não implica escolher AWS.
- **KIMURA, Júlia.** Código Mermaid do C4 nível 2 — nuvem/APIs, compartilhado no grupo. Base do diagrama integrado.

## Como ler o desenho

O código da Júlia foi preservado, incluindo nomes, tecnologias, cores e conexões. O complemento do Kauê está no final do Mermaid: base local, agente de sincronização e consumo das validações pelos serviços de Cartões e Recarga e de Sincronização.

A ligação original do validador com o gateway resume a sincronização. O agente acrescentado detalha quem executa esse envio; não representa um segundo envio do mesmo lote. A base local guarda as operações até a confirmação do backend. Os identificadores são mantidos nos reenvios para evitar outra cobrança.

SQLite é a proposta para a base local. As células do ADR 0005 e os detalhes de persistência e confirmação dos eventos devem ser tratados nos documentos de arquitetura; o complemento não muda a estrutura de nuvem enviada pela Júlia.

## Pontos para a revisão do grupo

- A pergunta 2 descreve escrita de créditos no chip, mas o ADR 0002 define uma visão local assinada e versionada, sem definir esse mecanismo de escrita. A pergunta 1 segue o ADR; a diferença precisa ser alinhada pela equipe.
- Na pergunta 3, tópicos exclusivos não garantem isolamento físico nem armazenamento ilimitado. O desenho original mostra um barramento; o isolamento de recursos e os limites de capacidade precisam ser alinhados com o texto pelo grupo.
- O limite de cinco minutos do spike é uma regra de demonstração. Duas viagens próximas do mesmo cartão podem indicar conflito, mas não comprovam sozinhas uso fraudulento da mesma passagem.

## Gerar o PNG

O conteúdo continua no Mermaid. Para manter as posições da foto, o PNG é gerado pelo script de layout fixo, que lê os textos e conexões desse arquivo. O SVG também fica disponível em `c4-containers.svg`.

Na raiz do repositório, com Python, Playwright e Chrome instalados (o script procura o Chrome no cache local do Puppeteer):

```sh
python 2-arquitetura/renderizar-c4.py
```

O script gera `c4-containers-layout.png`. Após conferir a imagem, copie-a para `c4-containers.png`. Renderizar o Mermaid diretamente usa posicionamento automático e não conserva o layout da foto.
