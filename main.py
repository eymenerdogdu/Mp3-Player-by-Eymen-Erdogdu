import pygame
import tkinter as tk
from tkinter import filedialog
import os

# Pygame mixer'ı başlat
pygame.mixer.init()

playing = True  # Müzik oynuyor mu kontrol değişkeni
current_time = 0  # Şu anki zaman
total_time = 0  # Toplam şarkı süresi
song_list = []  # Şarkı listesi
current_song = None  # Şu an çalan şarkı
current_index = 0  # Şu anki şarkının indexi
folder_path = ""  # Klasör yolu

def open_folder():
    global song_list, folder_path
    folder_path = filedialog.askdirectory()  # Klasör seçimi
    if folder_path:
        # Klasördeki tüm mp3 dosyalarını listele
        song_list = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
        listbox.delete(0, tk.END)  # Listbox'ı temizle
        for song in song_list:
            listbox.insert(tk.END, song)  # Listeye şarkıları ekle

        if song_list:
            # İlk şarkıyı seçip çalmaya başla
            play_selected_song(0)

def play_selected_song(index):
    global current_song, total_time, current_time, current_index
    selected_song = song_list[index]  # Seçilen şarkıyı al
    file_path = os.path.join(folder_path, selected_song)
    
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    current_song = selected_song
    total_time = pygame.mixer.Sound(file_path).get_length()
    current_time = 0  # Şarkı başladığında zamanı sıfırlıyoruz
    current_index = index  # Mevcut şarkının indexini güncelle
    song_label.config(text=current_song)  # Şarkı adını göster
    update_time_display()
    listbox.select_clear(0, tk.END)  # Önceki seçili öğeyi temizle
    listbox.selection_set(current_index)  # Yeni şarkıyı seçili yap
    btn_play_pause.config(text="Duraklat")

def update_time_display():
    global current_time
    if playing and current_song:
        # Şu anki zaman (saniye cinsinden)
        current_time_ms = pygame.mixer.music.get_pos()  # müzik pozisyonu
        current_time_sec = current_time + (current_time_ms / 1000.0)  # Milisaniyeyi saniyeye çevir
        
        # Zamanı dakika ve saniye formatına dönüştür
        current_min = int(current_time_sec) // 60
        current_sec = int(current_time_sec) % 60
        total_min = int(total_time) // 60
        total_sec = int(total_time) % 60
        
        # Zamanı etiket üzerinde göster
        time_display.config(text=f"{current_min}:{current_sec:02}/{total_min}:{total_sec:02}")
        
        # Her 1000 milisaniyede bir güncelleme yap
        root.after(1000, update_time_display)

def toggle_play_pause():
    global playing
    if playing:
        pygame.mixer.music.pause()
        btn_play_pause.config(text="Oynat")
    else:
        pygame.mixer.music.unpause()
        btn_play_pause.config(text="Duraklat")
    playing = not playing

def stop_music():
    pygame.mixer.music.stop()
    global playing
    playing = False
    btn_play_pause.config(text="Oynat")
    song_label.config(text="")
    time_display.config(text="0:00/0:00")  # Zamanı sıfırla
    global current_time
    current_time = 0  # Zamanı sıfırlıyoruz

def seek_forward():
    global current_time
    # 10 saniye ileri git
    new_time = current_time + 10
    if new_time < total_time:
        current_time = new_time
        pygame.mixer.music.set_pos(current_time)
    else:
        current_time = total_time  # Eğer şarkının sonuna geldiyssek, sonuna git
        pygame.mixer.music.set_pos(current_time)
    update_time_display()

def seek_backward():
    global current_time
    # 10 saniye geri git
    new_time = current_time - 10
    if new_time < 0:
        current_time = 0  # Şarkının başına git
        pygame.mixer.music.set_pos(current_time)
    else:
        current_time = new_time
        pygame.mixer.music.set_pos(current_time)
    update_time_display()

def next_song():
    global current_index
    if current_index < len(song_list) - 1:
        current_index += 1  # Bir sonraki şarkıya geç
    else:
        current_index = 0  # Eğer son şarkıyı çaldıysak, başa dön
    play_selected_song(current_index)

def previous_song():
    global current_index
    if current_index > 0:
        current_index -= 1  # Bir önceki şarkıya git
    else:
        current_index = len(song_list) - 1  # Eğer ilk şarkıya geldiysek, sona dön
    play_selected_song(current_index)

def on_song_select(event):
    selected_index = listbox.curselection()
    if selected_index:
        play_selected_song(selected_index[0])

# Tkinter pencere oluşturma
root = tk.Tk()
root.title("MP3 Player by Eymen ERDOĞDU")
root.geometry("350x500")
root.configure(bg="#2c3e50")

# Şarkı ismi etiketi
song_label = tk.Label(root, text="", wraplength=280, font=("Arial", 12, "bold"), fg="white", bg="#2c3e50")
song_label.pack(pady=10)

# Zaman etiketi (süreyi gösterecek alan)
time_frame = tk.Frame(root, bg="#34495e", bd=2, relief="solid")
time_frame.pack(pady=10, padx=20, fill="x")

time_display = tk.Label(time_frame, text="0:00/0:00", font=("Arial", 12), fg="white", bg="#34495e")
time_display.pack(padx=10, pady=5)

# Şarkı Listesi
listbox_frame = tk.Frame(root, bg="#2c3e50")
listbox_frame.pack(pady=10, padx=20, fill="x")

listbox = tk.Listbox(listbox_frame, font=("Arial", 10), width=40, height=10, bg="#34495e", fg="white", selectmode=tk.SINGLE)
listbox.pack()

# Şarkı seçildiğinde tetiklenecek olay
listbox.bind('<<ListboxSelect>>', on_song_select)

# Buton çerçevesi
button_frame = tk.Frame(root, bg="#2c3e50")
button_frame.pack(pady=10)

# Butonlar
btn_open_folder = tk.Button(button_frame, text="Klasör Aç", command=open_folder, width=10, font=("Arial", 10), bg="#3498db", fg="white", relief="ridge")
btn_open_folder.grid(row=0, column=0, padx=5)

btn_play_pause = tk.Button(button_frame, text="Oynat", command=toggle_play_pause, width=10, font=("Arial", 10), bg="#2ecc71", fg="white", relief="ridge")
btn_play_pause.grid(row=0, column=1, padx=5)

btn_stop = tk.Button(button_frame, text="Durdur", command=stop_music, width=10, font=("Arial", 10), bg="#e74c3c", fg="white", relief="ridge")
btn_stop.grid(row=0, column=2, padx=5)

# Zaman atlama butonları (geri ve ileri 10 saniye)
seek_frame = tk.Frame(root, bg="#2c3e50")
seek_frame.pack(pady=10)

btn_backward = tk.Button(seek_frame, text="-10sn", command=seek_backward, width=8, font=("Arial", 10), bg="#f39c12", fg="white", relief="ridge")
btn_backward.grid(row=0, column=0, padx=5)

btn_forward = tk.Button(seek_frame, text="+10sn", command=seek_forward, width=8, font=("Arial", 10), bg="#f39c12", fg="white", relief="ridge")
btn_forward.grid(row=0, column=1, padx=5)

# Şarkı geçiş butonları
navigation_frame = tk.Frame(root, bg="#2c3e50")
navigation_frame.pack(pady=10)

btn_previous = tk.Button(navigation_frame, text="Önceki", command=previous_song, width=10, font=("Arial", 10), bg="#9b59b6", fg="white", relief="ridge")
btn_previous.grid(row=0, column=0, padx=5)

btn_next = tk.Button(navigation_frame, text="Sonraki", command=next_song, width=10, font=("Arial", 10), bg="#9b59b6", fg="white", relief="ridge")
btn_next.grid(row=0, column=1, padx=5)

# Tkinter döngüsünü başlat
root.mainloop()
