# ADR 0002: manter o saldo autoritário no serviço de cartões e reconciliar operações offline

**Status:** aceito

**Contexto:** O sistema possui 2,5 milhões de cartões ativos, cerca de 150 mil recargas por dia e validadores que podem permanecer até quatro horas sem conexão 4G. Durante esse período, uma recarga feita no aplicativo pode não ser conhecida pelo ônibus, enquanto débitos realizados no ônibus ainda não chegaram ao backend. Portanto, não é possível manter consistência forte e imediata entre todos os validadores e o sistema central enquanto houver desconexão.

**Decisão:** Manter o saldo autoritário no serviço de Cartões e Recarga e permitir que o validador opere offline com uma visão local limitada, assinada e versionada. Recargas e débitos terão identificadores únicos e serão reconciliados de forma idempotente quando a comunicação for restabelecida.

**Alternativas consideradas:**

* Exigir consulta online ao saldo antes de cada validação: descartada porque a rede 4G pode ficar indisponível por até quatro horas e a passagem precisa continuar sendo validada.
* Considerar o saldo armazenado no cartão ou validador como única fonte de verdade: descartada porque diferentes ônibus desconectados e canais de recarga poderiam manter estados divergentes.
* Usar uma projeção CQRS como fonte para autorização: descartada porque projeções atualizadas de forma assíncrona podem apresentar saldo atrasado e não devem autorizar operações financeiras.

**Consequências:**

* **Positivas:** existe uma fonte autoritária para o saldo; a passagem continua funcionando durante períodos sem 4G; operações repetidas durante a sincronização não alteram o saldo mais de uma vez devido à idempotência; divergências podem ser identificadas e reconciliadas posteriormente.
* **Negativas:** o saldo conhecido pelo validador pode ficar temporariamente desatualizado; uma recarga realizada durante a desconexão pode não ficar disponível imediatamente no ônibus; são necessários mecanismos adicionais de versionamento, assinatura, idempotência e reconciliação; durante a desconexão aceita-se consistência eventual e um risco controlado de divergência.
