import streamlit as st
import pandas as pd
import plotly.express as px
import rdflib
from string import Template

# === RDF Paths ===
BOK_RDF_FILE_PATH = "./XP/graph_bok_nohours.ttl"
TTLS = ["./XP/align2025/all2025-aligned-again.ttl", "./data/all2025.ttl"]

# === Load reference graph (BOK) ===
gbok_ref = rdflib.Graph()
try:
    gbok_ref.parse(BOK_RDF_FILE_PATH, format="turtle")
except Exception as e:
    st.sidebar.error(f"❌ Error loading BOK: {e}")
    st.stop()

# === Load aligned and course graphs ===
# galign = rdflib.Graph()
# for ttl in TTLS:
#     try:
#         galign.parse(ttl, format="turtle")
#     except Exception as e:
#         st.sidebar.error(f"❌ Error loading {ttl}: {e}")
#         st.stop()
# st.sidebar.success("✅ RDF graph loaded")

@st.cache_resource
def load_galign():
    g = rdflib.Graph()
    for ttl in TTLS:
        g.parse(ttl, format="turtle")
    return g

galign = load_galign()


# === Query for track codes ===
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

results_parcours = galign.query(query_parcours)

parcours_dict = {}
for row in results_parcours:
    level = str(row.level)
    code = str(row.code)
    parcours_dict.setdefault(level, []).append(code)

# === Selection widgets ===
st.title("Radar View of KAs by Track and LLM")

col1, col2, col3 = st.columns(3)
with col1:
    L1_code = st.selectbox("Select L1 track", ["NONE"] + parcours_dict.get("L1", [""]), index=0)
    L2_code = st.selectbox("Select L2 track", ["NONE"] + parcours_dict.get("L2", [""]), index=0)
with col2:
    L3_code = st.selectbox("Select L3 track", ["NONE"] + parcours_dict.get("L3", [""]), index=0)
    M1_code = st.selectbox("Select M1 track", ["NONE"] + parcours_dict.get("M1", [""]), index=0)
with col3:
    M2_code = st.selectbox("Select M2 track", ["NONE"] + parcours_dict.get("M2", [""]), index=0)
    LLM_model = st.selectbox("Select LLM model", ["llama3-8b-8192", "qwen-qwq-32b", "deepseek-r1-distill-llama-70b"])

# === Main query: KA x KU ===
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

# === Reference query: all KUs per KA ===
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

# === Radar plot display ===
if st.button("📊 Generate radar view with reference"):
    results = get_ka_data(galign, L1_code,L2_code, L3_code, M1_code, M2_code, LLM_model)
    ref_results = get_reference_data(gbok_ref)

    # Extract reference KAs in order
    ka_order = []
    ref_data = []
    for row in ref_results:
        ka = str(row.ka)
        ka_order.append(ka)
        ref_data.append({"KA": ka, "nb_KU": int(row.nb_ku), "Source": "Reference"})

    # LLM results
    llm_data = []
    for row in results:
        llm_data.append({"KA": str(row.ka), "nb_KU": int(row.nb_ku), "Source": "Selection"})

    # Merge and sort
    df = pd.DataFrame(ref_data + llm_data)
    df["KA"] = pd.Categorical(df["KA"], categories=ka_order, ordered=True)
    df = df.sort_values("KA")

    if df.empty:
        st.warning("No data found.")
    else:
        custom_colors = ["skyblue", "red"]
        fig = px.line_polar(
            df,
            r="nb_KU",
            theta="KA",
            color="Source",
            line_close=True,
            color_discrete_sequence=custom_colors
        )
        fig.update_traces(fill='toself')
        fig.update_layout(title=f"Radar View: Reference (skyblue) vs Selection (red) according to {LLM_model}")
        st.plotly_chart(fig, use_container_width=True)
