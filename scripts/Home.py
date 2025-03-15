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
    SPARQLLM is a Retrieval-Augmented SPARQL Query engine. In this approach, external sources can be discovered during SPARQL query execution, allowing for the dynamic creation of a Knowledge Graph.
SPARQLLM is built on top of RDFLIB and is available at [https://github.com/momo54/SPARQLLM](https://github.com/momo54/SPARQLLM)

    """
)

st.write("## Use-Case")

st.write(
    """
    - We have the Knowledge Graph of our curricula in Computer Science in Nantes. It describes the lectures with their description, their level, their objective etc. But we don't know how the lectures of the master covers expected knowledge of a master in computer science. 

    - ACM/IEEE/AAAI released the 2023 curriculum for Computer Science [CS2023](https://csed.acm.org/) as a PDF. It describes knowledge units and knowledge areas of in Computer Science

    - The problem is to align the lectures of our curricula with 0 or many knowledge units of the ACM CS Curricula.
    """)
st.image("./scripts/slide1.png", caption="CS2023 Curriculum")

st.write("- Lectures are described with text, and metadata (level, objective, etc.), Knowledge Units are described with text and metadata.")
st.image("./scripts/slide2.png", caption="Matching image")



st.write("## The process")

st.write(
    """
    - The Knowledge Graph of our Master in Computer Science in Nantes is just a Turtle File.   

    - We extracted Knowledge Units from the PDF of CS2023 as Text files.

    - We indexed it with FAISS using LLM Model

    - We wrote a Retreival-Augmented SPARQLLLM query that perform alignments as a CONSTRUCT query that augment the origin Knowledge Graph

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
