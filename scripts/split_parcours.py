#!/usr/bin/env python3

import sys
from rdflib import Graph, Literal, URIRef

def split_parcours(input_file, output_file):
    g = Graph()
    g.parse(input_file, format="turtle")

    new_graph = Graph()

    for s, p, o in g:
        # On cible tous les prédicats qui se terminent par "parcours"
        if isinstance(p, URIRef) and p.endswith("parcours") and isinstance(o, Literal) and ',' in str(o):
            valeurs = [v.strip() for v in str(o).split(',')]
            for val in valeurs:
                new_graph.add((s, p, Literal(val)))
        else:
            new_graph.add((s, p, o))

    new_graph.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_parcours.py input.ttl output.ttl")
        sys.exit(1)
    split_parcours(sys.argv[1], sys.argv[2])
