import tkinter as tk
import subprocess
from tkinter import messagebox

class NewAdventureWindow:
    def __init__(self, root, main_menu_ref):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.root.title("New Adventure")
        self.root.geometry("600x400")
        self.root.configure(bg="#b2d8b2")
        self.placeholder = "Enter park name here"
        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self.root, bg="#222222", bd=5, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=250)

        tk.Label(container, text="NEW ADVENTURE", font=("Helvetica", 20, "bold"),
                 fg="yellow", bg="#222222").pack(pady=(10, 5))

        tk.Label(container, text="What is your safari park name?", font=("Helvetica", 13, "bold"),
                 fg="yellow", bg="#222222").pack()

        self.name_entry = tk.Entry(container, font=("Helvetica", 12), justify="center",
                                   bd=2, relief="solid", fg="gray", bg="white")
        self.name_entry.insert(0, self.placeholder)
        self.name_entry.bind("<FocusIn>", self.clear_placeholder)
        self.name_entry.pack(pady=10, ipadx=10, ipady=5)

        button_frame = tk.Frame(container, bg="#222222")
        button_frame.pack(pady=10)

        self.make_button(button_frame, "Back", self.on_back).grid(row=0, column=0, padx=10)
        self.make_button(button_frame, "Continue", self.on_continue).grid(row=0, column=1, padx=10)

    def make_button(self, parent, text, command):
        return tk.Button(parent, text=text, font=("Helvetica", 10, "bold"), width=10,
                         bg="#c58b39", fg="white", activebackground="#a4692f",
                         relief="raised", command=command)

    def clear_placeholder(self, event):
        if self.name_entry.get() == self.placeholder:
            self.name_entry.delete(0, tk.END)
            self.name_entry.config(fg="black")

    def on_back(self):
        self.root.destroy()
        self.main_menu_ref.deiconify()

    def on_continue(self):
        park_name = self.name_entry.get().strip()
        if not park_name or park_name == self.placeholder:
            messagebox.showwarning("Input Required", "Please enter a valid park name.")
            return
        self.root.destroy()
        subprocess.Popen(["python", "main.py"])

