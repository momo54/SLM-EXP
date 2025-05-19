import pdfplumber
import re
import pandas as pd
import sys

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

def export_to_rdf(ues, output_ttl):
    EX = Namespace("http://example.org/ue/")
    g = Graph()
    g.bind("ex", EX)

    for ue in ues:
        code = ue.get("Code", "Unknown")
        subj = URIRef(f"{EX}UE_{code}")
        g.add((subj, RDF.type, EX.UE))
        
        for k, v in ue.items():
            if k == "Code":
                g.add((subj, EX.code, Literal(v)))
            elif k == "Parcours":
                for item in re.split(r",\s*", v):
                    g.add((subj, EX.parcours, Literal(item)))
            else:
                pred = EX[k.lower().replace(" ", "_").replace("-", "_")\
                                .replace("é", "e").replace("è", "e").replace("ê", "e")]
                g.add((subj, pred, Literal(v)))
    
    g.serialize(destination=output_ttl, format="turtle")
    print(f"Export RDF terminé : {output_ttl}")

import re


def extract_text_blocks(pdf_path):
    import pdfplumber
    import re

    # Lire toutes les lignes de texte à partir de la page après "Description des UE"
    with pdfplumber.open(pdf_path) as pdf:
        lines = []
        found_start = False
        for page in pdf.pages:
            page_text = page.extract_text()
            if not page_text:
                continue
            page_lines = page_text.splitlines()
            if not found_start:
                for i, line in enumerate(page_lines):
                    if "Description des UE" in line:
                        found_start = True
                        lines.extend(page_lines[i + 1:])  # commence après
                        break
            elif found_start:
                lines.extend(page_lines)

    # Identifier les blocs : ligne avec code UE (X... ou Y...), suivie de "Lieu d’enseignement"
    blocs = []
    current_bloc = []
    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(r"^(X|Y)[A-Z0-9]{4,}\b.*", line):
            if i + 1 < len(lines) and "Lieu d’enseignement" in lines[i + 1]:
                if current_bloc:
                    blocs.append("\n".join(current_bloc))
                    current_bloc = []
        current_bloc.append(lines[i])
    if current_bloc:
        blocs.append("\n".join(current_bloc))

    return blocs

def extract_text_blocks_presque(pdf_path):
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        lines = []
        skip = True
        for page in pdf.pages:
            page_text = page.extract_text()
            if not page_text:
                continue
            if skip and "Description des UE" in page_text:
                skip = False
            if not skip:
                lines.extend(page_text.splitlines())

    blocs = []
    current_bloc = []
    for i in range(len(lines)):
        line = lines[i].strip()
        
        # Détection d'un code UE seul ou accompagné d'un titre
        if re.match(r"^(X|Y)[A-Z0-9]{4,}\b.*", line):
            # Ligne suivante doit contenir "Lieu d’enseignement"
            if i + 1 < len(lines) and "Lieu d’enseignement" in lines[i + 1]:
                if current_bloc:
                    blocs.append("\n".join(current_bloc))
                    current_bloc = []
        current_bloc.append(lines[i])

    if current_bloc:
        blocs.append("\n".join(current_bloc))

    return blocs

def extract_text_blocks_licence(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        skip = True
        for page in pdf.pages:
            page_text = page.extract_text()
            if skip:
                if "Description des UE" in page_text:
                    skip = False
                    text += page_text + "\n"
            else:
                text += page_text + "\n"

    # Trouver tous les blocs où le code UE commence une ligne
    matches = list(re.finditer(r"(?m)^X\d{2}[A-Z]\d{3}.*(?:\n.+)*?", text))
    
    blocs = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        bloc = text[start:end].strip()
        blocs.append(bloc)
    
    return blocs

def parse_bloc(bloc):
    ue = {}
    lignes = bloc.splitlines()
    if not lignes:
        return ue

    # On suppose que la première ligne commence par le code
    first_line = lignes[0].strip()
    match = re.match(r"^((X|Y)[A-Z0-9]{4,})\s+(.*)", first_line)
    if match:
        ue['Code'] = match.group(1)
        ue['Titre'] = match.group(3).strip()
    else:
        ue['Code'] = "Inconnu"
        ue['Titre'] = first_line  # fallback

    champs = {
        "Lieu d’enseignement": "Lieu",
        "Niveau": "Niveau",
        "Semestre": "Semestre",
        "Responsable de l’UE": "Responsable",
        "Volume horaire total": "Volume",
        "UE pré-requise": "Pre_requis",
        "Parcours d’études comprenant l’UE": "Parcours",
        "Pondération pour chaque matière": "Evaluation",
        "Obtention de l’UE": "Obtention",
        "Objectifs": "Objectifs",
        "Contenu": "Contenu",
        "Méthodes d’enseignement": "Methodes",
        "Langue d’enseignement": "Langue",
        "Bibliographie": "Bibliographie"
    }

    for champ_pdf, champ_clef in champs.items():
        pattern = rf"{champ_pdf}\s*:?[\n ]*(.*?)(?=\n[A-Z]|$)"
        match = re.search(pattern, bloc, re.DOTALL)
        if match:
            ue[champ_clef] = match.group(1).strip()

    return ue


def parse_bloc_licence(bloc):
    ue = {}
    code_match = re.search(r"^(X\d{2}[A-Z]\d{3})", bloc)
    title_match = re.search(r"^X\d{2}[A-Z]\d{3}\s+(.*)", bloc)
    if code_match:
        ue['Code'] = code_match.group(1)
    if title_match:
        ue['Titre'] = title_match.group(1).strip()

    champs = {
        "Lieu d’enseignement": "Lieu",
        "Niveau": "Niveau",
        "Semestre": "Semestre",
        "Responsable de l’UE": "Responsable",
        "Volume horaire total": "Volume",
        "UE pré-requise": "Pre_requis",
        "Parcours d’études comprenant l’UE": "Parcours",
        "Pondération pour chaque matière": "Evaluation",
        "Obtention de l’UE": "Obtention",
        "Objectifs": "Objectifs",
        "Contenu": "Contenu",
        "Méthodes d’enseignement": "Methodes",
        "Langue d’enseignement": "Langue",
        "Bibliographie": "Bibliographie"
    }

    for champ_pdf, champ_clef in champs.items():
        pattern = rf"{champ_pdf}\s*:?[\n ]*(.*?)(?=\n[A-Z]|$)"
        match = re.search(pattern, bloc, re.DOTALL)
        if match:
            ue[champ_clef] = match.group(1).strip()
    return ue

def main(pdf_path, output_csv):
    blocs = extract_text_blocks(pdf_path)
    ues = [parse_bloc(bloc) for bloc in blocs if bloc.strip()]
    df = pd.DataFrame(ues)
    df.to_csv(output_csv, index=False)
    print(f"Extraction terminée. {len(ues)} UE trouvées.")
    print(f"Extraction terminée. Fichier enregistré : {output_csv}")
    export_to_rdf(ues, output_csv.replace('.csv', '.ttl'))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_ues.py chemin_du_pdf chemin_sortie_csv")
    else:
        main(sys.argv[1], sys.argv[2])
