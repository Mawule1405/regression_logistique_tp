


import os
import pickle
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


class Training:
    def __init__(self, file_path, target_column):
        """
        Initialisation de la classe Training avec le chemin du fichier Excel et la colonne cible.
        
        :param file_path: Chemin du fichier Excel contenant les données
        :param target_column: Nom de la colonne cible (variable à prédire)
        """
        self.file_path = file_path
        self.target_column = target_column
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", max_categories=10)
        self.data = None



    def load_data(self):
        """
        Charger les données depuis le fichier Excel.
        """
        try:
            self.data = pd.read_excel(self.file_path, sheet_name="Sheet1")
        except FileNotFoundError:
            print(f"Erreur : Le fichier {self.file_path} n'a pas été trouvé.")
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")



    def prepare_data(self):
        """
        Préparer les données en séparant les variables indépendantes et la variable cible.
        """
        if self.data is None:
            print("Les données n'ont pas été chargées correctement.")
            return None, None, None, None

        # Vérifier les valeurs manquantes et les traiter
        self.data = self.data.dropna()  # Vous pouvez aussi utiliser une autre méthode comme fillna()

        X = self.data.drop(columns=[self.target_column])
        y = self.data[self.target_column]

        # Sélectionner les caractéristiques numériques et catégorielles
        numeric_features = X.select_dtypes(include=["int64", "float64"]).columns
        categorical_features = X.select_dtypes(include=["object"]).columns

        # Préparer le préprocesseur
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", self.scaler, numeric_features),
                ("cat", self.encoder, categorical_features)
            ]
        )

        # Séparer les données en train et test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
        
        # Appliquer le préprocesseur
        X_train = preprocessor.fit_transform(X_train)
        X_test = preprocessor.transform(X_test)
        
        self.preprocessor = preprocessor  # Sauvegarder le préprocesseur
        return X_train, X_test, y_train, y_test



    def train(self, X_train, y_train):
        """
        Entraîner le modèle de régression logistique avec les données d'entraînement.
        """
        self.model.fit(X_train, y_train)
        

    def evaluate(self, X_test, y_test):
        """
        Évaluer le modèle avec les données de test.
        """
        y_pred = self.model.predict(X_test)
        results = {
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "accuracy": accuracy_score(y_test, y_pred)
        }
        
        return results



    def save_model(self, directory="result", results=None):
        """
        Sauvegarder le modèle, le scaler, l'encodeur, et les résultats dans le dossier spécifié.
        
        :param directory: Dossier où les fichiers seront sauvegardés
        :param results: Résultats à sauvegarder (optionnel)
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        model_path = os.path.join(directory, "logistic_regression_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)

        preprocessor_path = os.path.join(directory, "preprocessor.pkl")
        with open(preprocessor_path, "wb") as f:
            pickle.dump(self.preprocessor, f)

        if results:
            results_path = os.path.join(directory, "training_results.json")
            with open(results_path, "w") as f:
                json.dump(results, f, indent=4)
        
        print(f"Modèle, préprocesseur et résultats sauvegardés dans {directory}")


    def prediction(self, input_data):
        """
        Prédire les résultats pour de nouvelles données en utilisant le modèle entraîné.
        
        :param input_data: Dictionnaire contenant les nouvelles données
        :return: Prédictions du modèle
        """
        # Vérifier si le préprocesseur a été chargé
        if not hasattr(self, 'preprocessor'):
            raise ValueError("Le préprocesseur n'a pas été chargé. Assurez-vous d'avoir entraîné le modèle ou chargé le préprocesseur.")
        else:
            print("Préprocesseur chargé avec succès.")

        # Vérifier si le modèle a été chargé
        if not hasattr(self, 'model'):
            raise ValueError("Le modèle n'a pas été chargé. Assurez-vous d'avoir entraîné ou chargé le modèle.")
        else:
            print("Modèle chargé avec succès.")

        # Vérifier si input_data est un dictionnaire
        if not isinstance(input_data, dict):
            raise ValueError("Les données d'entrée doivent être un dictionnaire.")
        
        # Convertir les données d'entrée en DataFrame
        try:
            input_df = pd.DataFrame([input_data])
            print(f"input_df créé avec succès:\n{input_df}")
        except Exception as e:
            raise ValueError(f"Erreur lors de la création du DataFrame à partir des données d'entrée: {e}")

        # Obtenir les noms des features après transformation
        numeric_features = self.preprocessor.transformers_[0][2]
        categorical_features = self.preprocessor.transformers_[1][2]
        expected_columns = list(numeric_features) + list(categorical_features)
        print(f"Colonnes attendues par le préprocesseur: {expected_columns}")
        
        # Compléter les colonnes manquantes avec des valeurs par défaut (par exemple, zéro)
        missing_columns = set(expected_columns) - set(input_df.columns)
        for column in missing_columns:
            input_df[column] = 0  # Ajout des colonnes manquantes avec une valeur par défaut (ici 0)
        #print(f"input_df après ajout des colonnes manquantes:\n{input_df}")
        
        # Réorganiser les colonnes pour correspondre à l'ordre attendu
        input_df = input_df[expected_columns]
        #print(f"input_df après réorganisation des colonnes:\n{input_df}")
        
        # Convertir les colonnes en types appropriés
        for col in numeric_features:
            input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
        for col in categorical_features:
            input_df[col] = input_df[col].astype(str)
        
        # Appliquer le préprocesseur aux nouvelles données
        try:
            input_transformed = self.preprocessor.transform(input_df)
            #print(f"Données transformées avec succès:\n{input_transformed}")
        except Exception as e:
            raise ValueError(f"Erreur lors de l'application du préprocesseur: {e}")

        # Vérifier si les données transformées ont la forme correcte
        if input_transformed.shape[1] != self.model.n_features_in_:
            raise ValueError(f"Le nombre de caractéristiques après transformation ({input_transformed.shape[1]}) "
                            f"ne correspond pas au nombre attendu par le modèle ({self.model.n_features_in_}).")
        else:
            print(f"Nombre de caractéristiques après transformation : {input_transformed.shape[1]}")

        # Faire des prédictions
        try:
            predictions = self.model.predict(input_transformed)
            #print(f"Prédictions effectuées : {predictions}")
        except Exception as e:
            raise ValueError(f"Erreur lors de la prédiction: {e}")
        
        return predictions


    