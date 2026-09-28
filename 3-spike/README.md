# Spike: saldo autoritário e reconciliação offline (ADR 0002)

## O que prova

Este código demonstra o mecanismo da ADR 0002: o saldo autoritário fica no backend, o validador decide localmente sem rede e as operações são processadas quando a conexão volta. A simulação mostra a recarga online, o tratamento de registros reenviados sem repetir débitos ou créditos e a identificação de divergências. Ela não define como resolver financeiramente essas divergências.

A simulação cobre quatro mecanismos num único fluxo:

1. **Decisão offline**: dois ônibus (onibus-101 e onibus-205) validam passagens usando só o saldo em cache local, sem chamar o backend. O cartão-A, com R$ 6,00, é aceito nos dois ônibus com 4 minutos de diferença; cada um vê saldo positivo na própria cópia, porque nenhum sabe do outro.
2. **Recarga online**: enquanto os ônibus seguem offline, uma recarga de app chega direto ao backend e entra no mesmo saldo autoritário que os débitos embarcados vão atualizar depois.
3. **Reentrega idempotente**: o mesmo lote de um ônibus e a mesma recarga chegam duas vezes ao backend (simulando uma rede que confirma tarde e reenvia). O backend reconhece o identificador já processado e ignora a segunda entrega, então nada é debitado ou creditado em dobro por causa da rede.
4. **Suspeita de conflito**: o backend compara os usos do mesmo cartão em ônibus diferentes. No exemplo, o intervalo de 4 minutos gera um alerta pela regra de menos de 5 minutos. Essa regra é apenas demonstrativa: sem considerar localização e regras de integração, o intervalo não comprova fraude nem reutilização da mesma passagem. O script também bloqueia o cartão para a próxima sincronização, como parte do exemplo, não como uma política definitiva de bloqueio.

O saldo do cartão-A termina em **-R$ 4,00** porque o backend aplica duas operações diferentes de R$ 5,00 ao saldo inicial de R$ 6,00. Isso mostra a divergência causada pelo uso das cópias locais durante a desconexão; não é uma cobrança repetida por reenvio de mensagem. O experimento detecta e registra essa situação, mas não decide quais cobranças devem ser mantidas ou estornadas, quem assume a diferença nem como funciona a contestação. Essas decisões dependem de uma política de negócio que ainda precisa ser definida. O bloqueio demonstrado não resolve o saldo negativo.

## Como rodar

```
cd 3-spike
python3 spike.py
```

Usa só biblioteca padrão do Python 3.12. O próprio script imprime o resultado na tela e, ao mesmo tempo, grava exatamente o mesmo conteúdo em `saida-esperada.txt`, na mesma pasta. Não é preciso redirecionar a saída manualmente; rodar o comando acima já gera o arquivo.

## O que aconteceria se a decisão estivesse errada

Se o validador exigisse confirmação online a cada passagem, os dois ônibus não teriam aceitado nenhum embarque durante a desconexão, descumprindo o SLA de 99,9% nas janelas de até 4 horas sem 4G previstas no caso.

Se o backend não fosse idempotente por identificador de transação, qualquer reenvio de rede, comum quando a confirmação demora e o ônibus tenta de novo, debitaria ou creditaria o mesmo valor mais de uma vez, cobrando passageiros a mais ou multiplicando recargas por engano.

Sem comparar os usos por horário, o backend ainda registraria o saldo negativo, mas não geraria o alerta sobre as viagens próximas em ônibus diferentes. Esse alerta ajuda a encaminhar o caso para análise; sozinho, não comprova fraude nem resolve a diferença financeira.
