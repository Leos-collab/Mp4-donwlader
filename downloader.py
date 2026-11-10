import os
import re
import yt_dlp

def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivos no Windows."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_video_info(url: str):
    """Obtém informações básicas do vídeo antes do download."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Vídeo'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader', 'Desconhecido')
        }

def download_video(url: str, output_dir: str = "videos", quality: str = "best", progress_callback = None):
    """
    Realiza o download do vídeo em formato MP4.
    
    :param url: URL do vídeo (YouTube, etc.)
    :param output_dir: Diretório onde o arquivo será salvo
    :param quality: 'best', '1080p', '720p', '480p', ou 'mp3'
    :param progress_callback: Função chamada com dict contendo status do progresso
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Configuração de formato de acordo com a qualidade escolhida
    if quality == "mp3":
        ydl_format = 'bestaudio/best'
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        merge_format = None
    elif quality == "1080p":
        ydl_format = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        postprocessors = []
        merge_format = 'mp4'
    elif quality == "720p":
        ydl_format = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]'
        postprocessors = []
        merge_format = 'mp4'
    elif quality == "480p":
        ydl_format = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]'
        postprocessors = []
        merge_format = 'mp4'
    else: # 'best'
        ydl_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best'
        postprocessors = []
        merge_format = 'mp4'

    def hook(d):
        if progress_callback:
            status = d.get('status')
            if status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                percent = (downloaded / total * 100) if total > 0 else 0
                speed = d.get('speed') or 0
                eta = d.get('eta') or 0
                
                # Nome do arquivo/título em download
                filename = d.get('filename', '')
                
                progress_callback({
                    'status': 'downloading',
                    'percent': percent,
                    'downloaded_bytes': downloaded,
                    'total_bytes': total,
                    'speed': speed,
                    'eta': eta,
                    'filename': os.path.basename(filename)
                })
            elif status == 'finished':
                progress_callback({
                    'status': 'finished',
                    'percent': 100.0,
                    'filename': os.path.basename(d.get('filename', ''))
                })

    outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': ydl_format,
        'outtmpl': outtmpl,
        'progress_hooks': [hook],
        'noplaylist': True,
        'no_warnings': True,
        'windowsfilenames': True,
    }

    if merge_format:
        ydl_opts['merge_output_format'] = merge_format
    if postprocessors:
        ydl_opts['postprocessors'] = postprocessors

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('title', 'Vídeo')

