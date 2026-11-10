import os
import sys
from downloader import download_video

def format_bytes(size):
    if not size:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def progress_bar(info):
    if info['status'] == 'downloading':
        pct = info['percent']
        speed = format_bytes(info['speed']) + "/s"
        eta = f"{int(info['eta'])}s" if info['eta'] else "--"
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = '█' * filled + '-' * (bar_len - filled)
        sys.stdout.write(f"\r[{bar}] {pct:5.1f}% | Vel: {speed} | Restante: {eta}")
        sys.stdout.flush()
    elif info['status'] == 'finished':
        sys.stdout.write("\nConcluindo processamento/mesclagem...\n")
        sys.stdout.flush()

def main():
    print("=" * 55)
    print("      🎬 BAIXADOR DE VÍDEOS MP4 - PYTHON 🎬")
    print("=" * 55)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
    os.makedirs(output_dir, exist_ok=True)

    while True:
        print("\nDiretório de destino:", output_dir)
        url = input("\nCole a URL do vídeo (ou 'sair' para encerrar): ").strip()
        if not url:
            continue
        if url.lower() in ['sair', 'exit', 'q']:
            print("Até logo!")
            break

        print("\nEscolha a qualidade:")
        print("1 - Melhor qualidade (Padrão / Full HD / 4K)")
        print("2 - 1080p")
        print("3 - 720p")
        print("4 - 480p")
        print("5 - Apenas Áudio (MP3)")
        choice = input("Opção [1-5, Enter para 1]: ").strip()

        qualities = {
            "1": "best",
            "2": "1080p",
            "3": "720p",
            "4": "480p",
            "5": "mp3"
        }
        quality = qualities.get(choice, "best")

        print(f"\nIniciando download ({quality})...")
        try:
            title = download_video(url, output_dir=output_dir, quality=quality, progress_callback=progress_bar)
            print(f"✅ Download concluído com sucesso: {title}\n")
        except Exception as e:
            print(f"\n❌ Erro ao baixar o vídeo: {e}\n")

if __name__ == "__main__":
    main()

