
This is a demo scenario for [SPARQLLM](https://github.com/GDD-Nantes/SPARQLLM), a Retrieval-Augmented SPARQL Query engine. A video of the demo is available on [YouTube](https://www.youtube.com/watch?v=Oob2ci2TsGE). The demo has been accepted to [ESWC2025](https://2025.eswc-conferences.org/).



# Install software

install with virtualenv (recommended):
```
virtualenv xp-env
source xp-env/bin/activate
pip install -r requirements.txt
```

To follow SPARQLLM updates, you can update SPARQLLM with `pip install --upgrade git+https://github.com/GDD-Nantes/SPARQLLM.git` (@branch_name for a branch) 
Sometimes, i need "pip install --no-cache-dir --force-reinstall git+https://github.com/GDD-Nantes/SPARQLLM.git"

# Index the Body of Knowledge with Faiss

Need Ollama installed, For Linux, MacOS:
```
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1:latest
ollama pull nomic-embed-text
```

Index the Body of Knowledge:
```
slm-index-faiss --txt-folder ./data/BodyOfKnowledge --faiss-dir ./XP/bok_store --recurse 
```

# Get the KG of graduation

* get the data on `https://github.com/momo54/NUCS-KG`:
```
 wget https://raw.githubusercontent.com/momo54/NUCS-KG/master/XP/all.ttl -O ./data/all2025.ttl
```

* You can also get the exam2desc data from `https://github.com/momo54/exam2rdf`
```
https://github.com/momo54/exam2rdf/raw/refs/heads/master/exam2desc.ttl -o ./data/exam2desc.ttl
```

* You can also get JSON data from the CS2023 body of knowledge from `https://github.com/momo54/BOK-KG`
  

# run the query to align our cursus to BOK

Check config.bok to adjust parameter. Run the following neuro-semantic query (long):
```
slm-run --config config.bok --load ./data/all2025.ttl --format turtle -f queries/bok-graph-construct-cli.sparql --debug -o ./XP/align2025/all2025-aligned-again.ttl --keep-store ./XP/align2025/all2025-aligned-again.nq
```


Notes: 
Faiss relies on  FlatIP to index with  normalisation. Score close to 1 is good, 0 or minus -> not similar

# Run the UI to explore the results

User Interface to see SPARQLLM in action on the BOK Use-Case:
```
streamlit run scripts/HOME.py
streamlit run scripts/HOME.py --server.port 8502
streamlit run scripts/HOME.py --server.port 8501
streamlit run scripts/pages/2_Alignment_radar.py --server.port 8503
```

hmm... seems that having loaded SPARQLLM in one page impact RDFLIB in other pages.
Maybe better to isolate with multiple server... It seems tha lazy-join forced for radar queries slow-down its processing.

Check `./scripts/pages`to adjust inputs files if changed it.

