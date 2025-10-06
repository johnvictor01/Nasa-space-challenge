# utils/preprocessing.py
import numpy as np

def criar_features_ciclicas(dia: int, mes: int):
    """
    Retorna um array 2D com features cíclicas para dia e mês.
    """
    mes_sin = np.sin(2 * np.pi * mes / 12)
    mes_cos = np.cos(2 * np.pi * mes / 12)
    dia_sin = np.sin(2 * np.pi * dia / 31)
    dia_cos = np.cos(2 * np.pi * dia / 31)
    
    return np.array([[mes_sin, mes_cos, dia_sin, dia_cos]])
