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
    This web application show case how SPARQLLM can be used
    to pilot, with SPARQL queries, the integration of knowledge graph, documents indexed with a vector database, and LLMs agents for KG completion and verification. 
    """
)

st.write("## Contact")

st.write("## Acknowledgment")

