import streamlit as st
import rdflib
from pathlib import Path
import pandas as pd
from string import Template

# === Constantes fichiers ===
ALIGNMENT_RDF_FILE_PATH = "./XP/align2025/all2025-aligned-again.ttl"
COURSES_RDF_FILE_PATH = "./data/all2025.ttl"


# === Chargement du graphe RDF fusionné ===
g = rdflib.Graph()
try:
    g.parse(ALIGNMENT_RDF_FILE_PATH, format="turtle")
    g.parse(COURSES_RDF_FILE_PATH, format="turtle")
    st.sidebar.success("✅ RDF graph loaded successfully!")
except Exception as e:
    st.sidebar.error(f"❌ Error loading RDF files: {e}")
    st.stop()

# === Requête SPARQL ===
# === Requête SPARQL pour récupérer les couples (level, code) ===
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

# Formatage en liste (label + valeur)
parcours_options = [(str(r.level), str(r.code)) for r in results_parcours]
parcours_labels = [f"{level} — {code}" for level, code in parcours_options]

# Affichage dans la sidebar
selection_label = st.sidebar.selectbox("🎓 Choisissez un parcours (niveau + code)", parcours_labels)

# Extraction des valeurs sélectionnées
selected_level, selected_code = parcours_options[parcours_labels.index(selection_label)]

if ("last_level" not in st.session_state
        or "last_code" not in st.session_state
        or st.session_state.last_level != selected_level
        or st.session_state.last_code != selected_code):
    st.session_state.index = 0
    st.session_state.last_level = selected_level
    st.session_state.last_code = selected_code

template_query = Template("""
PREFIX provo: <http://provo.org/> 
PREFIX course: <http://example.org/course/> 
PREFIX align: <http://align.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?ue ?ue_text ?ku ?ku_source (GROUP_CONCAT(CONCAT(?answer,':',?model);separator=",") as ?rep)
WHERE {
    { select ?ue (group_concat(distinct ?label) as ?labels)
              (group_concat(distinct ?content) as ?contents)
              (group_concat(distinct ?objective) as ?objectives)
        WHERE {
            ?ue course:parcours_level "${LEVEL}" ;
                course:parcours_code "${CODE}" .
            ?ue rdfs:label ?label .
            ?ue course:content ?content .
            ?ue course:objective ?objective .
        } group by ?ue 
    }
    BIND(CONCAT("Course name: ",STR(?labels),
                "Objective: ",STR(?objectives),
                "Course content: ",STR(?contents)) AS ?ue_text)                          
  ?ue align:to [
    course:ku ?ku ;
    align:ku_source ?ku_source ;
    course:answer ?answer ;
    align:score ?score ;
    provo:wasGeneratedBy [ provo:used ?model ]
  ] .
} GROUP BY ?ue ?ku
""")


print(f"=== Requête SPARQL ===\n{template_query.substitute(LEVEL=selected_level, CODE=selected_code)}")

# Requête adaptée au parcours sélectionné
query = template_query.substitute(
    LEVEL=selected_level,
    CODE=selected_code,
)

# === Exécution de la requête ===
results = g.query(query)
st.text(f"### Query results: {len(results)} alignments found")

# === Conversion vers liste Python ===
#@st.cache_data
#@st.cache_data

def extract_alignments(_results):
    data = []
    for row in _results:
        ue, ue_text, ku, ku_source, rep = row  # déballer explicitement
        data.append({
            "ue_uri": str(ue),
            "ue_text": str(ue_text),
            "ku": str(ku),
            "ku_source": str(ku_source),
            "answer": str(rep)
        })
    return data

alignments = extract_alignments(results)
st.sidebar.info(f"📦 {len(alignments)} alignements extraits")

# === Interface Streamlit ===
st.title("🔎 Validation manuelle des alignements UE ↔️ KU")

if "index" not in st.session_state:
    st.session_state.index = 0

if "annotations" not in st.session_state:
    st.session_state.annotations = {}

if len(alignments) == 0:
    st.warning("Aucun alignement trouvé dans les fichiers RDF.")
    st.stop()

index = st.session_state.index
row = alignments[index]

st.markdown(f"### Alignement {index + 1} / {len(alignments)}")
st.markdown(f"- **UE URI**: `{row['ue_uri']}`")
st.markdown(f"- **KU**: `{row['ku']}`")
st.markdown(f"- **Fichier KU**: `{row['ku_source']}`")

# === Chargement du texte de la KU ===
ku_path = Path(row["ku_source"].replace("file://", ""))
if ku_path.exists():
    ku_text = ku_path.read_text(encoding="utf-8")
else:
    ku_text = "⚠️ Fichier KU introuvable."

# === Affichage côte à côte ===
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Texte de l'UE")
    st.text_area("UE", row["ue_text"], height=300, disabled=True)
with col2:
    st.markdown("#### Texte de la KU")
    st.text_area("KU", ku_text, height=300, disabled=True)

# === Analyse des réponses LLM ===
# Format: "0:modelA,1:modelB,0:modelC"
# Format attendu : "0:modelA,1:modelB,0:modelC"
votes = row["answer"].split(",")
parsed_votes = []

for v in votes:
    try:
        vote, model = v.split(":", 1)
        parsed_votes.append((vote.strip(), model.strip()))
    except ValueError:
        continue  # ignore lignes mal formées

# Tri lexicographique par nom de modèle
parsed_votes.sort(key=lambda x: x[1])

# Comptage
yes_votes = sum(1 for vote, _ in parsed_votes if vote == "1")
total = len(parsed_votes)

st.markdown(f"**Votes LLM :** {yes_votes}/{total} modèles ont validé l'alignement.")

# Affichage ligne unique
vote_line = " ".join([f"{'✅' if vote == '1' else '❌'} {model}" for vote, model in parsed_votes])
st.markdown(f"**Détail des votes :** {vote_line}")
    
# === Interface d’annotation humaine ===
decision = st.radio("Votre validation humaine :", ["Non évalué", "✅ Valide", "❌ Invalide"], key=index)
commentaire = st.text_input("💬 Commentaire (optionnel)", key=f"comment_{index}")

if st.button("💾 Enregistrer"):
    st.session_state.annotations[index] = {
        "ue": row["ue_uri"],
        "ku": row["ku"],
        "decision": decision,
        "comment": commentaire
    }
    st.success("Décision enregistrée")

# === Navigation ===
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("⬅️ Précédent") and index > 0:
        st.session_state.index -= 1
with col_next:
    if st.button("➡️ Suivant") and index < len(alignments) - 1:
        st.session_state.index += 1

# === Export des annotations ===
if st.button("📤 Exporter toutes les validations"):
    df_out = pd.DataFrame.from_dict(st.session_state.annotations, orient="index")
    df_out.to_csv("annotations_export.csv", index=False)
    st.success("Exporté vers `annotations_export.csv`")
