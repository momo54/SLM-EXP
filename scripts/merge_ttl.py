import os
import click
from rdflib import Graph

def find_ttl_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".ttl"):
                yield os.path.join(root, file)

@click.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Fichier de sortie TTL (optionnel)")
def merge_ttl(directory, output):
    merged_graph = Graph()

    for ttl_file in find_ttl_files(directory):
        print(f"Loading {ttl_file}")
        merged_graph.parse(ttl_file, format="turtle")

    if output:
        merged_graph.serialize(destination=output, format="turtle")
        print(f"\nMerged graph written to: {output}")
    else:
        print(merged_graph.serialize(format="turtle"))

if __name__ == "__main__":
    merge_ttl()
