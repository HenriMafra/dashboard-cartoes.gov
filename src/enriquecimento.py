import pandas as pd
import requests
import time
import os

# Caminhos
ARQUIVO_LIMPO = "C:/Users/henri/PORTAL DE TRANSPARÊNCIA/src/data/processed/cartoes_36000_01-2024_12-2024_limpo.csv"
ARQUIVO_SAIDA = "C:/Users/henri/PORTAL DE TRANSPARÊNCIA/src/data/processed/tabelas/cnpjs_enriquecidos.csv"


def buscar_dados_cnpj(cnpj_limpo):
    """Busca dados na Brasil API."""
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            return dados.get("uf", "NA"), dados.get("municipio", "NA")
        else:
            return "NA", "NA"
    except Exception:
        return "NA", "NA"


def enriquecer_top_estabelecimentos(n_top=200):
    print(f"Lendo base principal para extrair os top {n_top} CNPJs...")
    df = pd.read_csv(ARQUIVO_LIMPO, encoding="utf-8-sig")

    # Filtra apenas os que parecem ter um CNPJ válido (tamanho > 10)
    df_cnpjs = df.dropna(subset=['estab_cnpj']).copy()

    # Agrupa para pegar os maiores recebedores
    top_estab = df_cnpjs.groupby(["estab_cnpj", "estab_nome"])["valorTransacao"].sum().reset_index()
    top_estab = top_estab.sort_values("valorTransacao", ascending=False).head(n_top)

    resultados = []

    print(f"Iniciando consultas na BrasilAPI para {n_top} empresas...")
    print("Isso deve levar cerca de 1 a 2 minutos.\n")

    for index, row in top_estab.iterrows():
        cnpj_original = str(row['estab_cnpj'])
        # Limpa o CNPJ (tira pontos, traços, barras)
        cnpj_numeros = ''.join(filter(str.isdigit, cnpj_original))

        if len(cnpj_numeros) == 14:
            uf, municipio = buscar_dados_cnpj(cnpj_numeros)
            print(f"Consultado: {cnpj_numeros} | {row['estab_nome'][:20]}... -> UF: {uf}")
        else:
            uf, municipio = "NA", "NA"

        resultados.append({
            "estab_cnpj": cnpj_original,
            "uf": uf,
            "municipio": municipio
        })

        # Pausa de meio segundo para não sobrecarregar a API pública
        time.sleep(0.5)

    # Salva o resultado
    df_resultado = pd.DataFrame(resultados)

    # Junta com os valores totais para facilitar no mapa
    df_final = pd.merge(top_estab, df_resultado, on="estab_cnpj", how="left")

    # Remove os que não conseguimos achar (NA)
    df_final = df_final[df_final["uf"] != "NA"]

    df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print(f"\n✅ Concluído! Dados salvos em: {ARQUIVO_SAIDA}")
    print(f"Total de locais encontrados com sucesso: {len(df_final)}")


if __name__ == "__main__":
    enriquecer_top_estabelecimentos(200)