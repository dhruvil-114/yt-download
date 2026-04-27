import customtkinter as ctk
import yt_dlp
from tkinter import filedialog
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeMaster(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YT MASTER v1.4 - Dynamic Scraper")
        self.geometry("600x580")

        # UI Design
        self.label = ctk.CTkLabel(self, text="YOUTUBE MASTER", font=("Orbitron", 30, "bold"), text_color="#FF0000")
        self.label.pack(pady=20)

        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste YouTube Link...", width=450, height=45)
        self.url_entry.pack(pady=10)

        self.fetch_btn = ctk.CTkButton(self, text="FETCH ALL QUALITIES", command=self.start_fetch, 
                                      fg_color="#333333", hover_color="#444444")
        self.fetch_btn.pack(pady=10)

        # Dynamic Dropdown
        self.quality_var = ctk.StringVar(value="Waiting for link...")
        self.quality_menu = ctk.CTkOptionMenu(self, variable=self.quality_var, values=["Scan a video first"], width=350)
        self.quality_menu.pack(pady=15)
        self.quality_menu.configure(state="disabled")

        # Progress
        self.progress_label = ctk.CTkLabel(self, text="0%", font=("Arial", 14))
        self.progress_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self, width=450)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Status: Idle", text_color="gray")
        self.status_label.pack(pady=10)

        self.download_btn = ctk.CTkButton(self, text="DOWNLOAD SELECTED", command=self.start_download, 
                                         fg_color="#FF0000", text_color="white", font=("Arial", 16, "bold"),
                                         height=50, width=200, state="disabled")
        self.download_btn.pack(pady=20)

        self.formats_map = {} # Quality name -> Format ID map

    def start_fetch(self):
        url = self.url_entry.get().strip()
        if not url: return
        self.status_label.configure(text="🔍 Scanning all available formats...", text_color="yellow")
        self.fetch_btn.configure(state="disabled")
        threading.Thread(target=self.fetch_all_qualities, args=(url,), daemon=True).start()

    def fetch_all_qualities(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                temp_map = {}
                # Sirf Video+Audio combo ya best video formats filter karna
                for f in formats:
                    height = f.get('height')
                    ext = f.get('ext')
                    if height and height not in [item[0] for item in temp_map.values()]:
                        res_name = f"{height}p - .{ext}"
                        # format_id store karna taaki accurate download ho
                        temp_map[res_name] = (height, f['format_id'])

                # MP3 option manually add karna
                res_list = sorted(temp_map.keys(), key=lambda x: int(x.split('p')[0]), reverse=True)
                res_list.append("Audio Only (MP3)")
                
                self.formats_map = temp_map
                self.quality_menu.configure(values=res_list, state="normal")
                self.quality_var.set(res_list[0])
                self.download_btn.configure(state="normal")
                self.status_label.configure(text=f"✅ Done: {info.get('title')[:30]}...", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text="❌ Fetch Error!", text_color="red")
        self.fetch_btn.configure(state="normal")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                self.progress_bar.set(float(p)/100)
                self.progress_label.configure(text=f"{int(float(p))}%")
            except: pass

    def start_download(self):
        path = filedialog.askdirectory()
        if not path: return
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self.download_now, args=(path,), daemon=True).start()

    def download_now(self, path):
        url = self.url_entry.get()
        choice = self.quality_var.get()
        
        ydl_opts = {
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'quiet': True,
        }

        if choice == "Audio Only (MP3)":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            })
        else:
            # Jo format ID fetch ki thi wahi use karna
            f_id = self.formats_map[choice][1]
            ydl_opts.update({'format': f'{f_id}+bestaudio/best'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="✅ Task Complete!", text_color="#00FF00")
        except:
            self.status_label.configure(text="❌ Error during download", text_color="red")
        
        self.download_btn.configure(state="normal")

if __name__ == "__main__":
    YouTubeMaster().mainloop()