# utils/io_utils.py
import os
import gzip
import pickle

def carregar_pickle_gz(caminho):
    """
    Carrega um arquivo .pkl.gz, retorna None se falhar.
    """
    try:
        with gzip.open(caminho, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None

def carregar_modelos(cidade_path, campo):
    """
    Retorna lista de modelos [LR, RF, XGB] e scaler.
    """
    modelos = []
    scaler = None

    # Caminhos
    lr_path = os.path.join(cidade_path, f"{campo}_LinearRegression.pkl.gz")
    rf_path = os.path.join(cidade_path, f"{campo}_RandomForest.pkl.gz")
    xgb_path = os.path.join(cidade_path, f"{campo}_XGBoost.pkl.gz")
    scaler_path = os.path.join(cidade_path, f"{campo}_scaler.pkl.gz")

    # Carregar modelos
    for path in [lr_path, rf_path, xgb_path]:
        modelo = carregar_pickle_gz(path)
        if modelo:
            modelos.append(modelo)

    scaler = carregar_pickle_gz(scaler_path)
    return modelos, scaler
