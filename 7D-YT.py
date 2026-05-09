import customtkinter as ctk
import threading
import subprocess
import json
import os
import sys
import re
import webbrowser
import urllib.request
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk
from PIL import Image

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
# YouTube palette
YT_RED       = "#FF0037"
YT_RED_DARK  = "#8B0035"
YT_RED_HOVER = "#FF315E"
BG_DARK      = "#111111"
BG_CARD      = "#1A1A1A"
BG_CARD2     = "#222222"
BG_INPUT     = "#121212"
TEXT_WHITE   = "#FFFFFF"
TEXT_GREY    = "#968FB4"
TEXT_DARK    = "#66606E"
BORDER       = "#333333"
SUCCESS      = "#6BCE94"
WARNING      = "#FFA263"

# ── Helper: run yt-dlp ────────────────────────────────────────────────────────
def which_ytdlp():
    for name in ("yt-dlp", "yt-dlp.exe"):
        path = subprocess.run(
            ["where" if sys.platform == "win32" else "which", name],
            capture_output=True, text=True
        )
        if path.returncode == 0:
            return name
    return "yt-dlp"


YTDLP = which_ytdlp()


# ══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SevenDownloader - YT")
        self.geometry("820x760")
        self.minsize(720, 680)
        self.configure(fg_color=BG_DARK)
        self.iconbitmap("youtube_logo.ico")

        # State
        self.video_info   = None
        self.formats      = []
        self.dl_thread    = None
        self.fetch_thread = None
        self.save_dir     = str(Path.home() / "Downloads")

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ──
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # Logo / title area
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        try:
            logo_img = ctk.CTkImage(
                light_image=__import__("PIL").Image.open("youtube_logo.png"),
                dark_image=__import__("PIL").Image.open("youtube_logo.png"),
                size=(36, 26)
            )
            ctk.CTkLabel(logo_frame, image=logo_img, text="").pack(side="left", padx=(0, 10))
        except Exception:
            # Red play-button placeholder if logo not found
            play_btn = ctk.CTkLabel(
                logo_frame, text="▶", font=ctk.CTkFont(size=28, weight="bold"),
                text_color=YT_RED
            )
            play_btn.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            logo_frame, text="7D-YT",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_WHITE
        ).pack(side="left")

        # this does not work. i want to kms
        self.mode_btn = ctk.CTkButton(
            header, text="☀  Light", width=90, height=32,
            fg_color=BG_CARD2, hover_color=BORDER,
            border_width=1, border_color=BORDER,
            text_color=TEXT_GREY, corner_radius=8,
            font=ctk.CTkFont(size=12),
            command=self._toggle_mode
        )
        self.mode_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        # ── URL bar ──
        url_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16)
        url_frame.grid(row=1, column=0, padx=20, pady=(16, 8), sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            url_frame, text="Paste YouTube URL",
            font=ctk.CTkFont(size=11), text_color=TEXT_DARK
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(14, 0), sticky="w")

        self.url_var = tk.StringVar()
        self.url_entry = ctk.CTkEntry(
            url_frame, textvariable=self.url_var,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=46, corner_radius=10,
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_WHITE, placeholder_text_color=TEXT_DARK,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=1, column=0, padx=(16, 8), pady=(6, 16), sticky="ew")
        self.url_entry.bind("<Return>", lambda e: self._fetch_info())

        self.fetch_btn = ctk.CTkButton(
            url_frame, text="Fetch Info", width=110, height=46,
            fg_color=BG_CARD2, hover_color="#2A2A2A",
            border_width=1, border_color=BORDER,
            text_color=TEXT_WHITE, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._fetch_info
        )
        self.fetch_btn.grid(row=1, column=1, padx=(0, 8), pady=(6, 16))

        self.preview_btn = ctk.CTkButton(
            url_frame, text="▶  Preview", width=110, height=46,
            fg_color=YT_RED, hover_color=YT_RED_HOVER,
            text_color=TEXT_WHITE, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._preview,
            state="disabled"
        )
        self.preview_btn.grid(row=1, column=2, padx=(0, 16), pady=(6, 16))

        # ── Main content (scrollable) ──
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.grid(row=2, column=0, padx=20, pady=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # ── Video info card ──
        self.info_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=16)
        self.info_card.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        self.info_card.grid_columnconfigure(0, weight=1)

        self.thumb_label = ctk.CTkLabel(
            self.info_card, text="No thumbnail yet",
            font=ctk.CTkFont(size=12), text_color=TEXT_DARK
        )
        self.thumb_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="")

        self.title_label = ctk.CTkLabel(
            self.info_card,
            text="Enter a URL and click Fetch Info to begin",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_WHITE, wraplength=650, justify="left"
        )
        self.title_label.grid(row=1, column=0, padx=20, pady=(0, 4), sticky="w")

        self.meta_label = ctk.CTkLabel(
            self.info_card, text="",
            font=ctk.CTkFont(size=12), text_color=TEXT_GREY, justify="left"
        )
        self.meta_label.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="w")

        # ── Settings card ──
        settings_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=16)
        settings_card.grid(row=1, column=0, pady=(0, 12), sticky="ew")
        settings_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            settings_card, text="Download Settings",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_GREY
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 12), sticky="w")

        # Format
        ctk.CTkLabel(
            settings_card, text="Format",
            font=ctk.CTkFont(size=12), text_color=TEXT_GREY
        ).grid(row=1, column=0, padx=20, pady=(0, 4), sticky="w")

        self.format_var = tk.StringVar(value="MP4 (Video)")
        self.format_seg = ctk.CTkSegmentedButton(
            settings_card,
            values=["MP4 (Video)", "MP3 (Audio)"],
            variable=self.format_var,
            fg_color=BG_CARD2,
            selected_color=YT_RED,
            selected_hover_color=YT_RED_HOVER,
            unselected_color=BG_CARD2,
            unselected_hover_color=BG_INPUT,
            text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=10,
            command=self._on_format_change
        )
        self.format_seg.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="w")

        # Res
        res_col = ctk.CTkFrame(settings_card, fg_color="transparent")
        res_col.grid(row=1, column=1, rowspan=2, padx=20, pady=(0, 16), sticky="nsew")

        ctk.CTkLabel(
            res_col, text="Resolution / Quality",
            font=ctk.CTkFont(size=12), text_color=TEXT_GREY
        ).pack(anchor="w", pady=(0, 4))

        self.res_var = tk.StringVar(value="Best available")
        self.res_menu = ctk.CTkOptionMenu(
            res_col,
            variable=self.res_var,
            values=["Best available"],
            fg_color=BG_CARD2, button_color=BG_INPUT,
            button_hover_color=BORDER,
            text_color=TEXT_WHITE, dropdown_fg_color=BG_CARD2,
            dropdown_hover_color=BG_INPUT, dropdown_text_color=TEXT_WHITE,
            height=40, corner_radius=10,
            font=ctk.CTkFont(size=13),
            width=220
        )
        self.res_menu.pack(anchor="w")

        # ── Save location ──
        dir_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=16)
        dir_card.grid(row=2, column=0, pady=(0, 12), sticky="ew")
        dir_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            dir_card, text="Save To",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_GREY
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 8), sticky="w")

        self.dir_var = tk.StringVar(value=self.save_dir)
        self.dir_entry = ctk.CTkEntry(
            dir_card, textvariable=self.dir_var,
            height=40, corner_radius=10,
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_GREY, font=ctk.CTkFont(size=12)
        )
        self.dir_entry.grid(row=1, column=0, padx=(16, 8), pady=(0, 16), sticky="ew")

        ctk.CTkButton(
            dir_card, text="Browse", width=90, height=40,
            fg_color=BG_CARD2, hover_color=BORDER,
            border_width=1, border_color=BORDER,
            text_color=TEXT_WHITE, corner_radius=10,
            font=ctk.CTkFont(size=12),
            command=self._browse_dir
        ).grid(row=1, column=1, padx=(0, 16), pady=(0, 16))

        # ── Progress card ──
        prog_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=16)
        prog_card.grid(row=3, column=0, pady=(0, 12), sticky="ew")
        prog_card.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(prog_card, fg_color="transparent")
        top_row.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="ew")
        top_row.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            top_row, text="Ready",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_GREY
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.pct_label = ctk.CTkLabel(
            top_row, text="",
            font=ctk.CTkFont(size=12), text_color=TEXT_DARK
        )
        self.pct_label.grid(row=0, column=1, sticky="e")

        self.progress = ctk.CTkProgressBar(
            prog_card, height=8, corner_radius=4,
            fg_color=BG_INPUT, progress_color=YT_RED
        )
        self.progress.set(0)
        self.progress.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="ew")

        self.speed_label = ctk.CTkLabel(
            prog_card, text="",
            font=ctk.CTkFont(size=11), text_color=TEXT_DARK
        )
        self.speed_label.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="w")

        # ── Download button ──
        self.dl_btn = ctk.CTkButton(
            scroll, text="⬇  Download",
            height=54, corner_radius=14,
            fg_color=YT_RED, hover_color=YT_RED_HOVER,
            text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_download,
            state="disabled"
        )
        self.dl_btn.grid(row=4, column=0, pady=(4, 24), sticky="ew")

        # ── Logss ──
        log_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=16)
        log_card.grid(row=5, column=0, pady=(0, 8), sticky="ew")
        log_card.grid_columnconfigure(0, weight=1)

        log_hdr = ctk.CTkFrame(log_card, fg_color="transparent")
        log_hdr.grid(row=0, column=0, padx=20, pady=(12, 0), sticky="ew")
        log_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_hdr, text="Log",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_GREY
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            log_hdr, text="Clear", width=60, height=24,
            fg_color="transparent", hover_color=BG_CARD2,
            text_color=TEXT_DARK, corner_radius=6,
            font=ctk.CTkFont(size=11),
            command=self._clear_log
        ).grid(row=0, column=1, sticky="e")

        self.log_box = ctk.CTkTextbox(
            log_card, height=120, corner_radius=10,
            fg_color=BG_INPUT, text_color=TEXT_GREY,
            font=ctk.CTkFont(family="Consolas", size=11),
            border_width=0
        )
        self.log_box.grid(row=1, column=0, padx=16, pady=(8, 16), sticky="ew")
        self.log_box.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────
    def _toggle_mode(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.mode_btn.configure(text="🌙  Dark")
        else:
            ctk.set_appearance_mode("dark")
            self.mode_btn.configure(text="☀  Light")

    def _browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.save_dir)
        if path:
            self.save_dir = path
            self.dir_var.set(path)

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _log(self, msg, color=None):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, color=TEXT_GREY):
        self.status_label.configure(text=text, text_color=color)

    def _preview(self):
        url = self.url_var.get().strip()
        if url:
            webbrowser.open(url)

    def _on_format_change(self, value):
        if value == "MP3 (Audio)":
            self.res_menu.configure(values=["Best (320kbps)", "128kbps", "192kbps", "256kbps"])
            self.res_var.set("Best (320kbps)")
        else:
            self._populate_resolutions()

    def _populate_resolutions(self):
        if not self.formats:
            self.res_menu.configure(values=["Best available"])
            self.res_var.set("Best available")
            return
        # Collect unique heights from video+audio formats
        heights = sorted(
            {f["height"] for f in self.formats if f.get("height") and f.get("vcodec", "none") != "none"},
            reverse=True
        )
        labels = [f"{h}p" for h in heights] if heights else []
        labels = ["Best available"] + labels
        self.res_menu.configure(values=labels)
        self.res_var.set(labels[0])

    # ── Fetch vid info ──────────────────────────────────────────────────────
    def _fetch_info(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please paste a YouTube URL first.")
            return
        if self.fetch_thread and self.fetch_thread.is_alive():
            return
        self.fetch_btn.configure(state="disabled", text="Fetching…")
        self.preview_btn.configure(state="disabled")
        self.dl_btn.configure(state="disabled")
        self._set_status("Fetching video info…", WARNING)
        self.progress.set(0)
        self.pct_label.configure(text="")
        self.speed_label.configure(text="")
        self.fetch_thread = threading.Thread(target=self._fetch_worker, args=(url,), daemon=True)
        self.fetch_thread.start()

    def _fetch_worker(self, url):
        try:
            result = subprocess.run(
                [YTDLP, "--dump-json", "--no-playlist", url],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                self.after(0, self._fetch_error, result.stderr)
                return
            info = json.loads(result.stdout)
            self.after(0, self._fetch_done, info)
        except Exception as e:
            self.after(0, self._fetch_error, str(e))

    def _fetch_error(self, msg):
        self._set_status("Error fetching info", YT_RED)
        self._log(f"[ERROR] {msg}")
        self.fetch_btn.configure(state="normal", text="Fetch Info")

    def _fetch_done(self, info):
        self.video_info = info
        self.formats = info.get("formats", [])

        title    = info.get("title", "Unknown")
        channel  = info.get("uploader", "")
        duration = info.get("duration", 0)
        views    = info.get("view_count", 0)
        mins, secs = divmod(int(duration), 60)
        hrs, mins  = divmod(mins, 60)
        dur_str = f"{hrs}:{mins:02d}:{secs:02d}" if hrs else f"{mins}:{secs:02d}"
        views_str = f"{views:,}" if views else "N/A"

        # reset thumbnail
        self.thumb_label.configure(image="", text="Loading thumbnail…")

        # Pick thumbnail URL
        thumb_url = None
        thumbnails = info.get("thumbnails")
        if thumbnails:
            # prefer the largest one
            for t in reversed(thumbnails):
                u = t.get("url", "")
                if u.startswith("http"):
                    thumb_url = u
                    break
        if not thumb_url:
            thumb_url = info.get("thumbnail", "")

        if thumb_url:
            threading.Thread(target=self._load_thumbnail, args=(thumb_url,), daemon=True).start()
        else:
            self.thumb_label.configure(text="No thumbnail available")

        self.title_label.configure(text=title[:90] + ("…" if len(title) > 90 else ""))
        self.meta_label.configure(
            text=f"📺  {channel}    ⏱  {dur_str}    👁  {views_str} views"
        )

        self._populate_resolutions()
        self.fetch_btn.configure(state="normal", text="Fetch Info")
        self.preview_btn.configure(state="normal")
        self.dl_btn.configure(state="normal")
        self._set_status(f"Ready — {title[:50]}", SUCCESS)
        self._log(f"[INFO] Fetched: {title}")

    def _load_thumbnail(self, url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = BytesIO(resp.read())
            img = Image.open(data).convert("RGB")

            # Resize to 16:9 at 480px wide
            target_w, target_h = 480, 270
            img = img.resize((target_w, target_h), Image.LANCZOS)

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))
            self.after(0, self._show_thumbnail, ctk_img)
        except Exception as e:
            self.after(0, lambda: self.thumb_label.configure(text="Could not load thumbnail", image=""))
            self._log(f"[WARN] Thumbnail error: {e}")

    def _show_thumbnail(self, ctk_img):
        self._thumb_ref = ctk_img          # keep reference so GC doesn't collect it
        self.thumb_label.configure(image=ctk_img, text="")

    # ── Download ──────────────────────────────────────────────────────────────
    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            return
        if self.dl_thread and self.dl_thread.is_alive():
            messagebox.showinfo("In Progress", "A download is already running.")
            return
        self.dl_btn.configure(state="disabled")
        self.progress.set(0)
        self.pct_label.configure(text="0%")
        self.speed_label.configure(text="")
        self._set_status("Starting download…", WARNING)

        fmt   = self.format_var.get()
        res   = self.res_var.get()
        dest  = self.dir_var.get().strip() or self.save_dir

        self.dl_thread = threading.Thread(
            target=self._download_worker,
            args=(url, fmt, res, dest),
            daemon=True
        )
        self.dl_thread.start()

    def _build_ydl_cmd(self, url, fmt, res, dest):
        out_tmpl = os.path.join(dest, "%(title)s.%(ext)s")
        cmd = [YTDLP, "--newline", "-o", out_tmpl, "--no-playlist"]

        if fmt == "MP3 (Audio)":
            kbps = "320" if "Best" in res else res.replace("kbps", "")
            cmd += [
                "-x", "--audio-format", "mp3",
                "--audio-quality", kbps + "k"
            ]
        else:
            if res == "Best available":
                cmd += ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"]
            else:
                height = res.replace("p", "")
                cmd += [
                    "-f",
                    f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]"
                ]
            cmd += ["--merge-output-format", "mp4"]

        cmd.append(url)
        return cmd

    def _download_worker(self, url, fmt, res, dest):
        cmd = self._build_ydl_cmd(url, fmt, res, dest)
        self._log(f"[CMD] {' '.join(cmd)}")

        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            pct_re    = re.compile(r"\[download\]\s+([\d.]+)%")
            speed_re  = re.compile(r"at\s+([\d.]+\s*\w+/s)")
            eta_re    = re.compile(r"ETA\s+([\d:]+)")

            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                self.after(0, self._log, line)

                m_pct = pct_re.search(line)
                if m_pct:
                    pct = float(m_pct.group(1)) / 100
                    pct_str = f"{m_pct.group(1)}%"
                    m_spd = speed_re.search(line)
                    m_eta = eta_re.search(line)
                    speed_str = m_spd.group(1) if m_spd else ""
                    eta_str   = f"ETA {m_eta.group(1)}" if m_eta else ""
                    detail = "  ".join(filter(None, [speed_str, eta_str]))
                    self.after(0, self._update_progress, pct, pct_str, detail)

            proc.wait()
            if proc.returncode == 0:
                self.after(0, self._download_done)
            else:
                self.after(0, self._download_fail, f"yt-dlp exited with code {proc.returncode}")
        except FileNotFoundError:
            self.after(0, self._download_fail,
                       "yt-dlp not found. Install with:  pip install yt-dlp")
        except Exception as e:
            self.after(0, self._download_fail, str(e))

    def _update_progress(self, pct, pct_str, detail):
        self.progress.set(pct)
        self.pct_label.configure(text=pct_str)
        self.speed_label.configure(text=detail)
        self._set_status("Downloading…", WARNING)

    def _download_done(self):
        self.progress.set(1)
        self.pct_label.configure(text="100%")
        self.speed_label.configure(text="")
        self._set_status("✓  Download complete!", SUCCESS)
        self._log("[DONE] Download finished successfully.")
        self.dl_btn.configure(state="normal")
        messagebox.showinfo("Done", "Download complete!\nFile saved to:\n" + self.save_dir)

    def _download_fail(self, msg):
        self._set_status("Download failed", YT_RED)
        self._log(f"[ERROR] {msg}")
        self.dl_btn.configure(state="normal")
        messagebox.showerror("Error", msg)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
