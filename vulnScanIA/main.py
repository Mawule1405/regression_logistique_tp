import customtkinter as ctk
import entrainment as ent
import prediction as pr
import goout as gt


ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")
windows = ctk.CTk()
windows.title("Régression logistique")

# Obtenir les dimensions de l'écran
screen_width = windows.winfo_screenwidth()
screen_height = windows.winfo_screenheight()

# Définir la taille de la fenêtre en fonction des dimensions de l'écran
windows.geometry(f"{screen_width}x{screen_height}+0+0")

aside = ctk.CTkFrame(windows, width=200,fg_color="#fff", height=screen_height-10)
aside.place(x=5, y=5)

screen = ctk.CTkFrame(windows, width=screen_width-220,fg_color="#fff", bg_color="#fff",border_color="#000", border_width=1 , height=screen_height-20)
screen.place(x=210, y=5)

# Ajouter des boutons à l'aside
train_button = ctk.CTkButton(aside, text="Entraînement",fg_color="#000", width=175, command=lambda: ent.train_model(screen))
train_button.pack(pady=5, padx=5)

predict_button = ctk.CTkButton(aside, text="Prédiction",fg_color="#000", width=175, command=lambda: pr.predict(screen, screen_height, screen_height))
predict_button.pack(pady=5, padx=5)

out_button = ctk.CTkButton(aside, text="Quitter",fg_color="#000", width=175, command=lambda: gt.goout(windows))
out_button.pack(pady=5, padx=5)


ent.train_model(screen)
     
        
        


windows.mainloop()
