
import tkinter as tk
from settings_page import SafariSettingsApp
from new_game import NewAdventureWindow
from load_game import LoadGameWindow
import pygame
import os

ASSET_DIR = "assets"

pygame.mixer.init()

bg_music = os.path.join(ASSET_DIR, "song.wav")
roar_sound = os.path.join(ASSET_DIR, "lion-roaring.mp3")

pygame.mixer.music.load(bg_music)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

roar = pygame.mixer.Sound(roar_sound)
roar.set_volume(0.5)
roar.play()

def open_settings():
    main_root.withdraw()
    settings_window = tk.Toplevel()
    SafariSettingsApp(settings_window, main_root, pygame.mixer.music, roar)

def open_new_game():
    main_root.withdraw()
    new_game_window = tk.Toplevel()
    NewAdventureWindow(new_game_window, main_root)
    new_game_window.protocol(
        "WM_DELETE_WINDOW",
        lambda: (new_game_window.destroy(), main_root.deiconify())
    )

def open_load_game():
    main_root.withdraw()
    load_window = tk.Toplevel()
    LoadGameWindow(load_window, main_root)

def exit_game():
    main_root.quit()

main_root = tk.Tk()
main_root.geometry("1024x600")
main_root.configure(bg="#88c999")

bg_image = tk.PhotoImage(file=os.path.join(ASSET_DIR, "main_menu_image.png"))
bg_label = tk.Label(main_root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

button_frame = tk.Frame(main_root, pady=20)
button_frame.place(relx=0.5, rely=0.7, anchor="center")

def make_button(text, cmd):
    return tk.Button(
        button_frame, text=text, width=18, height=2,
        font=("Helvetica", 10, "bold"),
        bg="#c58b39", activebackground="#a4692f",
        command=cmd
    )

make_button("NEW GAME", open_new_game).grid(row=0, column=0, padx=10)
make_button("LOAD GAME", open_load_game).grid(row=0, column=1, padx=10)
make_button("SETTINGS", open_settings).grid(row=0, column=2, padx=10)
make_button("EXIT",   exit_game).grid(row=0, column=3, padx=10)

main_root.protocol("WM_DELETE_WINDOW", main_root.quit)
main_root.mainloop()
