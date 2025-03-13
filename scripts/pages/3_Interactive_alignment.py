import streamlit as st
import time

st.set_page_config(
    page_title="Demo 2",
    page_icon="🚀",
    layout="wide",
)

sample_course_desc = """The Master 2 program in Computer Science with a specialization in the Semantic Web provides advanced education in technologies and standards such as RDF (Resource Description Framework) and OWL (Web Ontology Language). Students learn to structure and query data to enhance interoperability across information systems. The curriculum includes ontology engineering, SPARQL query language, and practical applications of the Semantic Web. Graduates are prepared for careers in knowledge management, artificial intelligence, and data integration. The program emphasizes hands-on experience through research projects and industrial collaborations, addressing current challenges in the field."""

# set the title of the streamlit page in the side bar
st.title("🔎 Interactive alignment")
st.sidebar.header("🔍 Interactive alignment")

# input text area for the text to be aligned
text = st.text_area(
    "📝 Short description of a computer science course:",
    height=200,
    value=sample_course_desc,
)

# button to align the text
if st.button("Align"):
    st.write("Alignment in progress...")
    # simulate a long process by waiting for 2 seconds
    time.sleep(2)
    st.write("Alignment done!")
