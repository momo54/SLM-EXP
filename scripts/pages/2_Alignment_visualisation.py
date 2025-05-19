import streamlit as st
import pandas as pd
import plotly.express as px
import rdflib

BOK_RDF_FILE_PATH = "./XP/graph_bok_nohours.ttl"
ALIGNMENT_RDF_FILE_PATH = "./XP/bokc.ttl"
COURSES_RDF_FILE_PATH = "./data/courses.ttl"

radar_plots = None

st.set_page_config(
    page_title="Demo 1",
    page_icon="🚀",
)

if not "selected_course" in st.session_state:
    st.session_state["selected_course"] = []


def create_figure(data):
    # distinct count of s for each ka in the matched_courses dataframe
    ka_count = data.groupby("ka")["s"].nunique()
    ka_count = ka_count.reset_index()
    ka_count.columns = ["ka", "count"]

    # sort the ka_count dataframe by ka label
    ka_count = ka_count.sort_values(by="ka")

    fig = px.line_polar(
        r=list(ka_count["count"]),
        theta=list(ka_count["ka"]),
        line_close=True,
    )

    return fig


def handle_course_selection():
    with st.sidebar:
        st.multiselect(
            "Choose your course",
            st.session_state["learning_path"],
            key="selected_course",
            on_change=handle_course_selection,
        )


# set the title of the streamlit page in the side bar
st.title("🔎 Courses aligned to reference Computer Science knowledge areas.")
st.write(
    "This page displays the courses aligned to the reference Computer Science knowledge areas as defined in the Computer Science body of knowledge book."
)
st.sidebar.header("🔍 Requête SPARQL")
st.sidebar.slider("Alignment confidence", 0.5, 1.0, 0.7, key="threshold")

# Chargement du fichier RDF
g = rdflib.Graph()
try:
    g.parse(ALIGNMENT_RDF_FILE_PATH, format="turtle")
    g.parse(COURSES_RDF_FILE_PATH, format="turtle")
    st.sidebar.success("RDF graph loaded successfully!")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement du fichier RDF : {e}")
    st.stop()

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
        course:ku ?ku .
   FILTER (?ans = "1" && ?score > {st.session_state["threshold"]})  
}}"""

# a text area to display the query with 30 lines
# query = st.text_area("Retrieving aligned courses:", aligned_courses, height=200)
query = st.text_area("Retrieving aligned courses:", aligned_courses, height=200)
if st.button("Run query"):
    try:
        results = g.query(query)

        # Transformation en DataFrame
        data = []
        for row in results:
            data.append([str(value) for value in row])

        df = pd.DataFrame(data, columns=[str(var) for var in results.vars])
        st.session_state["matched_courses"] = df

        st.write("### Query results:")
        st.dataframe(df)

        learning_path = set()
        for p in df["path"].unique():
            p = p.split(",")
            learning_path.update(p)

        st.session_state["learning_path"] = sorted(learning_path)

        with st.sidebar:
            course = st.multiselect(
                "Choose your course",
                st.session_state["learning_path"],
                key="selected_course",
                on_change=handle_course_selection,
            )

        f = create_figure(df)
        st.plotly_chart(f)

    except Exception as e:
        st.sidebar.error(f"Error while executing the SPARQL query: {e}")

if len(st.session_state["selected_course"]) > 0:
    fig = px.line_polar()
    learning_path = st.session_state["selected_course"]
    matched_courses = st.session_state["matched_courses"]
    colors = px.colors.qualitative.Set1

    courses = matched_courses
    ka_count = courses.groupby("ka")["s"].nunique()
    ka_count = ka_count.reset_index()
    ka_count.columns = ["ka", "count"]
    ka_count = ka_count.sort_values(by="ka")
    css_color = "#d3d3d3"
    trace = px.line_polar(
        r=list(ka_count["count"]),
        theta=list(ka_count["ka"]),
        line_close=True,
        # line_shape="spline",
    ).data[0]
    trace.line.color = css_color
    trace.name = "all courses"
    fig.add_trace(trace)

    for path in learning_path:
        courses = matched_courses[matched_courses["path"].str.contains(path)]
        ka_count = courses.groupby("ka")["s"].nunique()
        ka_count = ka_count.reset_index()
        ka_count.columns = ["ka", "count"]
        ka_count = ka_count.sort_values(by="ka")

        c = learning_path.index(path)
        css_color = colors[c]

        trace = px.line_polar(
            r=list(ka_count["count"]),
            theta=list(ka_count["ka"]),
            line_close=True,
            # line_shape="spline",
        ).data[0]
        trace.line.color = css_color
        trace.name = path
        fig.add_trace(trace)

    fig.update_traces(showlegend=True)

    # st.session_state.figure = fig

    # st.plotly_chart(fig)

    # st.session_state.figure = fig

    # if st.session_state.figure:
    st.plotly_chart(fig, use_container_width=True)
