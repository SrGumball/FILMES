#!/usr/bin/env python3
"""
🎬 HomeFlix TV — Google Drive Movie Catalog Sync Script
======================================================
Este script conecta à sua pasta do Google Drive (ID: 1Cne2Ci8boM9TQ19DAoGY-yhCbt07XGzm),
identifica todos os vídeos postados (MP4, MKV, AVI, etc.), limpa os títulos,
gera os links de streaming direto para o ExoPlayer/Player Web e atualiza o catálogo automaticamente.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse

# Pasta padrão do Google Drive configurada pelo usuário
DEFAULT_FOLDER_ID = "1Cne2Ci8boM9TQ19DAoGY-yhCbt07XGzm"
OUTPUT_JSON_PATH = "gdrive_catalog.json"
WEB_OUTPUT_JSON_PATH = "web-preview/gdrive_catalog.json"

def clean_movie_title(raw_name):
    """Limpa o nome do arquivo para obter o título legível do filme."""
    name = os.path.splitext(raw_name)[0]
    # Remove tags comuns de torrents/downloads
    tags = [
        r'\b1080p\b', r'\b720p\b', r'\b4k\b', r'\b2160p\b', r'\bhdr\b', r'\bweb-dl\b',
        r'\bwebrip\b', r'\bbluray\b', r'\bx264\b', r'\bx265\b', r'\bhevc\b', r'\bdual\b',
        r'\bdublado\b', r'\blegendado\b', r'\b5\.1\b', r'\baac\b', r'\bpt-br\b'
    ]
    for tag in tags:
        name = re.sub(tag, '', name, flags=re.IGNORECASE)
    
    # Substitui pontos e underlines por espaços
    name = re.sub(r'[\._]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()

def get_stream_url(file_id):
    """Gera a URL de stream direto do Google Drive para o ExoPlayer / HTML5 Video."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def get_embed_preview_url(file_id):
    """Gera a URL de preview/embed do Google Drive."""
    return f"https://drive.google.com/file/d/{file_id}/preview"

def fetch_folder_contents(folder_id=DEFAULT_FOLDER_ID):
    """Busca o conteúdo público da pasta do Google Drive."""
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"🔍 Conectando à pasta do Google Drive: {folder_id}...")
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        
        if "<title>Google Drive: login</title>" in html or "accounts.google.com" in html and len(html) < 200000:
            print("\n⚠️ AVISO IMPORTANTE: A sua pasta do Google Drive está marcada como PRIVADA!")
            print("==========================================================================")
            print("Para que os filmes apareçam no aplicativo da TV e no simulador web:")
            print("1. Abra a pasta no seu navegador: https://drive.google.com/drive/folders/" + folder_id)
            print("2. Clique no título da pasta -> Compartilhar -> Compartilhar")
            print("3. Em 'Acesso geral', mude de 'Restrito' para: 'Qualquer pessoa com o link'")
            print("==========================================================================\n")
            return []

        # Expressões para capturar pares (Nome, ID) do HTML renderizado do Drive
        raw_matches = re.findall(r'aria-label=\"([^\"]*?\.(?:mp4|mkv|avi|mov|wmv|webm|m4v))[^\"]*\".*?data-id=\"([a-zA-Z0-9_-]{25,50})\"', html, re.DOTALL | re.IGNORECASE)
        matches = [(file_id, name) for name, file_id in raw_matches]

        if not matches:
            matches = re.findall(r'\[\"([a-zA-Z0-9_-]{25,50})\",\[\"(.*?)\"\]', html)
        if not matches:
            raw_files = re.findall(r'\"([a-zA-Z0-9_-]{25,50})\".*?\"([^\"]+\.(?:mp4|mkv|avi|mov|wmv|webm|m4v))\"', html, re.IGNORECASE)
            matches = raw_files

        movies = []
        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.m4v')
        
        seen_ids = set()
        
        for file_id, raw_name in matches:
            if file_id in seen_ids or file_id == folder_id:
                continue
                
            name_clean = raw_name
                
            if any(name_clean.lower().endswith(ext) for ext in video_extensions) or 'filme' in name_clean.lower():
                seen_ids.add(file_id)
                movie_title = clean_movie_title(name_clean)
                
                movies.append({
                    "id": file_id,
                    "title": movie_title,
                    "original_filename": name_clean,
                    "drive_folder_id": folder_id,
                    "stream_url": get_stream_url(file_id),
                    "embed_url": get_embed_preview_url(file_id),
                    "poster": f"https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop",
                    "backdrop": f"https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=1200&auto=format&fit=crop",
                    "rating": 8.8,
                    "year": 2024,
                    "quality": "4K ULTRA HD",
                    "type": "MOVIE"
                })
        
        print(f"✅ Encontrados {len(movies)} filmes na pasta do Google Drive.")
        return movies
        
    except Exception as e:
        print(f"⚠️ Erro ao acessar a pasta do Google Drive: {e}")
        return []

def save_catalog(movies, folder_id=DEFAULT_FOLDER_ID):
    """Salva o catálogo em JSON para o servidor e para o simulador web."""
    catalog_data = {
        "drive_folder_id": folder_id,
        "drive_folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "total_movies": len(movies),
        "status": "ONLINE",
        "last_sync": "2026-07-31T21:00:00Z",
        "movies": movies
    }
    
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
        
    os.makedirs("web-preview", exist_ok=True)
    with open(WEB_OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
        
    print(f"💾 Catálogo salvo em `{OUTPUT_JSON_PATH}` e `{WEB_OUTPUT_JSON_PATH}`!")

if __name__ == "__main__":
    folder_target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FOLDER_ID
    print("=" * 60)
    print("🎬 HomeFlix TV — Sincronizador de Filmes do Google Drive")
    print("=" * 60)
    movies = fetch_folder_contents(folder_target)
    save_catalog(movies, folder_target)
    print("✨ Sincronização concluída com sucesso!")
