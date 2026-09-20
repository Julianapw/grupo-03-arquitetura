"""
Spike da ADR 0002: saldo autoritario e validacao embarcada local durante
ausencia de conexao.

Prova quatro coisas ao mesmo tempo:
1. O validador decide sozinho, sem rede, usando so o saldo em cache local,
   entao a passagem continua funcionando durante a desconexao.
2. O mesmo cartao pode ser aceito em dois onibus desconectados ao mesmo
   tempo, e isso e descoberto pelo horario na reconciliacao.
3. Uma recarga feita pelo aplicativo entra no mesmo fluxo de reconciliacao
   do backend, que e o dono do saldo autoritario.
4. Reentrega de rede (o mesmo lote ou a mesma recarga chegando duas vezes
   ao backend) nao debita nem credita em dobro, porque o backend e
   idempotente por identificador unico de transacao.
"""

import sys
from dataclasses import dataclass, field
from decimal import Decimal
from io import StringIO

ARQUIVO_SAIDA = "saida-esperada.txt"


TARIFA = Decimal("5.00")


@dataclass(frozen=True)
class Validacao:
    id: str
    cartao_id: str
    onibus_id: str
    minuto: int
    decisao: str  # "aceita" ou "recusada"


@dataclass
class ValidadorEmbarcado:
    onibus_id: str
    saldo_local: dict = field(default_factory=dict)
    cartoes_bloqueados_localmente: set = field(default_factory=set)
    log_local: list = field(default_factory=list)

    def receber_snapshot_de_saldo(self, saldos: dict) -> None:
        self.saldo_local.update(saldos)

    def validar(self, cartao_id: str, minuto: int) -> Validacao:
        if cartao_id in self.cartoes_bloqueados_localmente:
            decisao = "recusada"
        else:
            saldo_conhecido = self.saldo_local.get(cartao_id, Decimal("0.00"))
            if saldo_conhecido >= TARIFA:
                decisao = "aceita"
                self.saldo_local[cartao_id] = saldo_conhecido - TARIFA
            else:
                decisao = "recusada"

        evento = Validacao(
            id=f"{self.onibus_id}-{len(self.log_local) + 1}",
            cartao_id=cartao_id, onibus_id=self.onibus_id,
            minuto=minuto, decisao=decisao,
        )
        self.log_local.append(evento)
        return evento

    def sincronizar(self) -> list:
        return list(self.log_local)

    def receber_lista_de_bloqueio(self, cartoes: set) -> None:
        self.cartoes_bloqueados_localmente |= cartoes


class BackendDeReconciliacao:

    JANELA_MINIMA_MINUTOS = 5

    def __init__(self, saldos_iniciais: dict) -> None:
        self.saldo_autoritativo = dict(saldos_iniciais)
        self.processados: set = set()
        self.eventos_aceitos: list[Validacao] = []
        self.conflitos: list = []
        self.bloqueados: set = set()

    def creditar_recarga(self, id_transacao: str, cartao_id: str, valor: Decimal) -> None:
        if id_transacao in self.processados:
            print(f"  -> [IGNORADA] recarga {id_transacao} ja processada (reentrega de rede)")
            return
        self.processados.add(id_transacao)
        self.saldo_autoritativo[cartao_id] = self.saldo_autoritativo.get(cartao_id, Decimal("0")) + valor
        print(f"  -> [RECARGA] {cartao_id} +R$ {valor} | saldo: R$ {self.saldo_autoritativo[cartao_id]}")

    def reconciliar_lote(self, nome_lote: str, eventos: list) -> None:
        print(f"\n--- reconciliando {nome_lote} ({len(eventos)} evento(s)) ---")
        for evento in eventos:
            if evento.id in self.processados:
                print(f"  -> [IGNORADA] {evento.id} ja processado (reentrega de rede)")
                continue
            self.processados.add(evento.id)
            if evento.decisao != "aceita":
                continue
            self.saldo_autoritativo[evento.cartao_id] -= TARIFA
            self.eventos_aceitos.append(evento)
            saldo = self.saldo_autoritativo[evento.cartao_id]
            status = "conflito, saldo negativo" if saldo < 0 else "ok"
            if saldo < 0:
                self.conflitos.append(f"{evento.cartao_id} ficou negativo em {evento.id} ({evento.onibus_id})")
            print(f"  -> [DEBITO] {evento.cartao_id} -R$ {TARIFA} | saldo: R$ {saldo} | {status}")

    def detectar_duplicidade_fisica(self) -> list:
        alertas = []
        por_cartao: dict = {}
        for e in self.eventos_aceitos:
            por_cartao.setdefault(e.cartao_id, []).append(e)
        for cartao_id, lista in por_cartao.items():
            lista_ordenada = sorted(lista, key=lambda v: v.minuto)
            for anterior, atual in zip(lista_ordenada, lista_ordenada[1:]):
                mesmo_onibus = anterior.onibus_id == atual.onibus_id
                intervalo = atual.minuto - anterior.minuto
                if not mesmo_onibus and intervalo < self.JANELA_MINIMA_MINUTOS:
                    alertas.append(
                        f"cartao {cartao_id}: aceito em {anterior.onibus_id} no minuto "
                        f"{anterior.minuto} e em {atual.onibus_id} no minuto {atual.minuto} "
                        f"(intervalo de {intervalo} min) -- fisicamente impossivel"
                    )
                    self.bloqueados.add(cartao_id)
        return alertas


def main() -> None:
    print("SPIKE: valida a ADR 0002 (saldo autoritario e reconciliacao offline)\n")

    saldos_iniciais = {
        "cartao-A": Decimal("6.00"),
        "cartao-B": Decimal("10.00"),
        "cartao-C": Decimal("20.00"),
    }
    backend = BackendDeReconciliacao(saldos_iniciais)
    onibus_101 = ValidadorEmbarcado(onibus_id="onibus-101")
    onibus_205 = ValidadorEmbarcado(onibus_id="onibus-205")
    onibus_101.receber_snapshot_de_saldo(saldos_iniciais)
    onibus_205.receber_snapshot_de_saldo(saldos_iniciais)

    print(f"Tarifa: R$ {TARIFA} | Saldos iniciais: "
          f"{ {k: str(v) for k, v in saldos_iniciais.items()} }\n")

    print("Fase 1 - os dois onibus estao sem conexao 4G, decidindo so com o saldo local.\n")
    turno = [
        (onibus_101, "cartao-A", 0),
        (onibus_101, "cartao-B", 3),
        (onibus_205, "cartao-A", 4),   # mesmo cartao-A, 4 min depois, outro onibus
        (onibus_101, "cartao-C", 10),
        (onibus_205, "cartao-C", 40),  # mesmo cartao-C, 40 min depois, sem alerta
    ]
    for validador, cartao_id, minuto in turno:
        evento = validador.validar(cartao_id, minuto)
        print(f"[offline] {evento.onibus_id} minuto {evento.minuto:>3}: "
              f"cartao {evento.cartao_id} -> {evento.decisao}")

    print("\nFase 2 - enquanto os onibus seguem offline, uma recarga chega pelo app "
          "(canal online, direto no backend).")
    backend.creditar_recarga("recarga-app-b-1", "cartao-B", Decimal("20.00"))

    print("\nFase 3 - os onibus reconectam e enviam os lotes ao backend.")
    lote_101 = onibus_101.sincronizar()
    lote_205 = onibus_205.sincronizar()
    backend.reconciliar_lote("lote onibus-101", lote_101)
    backend.reconciliar_lote("lote onibus-205", lote_205)

    print("\nFase 4 - reentrega de rede: o mesmo lote e a mesma recarga chegam de novo.")
    backend.reconciliar_lote("lote onibus-101 (reenviado)", lote_101)
    backend.creditar_recarga("recarga-app-b-1", "cartao-B", Decimal("20.00"))

    print("\nFase 5 - o backend cruza os eventos aceitos por horario, entre onibus diferentes.")
    alertas = backend.detectar_duplicidade_fisica()
    if alertas:
        print("Alertas de uso duplicado:")
        for a in alertas:
            print(f" - {a}")

    print("\nRELATORIO FINAL")
    for cartao_id in sorted(backend.saldo_autoritativo):
        saldo = backend.saldo_autoritativo[cartao_id]
        marcador = " <- negativo" if saldo < 0 else ""
        print(f" - {cartao_id}: R$ {saldo}{marcador}")
    print(f"\nTransacoes unicas processadas: {len(backend.processados)}")
    print(f"Conflitos de saldo negativo: {backend.conflitos or 'nenhum'}")
    print(f"Cartoes bloqueados: {sorted(backend.bloqueados) or 'nenhum'}")

    print("\nFase 6 - proxima conexao: onibus recebem a lista de bloqueio e recusam o cartao.")
    onibus_101.receber_lista_de_bloqueio(backend.bloqueados)
    evento_final = onibus_101.validar("cartao-A", 100)
    print(f"[offline] {evento_final.onibus_id} minuto {evento_final.minuto:>3}: "
          f"cartao {evento_final.cartao_id} -> {evento_final.decisao}")


class _Tee:

    def __init__(self, *destinos) -> None:
        self._destinos = destinos

    def write(self, dado: str) -> None:
        for destino in self._destinos:
            destino.write(dado)

    def flush(self) -> None:
        for destino in self._destinos:
            destino.flush()


if __name__ == "__main__":
    buffer = StringIO()
    saida_original = sys.stdout
    sys.stdout = _Tee(saida_original, buffer)
    try:
        main()
    finally:
        sys.stdout = saida_original

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo:
        arquivo.write(buffer.getvalue())