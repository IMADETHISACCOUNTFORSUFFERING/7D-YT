
# 7D-YT
7D-YT has YT on its name,, however it Supports videos from other social medias such as Dailymotion, Instagram, Twitter, etc...
It is essentially a Universal video Downloader since it uses yt-dlp as well as ffmpeg for downloading Audio files and other formats!

## Features

- Easy to use interface
- Resolution Control: Select your preferred resolution
- Visual Progress: A clear download progress bar and completion indicator
- Automatic Setup: The installer attempts to configure ffmpeg for you automatically.
- You can download The thumbnail!

## Installation (Windows)
 1. Navigate to the [Releases](https://github.com/uminaoshii/7D-YT/releases/tag/v1) page

 2. Download `SevenDownloaderSetupyaay.exe`

 3. Run the installer and follow the prompts.

- Note: During installation, a command prompt may briefly open while the installer sets up ffmpeg. If this automatic setup fails, you will need to install ffmpeg manually [here](https://ffmpeg.org/download.html).
  
![Divider](hr.png)

## Linux (Manual Build)

If you wish to run the application from source on Linux, follow these steps:

1. Clone the repo
```
git clone https://github.com/uminaoshii/7D-YT.git
cd 7D-YT

 ```
 2. Install dependencies
 ```
pip install yt-dlp
 ```
3. Install ffmpeg in your distro
- Arch Linux or Arch based Distros
 ```
 sudo pacman -S ffmpeg
  ```
  - Debian/Ubuntu
 ```
 sudo apt install ffmpeg
  ```

- Fedora
 ```
 sudo dnf install ffmpeg
  ```

4. verify install by running
 ```
ffmpeg -version

 ```

5. run the Application
 ```
python 7D-YT.py
 ```
 ---
## Troubleshooting

- FFmpeg missing: If the app fails to convert to MP3, verify that `ffmpeg -version` works in your terminal.
- Beta Status: This project is currently a functional test. If you encounter bugs, please open an issue!

---

## ejhghogshofgnlajhgo;h;skfjg; 
