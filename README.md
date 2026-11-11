# 🎬 Baixador de Vídeos MP4 (YouTube, TikTok & Instagram)

Aplicação em Python para baixar vídeos em alta definição no formato universal **MP4** a partir de links de múltiplas plataformas (**YouTube, TikTok, Instagram Reels/Posts, Twitter/X, etc.**) utilizando **yt-dlp** e **FFmpeg**.

---

## 🚀 Como Executar

Você tem duas formas de usar:

### 1. Interface Gráfica (Recomendado)
- Dê dois cliques em **`iniciar.bat`**, ou
- No terminal:
  ```powershell
  python app.py
  ```

### 2. Modo Terminal (CLI)
- Dê dois cliques em **`iniciar_terminal.bat`**, ou
- No terminal:
  ```powershell
  python cli.py
  ```

---

## 🛠️ Novidades e Recursos

- **Plataformas Suportadas**:
  - **YouTube**: Vídeos longos, Shorts, playlists individuais.
  - **TikTok**: Vídeos, links curtos (`vm.tiktok.com`, `vt.tiktok.com`, `tiktok.com/@...`).
  - **Instagram**: Reels, posts com vídeo, links diretos ou links gerados pelo botão de compartilhar (`/share/reel/`, etc.).
  - **Twitter / X, Facebook, Twitch** e centenas de outros sites.
- **Áudio e Vídeo Sempre Juntos (MP4 com áudio AAC)**:
  - O sistema junta automaticamente os fluxos separados de vídeo e áudio em um único arquivo `.mp4` usando o FFmpeg com áudio codificado em AAC.
  - Compatível com qualquer reprodutor do Windows (Windows Media Player, Filmes e TV, VLC), celulares e WhatsApp.
  - Limpeza e mesclagem automática de qualquer resíduo (`.fXXX.mp4` e `.fXXX.m4a`).
- **Resoluções e Qualidades**:
  - Máxima Qualidade (Full HD, 2K, 4K, Reels verticais 1080x1920)
  - 1080p (Full HD)
  - 720p (HD)
  - 480p (SD)
  - Apenas Áudio (MP3)
- **Pasta Padrão `videos/`**: Todos os downloads são salvos diretamente na pasta `videos/`.
- **Acompanhamento em Tempo Real**: Progresso com percentual, velocidade, tempo estimado (ETA) e aviso claro de mesclagem com FFmpeg (não trava a janela).
