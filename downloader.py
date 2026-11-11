import os
import re
import shutil
import subprocess
import yt_dlp

def get_ffmpeg_path() -> str:
    """Localiza o binário do ffmpeg no sistema."""
    # 1. Verifica no PATH do sistema
    p = shutil.which("ffmpeg")
    if p:
        return p
    # 2. Verifica no pacote WinGet (comum no Windows)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    winget_dir = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_dir):
        for root, _, files in os.walk(winget_dir):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
    return "ffmpeg"

def clean_url(url: str) -> str:
    """Normaliza e limpa URLs do Instagram, TikTok e YouTube."""
    url = url.strip()
    # Converte links de compartilhamento mobile do Instagram (ex: /share/reel/ ou /share/p/)
    url = re.sub(r'instagram\.com/share/(reel|p)/', r'instagram.com/\1/', url)
    return url

def merge_leftover_streams(output_dir: str):
    """
    Verifica se ficaram arquivos residuais separados (.fXXX.mp4 e .fXXX.m4a)
    e mescla automaticamente em um único arquivo .mp4 definitivo com áudio AAC.
    """
    if not os.path.exists(output_dir):
        return

    ffmpeg_bin = get_ffmpeg_path()
    files = os.listdir(output_dir)
    
    # Mapear vídeos separados (.fXXX.mp4 ou .fXXX.webm)
    video_parts = {}
    audio_parts = {}
    
    for f in files:
        full_path = os.path.join(output_dir, f)
        # Ex: "Meu Video.f398.mp4"
        m_vid = re.match(r'^(.*?)\.f\w+\.(mp4|webm|mkv)$', f, re.IGNORECASE)
        if m_vid:
            base_name = m_vid.group(1)
            video_parts[base_name] = full_path
            
        m_aud = re.match(r'^(.*?)\.f\w+\.(m4a|webm|opus|mp3|aac)$', f, re.IGNORECASE)
        if m_aud:
            base_name = m_aud.group(1)
            audio_parts[base_name] = full_path

    # Para cada par encontrado, mesclar se o .mp4 final não existir
    for base_name, vid_file in video_parts.items():
        if base_name in audio_parts:
            aud_file = audio_parts[base_name]
            final_mp4 = os.path.join(output_dir, f"{base_name}.mp4")
            temp_mp4 = os.path.join(output_dir, f"{base_name}.temp.mp4")
            
            # Remove arquivo temp corrompido se existir
            if os.path.exists(temp_mp4):
                try:
                    os.remove(temp_mp4)
                except Exception:
                    pass

            cmd = [
                ffmpeg_bin, "-y",
                "-i", vid_file,
                "-i", aud_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-movflags", "+faststart",
                final_mp4
            ]
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                # Se mesclou com sucesso, remove os arquivos separados
                if os.path.exists(final_mp4) and os.path.getsize(final_mp4) > 0:
                    try:
                        os.remove(vid_file)
                        os.remove(aud_file)
                    except Exception:
                        pass
            except Exception:
                pass

def get_video_info(url: str):
    """Obtém informações básicas do vídeo antes do download."""
    url = clean_url(url)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
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
    Realiza o download de vídeos em formato MP4 compatível com YouTube, TikTok e Instagram.
    Garante que o áudio seja mesclado e convertido para AAC, compatível com todos os players.
    """
    url = clean_url(url)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_path()

    # Formatos compatíveis tanto com vídeos horizontais (YouTube) quanto verticais (TikTok/Reels)
    if quality == "mp3":
        ydl_format = 'bestaudio/best'
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        merge_format = None
        postprocessor_args = None
    elif quality == "1080p":
        # Suporta altura <= 1080 (horizontal) OU largura <= 1080 (vertical TikTok/Reels)
        ydl_format = '(bestvideo*[height<=1080]/bestvideo*[width<=1080])+bestaudio/(best[height<=1080]/best[width<=1080])/best'
        postprocessors = []
        merge_format = 'mp4'
        postprocessor_args = {'merger': ['-c:v', 'copy', '-c:a', 'aac']}
    elif quality == "720p":
        ydl_format = '(bestvideo*[height<=720]/bestvideo*[width<=720])+bestaudio/(best[height<=720]/best[width<=720])/best'
        postprocessors = []
        merge_format = 'mp4'
        postprocessor_args = {'merger': ['-c:v', 'copy', '-c:a', 'aac']}
    elif quality == "480p":
        ydl_format = '(bestvideo*[height<=480]/bestvideo*[width<=480])+bestaudio/(best[height<=480]/best[width<=480])/best'
        postprocessors = []
        merge_format = 'mp4'
        postprocessor_args = {'merger': ['-c:v', 'copy', '-c:a', 'aac']}
    else:  # 'best'
        # Seleciona o melhor vídeo e melhor áudio, ou fluxo único de melhor qualidade
        ydl_format = 'bestvideo*+bestaudio/best'
        postprocessors = []
        merge_format = 'mp4'
        postprocessor_args = {'merger': ['-c:v', 'copy', '-c:a', 'aac']}

    def hook(d):
        if not progress_callback:
            return
        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            percent = (downloaded / total * 100) if total > 0 else 0
            speed = d.get('speed') or 0
            eta = d.get('eta') or 0
            filename = os.path.basename(d.get('filename', ''))
            
            progress_callback({
                'status': 'downloading',
                'percent': percent,
                'downloaded_bytes': downloaded,
                'total_bytes': total,
                'speed': speed,
                'eta': eta,
                'filename': filename
            })
        elif status == 'finished':
            progress_callback({
                'status': 'processing',
                'percent': 100.0,
                'filename': os.path.basename(d.get('filename', ''))
            })

    def pp_hook(d):
        if not progress_callback:
            return
        pp_name = d.get('postprocessor', '')
        status = d.get('status')
        if status == 'started':
            progress_callback({
                'status': 'merging',
                'percent': 100.0,
                'step': f"Mesclando com FFmpeg ({pp_name})..."
            })
        elif status == 'finished':
            progress_callback({
                'status': 'finished',
                'percent': 100.0,
                'step': "Pronto!"
            })

    outtmpl = os.path.join(output_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': ydl_format,
        'outtmpl': outtmpl,
        'progress_hooks': [hook],
        'postprocessor_hooks': [pp_hook],
        'noplaylist': True,
        'no_warnings': True,
        'windowsfilenames': True,
        'ffmpeg_location': ffmpeg_bin,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        }
    }

    if merge_format:
        ydl_opts['merge_output_format'] = merge_format
    if postprocessors:
        ydl_opts['postprocessors'] = postprocessors
    if postprocessor_args:
        ydl_opts['postprocessor_args'] = postprocessor_args

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Vídeo')
    finally:
        # Varredura de segurança para garantir que nenhum resíduo separado fique na pasta
        merge_leftover_streams(output_dir)

    return title
