
# Input

```
./data/BodyOfKnowledge
```

Knowledge Unit as TXT file in Knowledge Are directories.

# Index the Body Of Knowledge 

Install SPARQLLM Globally 

```
pip install git+https://github.com/momo54/SPARQLLM.git
```
You can update SPARQLLM with `pip install --upgrade git+https://github.com/momo54/SPARQLLM.git`

install with virtualenv (recommended):
```
virtualenv xp-env
source xp-venv/bin/activate
pip install -r requirements.txt
```

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

Check config.bok to adjust parameter. Run the query (quite long):
```
slm-run --load data/courses.ttl --config config.bok --format=turtle -f queries/bok-graph.sparql --debug -o ./XP/bok.result --keep-store ./XP/bok.nq 
```

Notes: 
Faiss relies on  FlatIP to index with  normalisation. Score close to 1 is good, 0 or minus -> not similar


# Some notes
- File name of BOK with ' ' and ',' !! -> scripts/sanitize.py
