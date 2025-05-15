This is a demo scenario for SPARQLLM, a Retrieval-Augmented SPARQL Query engine. A video of the demo is available on YouTube. The demo has been accepted to ESWC2025.

Input

./data/BodyOfKnowledge (BOK) is the extraction of Knowledge Units (KU) from [https://csed.acm.org/], aggregated per Knowledge AREA (KA). Knowledge Unit as TXT file in Knowledge Area directories.

./data/courses.ttl is a knowledge graph representation of an (old) Master Program in Computer Science at University of Nantes. The objective is to align the UE of the Nantes curricula (NC) to the KU of BOK. SPARQLLM is used to implement a pipeline that:

- Enumerates UEs from NC
- Finds 3 KU candidates with Vector Search
- Asks LLM to confirm if really the UE is aligned to KU and why.
- The output is an alignment of UE to KU that can be displayed on a radar view.

BOK Radar

Index the Body of Knowledge

Install SPARQLLM Globally

# Index the Body Of Knowledge 



install with virtualenv (recommended):

virtualenv xp-env
source xp-env/bin/activate
pip install -r requirements.txt
Need Ollama installed, for Linux, MacOS:

curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.1:latest
ollama pull nomic-embed-text
Index the Body of Knowledge:

slm-index-faiss --txt-folder ./data/BodyOfKnowledge --faiss-dir ./XP/bok_store --recurse
Run the query to align the cursus to BOK:

Check config.bok to adjust parameters. Run the query (quite fast but limited to 1):

slm-run --config config.bok -f queries/bok-graph-limit1.sparql --debug -o ./XP/bok.result --keep-store ./XP/bok.nq
Same query with Construct instead of Select (long):

slm-run --config config.bok -f queries/bok-graph-construct.sparql --debug -o ./XP/bokc.ttl --keep-store ./XP/bokc.nq
Run the UI to explore the results

User Interface to see SPARQLLM in action on the BOK Use-Case:

streamlit run scripts/HOME.py

🧩 Dépendances

Ce projet utilise :  
- pandas : traitement et manipulation des fichiers CSV  
- rdflib : génération et validation des graphes RDF  
- SPARQLLM : alignement sémantique (optionnel)

Toutes les dépendances sont listées dans `requirements.txt`.

🎯 Pipeline résumé

- Les maquettes PDF sont converties en `.csv` via iLovePDF + Apple Numbers  
- Les fichiers `.csv` sont nettoyés automatiquement avec `clean_vertical_csv.py`  
- Les CSV nettoyés sont transformés en RDF avec `csv_to_rdf.py`  
- Les fichiers RDF sont vérifiés par `validate_rdf.py` et `validate_rdf_quality.py`

Contexte

Ce travail est réalisé dans le cadre de mon stage de recherche au LS2N (Université de Nantes) dans le projet SPARQLLLM, encadré par Hala Skaf-Molli et Pascal Molli. Cette branche permet d'ajouter mes propres modifications et fichiers sans affecter les travaux effectués dans la branche groquick.

📘 Lien vers le dépôt pour la transformation des maquettes PDF en RDF : [Licence Maquettes RDF](https://github.com/nourrekik/licence-maquettes-rdf)
