import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

CHAVE = os.getenv("CHAVE_API")
URL_CARTOES = "https://api.portaldatransparencia.gov.br/api-de-dados/cartoes"
URL_ORGAOS  = "https://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi"


def listar_orgaos() -> pd.DataFrame:
    """
    Lista todos os orgaos disponiveis no SIAFI.
    Util para descobrir o codigo do orgao que deseja consultar.
    """
    if not CHAVE:
        raise ValueError("Chave de API nao encontrada. Verifique o arquivo .env")

    headers = {"chave-api-dados": CHAVE}
    todos = []
    pagina = 1

    print("Buscando orgaos disponiveis...\n")

    while True:
        url = f"{URL_ORGAOS}?pagina={pagina}"
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na pagina {pagina}: {e}")
            break

        if not dados:
            break

        todos.extend(dados)
        pagina += 1
        time.sleep(0.3)

    df = pd.DataFrame(todos)
    print(f"Total de orgaos encontrados: {len(df)}")
    print(df[["codigo", "descricao"]].to_string(index=False))
    return df


def coletar_cartoes(mes_inicio: str, mes_fim: str, codigo_orgao: str) -> pd.DataFrame:
    """
    Coleta dados de cartoes de pagamento do governo federal.

    Parametros:
        mes_inicio:   formato 'MM/AAAA' (ex: '01/2024')
        mes_fim:      formato 'MM/AAAA' (ex: '12/2024')
        codigo_orgao: codigo SIAFI do orgao (ex: '20000' para Presidencia)

    Retorna:
        DataFrame com todos os registros coletados.
    """
    if not CHAVE:
        raise ValueError("Chave de API nao encontrada. Verifique o arquivo .env")

    headers = {"chave-api-dados": CHAVE}
    todos = []
    pagina = 1

    print(f"Iniciando coleta: orgao {codigo_orgao} | {mes_inicio} ate {mes_fim}\n")

    while True:
        url = (
            f"{URL_CARTOES}"
            f"?mesAnoInicio={mes_inicio}"
            f"&mesAnoFim={mes_fim}"
            f"&codigoOrgao={codigo_orgao}"
            f"&pagina={pagina}"
        )

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP na pagina {pagina}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexao na pagina {pagina}: {e}")
            break

        if not dados:
            print(f"Coleta finalizada na pagina {pagina - 1}.")
            break

        todos.extend(dados)
        print(f"Pagina {pagina:>4} | Registros acumulados: {len(todos)}")
        pagina += 1
        time.sleep(0.4)

    if not todos:
        print("Nenhum dado coletado.")
        return pd.DataFrame()

    df = pd.DataFrame(todos)

    os.makedirs("data/raw", exist_ok=True)
    inicio_fmt = mes_inicio.replace("/", "-")
    fim_fmt    = mes_fim.replace("/", "-")
    nome_arquivo = f"data/raw/cartoes_{codigo_orgao}_{inicio_fmt}_{fim_fmt}.csv"
    df.to_csv(nome_arquivo, index=False, encoding="utf-8-sig")

    print(f"\nArquivo salvo em: {nome_arquivo}")
    print(f"Total de registros: {len(df)}")
    print(f"Colunas disponiveis: {list(df.columns)}")

    return df


if __name__ == "__main__":
    # Descomente a linha abaixo para ver todos os orgaos e seus codigos
    # listar_orgaos()

    # Altere o codigo_orgao conforme o orgao que deseja analisar
    # Exemplos:
    #   "20000" - Presidencia da Republica
    #   "36000" - Ministerio da Educacao
    #   "30000" - Ministerio da Defesa
    #   "39252" - Ministerio da Saude

    df = coletar_cartoes(
        mes_inicio="01/2024",
        mes_fim="12/2024",
        codigo_orgao="36000"
    )

    if not df.empty:
        print("\nPrimeiras linhas:")
        print(df.head())