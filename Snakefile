from pathlib import Path

# Dossiers source et sortie
srcdir = Path("./data/master2025").resolve()
outdir = Path("./XP/align/master2025")

# Trouver tous les fichiers .ttl en entrée
ttl_files = list(srcdir.rglob("*.ttl"))

# Construire les cibles de sortie
output_ttl_files = [str(outdir / f"{f.stem}.ttl") for f in ttl_files]
print("Output files:", output_ttl_files)

rule all:
    input:
        output_ttl_files

rule align:
    input:
        ttl = lambda wildcards: next(f for f in ttl_files if f.stem == wildcards.name)
    output:
        ttl = outdir / "{name}.ttl",
        store = outdir / "{name}.nq"
    shell:
        """
        slm-run \
            --config config.bok \
            --load {input.ttl} \
            --format turtle \
            -f queries/bok-graph-construct-cli.sparql \
            -o {output.ttl} \
            --keep-store {output.store}
        """
