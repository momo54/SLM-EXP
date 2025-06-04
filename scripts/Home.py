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
    page_title="SLM-EXP home",
    page_icon="👋",
)


st.title("🔎 Demo SPARQLLM")

st.write(
    """
    - SPARQLLM is a Neuro-Symbolic SPARQL Engine. 
    - It allows to execute neuro-symbolic queries mixing  neural processing and SPARQL processing.
    - SPARQLLM return neuro-symbolic results.  
    """)

st.markdown(
    """
    ```
    SELECT ?msg {
    BIND('''Say Hello to the neuro-symbolic world:
    Return *ONLY* a JSON-LD object of type `Event` in the following format:
    {
      "@context": "http://schema.org/",
      "@type": "Event",
      "message": "text",
    }
    ''' AS ?prompt)
    BIND(<http://example.org/hello> AS ?uri)
    BIND(ex:SLM-LLMGRAPH_GROQ(?prompt,?uri) AS ?g)
     GRAPH ?g {
        ?uri ex:has_schema_type ?bn . 
        ?root a schema:Event. 
        ?root schema:message ?msg .
     }
    }
    ```
    """)

st.write(
     """
    - If we run this query, we get a JSON-LD object of type `Event` with a message saying "Hello to the neuro-symbolic world".
    """)



st.write("## Use-Case for a Computer Science Program")

st.write(
    """
    - We have a Knowledge Graph representing a Master Computer Science program. It describes the courses with their tracks, their description, their level, their objective etc. But we don't know how the tracks  cover the body of knowledge in computer science. 

    - ACM/IEEE/AAAI released Computer Science curricula [CS2023](https://csed.acm.org/) as a PDF document of 459 pages. It includes description of knowledge units and knowledge areas of in Computer Science

    - The problem is to align the courses of the tracks of the computer science program with  knowledge units of the ACM CS Curricula.
    - **PROBLEM : Can we write a SPARQLLM query to align the courses of the program with the knowledge units of the ACM CS Curricula ?**
    """)
st.image("./scripts/slide1.png", caption="CS2023 Curriculum")

st.write("- Courses are described with text, and metadata (track, level, objective, etc.), Knowledge Units are described with text and metadata.")
st.image("./scripts/slide2.png", caption="Matching image")


st.write("## SPARQLLM Master Program use-Case setup")

st.write(
    """
    - The Knowledge Graph of a Master Computer Science Program  is just a Turtle File.   

    - We extracted the 162 Knowledge Units from the PDF of the ACM Computer Science Curricula CS2023 as Text files. Knowledge Units are linked to 17 Knowledge Areas.

    - We indexed it with `FAISS`, a vector database, using a LLM Model (`nomic-embed-text`)

    - We wrote a Retreival-Augmented SPARQLLLM query that search over for knowledge units and check for alignement.

    - We wrote a UI allowing to see the profiles of the different track of Master in Nantes.
    """)
st.image("./scripts/radar.png", caption="Radar image")

st.write("## Contact")

st.write(
    """
            - Pascal Molli (Nantes Université)
            - Hala Skaf-Molli (Nantes Université)
            - Sebastien Ferré (University of Rennes)
            - Alban Gaignard (CNRS)
            - Peggy Cellier (University of Rennes)         
         """
)


st.write("## Acknowledgment")

st.write(
    """- Master Students of Nantes Université in Computer Science
    - denez guery
    - corentin guillemot
    - malo le-gallic
    - wiame.taii,
    - mohammed.ouedrhiri
    """)
