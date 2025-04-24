
import tkinter as tk
from tkinter import messagebox

class LoadGameWindow:
    def __init__(self, root, main_menu_ref):
        self.root = root
        self.main_menu_ref = main_menu_ref
        self.root.title("Load Safari Game")
        self.root.geometry("1024x600")
        self.root.configure(bg="#b2d8b2")

        self.saved_games = [
            {
                "name": "Serengeti Safari",
                "date": "April 23, 2025 - 3:23 AM",
                "money": "$125,000",
                "rating": "4,567.5",
                "visitors": "110,000"
            },
            {
                "name": "Tiger Paradise",
                "date": "April 21, 2025 - 3:23 AM",
                "money": "$95,000",
                "rating": "4,123.8",
                "visitors": "87,500"
            },
            {
                "name": "Lion Kingdom",
                "date": "April 20, 2025 - 1:00 PM",
                "money": "$78,000",
                "rating": "3,987.2",
                "visitors": "74,200"
            },
            {
                "name": "Lion Kingdom",
                "date": "April 23, 2025 - 1:00 PM",
                "money": "$87,000",
                "rating": "4,387.2",
                "visitors": "74,200"
            }
        ]

        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self.root, bg="#222222", bd=5, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=520, height=400)

        top_bar = tk.Frame(container, bg="#222222")
        top_bar.pack(fill="x", pady=(10, 0), padx=10)
        tk.Label(top_bar,
                 text="Load Saved Game",
                 font=("Helvetica", 22, "bold"),
                 fg="yellow",
                 bg="#222222"
        ).pack(side="left")
        back_btn = tk.Button(top_bar,
                             text="Back",
                             font=("Helvetica", 9, "bold"),
                             width=10,
                             bg="#c58b39",
                             fg="white",
                             activebackground="#a4692f",
                             command=self.back
        )
        back_btn.pack(side="right")

        canvas = tk.Canvas(container, bg="#222222", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#222222")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(5, 10))
        scrollbar.pack(side="right", fill="y", pady=(5, 10))

        for game in self.saved_games:
            self.create_game_entry(scrollable_frame, game)

    def create_game_entry(self, parent, game_data):
        frame = tk.Frame(parent, bg="#333333", bd=2, relief="groove")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame,
                 text=game_data["name"],
                 font=("Helvetica", 13, "bold"),
                 fg="orange",
                 bg="#333333"
        ).pack(anchor="w", padx=10, pady=(5, 0))
        tk.Label(frame,
                 text=f"Saved: {game_data['date']}",
                 fg="white",
                 bg="#333333",
                 font=("Helvetica", 10)
        ).pack(anchor="w", padx=10)
        details = (f"{game_data['money']}    "
                   f"Rating: {game_data['rating']}    "
                   f"Visitors: {game_data['visitors']}")
        tk.Label(frame,
                 text=details,
                 fg="white",
                 bg="#333333",
                 font=("Helvetica", 10)
        ).pack(anchor="w", padx=10)

        btn = tk.Button(frame,
                        text="Load Game",
                        font=("Helvetica", 9, "bold"),
                        bg="#c58b39",
                        fg="white",
                        activebackground="#a4692f",
                        command=lambda g=game_data: self.load_game(g)
        )
        btn.pack(side="right", padx=10, pady=5)

    def load_game(self, game_data):
        messagebox.showinfo("Game Loaded", f"Loaded game: {game_data['name']}")
        self.root.destroy()
        self.main_menu_ref.deiconify()

    def back(self):
        self.root.destroy()
        self.main_menu_ref.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    LoadGameWindow(root, root)
    root.mainloop()
