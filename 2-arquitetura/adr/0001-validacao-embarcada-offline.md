# ADR 0001: permitir validação embarcada local durante ausência de conexão

**Status:** aceita

**Contexto:**  
O sistema possui 1.200 validadores e realiza cerca de 900 mil validações por dia, com pico de 120 validações por segundo. Os ônibus podem permanecer por até quatro horas sem conexão 4G, mas a validação da passagem é um serviço crítico e está sujeita ao SLA de 99,9%, com multa por indisponibilidade. Portanto, a decisão de aceitar ou recusar uma passagem não pode depender de uma comunicação online com o backend.

**Decisão:**  
Permitir que o validador embarcado realize localmente a decisão de aceitar ou recusar a passagem, utilizando os dados mínimos necessários armazenados no dispositivo. Cada validação será registrada localmente com identificador único, horário, cartão e veículo e, quando a conexão for restabelecida, será sincronizada com o backend para processamento e reconciliação.

**Alternativas consideradas:**

* Exigir comunicação online com o backend em toda validação: descartada porque uma perda de conexão 4G impediria a validação das passagens durante períodos que podem chegar a quatro horas.

* Liberar automaticamente todas as passagens quando não houver conexão: descartada porque manteria a disponibilidade, mas eliminaria controles importantes de tarifa e utilização dos cartões.

* Bloquear todas as validações durante a ausência de conexão: descartada porque tornaria o transporte indisponível sempre que houvesse falha de comunicação e seria incompatível com o SLA dos serviços críticos.

**Consequências:**

* **Positivas:** a validação continua funcionando mesmo sem 4G; falhas temporárias de comunicação não interrompem o embarque; o tempo de resposta da validação não depende da latência da rede; operações realizadas offline podem ser sincronizadas posteriormente.

* **Negativas:** o validador trabalha temporariamente com informações que podem estar desatualizadas; não é possível impedir completamente o uso simultâneo do mesmo cartão em dois ônibus desconectados; é necessário armazenar operações localmente e implementar sincronização e reconciliação após o retorno da conexão.
