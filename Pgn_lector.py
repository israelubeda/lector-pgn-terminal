
import sys
from pathlib import Path

import chess
import chess.pgn
from color_latam import color_hex, colorear

# Paleta visual
CLARA = "#D9C7A5"
OSCURA = "#657E65"
ORIGEN = "#D49A48"
DESTINO = "#E5C85B"
PIEZA_BLANCA = "#FFFFFF"
PIEZA_NEGRA = "#151A24"

PIEZAS = {
    "P": "♙", "N": "♘", "B": "♗",
    "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝",
    "r": "♜", "q": "♛", "k": "♚",
}

RESET = "\033[0m"


def prefijo_color(hexadecimal, fondo=False):
    """Obtiene el código ANSI generado por color_latam."""
    marcador = "__PIEZA__"
    cadena = color_hex(
        marcador, hexadecimal, fondo=fondo
    )
    return cadena.split(marcador, 1)[0]


def casilla(texto, fondo, frente):
    return (
        prefijo_color(fondo, fondo=True)
        + prefijo_color(frente)
        + texto
        + RESET
    )


def cargar_partidas(ruta):
    partidas = []
    with open(ruta, encoding="utf-8-sig") as archivo:
        while (partida := chess.pgn.read_game(archivo)):
            partidas.append(partida)
    return partidas


def mostrar_tablero(tablero, ultimo=None):
    print()
    print(colorear("     A  B  C  D  E  F  G  H",
                   "cian", negrita=True))

    for fila in range(7, -1, -1):
        linea = f" {fila + 1}  "

        for columna in range(8):
            sq = chess.square(columna, fila)
            pieza = tablero.piece_at(sq)

            fondo = (
                CLARA if (fila + columna) % 2 else OSCURA
            )

            if ultimo:
                if sq == ultimo.from_square:
                    fondo = ORIGEN
                elif sq == ultimo.to_square:
                    fondo = DESTINO

            simbolo = (
                PIEZAS[pieza.symbol()] if pieza else " "
            )

            frente = (
                PIEZA_BLANCA
                if pieza is None or pieza.color
                else PIEZA_NEGRA
            )

            linea += casilla(
                f" {simbolo} ", fondo, frente
            )

        print(linea + f"  {fila + 1}")

    print(colorear("     A  B  C  D  E  F  G  H",
                   "cian", negrita=True))


def preparar(partida):
    tablero = partida.board()
    jugadas = []

    for movimiento in partida.mainline_moves():
        san = tablero.san(movimiento)
        jugadas.append((movimiento, san))
        tablero.push(movimiento)

    return jugadas


def mostrar(partida, jugadas, posicion, numero, total):
    print("\033[2J\033[H", end="")

    print(color_hex(
        " ♟ PGN READER · COLOR LATAM ♔ ",
        "#50D5ED", negrita=True
    ))
    print(colorear(f"Partida {numero}/{total}", "amarillo"))

    encabezados = partida.headers
    print(
        f"{encabezados.get('White', 'Blancas')} "
        "vs "
        f"{encabezados.get('Black', 'Negras')}"
    )
    print("Resultado:", encabezados.get("Result", "*"))

    tablero = partida.board()
    for movimiento, _ in jugadas[:posicion]:
        tablero.push(movimiento)

    ultimo = (
        jugadas[posicion - 1][0]
        if posicion else None
    )

    mostrar_tablero(tablero, ultimo)

    if posicion:
        san = jugadas[posicion - 1][1]
        indice = (posicion + 1) // 2
        turno = "..." if posicion % 2 == 0 else "."
        print(color_hex(
            f"\n Jugada: {indice}{turno} {san}",
            "#E5C85B", negrita=True
        ))
    else:
        print("\n Posición inicial")

    print(f" Progreso: {posicion}/{len(jugadas)}")
    print(colorear(
        "\n [Enter/n] Siguiente  [p] Anterior",
        "cian"
    ))
    print(colorear(
        " [i] Inicio  [f] Final  [j] Ir a jugada",
        "cian"
    ))
    print(colorear(
        " [c] Cambiar partida  [q] Salir",
        "cian"
    ))


def main():
    if len(sys.argv) < 2:
        sys.exit(
            "Uso: python pgnreader.py partida.pgn"
        )

    ruta = Path(sys.argv[1])
    if not ruta.is_file():
        sys.exit("No existe el archivo PGN.")

    partidas = cargar_partidas(ruta)
    if not partidas:
        sys.exit("No se encontraron partidas.")

    actual = 0
    posicion = 0

    while True:
        partida = partidas[actual]
        jugadas = preparar(partida)

        posicion = min(posicion, len(jugadas))

        mostrar(
            partida, jugadas, posicion,
            actual + 1, len(partidas)
        )

        comando = input("\n> ").strip().lower()

        if comando == "q":
            break

        elif comando in ("", "n"):
            posicion = min(
                posicion + 1, len(jugadas)
            )

        elif comando == "p":
            posicion = max(0, posicion - 1)

        elif comando == "i":
            posicion = 0

        elif comando == "f":
            posicion = len(jugadas)

        elif comando == "j":
            try:
                valor = int(input("Media jugada: "))
                posicion = max(
                    0, min(valor, len(jugadas))
                )
            except ValueError:
                pass

        elif comando == "c":
            actual = (actual + 1) % len(partidas)
            posicion = 0


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nHasta pronto.")
