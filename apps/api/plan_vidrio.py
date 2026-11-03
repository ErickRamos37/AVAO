"""Medidas de los dos vidrios iguales de una ventana California por mitad."""

from apps.api.medidas import centro_16


def calcular_plan_vidrio(ancho_16: int, alto_16: int) -> tuple[int, int, int]:
    ancho_vidrio_16 = centro_16(ancho_16) - 32
    alto_vidrio_16 = alto_16 - 32
    if ancho_vidrio_16 <= 0 or alto_vidrio_16 <= 0:
        raise ValueError("las medidas producen un vidrio de ancho o alto cero o negativo")
    return ancho_vidrio_16, alto_vidrio_16, 2
