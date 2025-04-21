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
    - SPARQLLM is a Retrieval-Augmented SPARQL Query engine. 
      - Many times, information is not available in the Knowledge Graph but in external sources.
      - SPARQLLM can search and extract knowledge from external sources  during query processing
    - The key idea is to have User-Defined Functions (UDFs) to dynamically generate named graphs by retrieving relevant information from external sources.
    """)

st.markdown(
    """
    ```
      BIND(ex:SLM-SEARCH(?course_desc,?course,3) AS ?search_graph)
      GRAPH ?search_graph {
        ?course ex:is_aligned_with ?bn .
        ?bn ex:has_score ?score .
        ?bn ex:has_source ?ku_source .
        ?bn ex:has_chunk ?chunk .
    }
    ```
    """)

st.markdown(
    """
    ```
    BIND(CONCAT(" some prompt returning a schema.org type report with answer and explain property",?) AS ?prompt)
    BIND(ex:SLM-LLMGRAPH(?prompt,?course) AS ?llm_graph)
    GRAPH ?llm_graph {
        ?course ex:has_schema_type ?root .
        ?root a <http://schema.org/Report>  .
        ?root <http://schema.org/answer> ?answer .
        ?root <http://schema.org/explain> ?explain .    
    }
    ```
    """)




st.write(
     """
    - We mainly implemented 2 series of UDFs:
      - we implemented `SLM-SEARCH` for local keyword search (Whoosh), local vector database (FAISS) and web search (Google)
      - we implemented `SLM-LLM` for Language Model (LLM) with local OLLAMA models, MistralAI models, and OPenAI models.
    """)



st.write("## Use-Case for a Computer Science Program")

st.write(
    """
    - We have a Knowledge Graph representing a Master Computer Science program. It describes the courses with their tracks, their description, their level, their objective etc. But we don't know how the tracks  cover the body of knowledge in computer science. 

    - ACM/IEEE/AAAI released Computer Science curricula [CS2023](https://csed.acm.org/) as a PDF document of 459 pages. It includes description of knowledge units and knowledge areas of in Computer Science

    - The problem is to align the courses of the tracks of the computer science program with  knowledge units of the ACM CS Curricula.
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
