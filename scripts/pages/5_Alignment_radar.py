import streamlit as st
import pandas as pd
import plotly.express as px
import rdflib
from string import Template

# === Chemins RDF ===
BOK_RDF_FILE_PATH = "./XP/graph_bok_nohours.ttl"
TTLS = ["./XP/align2025/all2025-aligned-again.ttl", "./data/all2025.ttl"]

# === Chargement du graphe de référence (BOK) ===
gbok_ref = rdflib.Graph()
try:
    gbok_ref.parse(BOK_RDF_FILE_PATH, format="turtle")
except Exception as e:
    st.sidebar.error(f"❌ Erreur chargement BOK : {e}")
    st.stop()

# === Chargement des graphes alignés et cours ===
g = rdflib.Graph()
for ttl in TTLS:
    try:
        g.parse(ttl, format="turtle")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur chargement {ttl} : {e}")
        st.stop()
st.sidebar.success("✅ RDF graph loaded")

# === Query pour codes de parcours ===
query_parcours = """
PREFIX ex: <http://example.org/course/>
SELECT ?level ?code
WHERE {
    ?ue ex:parcours_level ?level ;
        ex:parcours_code ?code .
}
GROUP BY ?level ?code
ORDER BY ?level 
"""

results_parcours = g.query(query_parcours)

parcours_dict = {}
for row in results_parcours:
    level = str(row.level)
    code = str(row.code)
    parcours_dict.setdefault(level, []).append(code)

# === Widgets de sélection ===
st.title("Radar View des KA par parcours et LLM")

col1, col2, col3 = st.columns(3)
with col1:
    L1_code = st.selectbox("Choisir le parcours L1", parcours_dict.get("L1", [""]), index=0)
    L2_code = st.selectbox("Choisir le parcours L2", parcours_dict.get("L2", [""]), index=0)
with col2:
    L3_code = st.selectbox("Choisir le parcours L3", parcours_dict.get("L3", [""]), index=0)
    M1_code = st.selectbox("Choisir le parcours M1", parcours_dict.get("M1", [""]), index=0)
with col3:
    M2_code = st.selectbox("Choisir le parcours M2", parcours_dict.get("M2", [""]), index=0)
    LLM_model = st.selectbox("Choisir le modèle LLM", ["llama3-8b-8192", "qwen-qwq-32b", "deepseek-r1-distill-llama-70b"])

# === Requête principale KA x KU ===
def get_ka_data(graph, L1_code,L2_code, L3_code, M1_code, M2_code, LLM_model):
    template_query = Template("""
        PREFIX ex: <http://example.org/course/>
        prefix ns1: <http://provo.org/> 
        prefix ns3: <http://align.org/> 
        prefix xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?ka (COUNT(DISTINCT ?ku) AS ?nb_ku) WHERE {
        {
            SELECT DISTINCT ?ue WHERE {
                {
                    ?ue a ex:UE ;
                        ex:parcours_level "L1" ;
                        ex:parcours_code "${L1_code}" .
                } UNION {
                    ?ue a ex:UE ;
                        ex:parcours_level "L2" ;
                        ex:parcours_code "${L2_code}" .
                } UNION {
                    ?ue a ex:UE ;
                        ex:parcours_level "L3" ;
                        ex:parcours_code "${L3_code}" .
                } UNION {
                    ?ue a ex:UE ;
                        ex:parcours_level "M1" ;
                        ex:parcours_code "${M1_code}" .
                } UNION {
                    ?ue a ex:UE ;
                        ex:parcours_level "M2" ;
                        ex:parcours_code "${M2_code}" .
                }
            }
        }
        ?ue ns3:to [
            ex:answer "1" ;
            ex:ku ?ku ;
            ex:ka ?ka ;
            ns1:wasGeneratedBy [ ns1:used "${LLM_model}" ]
        ] .
        }
        GROUP BY ?ka
    """)
    query = template_query.substitute(
        L1_code=L1_code,
        L2_code=L2_code,
        L3_code=L3_code,
        M1_code=M1_code,
        M2_code=M2_code,
        LLM_model=LLM_model
    )
    return graph.query(query)

# === Requête de référence : toutes les KUs par KA ===
def get_reference_data(graph):
    distinct_ku = """
    PREFIX bok: <http://example.org/bok/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT ?ka (COUNT(DISTINCT ?ku) AS ?nb_ku)
    WHERE {
      ?ku bok:part_of ?ka .
    } 
    GROUP BY ?ka
    ORDER BY ?ka
    """
    return graph.query(distinct_ku)

# === Affichage radar ===
if st.button("📊 Générer la radar view avec référence"):
    results = get_ka_data(g, L1_code,L2_code, L3_code, M1_code, M2_code, LLM_model)
    ref_results = get_reference_data(gbok_ref)

    # Extraire les KAs de référence dans l'ordre
    ka_order = []
    ref_data = []
    for row in ref_results:
        ka = str(row.ka)
        ka_order.append(ka)
        ref_data.append({"KA": ka, "nb_KU": int(row.nb_ku), "Source": "Référence"})

    # Résultats LLM
    llm_data = []
    for row in results:
        llm_data.append({"KA": str(row.ka), "nb_KU": int(row.nb_ku), "Source": f"{LLM_model}"})

    # Fusionner et ordonner
    df = pd.DataFrame(ref_data + llm_data)
    df["KA"] = pd.Categorical(df["KA"], categories=ka_order, ordered=True)
    df = df.sort_values("KA")

    if df.empty:
        st.warning("Aucune donnée trouvée.")
    else:
        fig = px.line_polar(df, r="nb_KU", theta="KA", color="Source", line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(title=f"Radar View : {LLM_model} vs Référence globale")
        st.plotly_chart(fig, use_container_width=True)
