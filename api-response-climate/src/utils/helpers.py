# utils/helpers.py
import numpy as np

def corrigir_falsos_negativos(valor, campo):
    """
    Ajusta previsões de chuva para reduzir falsos negativos.
    """
    if campo == "precipitacao_mm" and not np.isnan(valor):
        if 0 < valor < 2:
            return valor * 1.5
        elif valor >= 2:
            return valor
        else:
            return 0.5
    return valor
