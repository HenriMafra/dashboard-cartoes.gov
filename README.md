# 💳 Dashboard de Gastos - Cartões de Pagamento GovBR



![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)

![Python](https://img.shields.io/badge/Python-3.9+-blue)

![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red)



Dashboard interativo e analítico para monitoramento de despesas com cartões de pagamento do Governo Federal Brasileiro (ano 2024). O projeto foca em transparência, detecção de anomalias e visualização de dados.



## Link do Projeto

[👉 Clique aqui para acessar o Dashboard Online](https://dashboard-cartoesgov-a69fyt3udebrewhsyskt8p.streamlit.app/)



---



## Funcionalidades Principais



* **Visão Geral:** KPIs automáticos com total gasto, ticket médio e volume de transações.

* **Rankings Inteligentes:** Gráficos de barras horizontais com os 10 órgãos e fornecedores que mais movimentaram recursos.

* **Análise de Anomalias:** * Gráfico de dispersão para identificação de *outliers*.

    * Cards de detalhamento para transações de altíssimo valor.

    * **Treemap Interativo** para detecção de compras fragmentadas.

* **Mapa de Calor:** Distribuição geográfica dos gastos por estado (UF).



## Tecnologias Utilizadas



* **Linguagem:** Python

* **Visualização:** Plotly Express (Gráficos Interativos)

* **Interface:** Streamlit (Customizado com CSS para Dark Mode)

* **Manipulação de Dados:** Pandas

* **Deploy:** Streamlit Community Cloud



---



## Estrutura do Repositório



* `app.py`: Arquivo principal com a lógica do dashboard.

* `.streamlit/config.toml`: Configurações de tema (Dark Mode).

* `requirements.txt`: Dependências do projeto.

* `src/data/`: Pasta contendo os datasets processados (CSVs).



## 🧑‍💻 Autor

**HenriMafra**

- [LinkedIn](www.linkedin.com/in/henrimafra)

- [GitHub](https://github.com/HenriMafra)
