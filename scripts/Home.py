import streamlit as st
import rdflib
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os
import time

# 📂 Chemin du fichier RDF (modifie si besoin)
RDF_FILE_PATH = "./XP/bokc.ttl"

st.set_page_config(
    page_title="SLM-EXPE home",
    page_icon="👋",
)

# with st.sidebar:
# st.page_link("streamlit-ui.py", label="SLM-EXPE", icon="🔥")
# st.page_link("pages/page_1.py", label="Demo 1", icon="🛡️")

st.title("🔎 SLM-EXPE home")

# a paragraph describing the app
st.write(
    """
    This web application show case how SPARQLLM can be used
    to pilot, with SPARQL queries, the integration of knowledge graph, documents indexed with a vector database, and LLMs agents for KG completion and verification. 
    """
)

# an image
st.image(
    "./data/summary.jpg",
    caption="IA generated image: 'a diagram with a conductor, plumbing pipes, which connect a library, and scientific databases, and web pages'",
)

st.write("## Contact")

st.write("## Acknowledgment")

# st.sidebar.header("📂 Fichier RDF chargé")
# st.sidebar.write(f"✅ Fichier utilisé : `{RDF_FILE_PATH}`")

# # Bouton pour ouvrir une nouvelle page Streamlit dans la barre latérale
# if st.sidebar.button("Ouvrir une nouvelle page"):
#     st.experimental_set_query_params(page="new_page")

# # Gestion de la navigation entre les pages
# query_params = st.experimental_get_query_params()
# if query_params.get("page") == ["new_page"]:
#     st.title("Nouvelle Page")
#     st.write("Bienvenue sur la nouvelle page !")
#     st.stop()

# Chargement du fichier RDF
# g = rdflib.Graph()
# try:
#     g.parse(RDF_FILE_PATH, format="turtle")
#     st.sidebar.success("✅ Graph chargé avec succès !")
# except Exception as e:
#     st.sidebar.error(f"Erreur lors du chargement du fichier RDF : {e}")
#     st.stop()

# # 📝 Zone de saisie pour la requête SPARQL
# default_query = """
# PREFIX align: <http://align.org/>
# PREFIX course: <http://example.org/course/>

# SELECT ?s ?score ?ku WHERE {
#    ?s align:to ?bn .
#    ?bn course:ku ?ku .
#    ?bn align:score ?score
# } LIMIT 100
# """

# aligned_courses = """
# PREFIX course: <http://example.org/course/>

# SELECT ?s ?ans ?score ?ku WHERE {
#    ?s align:to ?bn .
#    ?bn course:ku ?ku ;
#             align:score ?score ;
#             course:answer ?ans .
#    FILTER (?ans = "1" && ?score > 0.7)
# }
# """

# query = st.text_area("📝 Entrez votre requête SPARQL :", default_query, height=200)

# # 🎯 Exécution de la requête SPARQL
# if st.button("Exécuter la requête"):
#     try:
#         results = g.query(query)

#         # Transformation en DataFrame
#         data = []
#         for row in results:
#             data.append([str(value) for value in row])

#         df = pd.DataFrame(data, columns=[str(var) for var in results.vars])
#         st.write("### 🔍 Résultats de la requête :")
#         st.dataframe(df)

#         # 🕸️ Création du graphe interactif avec Pyvis
#         if len(df.columns) == 3:
#             st.write("### 🕸️ Visualisation interactive du graphe")

#             # Création du graphe avec NetworkX
#             G = nx.Graph()
#             for _, row in df.iterrows():
#                 source, score, ku = row  # Suppression de la conversion inutile
#                 print(f"Ajout de l'arête : {source} → {ku} avec score {score}")  # DEBUG
#                 G.add_edge(str(source), str(ku), weight=score, label=f"Score: {score}")

#             print(f"Nombre total de nœuds : {len(G.nodes())}")
#             print(f"Nombre total d'arêtes : {len(G.edges())}")

#             # 📌 Contrôles interactifs dans Streamlit
#             st.sidebar.header("⚙️ Paramètres du Graphe")

#             node_size = st.sidebar.slider("Taille des nœuds", 5, 50, 15)
#             edge_width = st.sidebar.slider("Épaisseur des arêtes", 1, 10, 3)
#             show_labels = st.sidebar.checkbox("Afficher les labels des nœuds", True)
#             show_score = st.sidebar.checkbox("Afficher les scores sur les arêtes", True)
#             layout_fixed = st.sidebar.checkbox("Disposition statique", False)

#             # 🎨 Choix des couleurs pour les types de nœuds (source et ku)
#             source_color = st.sidebar.color_picker(
#                 "Couleur des nœuds Source", "#1f78b4"
#             )
#             ku_color = st.sidebar.color_picker("Couleur des nœuds KU", "#33a02c")

#             # 📌 Création du graphe interactif Pyvis
#             net = Network(height="600px", width="100%", directed=True, notebook=False)

#             # Ajout des nœuds en s'assurant qu'ils ne sont pas `None`
#             for node in G.nodes():
#                 if node is None or node == "None":
#                     continue

#                 node_type = "source" if node in df["s"].values else "ku"
#                 color = source_color if node_type == "source" else ku_color
#                 net.add_node(
#                     str(node),
#                     label=str(node) if show_labels else "",
#                     title=str(node),
#                     color=color,
#                     size=node_size,
#                 )

#             # Ajout des arêtes en évitant les valeurs `None`
#             for edge in G.edges(data=True):
#                 source, target, data = edge

#                 if source is None or target is None:
#                     continue

#                 net.add_edge(
#                     str(source),
#                     str(target),
#                     label=data["label"] if show_score else "",
#                     width=edge_width,
#                 )

#             # 📂 Sauvegarde du graphe dans un fichier HTML temporaire
#             tmpfile_path = "graph.html"  # Nouveau fichier temporaire local

#             # Configurer les options Pyvis
#             # net.set_options("""
#             # var options = {
#             #   "nodes": { "borderWidth": 2, "shape": "dot" },
#             #   "edges": { "arrows": { "to": { "enabled": true } }, "smooth": false }
#             # };
#             # """)

#             # Appliquer la mise en page dynamique ou statique
#             net.force_atlas_2based(gravity=-50 if layout_fixed else -25)

#             # Sauvegarde du graphe
#             net.save_graph(tmpfile_path)
#             time.sleep(
#                 1
#             )  # 🛠️ Éviter que Streamlit tente de lire le fichier avant qu'il ne soit écrit complètement

#             # 📌 Lire et afficher le fichier dans Streamlit
#             with open(tmpfile_path, "r", encoding="utf-8") as f:
#                 html_content = f.read()

#             st.components.v1.html(html_content, height=650, scrolling=True)

#             # 🚀 Nettoyage : Optionnellement, supprimer le fichier après affichage
#             os.remove(tmpfile_path)

#     except Exception as e:
#         st.error(f"Erreur lors de l'exécution de la requête : {e}")
