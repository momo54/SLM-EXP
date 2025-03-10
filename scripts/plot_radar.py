import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Données extraites de l'image
data = [
    ["AI", "Artificial Intelligence", 12, 12, 18],
    ["AL", "Algorithmic Foundations", 5, 32, 32],
    ["AR", "Architecture and Organization", 11, 9, 16],
    ["DM", "Data Management", 13, 10, 26],
    ["FPL", "Foundations of Programming Languages", 22, 21, 19],
    ["GIT", "Graphics and Interactive Techniques", 12, 4, 70],
    ["HCI", "Human-Computer Interaction", 6, 8, 16],
    ["MSF", "Mathematical and Statistical Foundations", 5, 55, 145],
    ["NC", "Networking and Communication", 8, 7, 24],
    ["OS", "Operating Systems", 14, 8, 13],
    ["PDC", "Parallel and Distributed Computing", 5, 9, 26],
    ["SDF", "Software Development Fundamentals", 5, 43, None],
    ["SE", "Software Engineering", 9, 6, 21],
    ["SEC", "Security", 7, 6, 35],
    ["SEP", "Society, Ethics, and the Profession", 11, 18, 14],
    ["SF", "Systems Fundamentals", 9, 18, 8],
    ["SPD", "Specialized Platform Development", 8, 4, None]
]

# Création du DataFrame
df = pd.DataFrame(data, columns=["Code", "Knowledge Area", "# Knowledge Units", "CS Core Hours", "KA Core Hours"])

# Filtrer les données pour exclure la ligne "Total"
df_filtered = df.dropna()

# Données pour le radar chart
labels = df_filtered["Knowledge Area"].tolist()
values_cs = df_filtered["CS Core Hours"].tolist()
values_ka = df_filtered["KA Core Hours"].tolist()

# Nombre de variables
num_vars = len(labels)

# Calcul des angles pour chaque axe
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# Fermeture du graphique (bouclage)
values_cs += values_cs[:1]
values_ka += values_ka[:1]
angles += angles[:1]

# Création du radar chart avec deux séries de données
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Tracé pour CS Core Hours
ax.fill(angles, values_cs, color='blue', alpha=0.25, label="CS Core Hours")
ax.plot(angles, values_cs, color='blue', linewidth=2)

# Tracé pour KA Core Hours
ax.fill(angles, values_ka, color='red', alpha=0.25, label="KA Core Hours")
ax.plot(angles, values_ka, color='red', linewidth=2)

# Ajout des labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=10, rotation=45, ha="right")

# Titre et légende
ax.set_title("CS Core Hours vs KA Core Hours per Knowledge Area", fontsize=14)
ax.legend(loc="upper right")

# Affichage
plt.show()
