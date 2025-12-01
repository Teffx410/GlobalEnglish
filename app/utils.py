# app/utils.py

from datetime import datetime, timedelta, time

# ============================================================
# 1. CONVERSIÓN DE MINUTOS A EQUIVALENTES
# ============================================================
def minutes_to_equivalents(minutes: int | float, minutos_equiv: int) -> float:
    """
    Convierte minutos reales a equivalentes (horas) según el valor
    de equivalencia definido por el programa.

    Ejemplo:
    - minutos_equiv = 45  → cada 45 min cuenta como 1 hora equivalente
    """
    if minutos_equiv <= 0:
        raise ValueError("minutos_equiv debe ser mayor que cero")

    return round(minutes / minutos_equiv, 2)


# ============================================================
# 2. PARSEO DE FECHAS Y HORAS
# ============================================================
def parse_datetime(value: str) -> datetime:
    """
    Convierte un string a datetime. Acepta varios formatos comunes.
    """
    formatos = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M"
    ]

    for fmt in formatos:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    raise ValueError(f"No se reconoce el formato de fecha: {value}")


def parse_time(value: str) -> time:
    """
    Convierte un string HH:MM o HH:MM:SS a time.
    """
    formatos = ["%H:%M", "%H:%M:%S"]

    for fmt in formatos:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            pass

    raise ValueError(f"Formato de hora no válido: {value}")


# ============================================================
# 3. CÁLCULO DE DIFERENCIA ENTRE HORAS
# ============================================================
def calc_minutes_between(hora_inicio: str | time, hora_final: str | time) -> int:
    """
    Retorna la cantidad de minutos entre dos horas.
    Entrada puede ser string HH:MM o objetos time.
    """
    if isinstance(hora_inicio, str):
        hora_inicio = parse_time(hora_inicio)
    if isinstance(hora_final, str):
        hora_final = parse_time(hora_final)

    dt1 = datetime.combine(datetime.today(), hora_inicio)
    dt2 = datetime.combine(datetime.today(), hora_final)

    return int((dt2 - dt1).total_seconds() / 60)


# ============================================================
# 4. FORMATO ESTÁNDAR HH:MM
# ============================================================
def format_time(value: time | str | None) -> str:
    """
    Retorna hora en formato 'HH:MM'. Si el valor es None, retorna ''.
    """
    if value is None:
        return ""

    if isinstance(value, str):
        try:
            value = parse_time(value)
        except ValueError:
            return value  # Retorna como está si no es parseable

    return value.strftime("%H:%M")


# ============================================================
# 5. VERIFICAR SI UNA FECHA ESTÁ DENTRO DE UN RANGO
# ============================================================
def in_range(date_value: datetime | str, start: datetime | str, end: datetime | str) -> bool:
    """
    Verifica si date_value está entre start y end.
    """
    if isinstance(date_value, str):
        date_value = parse_datetime(date_value)
    if isinstance(start, str):
        start = parse_datetime(start)
    if isinstance(end, str):
        end = parse_datetime(end)

    return start <= date_value <= end
