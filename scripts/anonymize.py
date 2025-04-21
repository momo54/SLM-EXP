import argparse
from rdflib import Graph, Namespace

def filter_kg(input_file, output_file):
    # Définir le namespace correspondant à @prefix ns1: <http://example.org/course/>
    NS1 = Namespace("http://example.org/course/")

    # Charger le Knowledge Graph original
    g = Graph()
    g.parse(input_file, format="ttl")  # Adapter le format selon ton fichier

    # Créer un nouveau graphe sans les relations ns1:responsible
    filtered_g = Graph()
    for s, p, o in g:
        if p != NS1.responsible:
            filtered_g.add((s, p, o))

    # Sauvegarder le nouveau Knowledge Graph
    filtered_g.serialize(destination=output_file, format="ttl")  
    print(f"Nouveau Knowledge Graph sauvegardé dans {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filtrer un Knowledge Graph en supprimant la relation ns1:responsible")
    parser.add_argument("input", help="Fichier RDF d'entrée")
    parser.add_argument("output", help="Fichier RDF de sortie")
    
    args = parser.parse_args()
    
    filter_kg(args.input, args.output)
