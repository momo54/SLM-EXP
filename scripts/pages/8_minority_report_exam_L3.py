import streamlit as st
import pandas as pd
import rdflib
from urllib.parse import urlparse

# === Chargement du graphe RDF fusionné ===
g = rdflib.Graph()
TTLS = ["./XP/graph_bok_nohours.ttl", "./XP/l3/exam_l3.ttl", "./data/L3_merged.ttl"]
for ttl in TTLS:
    try:
        g.parse(ttl, format="turtle")
    except Exception as e:
        st.sidebar.error(f"Erreur lors du chargement de {ttl} : {e}")
        st.stop()

st.sidebar.success("✅ RDF graph loaded")

# === Requête pour extraire les alignements UE <-> KU ===
minority_query = """
PREFIX ns1: <http://provo.org/> 
PREFIX ns2: <http://example.org/course/> 
PREFIX ns3: <http://align.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?ue ?ku ?ku_source ?model ?answer ?score
WHERE {
  ?ue ns3:to [
    ns2:ku ?ku ;
    ns2:answer ?answer ;
    ns3:score ?score ;
    ns3:ku_source ?ku_source ;
    ns1:wasGeneratedBy [ ns1:used ?model ]
  ] .
}
ORDER BY ?ue ?ku ?model
"""

results = []
for row in g.query(minority_query):
    results.append({
        'UE': str(row.ue),
        'KU': str(row.ku),
        'KU_SOURCE': str(row.ku_source),
        'Model': str(row.model),
        'Answer': str(row.answer),
        'Score': float(row.score)
    })

df = pd.DataFrame(results)

# === Interface principale ===
st.title("🧪 Minority Report des examens de L3")

if not df.empty:
    # Pivot des réponses
    answer_pivot = df.pivot_table(index=['UE', 'KU'], columns='Model', values='Answer', aggfunc='first')
    score_pivot = df.pivot_table(index=['UE', 'KU'], columns='Model', values='Score', aggfunc='first')

    answer_pivot.columns = [f"{model} - Réponse" for model in answer_pivot.columns]
    score_pivot.columns = [f"{model} - Score" for model in score_pivot.columns]

    pivot_df = pd.concat([answer_pivot, score_pivot], axis=1).fillna("—")

    display_df = df.drop_duplicates(subset=['UE', 'KU'])[['UE', 'KU']].copy()
    display_df['Voir'] = display_df.apply(lambda row: f"{row['UE']}|||{row['KU']}", axis=1)

    selected_row = st.selectbox("Sélectionner une ligne pour voir les détails", display_df['Voir'])
    selected_ue, selected_ku = selected_row.split("|||")

    st.dataframe(pivot_df, use_container_width=True)

    # === Détails alignement
    st.subheader("🔎 Détails de l'alignement sélectionné")
    st.markdown(f"- **UE URI** : `{selected_ue}`")
    st.markdown(f"- **KU** : `{selected_ku}`")

    ku_file = f"file://{selected_ku.replace('http://example.org/', './').replace('_', '/')}.txt"
    st.markdown(f"- **Fichier KU**: `{ku_file}`")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📘 Texte de l'UE")
        ue_detail_query = f'''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ns1: <http://example.org/course/>
        SELECT ?label ?content ?objective
        WHERE {{
            <{selected_ue}> ns1:description ?label ;
                            ns1:hasTopic ?content ;
                            ns1:hasObjective ?objective .
        }}
        '''
        labels = set()
        contents = set()
        objectives = set()
        for r in g.query(ue_detail_query):
            labels.add(str(r.label))
            contents.add(str(r.content))
            objectives.add(str(r.objective))

        if labels or contents or objectives:
            st.markdown("**Labels :**")
            st.text("\n".join(sorted(labels)))
            st.markdown("**Objectifs :**")
            st.text("\n".join(sorted(objectives)))
            st.markdown("**Contenus :**")
            st.text("\n".join(sorted(contents)))
        else:
            st.info("Aucune description trouvée.")

    with col2:
        st.markdown("### 📕 Texte de la KU")
        try:
            ku_path = df[(df['UE'] == selected_ue) & (df['KU'] == selected_ku)].iloc[0]['KU_SOURCE']
            parsed_path = urlparse(ku_path).path
            with open(parsed_path, "r") as f:
                st.text(f.read())
        except Exception as e:
            st.warning(f"Impossible de lire le fichier KU : {e}")
else:
    st.warning("Aucune donnée alignée trouvée.")
