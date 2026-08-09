import json

def sum_numbers(a: int, b: int) -> str:
    """Soma dois números inteiros."""
    return f"O resultado da soma é {a + b}."

def get_current_time() -> str:
    """Retorna o horário atual simulado."""
    return "O horário atual é 20:41."

TOOLS = {
    "somar_numeros": sum_numbers,
    "obter_horario_atual": get_current_time
}
