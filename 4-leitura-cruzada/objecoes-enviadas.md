## ADR 0001
### 1 - O trecho
### 2 - O argumento
### 3 - A saída


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
### 2 - O argumento
### 3 - A saída

## ADR 0005
### 1 - O trecho
### 2 - O argumento
### 3 - A saída
