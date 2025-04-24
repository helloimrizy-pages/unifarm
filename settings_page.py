import tkinter as tk
from tkinter import ttk, messagebox

class SafariSettingsApp:
    def __init__(self, root, main_menu_ref, bg_music, roar):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.bg_music = bg_music
        self.roar = roar

        self.root.title("Safari Park Settings")
        self.root.geometry("1600x900")
        self.root.configure(bg="#b2d8b2")
        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self.root, bg="#333333", bd=3, relief="groove")
        container.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

        tk.Label(container, text="Safari Settings", font=("Helvetica", 22, "bold"), fg="yellow", bg="#333333").pack(pady=15)

        self.music_slider = self.add_slider(container, "Music Volume")
        self.sfx_slider = self.add_slider(container, "SFX Volume")

        button_frame = tk.Frame(container, bg="#333333")
        button_frame.pack(pady=20)

        self.make_button(button_frame, "Apply Changes", self.apply_changes).grid(row=0, column=0, padx=5)
        self.make_button(button_frame, "Back", self.back).grid(row=0, column=1, padx=5)
        self.make_button(button_frame, "Exit Game", self.exit_game).grid(row=1, column=0, columnspan=2, pady=10)


    def add_slider(self, parent, label_text):
        frame = tk.Frame(parent, bg="#333333")
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, font=("Helvetica", 11, "bold"), bg="#333333", fg="white").pack(anchor="w")
        slider = ttk.Scale(frame, from_=0, to=100, orient="horizontal", length=300)
        slider.set(50)
        slider.pack()
        return slider

    def make_button(self, parent, text, command):
        return tk.Button(parent, text=text, font=("Helvetica", 10, "bold"), width=14,
                         bg="#c58b39", fg="white", activebackground="#a4692f", command=command)

    def apply_changes(self):
        music_vol = self.music_slider.get() / 100.0
        sfx_vol = self.sfx_slider.get() / 100.0
        self.bg_music.set_volume(music_vol)
        self.roar.set_volume(sfx_vol)
        self.roar.play()  # play to test sfx
        messagebox.showinfo("Settings", f"Music: {int(music_vol*100)}%, SFX: {int(sfx_vol*100)}%")

    def back(self):
        self.root.destroy()
        self.main_menu_ref.deiconify()

    def exit_game(self):
        self.root.quit()
