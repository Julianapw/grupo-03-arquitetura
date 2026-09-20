# Spike: saldo autoritário e reconciliação offline (ADR 0002)

## O que prova

Este código prova a decisão mais arriscada do projeto, registrada na ADR 0002: o saldo autoritário do cartão vive no backend, o validador embarcado decide localmente sem rede, e a reconciliação, quando a conexão volta, precisa lidar ao mesmo tempo com uso duplicado, recarga online e reentrega de rede sem duplicar débito ou crédito.

A simulação cobre quatro mecanismos num único fluxo:

1. **Decisão offline**: dois ônibus (onibus-101 e onibus-205) validam passagens usando só o saldo em cache local, sem chamar o backend. O cartão-A, com R$ 6,00, é aceito nos dois ônibus com 4 minutos de diferença; cada um vê saldo positivo na própria cópia, porque nenhum sabe do outro.
2. **Recarga online**: enquanto os ônibus seguem offline, uma recarga de app chega direto ao backend e entra no mesmo saldo autoritário que os débitos embarcados vão atualizar depois.
3. **Reentrega idempotente**: o mesmo lote de um ônibus e a mesma recarga chegam duas vezes ao backend (simulando uma rede que confirma tarde e reenvia). O backend reconhece o identificador já processado e ignora a segunda entrega, então nada é debitado ou creditado em dobro por causa da rede.
4. **Duplicidade física**: depois de reconciliar os débitos legítimos, o backend cruza os eventos aceitos por horário. Como o cartão-A foi aceito em dois ônibus diferentes com só 4 minutos de intervalo, o backend aponta uso duplicado, fecha o saldo autoritário em -R$ 4,00 e bloqueia o cartão para a próxima sincronização.

## Como rodar

```
cd 3-spike
python3 spike.py
```

Usa só biblioteca padrão do Python 3.12. O próprio script imprime o resultado na tela e, ao mesmo tempo, grava exatamente o mesmo conteúdo em `saida-esperada.txt`, na mesma pasta. Não é preciso redirecionar a saída manualmente; rodar o comando acima já gera o arquivo.

## O que aconteceria se a decisão estivesse errada

Se o validador exigisse confirmação online a cada passagem, os dois ônibus não teriam aceitado nenhum embarque durante a desconexão, descumprindo o SLA de 99,9% nas janelas de até 4 horas sem 4G previstas no caso.

Se o backend não fosse idempotente por identificador de transação, qualquer reenvio de rede, comum quando a confirmação demora e o ônibus tenta de novo, debitaria ou creditaria o mesmo valor mais de uma vez, cobrando passageiros a mais ou multiplicando recargas por engano.

E se ninguém cruzasse os eventos aceitos por horário depois da reconciliação, a duplicidade do cartão-A nunca seria descoberta: o saldo ficaria negativo sem explicação, o cartão continuaria sendo usado normalmente, e o prejuízo se acumularia sem deixar rastro para auditoria.