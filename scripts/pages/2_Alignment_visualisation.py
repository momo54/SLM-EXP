import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import rdflib

# Chemins des fichiers RDF
ALIGNMENT_RDF_FILE_PATH = "./XP/bokc.ttl"
COURSES_RDF_FILE_PATH = "./data/courses.ttl"

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Course Alignment Visualization",
    page_icon="🚀",
)

def create_figure(matched_courses):
    # Données de base (tous les cours)
    ka_count_all = matched_courses.groupby("ka")["s"].nunique().reset_index()
    ka_count_all.columns = ["ka", "count"]
    ka_count_all = ka_count_all.sort_values(by="ka")

    # Simuler les données CS et KA (à remplacer par vos vraies données)
    ka_count_cs = ka_count_all.copy()
    ka_count_cs["count"] = ka_count_cs["count"] * 1.5  # Exemple de transformation

    ka_count_ka = ka_count_all.copy()
    ka_count_ka["count"] = ka_count_ka["count"] * 2  # Exemple de transformation

    # Création du graphique
    fig = go.Figure()
    
    # Ajouter les traces de fond (CS et KA)
    fig.add_trace(go.Scatterpolar(
        r=ka_count_cs["count"],
        theta=ka_count_cs["ka"],
        fill='toself',
        name='CS Core Hours',
        line_color='lightblue',
        opacity=0.3
    ))

    fig.add_trace(go.Scatterpolar(
        r=ka_count_ka["count"],
        theta=ka_count_ka["ka"],
        fill='toself',
        name='KA Core Hours',
        line_color='lightpink',
        opacity=0.3
    ))
    
    # Ajouter la trace pour tous les cours
    fig.add_trace(go.Scatterpolar(
        r=ka_count_all["count"],
        theta=ka_count_all["ka"],
        fill='toself',
        name='All Courses',
        line_color='darkgray',
        opacity=0.5
    ))
    
    # Extraire tous les parcours uniques
    all_paths = matched_courses["path"].str.split(",").explode().unique()
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'cyan']
    
    # Afficher chaque parcours sur le radar
    for i, path in enumerate(all_paths):
        courses = matched_courses[matched_courses["path"].str.contains(path)]
        ka_count = courses.groupby("ka")["s"].nunique().reset_index()
        ka_count.columns = ["ka", "count"]
        ka_count = ka_count.sort_values(by="ka")

        fig.add_trace(go.Scatterpolar(
            r=ka_count["count"],
            theta=ka_count["ka"],
            fill='toself',
            name=path,
            line_color=colors[i % len(colors)]
        ))

    # Mise en page du graphique
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                color='black',
                tickfont=dict(color='black', size=12)
            ),
            angularaxis=dict(
                color='black',
                tickfont=dict(size=12)
            )
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend=dict(
            font=dict(size=14, color="black"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            x=1.05,
            y=0.95
        )
    )

    return fig

# Titre et description
st.title("🔎 Courses aligned to reference Computer Science knowledge areas")
st.write("This page displays the courses aligned to the reference Computer Science knowledge areas as defined in the Computer Science body of knowledge book.")

# Configuration de la barre latérale
st.sidebar.header("🔍 SPARQL Query")
st.sidebar.slider("Alignment confidence", 0.5, 1.0, 0.7, key="threshold")

# Chargement du fichier RDF
g = rdflib.Graph()
try:
    g.parse(ALIGNMENT_RDF_FILE_PATH, format="turtle")
    g.parse(COURSES_RDF_FILE_PATH, format="turtle")
    st.sidebar.success("RDF graph loaded successfully!")
except Exception as e:
    st.sidebar.error(f"Error loading RDF file: {e}")
    st.stop()

# Requête SPARQL
aligned_courses = f"""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX align: <http://align.org/>
PREFIX course: <http://example.org/course/>
SELECT ?s ?label ?path ?ans ?score ?ka WHERE {{
   ?s rdfs:label ?label ;
        course:parcours ?path ;
        align:to ?bn .
   ?bn course:ka ?ka ;
        align:score ?score ; 
        course:answer ?ans .
   FILTER (?ans = "1" && ?score > {st.session_state["threshold"]})  
}}"""

# Zone de requête
query = st.text_area("Retrieving aligned courses:", aligned_courses, height=200)

# Bouton d'exécution de la requête
if st.button("Run query"):
    try:
        # Exécution de la requête
        results = g.query(query)

        # Transformation en DataFrame
        data = [[str(value) for value in row] for row in results]
        df = pd.DataFrame(data, columns=[str(var) for var in results.vars])
        st.session_state["matched_courses"] = df

        st.write("### Query results:")
        st.dataframe(df)

        # Création et affichage du graphique avec tous les parcours
        f = create_figure(df)
        st.plotly_chart(f)

    except Exception as e:
        st.sidebar.error(f"Error while executing the SPARQL query: {e}")
