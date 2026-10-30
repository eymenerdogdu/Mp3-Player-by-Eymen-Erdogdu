# Advanced MP3 Player

A modern, feature-rich desktop MP3 player built with Python, Tkinter, and the VLC media player engine. It features dynamic theme switching, metadata extraction, custom card-based playlists, and a sleek user interface designed for music enthusiasts.

## Features

* **Robust Audio Engine:** Powered by VLC (`python-vlc`) for smooth playback and precise time handling.
* **Rich Metadata Extraction:** Automatically parses ID3 tags (`mutagen`) to retrieve Song Titles, Artists, Albums, and high-resolution Album Art.
* **Modern Card-Based Playlist:** Replaces standard listboxes with custom two-line UI cards displaying thumbnails, titles, artists, and albums.
* **Dynamic Themes:** Switch instantly between multiple built-in color schemes:
* *Wine Ember* (Custom burgundy & amber tones)
* *Legacy* (Your original vibrant multi-colored button layout)
* *Dark (OLED)* (Sleek minimalist dark mode)
* *Light* (Clean bright interface)


* **Customizable Playlist Sizes:** Adjust playlist item dimensions and thumbnail scales via the **View > Playlist Size** menu (*Large*, *Normal*, *Small*, *Compact*).
* **Advanced Navigation & Controls:**
* Single-track looping (`🔁`)
* Precise relative seeking (`-20s`, `-10s`, `+10s`, `+20s`)
* Full keyboard shortcuts (Spotify-inspired)



## Keyboard Shortcuts

| Action | Shortcut |
| --- | --- |
| **Open Folder** | `Ctrl + O` |
| **Play / Pause** | `Space` |
| **Stop** | `Ctrl + S` |
| **Next Song** | `Ctrl + Right Arrow` |
| **Previous Song** | `Ctrl + Left Arrow` |
| **Fast Forward (+10s)** | `Right Arrow` |
| **Rewind (-10s)** | `Left Arrow` |
| **Fast Forward (+20s)** | `Shift + Right Arrow` |
| **Rewind (-20s)** | `Shift + Left Arrow` |
| **Toggle Loop** | `Ctrl + R` |
| **Quit** | `Ctrl + Q` |

## Requirements

Ensure you have Python installed along with the following packages:

pip install python-vlc mutagen pillow

*(Note: VLC Media Player must also be installed on your system for the audio backend to function properly).*

## Author

**Eymen ERDOĞDU**

* GitHub: [github.com/eymenerdogdu](https://github.com/eymenerdogdu)

## License

This project is licensed under the terms of the **MIT License**.
