"""Conversión entre medidas de cinta y dieciseisavos de pulgada."""

from math import gcd
import re


MAX_UNITS = 9_223_372_036_854_775_807  # INTEGER de SQLite; no es un límite del taller.
FRACTION = re.compile(r"([0-9]+)/([0-9]+)")


def parse_measure(text: str) -> int:
    """Acepta un entero seguido de cero o más fracciones sumadas con espacios."""
    parts = text.strip().split()
    if not parts:
        raise ValueError("Escribe una medida.")

    units = 0
    for index, part in enumerate(parts):
        if index == 0 and part.isascii() and part.isdecimal():
            units += int(part) * 16
            continue

        match = FRACTION.fullmatch(part)
        if not match:
            raise ValueError("Usa pulgadas como 24, 26 1/2 o 24 1/4 1/16.")
        numerator, denominator = map(int, match.groups())
        if denominator not in (2, 4, 8, 16) or numerator < 1 or numerator >= denominator:
            raise ValueError("Usa fracciones positivas menores que 1 con denominador 2, 4, 8 o 16.")
        units += numerator * (16 // denominator)

    if units <= 0:
        raise ValueError("La medida debe ser mayor que cero.")
    if units > MAX_UNITS:
        raise ValueError("La medida excede la capacidad de almacenamiento.")
    return units


def format_measure(units: int) -> str:
    """Muestra el valor equivalente como fracción simplificada."""
    whole, remainder = divmod(units, 16)
    if not remainder:
        return str(whole)
    divisor = gcd(remainder, 16)
    fraction = f"{remainder // divisor}/{16 // divisor}"
    return f"{whole} {fraction}" if whole else fraction


def centro_16(ancho_16: int) -> int:
    """Mitad del ancho, subiendo un posible 1/32 al siguiente 1/16."""
    return (ancho_16 + 1) // 2
