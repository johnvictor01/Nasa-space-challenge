import os
import numpy as np
import sys

# Adiciona a pasta src ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Agora podemos importar diretamente de utils
from utils.preprocessing import criar_features_ciclicas
from utils.helpers import corrigir_falsos_negativos
from utils.io_utils import carregar_modelos


campos = ['temp_media_c','temp_max_c','temp_min_c','umidade_pct','precipitacao_mm','vento_kmh']
def prever_cidade_data(cidade, data, model_dir="data/modelos"):
    mes = data.month
    dia = data.day

    X_input = criar_features_ciclicas(dia, mes)
    cidade_path = os.path.join(model_dir, cidade)
    print("Cidade path:", cidade_path)
    previsao = {'cidade': cidade, 'data': data.strftime("%Y-%m-%d")}

    for campo in campos:
        modelos, scaler = carregar_modelos(cidade_path, campo)
        if not modelos: 
            previsao[campo] = None
            continue

        previsoes = []
        for modelo in modelos:
            X_scaled = scaler.transform(X_input) if scaler else X_input
            valor = modelo.predict(X_scaled)[0]
            previsoes.append(corrigir_falsos_negativos(valor, campo))

        media = np.nanmean(previsoes)
        previsao[campo] = float(round(media, 2)) if not np.isnan(media) else None

    # Heurísticas
    previsao["VaiChover"] = bool(previsao.get("precipitacao_mm", 0) >= 1)
    previsao["DiaQuente"] = bool(previsao.get("temp_max_c", 0) >= 30)
    previsao["DiaFrio"] = bool(previsao.get("temp_min_c", 0) <= 18)
    previsao["DiaVentoso"] = bool(previsao.get("vento_kmh", 0) >= 20)
    previsao["DiaConfortavel"] = bool(
        previsao.get("temp_media_c") is not None
        and 20 <= previsao["temp_media_c"] <= 28
        and (previsao.get("umidade_pct") or 0) <= 70
        and not previsao.get("VaiChover", False)
    )

    return previsao
