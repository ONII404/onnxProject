import requests
import json
import time
import os
import sys
import random

# --- CONFIGURACIÓN ---
INPUT_FILE = "src/util/valid_ids(1917-2025).txt"     
OUTPUT_DIR = "src/util/raw_data"           

# TIEMPOS (Anti-Ban)
MIN_DELAY = 1.5                   # Mínimo tiempo a esperar (Normal)
MAX_DELAY = 2.5                   # Máximo tiempo a esperar (Normal)
RATE_LIMIT_DELAY = 60             # Espera si sale error 429 (1 minuto)
SERVER_ERROR_DELAY = 30 * 60      # 30 Minutos si sale error 500

BASE_URL = "https://api.jikan.moe/v4/anime"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def sleep_random():
    """Duerme un tiempo variable para parecer comportamiento humano"""
    sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(sleep_time)

def countdown_timer(seconds):
    """Muestra una cuenta regresiva en la misma línea para esperas largas"""
    try:
        for i in range(seconds, 0, -1):
            # Formato MM:SS
            mins, secs = divmod(i, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            
            sys.stdout.write(f"\r⏳ Enfriando servidor... {timer} restantes  ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r🚀 Reanudando operaciones...                   \n")
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido durante la espera.")
        sys.exit(0)

def request_safe(url):
    """
    Realiza una petición robusta con esperas largas en caso de error crítico.
    Retorna: (status_code, json_data)
    """
    while True:
        try:
            resp = requests.get(url, timeout=15)
            
            # CASO: Éxito (200)
            if resp.status_code == 200:
                try:
                    return 200, resp.json()
                except json.JSONDecodeError:
                    print(" [⚠️ JSON corrupto. Reintentando...] ", end="", flush=True)
                    time.sleep(2)
                    continue
            
            # CASO: No encontrado (404)
            if resp.status_code == 404:
                return 404, None

            # CASO: Bloqueo Rate Limit (429)
            if resp.status_code == 429:
                print(f"\n⚠️ RATE LIMIT (429).")
                countdown_timer(RATE_LIMIT_DELAY)
                continue 
            
            # CASO: Error de Servidor (500, 502, 503, 504)
            # AQUÍ APLICAMOS LA ESPERA DE 30 MINUTOS
            if resp.status_code >= 500:
                print(f"\n🔥 ERROR CRÍTICO ({resp.status_code}). Jikan está saturado.")
                print(f"   Activando protocolo de espera larga ({SERVER_ERROR_DELAY//60} min).")
                countdown_timer(SERVER_ERROR_DELAY)
                continue

            # Otros errores desconocidos (400, 403, etc)
            return resp.status_code, None

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error Conexión ({e}). Reintentando en 10s...", end="", flush=True)
            time.sleep(10)

def get_episodes(mal_id):
    """Descarga todos los episodios paginados"""
    all_episodes = []
    page = 1
    
    while True:
        url = f"{BASE_URL}/{mal_id}/episodes?page={page}"
        code, data = request_safe(url)
        
        if code != 200 or not data:
            break
            
        if 'data' not in data:
            break

        all_episodes.extend(data['data'])
        
        pagination = data.get('pagination', {})
        if not pagination or not pagination.get('has_next_page'):
            break
            
        page += 1
        sleep_random()
        
    return all_episodes

def process_anime(mal_id):
    # Organización por carpetas (Sharding)
    subfolder = str(mal_id // 1000)
    target_dir = os.path.join(OUTPUT_DIR, subfolder)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    filename = os.path.join(target_dir, f"{mal_id}.json")
    
    # Resume System
    if os.path.exists(filename):
        return "skipped" 

    print(f"📥 ID {mal_id}...", end=" ", flush=True)

    # 1. Metadata
    code, meta_resp = request_safe(f"{BASE_URL}/{mal_id}/full")
    
    if code == 404:
        print("❌ 404")
        return "404"
    
    if code != 200:
        print(f"⚠️ Error {code}")
        return "error"
    
    if 'data' not in meta_resp:
        print("⚠️ Sin data")
        return "error"

    metadata = meta_resp['data']
    sleep_random()

    # 2. Episodios
    print("Caps...", end=" ", flush=True)
    episodes = get_episodes(mal_id)

    # 3. Guardar
    final_object = {
        "id": mal_id,
        "fetched_at": time.ctime(),
        "metadata": metadata,
        "episodes": episodes
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_object, f, indent=4, ensure_ascii=False)
    
    title = metadata.get('title_english') or metadata.get('title') or "Sin título"
    # Limpieza básica de caracteres para consola
    safe_title = title.encode('ascii', 'ignore').decode('ascii')
    print(f"✅ {safe_title[:25]}...")
    
    return "success"

def main():
    ids_to_process = []
    
    if os.path.exists(INPUT_FILE):
        print(f"📂 Leyendo {INPUT_FILE}...")
        with open(INPUT_FILE, "r") as f:
            for line in f:
                if line.strip().isdigit():
                    ids_to_process.append(int(line.strip()))
    else:
        print(f"⚠️ No se encontró {INPUT_FILE}. Usando rango de prueba 1-50.")
        ids_to_process = list(range(1, 51))

    total = len(ids_to_process)
    print(f"🚀 Iniciando descarga de {total} animes con Protección Anti-500.\n")

    success_count = 0
    skipped_count = 0
    
    try:
        for index, mal_id in enumerate(ids_to_process):
            progress = f"[{index + 1}/{total}]"
            print(progress, end=" ")
            
            status = process_anime(mal_id)
            
            if status == "success":
                success_count += 1
                sleep_random()
            elif status == "skipped":
                skipped_count += 1
                print("⏩ Saltado")
            
    except KeyboardInterrupt:
        print("\n\n🛑 DETENIDO POR USUARIO.")
        print("Puedes volver a ejecutar el script y continuará donde se quedó.")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Descargados nuevos: {success_count}")
    print(f"   Saltados (Existían): {skipped_count}")
    print(f"   Total procesados: {success_count + skipped_count} / {total}")

if __name__ == "__main__":
    main()