import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Training as tr
import json

import constant as ct

def train_model(frame: ctk.CTkFrame):
    # Supprimer les widgets existants dans le frame
    for widget in frame.winfo_children():
        widget.destroy()
        
    

    charging_file_button = ctk.CTkButton(frame, text="Charger le fichier des données",font=ct.FONTN, fg_color="#000", width=300, command=lambda: load_file())
    charging_file_button.place(x=5, y=5)

    start_training_button = ctk.CTkButton(frame, text="Effectuez l'entraînement",font=ct.FONTN,fg_color="#000", width=200, command=lambda: start_training())
    start_training_button.place(x=5, y=35)
    
    previous_training_button = ctk.CTkButton(frame, text="Résultat de l'entrainement précédent",font=ct.FONTN,fg_color="#000", width=200, command=lambda: previous_training_result())
    previous_training_button.place(x=210, y=35)

    # Matrice de confusion avec les champs
    matrix_de_confusion = ctk.CTkFrame(frame, fg_color="#fff", width=200)
    matrix_de_confusion.place(x=5, y=70)

    ctk.CTkLabel(matrix_de_confusion, text="Matrice de confusion", font=ct.FONTN, anchor="w").place(x=5, y=5)
    vn_label = ctk.CTkLabel(matrix_de_confusion, text="0", font=ct.FONTB, anchor="w")
    vn_label.place(x=10, y=30)

    fn_label = ctk.CTkLabel(matrix_de_confusion, text="0", font=ct.FONTB, anchor="w")
    fn_label.place(x=80, y=30)

    fp_label = ctk.CTkLabel(matrix_de_confusion, text="0", font=ct.FONTB, anchor="w")
    fp_label.place(x=10, y=60)

    vp_label = ctk.CTkLabel(matrix_de_confusion, text="0", font=ct.FONTB, anchor="w")
    vp_label.place(x=80, y=60)

    
    rapport_de_classification = ctk.CTkFrame(frame, width = frame.winfo_width()-100, fg_color="#fff", height=frame.winfo_height()-200)
    rapport_de_classification.place(x=210, y=70)

    ctk.CTkLabel(rapport_de_classification, text="Rapport de classification", font=ct.FONTB).place(x=5, y=5)

    # Créer un TreeView pour afficher le rapport de classification
    style = ttk.Style()
    style.configure("Treeview", font=ct.FONTN, rowheight=ct.ROW_HEIGHT) 
    tree = ttk.Treeview(rapport_de_classification,style="Treeview", height=5, columns=("entity", "precision", "recall", "f1-score", "support"), show="headings")
    tree.heading("entity", text="Entité")
    tree.heading("precision", text="Précision")
    tree.heading("recall", text="Rappel")
    tree.heading("f1-score", text="F1-Score")
    tree.heading("support", text="Support")
    
    tree.place(x=5, y=40)

    # Label du path
    file_path_label = ctk.CTkLabel(frame, text="Aucun fichier chargé",font=ct.FONTN, width=600, text_color="#000", anchor="w")
    file_path_label.place(x=315, y=5)

    # Fonction pour charger le fichier Excel
    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            file_path_label.configure(text=file_path)
            return file_path
        return None

    # Fonction pour lancer l'entraînement
    def start_training():
        file_path = file_path_label.cget("text")
        if file_path == "Aucun fichier chargé":
            messagebox.showwarning("Avertissement", "Aucun fichier de données d'entraînement n'a été chargé!")
            return
        else:
            try:
                target_column = 'Pred'
                trainer = tr.Training(file_path, target_column)
                trainer.load_data()
                X_train, X_test, y_train, y_test = trainer.prepare_data()

                if X_train is not None and y_train is not None:
                    trainer.train(X_train, y_train)
                    results = trainer.evaluate(X_test, y_test)
                    trainer.save_model(directory="result", results=results)

                # Afficher les résultats sur l'interface
                results = read_json_file("result/training_results.json")
                display_results(tree, results)
                plot_classification_report(results, rapport_de_classification)
                
                messagebox.showinfo("Fin de l'entraînement", "L'entraînement a été effectué avec succès!")

            except Exception as e:
                messagebox.showerror("Erreur", f"Les données enregistrées dans le fichier chargé sont incompatibles !\n{e}")

    def display_results(tree, results):
        # Supprimer les anciennes données du TreeView
        for item in tree.get_children():
            tree.delete(item)

        # Ajouter les nouvelles données au TreeView
        classification_report = results.get("classification_report", {})
        for key, value in classification_report.items():
            if isinstance(value, dict):
                tree.insert("", "end", values=(f"Classe {key}", round(value["precision"],5), round(value["recall"],5), round(value["f1-score"], 5), round(value["support"], 5)))
            else:
                tree.insert("", "end", values=(key, value, "", "", ""))
                
        matrice = results.get("confusion_matrix")
        vn_label.configure(text=matrice[0][0])
        fn_label.configure(text=matrice[0][1])
        fp_label.configure(text=matrice[1][0])
        vp_label.configure(text=matrice[1][1])
        
        
    
    def plot_classification_report(report, frame : ctk.CTkFrame):
        """
        Crée un graphique du rapport de classification et l'affiche dans un canvas.

        :param report: Rapport de classification sous forme de dictionnaire (output de classification_report)
        :param frame: Frame tkinter pour afficher le graphique
        """
        # Extraire le rapport de classification
        classification_report = report.get("classification_report", {})
        if not classification_report:
            raise ValueError("Le rapport de classification est vide ou invalide.")

        # Récupérer les étiquettes des classes
        labels = list(classification_report.keys())
        for key in ["accuracy", "macro avg", "weighted avg"]:
            if key in labels:
                labels.remove(key)

        # Vérifiez que chaque label contient les clés attendues
        for label in labels:
            if not isinstance(classification_report[label], dict) or "precision" not in classification_report[label]:
                raise ValueError(f"Structure invalide pour le label {label}: {classification_report[label]}")

        # Extraire les scores pour chaque classe
        precision = [classification_report[label]["precision"] for label in labels]
        recall = [classification_report[label]["recall"] for label in labels]
        f1_score = [classification_report[label]["f1-score"] for label in labels]

        # Indices des classes pour l'axe des abscisses
        x = range(len(labels))
        width = 0.25  # Largeur de chaque barre

        # Supprimer les anciennes figures pour éviter les fuites de mémoire
        plt.close("all")

        # Créer une nouvelle figure Matplotlib
        fig, ax = plt.subplots()
        ax.bar([pos - width for pos in x], precision, width=width, label='Précision', align='center')
        ax.bar(x, recall, width=width, label='Rappel', align='center')
        ax.bar([pos + width for pos in x], f1_score, width=width, label='F1-Score', align='center')

        # Ajouter des détails au graphique
        ax.set_xlabel('Classes')
        ax.set_ylabel('Scores')
        ax.set_title('Rapport de classification')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        # Supprimer l'ancien canvas s'il existe déjà
        for widget in frame.winfo_children():
            if isinstance(widget , FigureCanvasTkAgg):
                widget.destroy()

        # Afficher le graphique dans le canvas Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().place(x=5, y=280, width= frame.winfo_width() - 300, height=300)


        
        

        

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

    def previous_training_result():
        results = read_json_file("result/training_results.json")
        display_results(tree, results)
        plot_classification_report(results, rapport_de_classification)
   