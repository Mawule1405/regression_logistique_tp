import customtkinter as ctk
import joblib  # Pour charger le modèle pré-sauvegardé
from Training import Training
from tkinter import messagebox

def predict(frame_c: ctk.CTkFrame, screen_width,screen_height ):
    # Supprimer les widgets existants dans le frame
    for widget in frame_c.winfo_children():
        widget.destroy()

    
    ctk.CTkLabel(frame_c, text="Test de vulnérabilité d'un système informatique",
                 font=("Times", 16, "bold")).place(x=5, y=10)
    frame = ctk.CTkFrame(frame_c, width=frame_c.winfo_width() - 20, height=500, fg_color="#fff", bg_color="#fff")
    frame.place(x=10, y=50)

    # Ajouter des labels et des combobox
    label1 = ctk.CTkLabel(frame, text="Version du système d'exploitation")
    label1.place(x=10, y=10)
    combo1 = ctk.CTkComboBox(frame, values=["obsolète", "récente"], width=300)
    combo1.place(x=350, y=10)

    label2 = ctk.CTkLabel(frame, text="Nombre de ports ouverts")
    label2.place(x=10, y=40)
    entry2 = ctk.CTkEntry(frame, placeholder_text="0", width=300)
    entry2.place(x=350, y=40)

    label3 = ctk.CTkLabel(frame, text="Fréquence des mises à jour logicielles")
    label3.place(x=10, y=70)
    combo3 = ctk.CTkComboBox(frame, values=["régulière", "irrégulière"], width=300)
    combo3.place(x=350, y=70)

    label4 = ctk.CTkLabel(frame, text="Type d'antivirus utilisé")
    label4.place(x=10, y=100)
    combo4 = ctk.CTkComboBox(frame, values=["robuste", "basique"], width=300)
    combo4.place(x=350, y=100)

    label5 = ctk.CTkLabel(frame, text="Présence de pare-feu actif")
    label5.place(x=10, y=130)
    combo5 = ctk.CTkComboBox(frame, values=["oui", "non"], width=300)
    combo5.place(x=350, y=130)

    label6 = ctk.CTkLabel(frame, text="Nombre d'utilisateurs ayant des privilèges administratifs")
    label6.place(x=10, y=160)
    entry6 = ctk.CTkEntry(frame, placeholder_text="0", width=300)
    entry6.place(x=350, y=160)

    label7 = ctk.CTkLabel(frame, text="Historique des attaques précédentes")
    label7.place(x=10, y=190)
    combo7 = ctk.CTkComboBox(frame, values=["aucune", "faible", "élevée"], width=300)
    combo7.place(x=350, y=190)

    # Ajouter des labels et des champs de saisie
    label8 = ctk.CTkLabel(frame, text="Complexité des mots de passe")
    label8.place(x=10, y=230)
    combo8 = ctk.CTkComboBox(frame, values=["faible", "élevée"], width=300)
    combo8.place(x=350, y=230)

    entry_label9 = ctk.CTkLabel(frame, text="Nombre de vulnérabilités connues non corrigées")
    entry_label9.place(x=10, y=260)
    entry9 = ctk.CTkEntry(frame, placeholder_text="0", width=300)
    entry9.place(x=350, y=260)
    
    result_label = ctk.CTkLabel(frame, text="" , font=("Times", 40 , "bold"))
    result_label.place(x=10, y=320)

    def execute_prediction():
        # Récupérer les valeurs des champs
        try:
            version_os = combo1.get()
            
            frequence_mises_a_jour = combo3.get()
            type_antivirus = combo4.get()
            pare_feu_actif = combo5.get()
            
            historique_attaques = combo7.get()
            complexite_mdp = combo8.get()
            
            
            if entry2.get() and entry6.get() and entry9.get() :
                ports_ouverts = int(entry2.get())  # Convertir en entier
                utilisateurs_admin = int(entry6.get())  # Convertir en entier
                vuln_non_corrigees = int(entry9.get())  # Convertir en entier
                
            else :
                messagebox.showwarning("Valeurs maquantes", "Tous les champs sont obligatoires")
                return
            # Mappage des valeurs catégoriques en numériques
            mappings = {
                "obsolète": 0, "récente": 1,
                "régulière": 1, "irrégulière": 0,
                "robuste": 1, "basique": 0,
                "oui": 1, "non": 0,
                "aucune": 0, "faible": 1, "élevée": 2,
                "faible": 0, "élevée": 1
            }

            # Appliquer les mappages
            input_data = {
                "VSO": mappings.get(version_os, -1),
                "NPO": ports_ouverts,
                "FMU": mappings.get(frequence_mises_a_jour, -1),
                "TAU": mappings.get(type_antivirus, -1),
                "PFA": mappings.get(pare_feu_actif, -1),
                "NUA": utilisateurs_admin,
                "HAP": mappings.get(historique_attaques, -1),
                "CMP": mappings.get(complexite_mdp, -1),
                "NVK": vuln_non_corrigees
            }

            if -1 in input_data.values():
                messagebox.showerror("Certaines données sont incorrectes!")
                return

            # Charger le modèle pré-sauvegardé
            model = joblib.load('result/logistic_regression_model.pkl')

            # Charger le préprocesseur pré-sauvegardé
            preprocessor = joblib.load('result/preprocessor.pkl')

            # Créer une instance de la classe Training avec le modèle et le préprocesseur chargés
            trainer = Training(file_path=None, target_column=None)
            trainer.model = model
            trainer.preprocessor = preprocessor

            # Faire la prédiction
            prediction = trainer.prediction(input_data)

            # Afficher le résultat de la prédiction
            result_label.configure(text = f"{"Vulnérable " if prediction[0] == 0 else "Non vulnérable"}".upper())
        
            
        except ValueError as e:
            messagebox.showerror("Erreur lors de la prédiction", str(e))
            

    bouton = ctk.CTkButton(frame, text="Exécuter", fg_color="#000", width=300, command=execute_prediction)
    bouton.place(x=10, y=290)
