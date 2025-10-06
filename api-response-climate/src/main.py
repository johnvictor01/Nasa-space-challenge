from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel
from server.previsao_service import prever_cidade_data

app = FastAPI(title="Previsão Climática")
erro = {
  "cidade": None,
  "data": None,
  "temp_media_c": None,
  "temp_max_c": None,
  "temp_min_c": None,
  "umidade_pct": None,
  "precipitacao_mm": None,
  "vento_kmh": None,
  "VaiChover": None,
  "DiaQuente": None,
  "DiaFrio": None,
  "DiaVentoso": None,
  "DiaConfortavel": None
}

class PrevisaoRequest(BaseModel):
    cidade: str
    data: str

# lista fixa de cidades da Paraíba
CIDADES_PB = [
    'paraiba-sobrado',
    'paraiba-guarabira',
    'paraiba-santarita',
    'paraiba-patos',
    'paraiba-campinagrande',
    'paraiba-cajazeiras',
    'paraiba-saobentinho',
    'paraiba-pombal',
    'paraiba-aguabranca',
    'paraiba-joaopessoa',
    'paraiba-bayeux'
]


@app.post("/previsao/")
def previsao(request: PrevisaoRequest):
    print(f"Recebendo requisição: cidade={request.cidade}, data={request.data}")
    if request.cidade ==(0 or "0") or request.data == (1 or "1"):
        print("Erro: Cidade ou data inválida")
        return erro
    
    try:
        data_dt = datetime.strptime(request.data, "%Y-%m-%d")
    except ValueError:
        print("Erro: Data inválida")
        raise HTTPException(status_code=400, detail="Data inválida. Use YYYY-MM-DD.")

    hoje = datetime.today()
    limite = hoje + timedelta(days=14)
    #if not (hoje <= data_dt <= limite):
     #   print("Erro: Data fora do intervalo permitido")
      #  raise HTTPException(status_code=400, detail="Data fora do intervalo permitido (até 2 semanas).")

    resultado = prever_cidade_data(request.cidade, data_dt)
    print(f"Resultado gerado: {resultado}")
    return resultado


@app.get("/mapa/")
def previsao_todas():
    """
    Retorna a previsão do dia atual para todas as cidades da Paraíba.
    """
    hoje_str = datetime.today().strftime("%Y-%m-%d")
    resultados = []

    for cidade in CIDADES_PB:
        try:
            resultado = prever_cidade_data(cidade, datetime.today())
            resultados.append(resultado)
        except Exception as e:
            print(f"Erro ao gerar previsão para {cidade}: {e}")
            # se houver erro, adiciona estrutura de erro
            erro_copia = erro.copy()
            erro_copia["cidade"] = cidade
            erro_copia["data"] = hoje_str
            resultados.append(erro_copia)

    return resultados
