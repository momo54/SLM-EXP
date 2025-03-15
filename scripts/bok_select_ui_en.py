import logging
import re
import sys
import tempfile
import streamlit as st
import rdflib
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os
import time

from SPARQLLM.udf.SPARQLLM import store
from SPARQLLM.config import ConfigSingleton


# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SPARQLLM.udf")
logger.setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Config file is required
CONFIG = "./config.bok"
args = sys.argv
if "--config" in args:
    index = args.index("--config")
    if index + 1 < len(args):  
        CONFIG = args[index + 1]

st.write(f"Config is : {CONFIG}")

if "config_singleton" not in st.session_state:
    st.session_state.config_singleton = ConfigSingleton(config_file=CONFIG)
# Retrieve the singleton instance
config_instance = st.session_state.config_singleton

# 🏗️ Load the Knowledge Graph with RDFLib
st.title("🔎 SPARQLLM on Computer Science Curricula")

# Initialize the offset in session_state
if "offset" not in st.session_state:
    st.session_state.offset = 0
st.write(f"ℹ️ Current offset: {st.session_state.offset}")

# 📝 Input area for the SPARQL query
with open("scripts/bok-graph-select-limit.sparql", "r", encoding="utf-8") as file:
    query_template = file.read()
query = query_template.replace("{OFFSET}", str(st.session_state.offset))
st.text_area("📝 Enter your SPARQL query:", query, height=400)


def display_named_graph(store):
    # Display the named graphs
    named_graphs = list(store.contexts())

    if not named_graphs:
        st.warning("⚠️ No named graphs found in the dataset.")
        return

    # Create a table of named graphs
    data = [{"Graph": str(c.identifier), "Triples": len(c)} for c in named_graphs]
    df = pd.DataFrame(data)

    # Display the table
    st.write("### 📊 Named Graphs and Their Content")
    st.dataframe(df)

    for selected_graph_obj in named_graphs:
        for s, p, o in selected_graph_obj:
            print(f"Subject: {s}, Predicate: {p}, Object: {o}")  # Debugging
        triples = [{"Subject": str(s), "Predicate": str(p), "Object": str(o)} 
                    for s, p, o in selected_graph_obj]
        if triples:
            df_triples = pd.DataFrame(triples)
            st.write(f"### 📜 Triples of Named Graph `{selected_graph_obj.identifier}`")
            st.dataframe(df_triples, use_container_width=True)
        else:
            st.info(f"ℹ️ The named graph `{selected_graph_obj.identifier}` contains no triples.")


# 🎯 Execute the SPARQL query
if st.button("Run Query"):
    try:
        results = store.query(query)
        if len(results) == 0:
            st.warning("No results found.")
        else:
            # Transform results into a DataFrame
            data = []
            for row in results:
                data.append([str(value) for value in row])
            
            df = pd.DataFrame(data, columns=[str(var) for var in results.vars])
            st.write("### 🔍 Query Results:")
            st.dataframe(df)

        display_named_graph(store)

        # Next button to increase offset
        st.session_state.offset += 1  # Increase the offset
        st.button("Next")

    except Exception as e:
        st.error(f"Error while executing the query: {e}")

# Display the log...
st.title("Logs")

# Placeholder for logs
log_placeholder = st.empty()

# Function to display logs with auto-scroll in HTML/JS
def update_logs():
#    logs_html = "<div id='log-container' style='height:300px; overflow-y:auto; padding:10px; background-color:#f8f9fa; border-radius:5px;'>"
    logs_html = "<div id='log-container' style='height:300px; overflow-y:auto; padding:10px; border-radius:5px;'>"
    logs_html += "<br>".join(st.session_state.log_messages)
    logs_html += "</div>"
    log_placeholder.markdown(logs_html, unsafe_allow_html=True)

def extract_function_name(logger_name):
    match = re.search(r'\.udf\.(\w+)', logger_name)
    return match.group(1) if match else "Unknown"

# Function to capture and display logs
class StreamlitHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)

        function_name = extract_function_name(record.name)
        formatted_entry = f"[{function_name}] {log_entry[:60]}"

        st.session_state.log_messages.append(formatted_entry)
        
        # Limit the number of displayed logs to avoid excessive memory usage
        if len(st.session_state.log_messages) > 1000:
            st.session_state.log_messages = st.session_state.log_messages[-1000:]

        update_logs() 

        # Update the log area with a scrollbar
        # log_placeholder.text_area("Logs", "\n".join(st.session_state.log_messages), height=300)


for handler in logger.handlers[:]:  # Copy the list to avoid removal errors
    logger.removeHandler(handler)

handler = StreamlitHandler()
logger.addHandler(handler)

# Disable log propagation to avoid duplicates
logger.propagate = False

if "log_messages" not in st.session_state:
    st.session_state.log_messages = []
