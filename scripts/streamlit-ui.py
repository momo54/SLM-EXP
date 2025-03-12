import streamlit as st
import rdflib
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile

# 📂 Chemin du fichier RDF (modifie si besoin)
RDF_FILE_PATH = "./XP/bokc.ttl"  

# 🏗️ Charger le Knowledge Graph avec RDFLib
st.title("🔎 SPARQL Query Interface for Local Knowledge Graph")

st.sidebar.header("📂 Fichier RDF chargé")
st.sidebar.write(f"✅ Fichier utilisé : `{RDF_FILE_PATH}`")

g = rdflib.Graph()
try:
    g.parse(RDF_FILE_PATH, format="turtle")  
    st.sidebar.success("✅ Graph chargé avec succès !")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement du fichier RDF : {e}")
    st.stop()

# 📝 Zone de saisie pour la requête SPARQL
default_query = """
SELECT ?s ?score ?ku WHERE {
   ?s <http://align.org/to> ?bn .
  ?bn <http://example.org/course/ku> ?ku .
  ?bn <http://align.org/score> ?score
} LIMIT 100
"""
query = st.text_area("📝 Entrez votre requête SPARQL :", default_query, height=200)

# 🎯 Exécution de la requête SPARQL
if st.button("Exécuter la requête"):
    try:
        results = g.query(query)

        # Transformation en DataFrame
        data = []
        for row in results:
            data.append([str(value) for value in row])
        
        df = pd.DataFrame(data, columns=[str(var) for var in results.vars])
        st.write("### 🔍 Résultats de la requête :")
        st.dataframe(df)

        # 🕸️ Création du graphe interactif avec Pyvis
        if len(df.columns) == 3:
            st.write("### 🕸️ Visualisation interactive du graphe")

            # Création du graphe avec NetworkX
            G = nx.DiGraph()
            for _, row in df.iterrows():
                source, score, ku = row
                G.add_edge(source, ku, weight=score, label=f"Score: {score}")

            # 📌 Création du graphe interactif Pyvis
            net = Network(height="600px", width="100%", directed=True, notebook=False)

            # Ajout des nœuds et arêtes
            for node in G.nodes():
                net.add_node(node, label=node, title=node)

            for edge in G.edges(data=True):
                source, target, data = edge
                net.add_edge(source, target, label=data["label"])

            # 📂 Sauvegarde temporaire du graphe en HTML
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
                net.save_graph(tmpfile.name)
                st.components.v1.html(open(tmpfile.name, "r").read(), height=650, scrolling=True)

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
