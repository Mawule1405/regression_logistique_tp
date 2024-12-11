def goout(windows):
    
    for w in windows.winfo_children():
        w.destroy()

    # Détruire la fenêtre principale
    try:
        windows.destroy()  # Supprime l'écran principal s'il existe
    except Exception as e:
        print("Erreur lors de la destruction de l'écran:", e)

