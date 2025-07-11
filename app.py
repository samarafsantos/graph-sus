import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components
import networkx as nx

sparql = SPARQLWrapper("http://localhost:7200/repositories/Trab-final")
sparql.setReturnFormat(JSON)

st.title("🔬 Grafo de Conhecimento - ANS/SUS")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔎 Consulta Avançada", "📊 Análise Temporal Personalizada", "📈 Drill-Down", "📊 Gráficos por Distribuição", "🧠 Grafo de Conhecimento"])

with tab1:
    st.subheader("Consulta por Filtros Individuais")

    years = ["2022", "2023", "2024"]
    months = ["01", "02", "03"]

    year = st.selectbox("Ano", [""] + years, key="year_tab1")
    month = st.selectbox("Mês", [""] + months, key="month_tab1")
    sex = st.selectbox("Sexo", ["", "Male", "Female"], key="sex_tab1")
    age = st.selectbox("Faixa Etária", ["", "20 a 29", "60 a 69", "70 a 79", "5 a 9"], key="age_tab1")
    size = st.selectbox("Porte - Hospital", ["", "GRANDE", "MÉDIO"], key="size_tab1")

    filters = ""
    if year:
        filters += f'FILTER (?ano = "{year}"^^xsd:gYear)\n'
    if month:
        filters += f'FILTER (?mes = "{month}"^^xsd:gMonth)\n'
    if sex:
        filters += f'FILTER (?sexo = dbr:{sex})\n'
    if age:
        filters += f'FILTER (?idade = "{age}")\n'
    if size:
        filters += f'FILTER (?porte = "{size}")\n'

    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX ex: <http://example.org/health/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?evento ?idade ?cid ?sexo ?municipio ?ano ?mes ?porte
    WHERE {{
      ?evento a dbo:MedicalProcedure ;
              dbo:ageRange ?idade ;
              dbo:disease ?cid ;
              dbo:sex ?sexo ;
              ex:ano ?ano ;
              ex:mes ?mes ;
              ex:municipioBeneficiario ?municipio ;
              ex:porte ?porte .
      {filters}
    }}
    """

    if st.button("Executar Consulta", key="query1"):
        sparql.setQuery(query)
        try:
            results = sparql.query().convert()
        except Exception as e:
            st.error(f"Erro na consulta SPARQL: {e}")
            st.stop()

        rows = []
        for r in results["results"]["bindings"]:
          rows.append({
              "Evento": r["evento"]["value"],
              "Idade": r["idade"]["value"],
              "CID": r["cid"]["value"].split("/")[-1],
              "Sexo": r["sexo"]["value"].split("/")[-1],
              "Município": r["municipio"]["value"],
              "Ano": r["ano"]["value"],
              "Mês": r["mes"]["value"],
              "Porte": r["porte"]["value"],
          })

        df = pd.DataFrame(rows)
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("Nenhum resultado encontrado.")

with tab2:
    st.subheader("📈 Estatísticas com Filtros Fixos")

    years = ["2022", "2023", "2024"]
    months = ["01", "02", "03"]

    col1, col2 = st.columns(2)
    with col1:
        year_start = st.selectbox("Ano inicial", years, key="year_start_tab2")
        month_start = st.selectbox("Mês inicial", months, key="month_start_tab2")
    with col2:
        year_end = st.selectbox("Ano final", years, key="year_end_tab2")
        month_end = st.selectbox("Mês final", months, key="month_end_tab2")

    st.markdown("### 🎚️ Filtros Adicionais")

    sex = st.selectbox("Sexo", ["", "Male", "Female"], key="sex_tab2")
    age = st.selectbox("Faixa Etária", ["", "20 a 29", "60 a 69", "70 a 79", "5 a 9"], key="age_tab2")
    city = st.text_input("Município do Beneficiário (código IBGE)", key="city_tab2")
    uf = st.selectbox("UF do Prestador", ["", "Rondonia"], key="uf_tab2")
    size = st.selectbox("Porte - Hospital", ["", "GRANDE", "MÉDIO"], key="size_tab2")
    cid = st.text_input("CID (ex: R52, N201)", key="cid_tab2")
    dur_min = st.number_input("Tempo de permanência mínimo", min_value=0, value=0, key="dur_min_tab2")
    dur_max = st.number_input("Tempo de permanência máximo", min_value=0, value=10, key="dur_max_tab2")

    if st.button("Consultar Estatísticas", key="consulta3"):
        start = int(year_start + month_start)
        end = int(year_end + month_end)

        filter_period = f"""
        BIND(CONCAT(STR(?ano), STR(?mes)) AS ?anoMes)
        FILTER(xsd:integer(?anoMes) >= {start} && xsd:integer(?anoMes) <= {end})
        """

        filtros = ""
        if sex:
            filtros += f"FILTER(?sexo = dbr:{sex})\n"
        if age:
            filtros += f'FILTER(?idade = "{age}")\n'
        if city:
            filtros += f'FILTER(?municipio = "{city}")\n'
        if uf:
            filtros += f"FILTER(?uf = dbr:{uf})\n"
        if size:
            filtros += f'FILTER(?porte = "{size}")\n'
        if cid:
            filtros += f"FILTER(?cid = icd:{cid})\n"
        filtros += f"FILTER(?dur >= {dur_min} && ?dur <= {dur_max})\n"

        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX ex: <http://example.org/health/>
        PREFIX icd: <http://purl.bioontology.org/ontology/ICD10/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?ano ?mes (COUNT(?evento) AS ?qtd)
        WHERE {{
          ?evento a dbo:MedicalProcedure ;
                  dbo:sex ?sexo ;
                  dbo:ageRange ?idade ;
                  ex:municipioBeneficiario ?municipio ;
                  dbo:region ?uf ;
                  ex:porte ?porte ;
                  dbo:disease ?cid ;
                  dbo:duration ?dur ;
                  ex:ano ?ano ;
                  ex:mes ?mes .
          {filter_period}
          {filtros}
        }}
        GROUP BY ?ano ?mes
        ORDER BY ?ano ?mes
        """

        st.code(query, language="sparql") # Debug

        sparql.setQuery(query)
        try:
            results = sparql.query().convert()
        except Exception as e:
            st.error(f"Erro na consulta SPARQL: {e}")
            st.stop()

        rows = []
        for r in results["results"]["bindings"]:
            rows.append({
                "Ano": r["ano"]["value"],
                "Mês": r["mes"]["value"],
                "Qtd": int(r["qtd"]["value"]),
            })

        if not rows:
            st.warning("Nenhum dado encontrado.")
        else:
            df = pd.DataFrame(rows)
            df["Ano-Mês"] = df["Ano"] + "-" + df["Mês"]
            st.bar_chart(df.set_index("Ano-Mês")["Qtd"])
            st.dataframe(df)

if "drill_level" not in st.session_state:
    st.session_state["drill_level"] = 0
if "selected_month" not in st.session_state:
    st.session_state["selected_month"] = None
if "selected_sex" not in st.session_state:
    st.session_state["selected_sex"] = None
if "selected_drill_final" not in st.session_state:
    st.session_state["selected_drill_final"] = None

with tab3:
    st.subheader("Análise Temporal com Drill-Down")

    years = ["2022", "2023", "2024"]
    months = ["01", "02", "03"]

    col1, col2 = st.columns(2)
    with col1:
        year_start = st.selectbox("Ano inicial", years, key="year_start_tab3_drill")
        month_start = st.selectbox("Mês inicial", months, key="month_start_tab3_drill")
    with col2:
        year_end = st.selectbox("Ano final", years, key="year_end_tab3_drill")
        month_end = st.selectbox("Mês final", months, key="month_end_tab3_drill")

    if st.button("Consultar", key="consulta_drill_root"):
        st.session_state["drill_level"] = 0
        st.session_state["selected_month"] = None
        st.session_state["selected_sex"] = None

    start = int(year_start + month_start)
    end = int(year_end + month_end)

    filter_period = f"""
    BIND(CONCAT(STR(?ano), STR(?mes)) AS ?anoMes)
    FILTER(xsd:integer(?anoMes) >= {start} && xsd:integer(?anoMes) <= {end})
    """

    if st.session_state["drill_level"] == 0:
        # Nível 0: Agrupado por mês
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX ex: <http://example.org/health/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?ano ?mes (COUNT(?evento) AS ?qtd)
        WHERE {{
            ?evento a dbo:MedicalProcedure ;
                    ex:ano ?ano ;
                    ex:mes ?mes .
            {filter_period}
        }}
        GROUP BY ?ano ?mes
        ORDER BY ?ano ?mes
        """
        sparql.setQuery(query)
        results = sparql.query().convert()

        rows = []
        for r in results["results"]["bindings"]:
            ano = r["ano"]["value"]
            mes = r["mes"]["value"]
            rows.append({
                "Ano-Mês": f"{ano}-{mes}",
                "Ano": ano,
                "Mês": mes,
                "Qtd": int(r["qtd"]["value"]),
            })

        df = pd.DataFrame(rows)
        st.subheader("📊 Procedimentos por Mês")
        st.bar_chart(df.set_index("Ano-Mês")["Qtd"])

        selected = st.selectbox("🔍 Ver detalhes de:", df["Ano-Mês"])
        if st.button("Drill-down para Sexo"):
            st.session_state["selected_month"] = selected
            st.session_state["drill_level"] = 1
            st.rerun()

    elif st.session_state["drill_level"] == 1:
        # Nível 1: Agrupado por sexo no mês selecionado
        ano, mes = st.session_state["selected_month"].split("-")

        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX ex: <http://example.org/health/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?sexo (COUNT(?evento) AS ?qtd)
        WHERE {{
            ?evento a dbo:MedicalProcedure ;
                    ex:ano "{ano}"^^xsd:gYear ;
                    ex:mes "{mes}"^^xsd:gMonth ;
                    dbo:sex ?sexo .
        }}
        GROUP BY ?sexo
        ORDER BY ?sexo
        """
        sparql.setQuery(query)
        results = sparql.query().convert()

        rows = []
        for r in results["results"]["bindings"]:
            sexo = r["sexo"]["value"].split("/")[-1]
            rows.append({
                "Sexo": sexo,
                "Qtd": int(r["qtd"]["value"]),
            })

        df = pd.DataFrame(rows)
        st.subheader(f"📊 Sexo em {ano}-{mes}")
        st.bar_chart(df.set_index("Sexo")["Qtd"])

        selected = st.selectbox("🔍 Ver detalhes de:", df["Sexo"])
        if st.button("Drill-down para Faixa Etária"):
            st.session_state["selected_sex"] = selected
            st.session_state["drill_level"] = 2
            st.rerun()

        if st.button("🔙 Voltar para Mês"):
            st.session_state["drill_level"] = 0
            st.rerun()

    elif st.session_state["drill_level"] == 2:
        # Nível 2: Faixa etária em mês + sexo
        ano, mes = st.session_state["selected_month"].split("-")
        sexo = st.session_state["selected_sex"]

        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX ex: <http://example.org/health/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?idade (COUNT(?evento) AS ?qtd)
        WHERE {{
            ?evento a dbo:MedicalProcedure ;
                    ex:ano "{ano}"^^xsd:gYear ;
                    ex:mes "{mes}"^^xsd:gMonth ;
                    dbo:sex dbr:{sexo} ;
                    dbo:ageRange ?idade .
        }}
        GROUP BY ?idade
        ORDER BY ?idade
        """
        sparql.setQuery(query)
        results = sparql.query().convert()

        rows = []
        for r in results["results"]["bindings"]:
            idade = r["idade"]["value"]
            rows.append({
                "Faixa Etária": idade,
                "Qtd": int(r["qtd"]["value"]),
            })

        df = pd.DataFrame(rows)
        st.subheader(f"📊 Faixa Etária em {ano}-{mes} ({sexo})")
        st.bar_chart(df.set_index("Faixa Etária")["Qtd"])

        if st.button("➡️ Drill-down Final"):
            st.session_state["selected_drill_final"] = st.selectbox("Escolha o próximo nível:", ["Município do Beneficiário", "CID_1"], key="final_choice")
            st.session_state["drill_level"] = 3
            st.rerun()

        if st.button("⬅️ Voltar para Sexo"):
            st.session_state["drill_level"] = 1
            st.rerun()

    elif st.session_state["drill_level"] == 3:
      ano, mes = st.session_state["selected_month"].split("-")
      sexo = st.session_state["selected_sex"]
      final_field = st.session_state["selected_drill_final"]
      final_pred = {
          "Município do Beneficiário": "ex:municipioBeneficiario",
          "CID_1": "dbo:disease"
      }[final_field]

      query = f"""
      PREFIX dbo: <http://dbpedia.org/ontology/>
      PREFIX dbr: <http://dbpedia.org/resource/>
      PREFIX ex: <http://example.org/health/>
      PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

      SELECT ?val (COUNT(?evento) AS ?qtd)
      WHERE {{
          ?evento a dbo:MedicalProcedure ;
                  ex:ano "{ano}"^^xsd:gYear ;
                  ex:mes "{mes}"^^xsd:gMonth ;
                  dbo:sex dbr:{sexo} ;
                  dbo:ageRange ?idade ;
                  {final_pred} ?val .
      }}
      GROUP BY ?val
      ORDER BY ?val
      """
      sparql.setQuery(query)
      results = sparql.query().convert()

      rows = []
      for r in results["results"]["bindings"]:
          val = r["val"]["value"]
          label = val.split("/")[-1] if "http" in val else val
          rows.append({final_field: label, "Qtd": int(r["qtd"]["value"])})

      df = pd.DataFrame(rows)
      st.subheader(f"🧩 {final_field} em {ano}-{mes} ({sexo})")
      st.bar_chart(df.set_index(final_field)["Qtd"])

      if st.button("⬅️ Voltar para Faixa Etária"):
          st.session_state["drill_level"] = 2
          st.rerun()

with tab4:
    st.subheader("📊 Distribuição dos Procedimentos por Categoria")

    category = st.selectbox("Escolha a categoria para visualização", {
        "Sexo": "dbo:sex",
        "Faixa Etária": "dbo:ageRange",
        "CID": "dbo:disease",
        "UF do Prestador": "dbo:region",
        "Porte": "ex:porte",
    })

    predicate = {
        "Sexo": "dbo:sex",
        "Faixa Etária": "dbo:ageRange",
        "CID": "dbo:disease",
        "UF do Prestador": "dbo:region",
        "Porte": "ex:porte",
    }[category]

    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX ex: <http://example.org/health/>
    PREFIX icd: <http://purl.bioontology.org/ontology/ICD10/>

    SELECT ?valor (COUNT(?evento) AS ?qtd)
    WHERE {{
        ?evento a dbo:MedicalProcedure ;
                {predicate} ?valor .
    }}
    GROUP BY ?valor
    ORDER BY DESC(?qtd)
    LIMIT 10
    """

    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
    except Exception as e:
        st.error(f"Erro ao consultar o GraphDB: {e}")
        st.stop()

    rows = []
    for r in results["results"]["bindings"]:
        value = r["valor"]["value"]
        label = value.split("/")[-1] if "http" in value else value
        rows.append({
            category: label,
            "Quantidade": int(r["qtd"]["value"])
        })

    df = pd.DataFrame(rows)

    if df.empty:
        st.warning("Nenhum dado encontrado para esta categoria.")
    else:
        st.subheader(f"📌 Top 10 - Distribuição por {category}")
        st.pyplot(
            df.set_index(category)["Quantidade"].plot.pie(
                autopct="%1.1f%%", figsize=(6, 6), ylabel=""
            ).figure
        )
        st.dataframe(df)

with tab5:
  st.subheader("🔗 Grafo Interativo dos Procedimentos e Relações")

  st.markdown(
      "Este grafo mostra a relação entre procedimentos médicos (`evento`) e seus atributos: "
      "**CID**, **Sexo**, **Faixa Etária**, e **Porte**."
  )

  st.info("Mostrando até 50 eventos para melhor desempenho.")

  query = """
  PREFIX dbo: <http://dbpedia.org/ontology/>
  PREFIX dbr: <http://dbpedia.org/resource/>
  PREFIX ex: <http://example.org/health/>
  PREFIX icd: <http://purl.bioontology.org/ontology/ICD10/>
  PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

  SELECT ?evento ?idade ?cid ?sexo ?porte
  WHERE {
    ?evento a dbo:MedicalProcedure ;
            dbo:ageRange ?idade ;
            dbo:disease ?cid ;
            dbo:sex ?sexo ;
            ex:porte ?porte .
  }
  LIMIT 50
  """

  sparql.setQuery(query)
  try:
      results = sparql.query().convert()
  except Exception as e:
      st.error(f"Erro ao buscar dados do grafo: {e}")
      st.stop()

  G = nx.Graph()

  for r in results["results"]["bindings"]:
      evento = r["evento"]["value"].split("/")[-1]
      cid = r["cid"]["value"].split("/")[-1]
      sexo = r["sexo"]["value"].split("/")[-1]
      idade = r["idade"]["value"]
      porte = r["porte"]["value"]

      G.add_node(evento, label=evento, title="Procedimento", color="lightblue", shape="dot")
      G.add_node(cid, label=cid, title="CID", color="salmon", shape="box")
      G.add_node(sexo, label=sexo, title="Sexo", color="orange", shape="ellipse")
      G.add_node(idade, label=idade, title="Faixa Etária", color="lightgreen", shape="ellipse")
      G.add_node(porte, label=porte, title="Porte", color="violet", shape="box")

      G.add_edge(evento, cid)
      G.add_edge(evento, sexo)
      G.add_edge(evento, idade)
      G.add_edge(evento, porte)

  net = Network(height="600px", width="100%", bgcolor="#FFF", font_color="white")
  net.from_nx(G)
  net.repulsion(node_distance=150, spring_length=200)

  net.save_graph("/tmp/grafo_streamlit.html")
  HtmlFile = open("/tmp/grafo_streamlit.html", "r", encoding="utf-8")
  components.html(HtmlFile.read(), height=650)