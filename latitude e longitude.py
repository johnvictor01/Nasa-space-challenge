# gera_cidades_paraiba.py
"""
Gera um dicionário Python com todas as cidades da Paraíba no formato:
"paraiba-nomecidade": (lat, lon)

Dependências:
    pip install requests ratelimit

Uso:
    python gera_cidades_paraiba.py
Saída:
    - cidades_paraiba.json  (chaves e (lat,lon))
    - cidades_paraiba.py    (variável `cidades_paraiba` com o dicionário)
"""

import requests
import time
import unicodedata
import json
from ratelimit import limits, sleep_and_retry

# Configurações
IBGE_ESTADO_ID = 25  # código IBGE para Paraíba
OUTPUT_JSON = "cidades_paraiba.json"
OUTPUT_PY = "cidades_paraiba.py"
USER_AGENT = "seu-email@exemplo.com - script para geocoding (respeitar politicas Nominatim)"

# Normaliza nomes para criar as chaves (remover acentos, espaços e deixar lowercase)
def normalize_name(name: str) -> str:
    name = name.lower()
    # remove acentos
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    # substitui espaços e caracteres inválidos por nada (concatena palavras)
    for ch in (" ", "-", "/", "\\", "'"):
        name = name.replace(ch, "")
    # remove outros caracteres que não alfanuméricos
    name = ''.join(c for c in name if c.isalnum())
    return name

# 1) pegar a lista de municípios da Paraíba via IBGE
def fetch_municipios_paraiba():
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{IBGE_ESTADO_ID}/municipios"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # cada item tem 'id' e 'nome'
    municipios = [(m["id"], m["nome"]) for m in data]
    return municipios

# 2) geocodificar cada município usando Nominatim (OpenStreetMap)
# Nominatim recomenda no máximo 1 request/segundo para bulk geocoding.
ONE_SECOND = 1

@sleep_and_retry
@limits(calls=1, period=ONE_SECOND)
def geocode_nominatim(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    }
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    # retorna (lat, lon) como floats
    r = results[0]
    return (float(r["lat"]), float(r["lon"]))

def main():
    print("Buscando lista de municípios (IBGE)...")
    municipios = fetch_municipios_paraiba()
    print(f"{len(municipios)} municípios encontrados.")

    cidades = {}
    erros = []

    for mid, nome in municipios:
        key = f"paraiba-{normalize_name(nome)}"
        query = f"{nome}, Paraíba, Brasil"
        try:
            coords = geocode_nominatim(query)
            # se Nominatim não achar, tentar "nome, PB, Brasil"
            if coords is None:
                time.sleep(1)
                coords = geocode_nominatim(f"{nome}, PB, Brasil")
        except Exception as e:
            print(f"[ERRO] {nome}: {e}")
            coords = None

        if coords is None:
            erros.append(nome)
            print(f"  -> sem coords: {nome}")
        else:
            cidades[key] = (round(coords[0], 6), round(coords[1], 6))
            print(f"  -> {key}: {cidades[key]}")
        # pequeno delay extra (não estritamente necessário por usa do ratelimit decorator)
        time.sleep(0.1)

    # Salva JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cidades, f, ensure_ascii=False, indent=2)

    # Salva módulo Python
    with open(OUTPUT_PY, "w", encoding="utf-8") as f:
        f.write("# arquivo gerado automaticamente\n")
        f.write("cidades_paraiba = \\\n")
        json.dump(cidades, f, ensure_ascii=False, indent=2)

    print(f"\nConcluído. {len(cidades)} cidades com coordenadas salvas em {OUTPUT_JSON}")
    if erros:
        print(f"{len(erros)} municípios sem coordenadas (lista parcial): {erros[:10]} ...")
        print("Você pode reprocessar esses nomes manualmente ou usar uma base oficial de centroides do IBGE.")

if __name__ == "__main__":
    main()
