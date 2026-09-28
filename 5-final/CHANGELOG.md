### Mudanças Realizadas a partir das objeções recebidas:

1. Para a objeção 3: A arquitetura celular do ADR 0005 não aparece na arquitetura executável.

O ADR 0005 já definia que Cartões e Recarga e o backend de Validação seriam implantados em células independentes, com os cartões distribuídos por uma chave de roteamento estável, sendo assim a mudança não contradiz o ADR ele se mantém o mesmo do início.
O problema era que nosso C4 mostrava esses serviços e o banco apenas uma vez. Então corrigimos o diagrama para representar explicitamente múltiplas células, cada uma com seus serviços críticos e seu armazenamento, mantendo os demais subdomínios fora das células.
Portando, a principal diferença é que os três elementos críticos que antes apareciam uma vez agora aparecem por célula.