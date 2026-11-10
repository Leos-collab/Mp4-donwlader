import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from downloader import download_video

def format_bytes(size):
    if not size:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixador de Vídeos MP4")
        self.root.geometry("640x440")
        self.root.minsize(580, 400)

        # Configurar tema e estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Cores
        self.bg_color = "#f4f6f9"
        self.primary_color = "#2563eb"
        self.root.configure(bg=self.bg_color)

        self.default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
        os.makedirs(self.default_dir, exist_ok=True)
        self.dest_folder = tk.StringVar(value=self.default_dir)
        self.is_downloading = False

        self._create_widgets()

    def _create_widgets(self):
        # Container principal com padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho / Título
        title_label = ttk.Label(
            main_frame, 
            text="🎬 Baixador de Vídeos MP4", 
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 4))

        subtitle_label = ttk.Label(
            main_frame, 
            text="Cole o link do vídeo para baixar em alta qualidade.", 
            font=("Segoe UI", 9)
        )
        subtitle_label.pack(anchor="w", pady=(0, 15))

        # Seção URL
        url_frame = ttk.LabelFrame(main_frame, text=" URL do Vídeo ", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X)

        self.url_entry = ttk.Entry(url_input_frame, font=("Segoe UI", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.url_entry.focus()

        paste_btn = ttk.Button(url_input_frame, text="📋 Colar", command=self._paste_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=(0, 4))

        clear_btn = ttk.Button(url_input_frame, text="🧹 Limpar", command=self._clear_url)
        clear_btn.pack(side=tk.LEFT)

        # Seção Configurações (Qualidade e Pasta)
        config_frame = ttk.Frame(main_frame)
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # Qualidade
        quality_group = ttk.LabelFrame(config_frame, text=" Formato / Qualidade ", padding="10")
        quality_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.quality_var = tk.StringVar(value="Melhor Qualidade (Full HD / 4K)")
        self.quality_combo = ttk.Combobox(
            quality_group, 
            textvariable=self.quality_var, 
            state="readonly",
            values=[
                "Melhor Qualidade (Full HD / 4K)",
                "1080p (Full HD)",
                "720p (HD)",
                "480p (SD)",
                "Apenas Áudio (MP3)"
            ]
        )
        self.quality_combo.pack(fill=tk.X)

        # Pasta de Destino
        dest_group = ttk.LabelFrame(config_frame, text=" Salvar Em ", padding="10")
        dest_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        folder_frame = ttk.Frame(dest_group)
        folder_frame.pack(fill=tk.X)

        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.dest_folder, font=("Segoe UI", 9))
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_btn = ttk.Button(folder_frame, text="📁 Alterar", command=self._choose_folder)
        browse_btn.pack(side=tk.LEFT, padx=(0, 2))

        open_dir_btn = ttk.Button(folder_frame, text="↗ Abrir", command=self._open_folder)
        open_dir_btn.pack(side=tk.LEFT)

        # Botão de Ação Principal
        self.download_btn = tk.Button(
            main_frame,
            text="⬇ BAIXAR VÍDEO",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self._start_download_thread
        )
        self.download_btn.pack(fill=tk.X, pady=(5, 12))

        # Seção de Progresso e Status
        status_frame = ttk.LabelFrame(main_frame, text=" Progresso ", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 5))

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 6))

        info_box = ttk.Frame(status_frame)
        info_box.pack(fill=tk.X)

        self.status_label = ttk.Label(info_box, text="Aguardando link para download...", font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)

        self.details_label = ttk.Label(info_box, text="", font=("Segoe UI", 9, "bold"))
        self.details_label.pack(side=tk.RIGHT)

    def _paste_clipboard(self):
        try:
            text = self.root.clipboard_get().strip()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, text)
        except Exception:
            pass

    def _clear_url(self):
        self.url_entry.delete(0, tk.END)
        self.status_label.config(text="Pronto.")
        self.details_label.config(text="")
        self.progress_bar['value'] = 0

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.dest_folder.get())
        if folder:
            self.dest_folder.set(folder)

    def _open_folder(self):
        path = self.dest_folder.get()
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Aviso", "A pasta selecionada não existe.")

    def _get_quality_code(self):
        mapping = {
            "Melhor Qualidade (Full HD / 4K)": "best",
            "1080p (Full HD)": "1080p",
            "720p (HD)": "720p",
            "480p (SD)": "480p",
            "Apenas Áudio (MP3)": "mp3"
        }
        return mapping.get(self.quality_var.get(), "best")

    def _update_progress(self, info):
        if info['status'] == 'downloading':
            pct = info.get('percent', 0.0)
            speed = format_bytes(info.get('speed', 0)) + "/s"
            eta = f"{int(info.get('eta', 0))}s" if info.get('eta') else "--"
            
            self.progress_bar['value'] = pct
            self.status_label.config(text=f"Baixando: {info.get('filename', '')[:35]}...")
            self.details_label.config(text=f"{pct:5.1f}% | {speed} | Restante: {eta}")
        elif info['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.status_label.config(text="Processando / Mesclando arquivos de vídeo e áudio...")
            self.details_label.config(text="Quase pronto...")

    def _download_worker(self, url, folder, quality_code):
        try:
            def callback(info):
                self.root.after(0, self._update_progress, info)

            title = download_video(
                url=url,
                output_dir=folder,
                quality=quality_code,
                progress_callback=callback
            )

            def on_success():
                self.progress_bar['value'] = 100
                self.status_label.config(text=f"✅ Concluído: {title}")
                self.details_label.config(text="100%")
                self.download_btn.config(state=tk.NORMAL, text="⬇ BAIXAR VÍDEO")
                self.is_downloading = False
                messagebox.showinfo("Sucesso", f"Download finalizado com sucesso!\n\nArquivo:\n{title}")

            self.root.after(0, on_success)

        except Exception as e:
            def on_error(err_msg):
                self.status_label.config(text="❌ Ocorreu um erro no download.")
                self.details_label.config(text="")
                self.download_btn.config(state=tk.NORMAL, text="⬇ BAIXAR VÍDEO")
                self.is_downloading = False
                messagebox.showerror("Erro no Download", f"Não foi possível baixar o vídeo:\n\n{err_msg}")

            self.root.after(0, on_error, str(e))

    def _start_download_thread(self):
        if self.is_downloading:
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira ou cole a URL do vídeo.")
            self.url_entry.focus()
            return

        folder = self.dest_folder.get().strip()
        if not folder:
            folder = self.default_dir

        quality_code = self._get_quality_code()

        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED, text="Baixando...")
        self.progress_bar['value'] = 0
        self.status_label.config(text="Obtendo informações do vídeo...")
        self.details_label.config(text="")

        thread = threading.Thread(
            target=self._download_worker, 
            args=(url, folder, quality_code), 
            daemon=True
        )
        thread.start()

def main():
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

