
This is a demo scenario for [SPARQLLM](https://github.com/GDD-Nantes/SPARQLLM), a Retrieval-Augmented SPARQL Query engine. A video of the demo is available on [YouTube](https://www.youtube.com/watch?v=Oob2ci2TsGE). The demo has been accepted to [ESWC2025](https://2025.eswc-conferences.org/).


# Input

* get the data:
```
 wget https://raw.githubusercontent.com/momo54/NUCS-KG/master/XP/all.ttl -O all.ttl
```

# Index the Body Of Knowledge 

install with virtualenv (recommended):
```
virtualenv xp-env
source xp-env/bin/activate
pip install -r requirements.txt
```

To follow SPARQLLM updates, you can update SPARQLLM with `pip install --upgrade git+https://github.com/GDD-Nantes/SPARQLLM.git` (@branch_name for a branch) 
Sometimes, i need "pip install --no-cache-dir --force-reinstall git+https://github.com/GDD-Nantes/SPARQLLM.git"


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
or : (if you want to compare with cs_core)
slm-index-faiss --txt-folder ./data/cs_core_txt --faiss-dir ./XP/cs_core_results/bok_store --recurse
```


# run the query to align our cursus to BOK

Check config.bok to adjust parameter. Run the query (quite fast but limit 1):
```
slm-run  --config config.bok  -f queries/bok-graph-limit1.sparql --debug -o ./XP/bok.result --keep-store ./XP/bok.nq 
```

The same query with Constuct instead of select (long):
```
slm-run --config config.bok  -f queries/bok-graph-construct.sparql --debug -o ./XP/bokc.ttl --keep-store ./XP/bokc.nq

pour l'alignement avec les maquettes : 
slm-run  --config config.bok --load ./data/all2025.ttl --format turtle  -f queries/bok-graph-construct-cli.sparql --debug -o ./XP/align2025/all2025-aligned-again.ttl --keep-store ./XP/all2025-aligned-again.nq

pour l'alignement avec les examens : 
slm-run --config config.bok --load ./data/exam2desc.ttl --format turtle -f queries/bok-graph-construct-cli-exam.sparql --debug -o ./XP/exam-align.ttl --keep-store ./XP/exam-align.nq


Notes: 
Faiss relies on  FlatIP to index with  normalisation. Score close to 1 is good, 0 or minus -> not similar

# run the UI to explore the results

User Interface to see SPARQLLM in action on the BOK Use-Case:
```
streamlit run scripts/Home.py
```

