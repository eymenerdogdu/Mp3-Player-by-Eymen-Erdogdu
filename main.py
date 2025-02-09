import pygame
import tkinter as tk
from tkinter import filedialog
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageTk
import io

# Created by Eymen ERDOĞDU
# GitHub: github.com/eymenerdogdu/Mp3-Player-by-Eymen-Erdogdu

pygame.mixer.init()

playing = False  
current_time = 0  
total_time = 0  
song_list = []  
current_song = None  
current_index = 0  
folder_path = ""  

root = tk.Tk()
root.title("MP3 Player - Created by Eymen ERDOĞDU")
root.geometry("400x650")
root.configure(bg="#2c3e50")

album_art_label = tk.Label(root, bg="#2c3e50")
album_art_label.pack(pady=10, fill="both", expand=True)

def create_default_image():
    global default_image
    default_image = Image.new("RGB", (200, 200), (50, 50, 50))  
    default_album_art = ImageTk.PhotoImage(default_image)
    album_art_label.config(image=default_album_art)
    album_art_label.image = default_album_art  

def show_album_art(mp3_path):
    try:
        audio = MP3(mp3_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):  
                image_data = tag.data
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((200, 200))  
                album_art_image = ImageTk.PhotoImage(image)
                
                album_art_label.config(image=album_art_image)
                album_art_label.image = album_art_image  
                return
    except Exception:
        pass

    album_art_label.config(image=default_image)
    album_art_label.image = default_image

song_name_textbox = tk.Text(root, height=2, font=("Arial", 12, "bold"), fg="white", bg="#2c3e50", wrap="word")
song_name_textbox.pack(pady=5, padx=10, fill="x")

listbox = tk.Listbox(root, font=("Arial", 10), height=10, bg="#34495e", fg="white", selectmode=tk.SINGLE)
listbox.pack(pady=10, padx=20, fill="both", expand=True)

def on_song_select(event):
    selected_index = listbox.curselection()
    if selected_index:
        play_selected_song(selected_index[0])

listbox.bind('<<ListboxSelect>>', on_song_select)

def play_selected_song(index):
    global current_song, total_time, current_time, current_index, playing
    selected_song = song_list[index]
    file_path = os.path.join(folder_path, selected_song)
    
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    playing = True
    current_song = selected_song
    total_time = pygame.mixer.Sound(file_path).get_length()
    current_time = 0
    current_index = index

    song_name_textbox.delete("1.0", tk.END)
    song_name_textbox.insert(tk.END, current_song)

    show_album_art(file_path)  
    update_time_display()
    listbox.select_clear(0, tk.END)
    listbox.selection_set(current_index)
    btn_play_pause.config(text="⏸️")

def open_folder():
    global song_list, folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        song_list = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
        listbox.delete(0, tk.END)
        for song in song_list:
            listbox.insert(tk.END, song)

        if song_list:
            play_selected_song(0)

time_display = tk.Label(root, text="0:00/0:00", font=("Arial", 12), fg="white", bg="#2c3e50")
time_display.pack(padx=10, pady=5)

def update_time_display():
    global current_time
    if playing and current_song:
        current_time_ms = pygame.mixer.music.get_pos()
        current_time_sec = current_time + (current_time_ms / 1000.0)

        current_min = int(current_time_sec) // 60
        current_sec = int(current_time_sec) % 60
        total_min = int(total_time) // 60
        total_sec = int(total_time) % 60

        time_display.config(text=f"{current_min}:{current_sec:02}/{total_min}:{total_sec:02}")

        root.after(1000, update_time_display)

def toggle_play_pause():
    global playing
    if playing:
        pygame.mixer.music.pause()
        btn_play_pause.config(text="▶️")
    else:
        pygame.mixer.music.unpause()
        btn_play_pause.config(text="⏸️")
    playing = not playing

def stop_music():
    pygame.mixer.music.stop()
    global playing, current_time
    playing = False
    btn_play_pause.config(text="▶️")
    song_name_textbox.delete("1.0", tk.END)
    time_display.config(text="0:00/0:00")
    current_time = 0

def play_next():
    global current_index
    if current_index < len(song_list) - 1:
        play_selected_song(current_index + 1)

def play_previous():
    global current_index
    if current_index > 0:
        play_selected_song(current_index - 1)

def seek_forward(seconds):
    global current_time
    new_time = current_time + seconds
    if new_time >= total_time:
        play_next()  # Eğer süreyi geçerse bir sonraki şarkıya geç
    else:
        pygame.mixer.music.set_pos(new_time)
        current_time = new_time
    update_time_display()

def seek_backward(seconds):
    global current_time
    new_time = max(0, current_time - seconds)
    pygame.mixer.music.set_pos(new_time)
    current_time = new_time
    update_time_display()

button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(pady=10)

btn_open_folder = tk.Button(button_frame, text="📂", command=open_folder, width=4, font=("Arial", 12), bg="#3498db", fg="white", relief="ridge")
btn_open_folder.grid(row=0, column=0, padx=5)

btn_prev = tk.Button(button_frame, text="⏮", command=play_previous, width=4, font=("Arial", 12), bg="#9b59b6", fg="white", relief="ridge")
btn_prev.grid(row=0, column=1, padx=5)

btn_play_pause = tk.Button(button_frame, text="▶️", command=toggle_play_pause, width=4, font=("Arial", 12), bg="#2ecc71", fg="white", relief="ridge")
btn_play_pause.grid(row=0, column=2, padx=5, pady=5)

btn_next = tk.Button(button_frame, text="⏭", command=play_next, width=4, font=("Arial", 12), bg="#9b59b6", fg="white", relief="ridge")
btn_next.grid(row=0, column=3, padx=5)

btn_stop = tk.Button(button_frame, text="⏹", command=stop_music, width=4, font=("Arial", 12), bg="#e74c3c", fg="white", relief="ridge")
btn_stop.grid(row=0, column=4, padx=5)

seek_frame = tk.Frame(root, bg="#2c3e50")
seek_frame.pack(pady=5)
btn_backward_20s = tk.Button(seek_frame, text="⏪ -20s", command=lambda: seek_backward(20), width=8, font=("Arial", 10), bg="#f39c12", fg="white", relief="ridge")
btn_backward_20s.grid(row=0, column=0, padx=5)

btn_backward = tk.Button(seek_frame, text="⏪ -10s", command=lambda: seek_backward(10), width=8, font=("Arial", 10), bg="#f39c12", fg="white", relief="ridge")
btn_backward.grid(row=0, column=1, padx=5)

btn_forward = tk.Button(seek_frame, text="+10s ⏩", command=lambda: seek_forward(10), width=8, font=("Arial", 10), bg="#f39c12", fg="white", relief="ridge")
btn_forward.grid(row=0, column=2, padx=5)

btn_forward_20s = tk.Button(seek_frame, text="+20s ⏩", command=lambda: seek_forward(20), width=8, font=("Arial", 10), bg="#f39c12", fg="white", relief="ridge")
btn_forward_20s.grid(row=0, column=3, padx=5)

# UI'ye imza ekleme
signature_label = tk.Label(root, text="Created by Eymen ERDOĞDU\nGitHub: github.com/eymenerdogdu", 
                           font=("Arial", 8), fg="white", bg="#2c3e50")
signature_label.pack(pady=5)

# Mainloop ile uygulamanın arayüzünü sürekli olarak güncelle
root.mainloop()
