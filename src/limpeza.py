import pandas as pd
import os

ARQUIVO    = "C:/Users/henri/PORTAL DE TRANSPARÊNCIA/src/data/processed/cartoes_36000_01-2024_12-2024_limpo.csv"
PASTA_SAIDA = "C:/Users/henri/PORTAL DE TRANSPARÊNCIA/src/data/processed/tabelas"


def carregar(caminho: str = ARQUIVO) -> pd.DataFrame:
    df = pd.read_csv(caminho, encoding="utf-8-sig", parse_dates=["dataTransacao", "mesExtrato"])
    print(f"Registros carregados: {len(df)}\n")
    return df


# ── PAGINA 1: VISAO GERAL ─────────────────────────────────────────────────────

def resumo_geral(df: pd.DataFrame) -> pd.DataFrame:
    data = {
        "metrica": [
            "total_registros",
            "total_gasto",
            "ticket_medio",
            "ticket_mediano",
            "maior_transacao",
            "menor_transacao",
            "total_unidades_gestoras",
            "total_portadores",
            "total_estabelecimentos",
            "periodo_inicio",
            "periodo_fim",
        ],
        "valor": [
            len(df),
            round(df["valorTransacao"].sum(), 2),
            round(df["valorTransacao"].mean(), 2),
            round(df["valorTransacao"].median(), 2),
            round(df["valorTransacao"].max(), 2),
            round(df["valorTransacao"].min(), 2),
            df["ug_nome"].nunique(),
            df["portador_nome"].nunique(),
            df["estab_nome"].nunique(),
            str(df["dataTransacao"].min().date()),
            str(df["dataTransacao"].max().date()),
        ]
    }
    return pd.DataFrame(data)


def gastos_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("mes")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
            maior_transacao=("valorTransacao", "max"),
        )
        .round(2)
        .reset_index()
    )


def gastos_por_tipo_cartao(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("tipoCartao")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
        )
        .sort_values("total_gasto", ascending=False)
        .round(2)
        .reset_index()
    )


def evolucao_mensal_por_tipo_cartao(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["mes", "tipoCartao"])
        .agg(total_gasto=("valorTransacao", "sum"))
        .round(2)
        .reset_index()
    )


def top_unidades_gestoras(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    return (
        df.groupby("ug_nome")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
            maior_transacao=("valorTransacao", "max"),
        )
        .sort_values("total_gasto", ascending=False)
        .head(n)
        .round(2)
        .reset_index()
    )


def participacao_ug_no_total(df: pd.DataFrame) -> pd.DataFrame:
    total = df["valorTransacao"].sum()
    result = (
        df.groupby("ug_nome")["valorTransacao"]
        .sum()
        .reset_index()
        .rename(columns={"valorTransacao": "total_gasto"})
    )
    result["percentual"] = (result["total_gasto"] / total * 100).round(2)
    return result.sort_values("total_gasto", ascending=False)


# ── PAGINA 2: ANALISE DE GASTOS ───────────────────────────────────────────────

def top_estabelecimentos(df: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    return (
        df.groupby(["estab_nome", "estab_cnpj", "estab_tipo"])
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
            primeira_transacao=("dataTransacao", "min"),
            ultima_transacao=("dataTransacao", "max"),
        )
        .sort_values("total_gasto", ascending=False)
        .head(n)
        .round(2)
        .reset_index()
    )


def gastos_por_dia_semana(df: pd.DataFrame) -> pd.DataFrame:
    ordem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return (
        df.groupby("dia_semana")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
        )
        .reindex(ordem)
        .round(2)
        .reset_index()
    )


def gastos_por_dia_do_mes(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("dia")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
        )
        .round(2)
        .reset_index()
    )


def gastos_fim_de_semana_vs_semana(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby("fim_de_semana")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
        )
        .round(2)
        .reset_index()
    )
    result["fim_de_semana"] = result["fim_de_semana"].map({True: "Fim de semana", False: "Dia util"})
    return result


def heatmap_mes_dia_semana(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["mes", "dia_semana"])
        .agg(total_gasto=("valorTransacao", "sum"))
        .round(2)
        .reset_index()
    )


def top_portadores(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    return (
        df[df["portador_nome"] != "NAO IDENTIFICADO"]
        .groupby("portador_nome")
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
            ticket_medio=("valorTransacao", "mean"),
            estabelecimentos_distintos=("estab_nome", "nunique"),
        )
        .sort_values("total_gasto", ascending=False)
        .head(n)
        .round(2)
        .reset_index()
    )


def gasto_por_portador_e_mes(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[df["portador_nome"] != "NAO IDENTIFICADO"]
        .groupby(["portador_nome", "mes"])
        .agg(total_gasto=("valorTransacao", "sum"))
        .round(2)
        .reset_index()
    )


# ── PAGINA 3: ANOMALIAS ───────────────────────────────────────────────────────

def transacoes_alto_valor(df: pd.DataFrame, percentil: float = 0.99) -> pd.DataFrame:
    limite = df["valorTransacao"].quantile(percentil)
    print(f"Limite percentil {percentil*100:.0f}%: R$ {limite:,.2f}")
    return (
        df[df["valorTransacao"] >= limite]
        [["dataTransacao", "valorTransacao", "estab_nome", "estab_cnpj",
          "ug_nome", "portador_nome", "tipoCartao", "dia_semana", "fim_de_semana"]]
        .sort_values("valorTransacao", ascending=False)
        .reset_index(drop=True)
    )


def gastos_fim_de_semana_detalhado(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[df["fim_de_semana"] == True]
        [["dataTransacao", "dia_semana", "valorTransacao", "estab_nome",
          "estab_cnpj", "ug_nome", "portador_nome", "tipoCartao"]]
        .sort_values("valorTransacao", ascending=False)
        .reset_index(drop=True)
    )


def compras_fragmentadas(df: pd.DataFrame, janela_horas: int = 24) -> pd.DataFrame:
    df_sorted = df.sort_values(["portador_nome", "estab_nome", "dataTransacao"])
    df_sorted = df_sorted[df_sorted["portador_nome"] != "NAO IDENTIFICADO"].copy()
    df_sorted["diff_horas"] = (
        df_sorted.groupby(["portador_nome", "estab_nome"])["dataTransacao"]
        .diff()
        .dt.total_seconds()
        .div(3600)
    )
    return (
        df_sorted[df_sorted["diff_horas"] <= janela_horas]
        [["dataTransacao", "diff_horas", "valorTransacao", "estab_nome",
          "portador_nome", "ug_nome", "tipoCartao"]]
        .sort_values("diff_horas")
        .reset_index(drop=True)
    )


def estabelecimentos_incomuns(df: pd.DataFrame) -> pd.DataFrame:
    palavras = [
        "JOALHERIA", "JOIA", "RELOJOARIA", "GAME", "CASINO", "BINGO",
        "LOTERIA", "TABACARIA", "CHARUTO", "NIGHTCLUB", "NIGHT CLUB",
        "MOTEL", "ADULT", "PERFUMARIA", "COSMETICO", "EROTICA", "SEX"
    ]
    padrao = "|".join(palavras)
    return (
        df[df["estab_nome"].str.contains(padrao, case=False, na=False)]
        [["dataTransacao", "valorTransacao", "estab_nome", "estab_cnpj",
          "ug_nome", "portador_nome", "dia_semana", "fim_de_semana"]]
        .sort_values("valorTransacao", ascending=False)
        .reset_index(drop=True)
    )


def concentracao_por_estabelecimento(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    total = df["valorTransacao"].sum()
    result = (
        df.groupby(["estab_nome", "estab_cnpj"])
        .agg(
            total_gasto=("valorTransacao", "sum"),
            total_transacoes=("id", "count"),
        )
        .sort_values("total_gasto", ascending=False)
        .head(n)
        .reset_index()
    )
    result["percentual_do_total"] = (result["total_gasto"] / total * 100).round(2)
    return result


def picos_mensais_por_ug(df: pd.DataFrame) -> pd.DataFrame:
    mensal = (
        df.groupby(["ug_nome", "mes"])
        .agg(total_gasto=("valorTransacao", "sum"))
        .reset_index()
    )
    media_ug = mensal.groupby("ug_nome")["total_gasto"].mean().rename("media_mensal")
    mensal = mensal.join(media_ug, on="ug_nome")
    mensal["variacao_pct"] = ((mensal["total_gasto"] - mensal["media_mensal"]) / mensal["media_mensal"] * 100).round(2)
    return mensal.sort_values("variacao_pct", ascending=False)


# ── Exportar todas as tabelas ─────────────────────────────────────────────────

def exportar_todas(df: pd.DataFrame, pasta: str = PASTA_SAIDA) -> None:
    os.makedirs(pasta, exist_ok=True)

    tabelas = {
        "resumo_geral":                     resumo_geral(df),
        "gastos_por_mes":                   gastos_por_mes(df),
        "gastos_por_tipo_cartao":           gastos_por_tipo_cartao(df),
        "evolucao_mensal_por_tipo_cartao":  evolucao_mensal_por_tipo_cartao(df),
        "top_unidades_gestoras":            top_unidades_gestoras(df),
        "participacao_ug_no_total":         participacao_ug_no_total(df),
        "top_estabelecimentos":             top_estabelecimentos(df),
        "gastos_por_dia_semana":            gastos_por_dia_semana(df),
        "gastos_por_dia_do_mes":            gastos_por_dia_do_mes(df),
        "gastos_fim_semana_vs_semana":      gastos_fim_de_semana_vs_semana(df),
        "heatmap_mes_dia_semana":           heatmap_mes_dia_semana(df),
        "top_portadores":                   top_portadores(df),
        "gasto_por_portador_e_mes":         gasto_por_portador_e_mes(df),
        "transacoes_alto_valor":            transacoes_alto_valor(df),
        "gastos_fim_semana_detalhado":      gastos_fim_de_semana_detalhado(df),
        "compras_fragmentadas":             compras_fragmentadas(df),
        "estabelecimentos_incomuns":        estabelecimentos_incomuns(df),
        "concentracao_por_estabelecimento": concentracao_por_estabelecimento(df),
        "picos_mensais_por_ug":             picos_mensais_por_ug(df),
    }

    for nome, tabela in tabelas.items():
        caminho = os.path.join(pasta, f"{nome}.csv")
        tabela.to_csv(caminho, index=False, encoding="utf-8-sig")
        print(f"Exportado: {nome}.csv ({len(tabela)} linhas)")

    print(f"\nTotal de tabelas exportadas: {len(tabelas)}")
    print(f"Pasta: {pasta}")


if __name__ == "__main__":
    df = carregar()
    exportar_todas(df)

