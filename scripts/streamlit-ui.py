import streamlit as st
import rdflib
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 📂 Chemin de ton fichier RDF (à modifier si besoin)
RDF_FILE_PATH = "./XP/bokc.ttl"  # Mets ici le chemin de ton fichier RDF

# 🏗️ Charger le Knowledge Graph avec RDFLib
st.title("🔎 SPARQL Query Interface for Local Knowledge Graph")

st.sidebar.header("📂 Fichier RDF chargé")
st.sidebar.write(f"✅ Fichier utilisé : `{RDF_FILE_PATH}`")

g = rdflib.Graph()
try:
    g.parse(RDF_FILE_PATH, format="turtle")  # Change le format si besoin (xml, json-ld, nt...)
    st.sidebar.success("Graph chargé avec succès ! 🟢")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement du fichier RDF : {e}")
    st.stop()

# 📝 Zone de saisie pour la requête SPARQL
default_query = """
SELECT ?s ?p ?o WHERE {
  ?s ?p ?o .
} LIMIT 10
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

        # 📊 Affichage sous forme de graphe si on a des relations (triplets)
        if len(df.columns) == 2 or len(df.columns) == 3:
            st.write("### 🕸️ Visualisation sous forme de graphe")
            G = nx.DiGraph()
            for _, row in df.iterrows():
                G.add_edge(row[df.columns[0]], row[df.columns[-1]], label=row[df.columns[1]] if len(df.columns) == 3 else None)

            plt.figure(figsize=(8, 5))
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", font_size=10)
            
            # Ajout des labels sur les arêtes
            edge_labels = nx.get_edge_attributes(G, 'label')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

            st.pyplot(plt)

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
