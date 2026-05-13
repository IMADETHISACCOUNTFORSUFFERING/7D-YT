# 7D-YT
7D is a youtube downloader, however it can also download videos from other social medias such as Dailymotion, Instagram, Twitter, etc...


i think this does not work so, maybe try a better tool like stacher7?
## Download
steps
1. go to the [Releases](https://github.com/IMADETHISACCOUNTFORSUFFERING/7D-YT/releases/tag/v1) page
2. download the `SevenDownloaderSetupyaay.exe`
3. run the installer and follow the prompts i guess
 note: The installer will automatically attempt to set up ffmpeg on your system to enable MP3 conversion, This may briefly open a command prompt window
also if ffmpeg for whatever reason fails to be installed and it keeps failing, just download it yourself [here](https://ffmpeg.org/download.html) should be easy

   ## On linux
   
   ```
   git clone https://github.com/IMADETHISACCOUNTFORSUFFERING/7D-YT.git
   ```
then
 ```
cd 7D-YT
 ```
then
 ```
pip install yt-dlp
 ```
then (figure out how to install it on ur distro.)
 ```
#arch
sudo pacman -S ffmpeg
#debian
sudo apt install ffmpeg
#fedora
sudo dnf install ffmpeg
#snap / any distro
sudo snap install ffmpeg
 ```
verify install by running
 ```
ffmpeg -version

 ```

run the thing
 ```
python 7D-YT.py
 ```
or again, figure out how to run it 

ill update this soon and make it easier

AGAIN note: The installer will automatically attempt to set up ffmpeg on your system to enable MP3 conversion, This may briefly open a command prompt window
also if ffmpeg for whatever reason fails to be installed and it keeps failing, just download it yourself [here](https://ffmpeg.org/download.html) should be easy
