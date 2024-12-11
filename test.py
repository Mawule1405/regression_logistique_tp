import json

def read_json_file(file_path):
    """
    Lit un fichier JSON et récupère les informations de la matrice de confusion,
    du rapport de classification et de la précision globale.

    :param file_path: Chemin du fichier JSON
    :return: Dictionnaire contenant les informations récupérées
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Récupérer les informations
    confusion_matrix = data.get("confusion_matrix", [])
    classification_report = data.get("classification_report", {})
    accuracy = data.get("accuracy", None)

    return {
        "confusion_matrix": confusion_matrix,
        "classification_report": classification_report,
        "accuracy": accuracy
    }

# Exemple d'utilisation
file_path = "result/training_results.json"  # Remplacez par le chemin de votre fichier JSON
results = read_json_file(file_path)

# Afficher les résultats
print("Matrice de confusion:")
for row in results["confusion_matrix"]:
    print(row)

print("\nRapport de classification:")
for key, value in results["classification_report"].items():
    if isinstance(value, dict):
        print(f"Classe {key}:")
        for metric, score in value.items():
            print(f"  {metric}: {score}")
    else:
        print(f"{key}: {value}")

print(f"\nPrécision globale: {results['accuracy']}")
