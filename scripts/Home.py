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
    SPARQLLM enable Retreival-Augmented SPARQL Query Processing. 
    It is built on top of RDFLIB and is available on [GitHub](https://github.com/momo54/SPARQLLM)

    This web application show case how SPARQLLM can be used
    to pilot, with SPARQL queries, the integration of knowledge graph, documents indexed with a vector database, and LLMs agents for KG completion and verification. 
    """
)

st.write("## Use-Case")

st.write(
    """
    - We have the Knowledge Graph of our curricula in Computer Science in Nantes. It describes the lectures with their description, their level, their objective etc.

    - ACM/IEEE/AAAI released the 2023 curriculum for Computer Science (CS2023) as a PDF. It describes knowledge units and knowledge areas of in Computer Science

    - The problem is to align the lectures of our curricula to the knowledge units of CS2023

    - We write the alignment process as a Retrieval-Augmented SPARQL query.
    """
)

st.write("## The process")

st.write(
    """
    - The Knowledge Graph of our Master in Computer Science in Nantes is just a Turtle File.   

    - We extracted Knowledge Units from the PDF of CS2023 as Text files.

    - We indexed it with FAISS using LLM Model

    - We wrote the SPARQLLLM query that perform alignements as a CONSTUCT query that augment the origin Knowledge Graph

    - We wrote a UI allowing to see the profiles of the different track of Master in Nantes.
    """
)


st.write("## Contact")

st.write("""
            - Pascal Molli (Nantes Université)
            - Hala Skaf-Molli (Nantes Université)
            - Sebastien Ferré (University of Rennes)
            - Alban Gaignard (CNRS)
            - Peggy Cellier (University of Rennes)         
         """)


st.write("## Acknowledgment")

st.write("- Students of Master Info of Nantes University")
