## ADR 0001 — Adotar arquitetura celular combinada com monolito modular e serverless
### 1 - O trecho

ADR 0001, campo Decisão, item 2: "Monolito Modular dentro de cada célula para concentrar validação, recargas e repasse financeiro em um único processo com módulos isolados e banco relacional por esquemas". Trecho do arquivo `2-Arquitetura/Documento de Arquitetura de Software - SIMUB.pdf`, seção 3, página 10.

### 2 - O argumento

A divisão em células faz sentido para impedir que uma cidade afete a outra. A dúvida é como o repasse vai funcionar junto das recargas e da validação no mesmo processo. Na resposta à pergunta 4, página 16, o grupo diz que vai reprocessar todas as viagens do mês para recalcular o repasse. Se isso acontecer durante um pico de recargas ou enquanto os ônibus enviam viagens acumuladas, essas tarefas podem disputar memória, processamento e acesso ao banco.

O ADR não explica como essa disputa será controlada. Separar os módulos organiza o código, mas eles continuam usando os recursos do mesmo processo. Isso pesa no Envelope D, que atende cidades de tamanhos diferentes: uma cidade maior pode precisar aumentar toda a aplicação só para dar conta do fechamento mensal. O Serverless atende às consultas dos passageiros, então não resolve esse problema. A catraca continua funcionando offline, mas as recargas e a sincronização podem ficar mais lentas.

### 3 - A saída

Manter as células e o monolito modular, mas executar o repasse em um processo separado, usando as mesmas regras do projeto. Assim, seria possível aumentar a capacidade do repasse sem aumentar toda a aplicação. Como o banco ainda seria compartilhado, o cálculo deveria trabalhar com lotes menores e um limite de conexões.

Antes de definir esses limites, testar o fechamento junto de um pico de recargas e envio de viagens. Haveria mais um processo para a equipe cuidar, mas sem precisar dividir todo o sistema em microsserviços para os 25 desenvolvedores manterem.


## ADR 0002 — Isolar modelo de escrita por eventos e pseudonimização de dados pessoais
### 1 - O trecho

ADR 0002: "Event Sourcing no Repasse Contábil: o subdomínio financeiro armazena as transações de viagem e recargas exclusivamente como um fluxo imutável de eventos (ViagemValidada, RecargaEfetuada) em tabela relacional append-only."

### 2 - O argumento

O Envelope D limita a equipe a 25 desenvolvedores para atender vários municípios. A decisão de usar Event Sourcing no Repasse Contábil é coerente com a necessidade de manter uma trilha auditável e recalcular tarifas, mas transforma o fluxo de eventos na fonte dos fatos financeiros do subdomínio.
O próprio ADR reconhece o lado negativo dessa escolha: a necessidade de manter rotinas de snapshots para otimizar a reprodução dos eventos. Para um time pequeno, esse custo pode se multiplicar a cada novo município, especialmente com o versionamento de eventos, a atualização de esquemas e a operação dessas rotinas em cada célula.
Como o repasse é um processo mensal e as alterações de tarifa exigem o reprocessamento do período afetado, questionamos se os snapshots devem ser um requisito operacional para cada fechamento, ou se o cálculo pode ser executado em lote diretamente sobre os eventos imutáveis e pseudonimizados.

### 3 - A saída

Manter a tabela relacional append-only para guardar os fatos imutáveis e pseudonimizados (viagens e recargas), preservando o uso de tokens opacos e o mecanismo de desvinculação previsto no ADR. No fechamento mensal, processar em lote apenas o período necessário e gravar o resultado do repasse em um Ledger Contábil Imutável, também append-only, atrelado à versão da regra de tarifa vigente na época.
Se uma tarifa mudar no passado, o sistema reprocessará em lote apenas os eventos e as regras daquele período. A diferença calculada será gravada como um novo lançamento de ajuste, sem apagar o histórico nem alterar os identificadores pseudonimizados. A exclusão cadastral e a destruição da chave de decifra continuarão ocorrendo por desvinculação e crypto-shredding, sem modificar os registros contábeis.
Isso preserva imutabilidade, auditoria, rastreabilidade e conformidade com a LGPD. Os snapshots deixam de ser um requisito para a correção do fechamento mensal e passam a ser apenas uma otimização opcional para acelerar a reprodução dos eventos. Dessa forma, reduzimos a complexidade de sustentação para os 25 desenvolvedores sem substituir a decisão de manter os fatos financeiros como eventos imutáveis.


## ADR 0003
### 1 - O trecho
### 2 - O argumento
### 3 - A saída

## ADR 0004
### 1 - O trecho

ADR 0004, campo Decisão: "As atualizações ocorrerão obrigatoriamente por implantação em ondas (Canary por Célula): uma cidade piloto recebe a versão nova, permanece sob monitoração sintética por 60 minutos e apenas então a versão é promovida para as demais células." E, no campo Alternativas consideradas: "Cluster Kubernetes unificado com Service Mesh complexo: descartada por demandar esforço contínuo de sustentação que consumiria metade do time de 25 desenvolvedores."

### 2 - O argumento

A ADR rejeita a "Atualização simultânea global (Big Bang)" por violar a contenção de raio de impacto do Envelope D, mas a decisão escrita promove a versão nova para todas as cidades restantes de uma vez só, depois de validar em uma única cidade piloto. Isso é Big Bang para cada cidade que não é a piloto: se o defeito só aparece sob uma condição que a piloto não tinha (carga, fuso horário, ou um plugin de regra tarifária específico de outro município, previsto no Microkernel da própria arquitetura), ele atinge todas as demais células ao mesmo tempo, exatamente o cenário que a alternativa descartada deveria evitar. O livro-referência do próprio grupo, no ADR de exemplo do capítulo de arquitetura celular, resolve isso com implantação em ondas de uma célula por vez, com trinta minutos de observação entre cada uma, não piloto-depois-todo-o-resto. Além disso, o ADR descarta a malha de serviços pelo custo de sustentação, mas não estima o custo de construir e manter, do zero, um motor de canary multi-tenant com monitoração sintética por célula e corte automático em 60 minutos, sem qualquer procedimento manual. Sem essa conta, não dá pra saber se a alternativa escolhida é de fato mais barata do que a rejeitada.

### 3 - A saída

Implantar em ondas sucessivas de tamanho crescente (por exemplo, 1 cidade, depois 3, depois 10, depois o restante), cada onda com sua própria janela de observação sintética, avançando para a próxima só se a anterior passar, o que mantém o raio de impacto de uma implantação defeituosa contido em uma fração pequena da base a cada vez. A primeira onda deve incluir cidades com plugins tarifários distintos entre si, não uma única cidade fixa, para cobrir a diversidade de configuração antes de promover para o restante. Para não repetir o custo de sustentação que a malha de serviços teria, usar uma ferramenta de entrega progressiva já existente para orquestrar as ondas, em vez de construir esse motor internamente.

## ADR 0005
### 1 - O trecho
### 2 - O argumento
### 3 - A saída
