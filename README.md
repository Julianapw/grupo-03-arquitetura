# Sistema de Bilhetagem e Mobilidade Urbana

**Grupo 03 | Envelope 02**

Ana Beatriz Maranho, Kaue Farias, Julia Kimura, Juliana Prado, Matias Amma e Ruan Dias Da Silva.

Este repositório reúne o projeto de arquitetura para o novo sistema de bilhetagem eletrônica da cidade, desenvolvido para a disciplina de Arquitetura de Software. O caso é o do transporte público (Caso Ônibus), com a situação sorteada correspondente ao Envelope 02.

## O cenário (Envelope 02 — Consórcio)

O sistema é desenvolvido por um consórcio de empresas de tecnologia, contratado formalmente pelo órgão gestor, e não por uma equipe pequena ou por um time interno do próprio órgão. Essa condição inicial influencia diretamente as decisões arquiteturais possíveis.

- Equipe de 40 desenvolvedores, organizada em 5 times.
- Orçamento robusto, nuvem pública e equipe própria de operação, o que permite considerar soluções de maior custo e complexidade operacional.
- Contrato com SLA de 99,9% e multa contratual por indisponibilidade, o que exige atenção especial a resiliência, redundância e observabilidade.

A divisão em 5 times também é um fator relevante: a arquitetura precisa permitir que esses times trabalhem em paralelo, com fronteiras de responsabilidade bem definidas entre os componentes do sistema.

## Premissas do sistema

| Premissa | Valor |
|---|---|
| Frota | 1.200 ônibus, cada um com validador embarcado |
| Validações | 900 mil/dia útil, pico de 120/s (6h30–8h30) |
| Cartões ativos | 2,5 milhões (25% com gratuidade ou desconto: estudante, idoso, PCD) |
| Recargas | 150 mil/dia (app, loja física, totem) |
| Telemetria | posição GPS por ônibus a cada 15s |
| Rede no ônibus | 4G intermitente, até 4h sem conexão em trechos do trajeto |
| Repasse financeiro | fechamento mensal por operadora, auditado, contestação em até 30 dias |
| Dados pessoais | histórico de viagens identificado é dado pessoal (LGPD) |

## Os subdomínios

| Subdomínio | O que faz | Natureza |
|---|---|---|
| Validação embarcada | aceita ou recusa a passagem no ônibus | tempo real, alto volume, sem rede |
| Cartões e recarga | saldo, recarga, bloqueio, gratuidades | transacional, envolve dinheiro |
| Telemetria da frota | recebe posição e estado dos veículos | fluxo contínuo |
| Informação ao passageiro | previsão de chegada, app, painéis | analítico, tolera atraso |
| Repasse e conciliação | calcula quanto cada operadora recebe | lote mensal, auditável |
| Integração externa | órgão gestor, operadoras, banco, adquirente | contratos formais, legado |
| Atendimento | segunda via, contestação, cadastro de gratuidade | transacional, baixo volume |

## Perguntas que a arquitetura precisa responder

1. Como o validador aceita a passagem sem rede, e como o sistema descobre depois que a mesma passagem foi usada em dois ônibus?
2. Como o saldo do cartão fica consistente entre recarga no app e uso no ônibus, com atraso de sincronização?
3. Como a telemetria escala no pico sem derrubar o resto do sistema?
4. Como o repasse mensal é recalculado se a regra de tarifa mudou no meio do mês?
5. Como o histórico de viagens de uma pessoa é apagado quando ela pede, sem quebrar a conciliação financeira?
