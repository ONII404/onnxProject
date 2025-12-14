import requests
import time
import json

# RANGO DE BÚSQUEDA
START_YEAR = 1917  # Puedes ir tan atrás como 1917
END_YEAR = 1989
SEASONS = ["winter", "spring", "summer", "fall"]

OUTPUT_FILE = "util/valid_ids.txt"

def get_ids_from_season(year, season):
    ids_found = []
    page = 1
    
    while True:
        print(f"📅 Consultando {season.capitalize()} {year} - Pag {page}...", end=" ")
        
        try:
            url = f"https://api.jikan.moe/v4/seasons/{year}/{season}?page={page}"
            resp = requests.get(url)
            
            if resp.status_code == 429:
                print("⚠️ Rate Limit. Esperando...")
                time.sleep(5)
                continue # Reintentar
            
            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code}")
                break

            data = resp.json()
            anime_list = data['data']
            
            if not anime_list:
                print("✅ (Fin de temporada)")
                time.sleep(1.5)
                break # No hay más datos en esta temporada
            
            # Extraer solo los IDs
            for anime in anime_list:
                ids_found.append(anime['mal_id'])
            
            # Verificar si hay siguiente página
            if not data.get('pagination', {}).get('has_next_page'):
                print(f"✅ Ok ({len(anime_list)} animes)")
                time.sleep(1.5)
                break
                
            print(f"✅ Ok")
            page += 1
            time.sleep(1.5) # Pausa ética

        except Exception as e:
            print(f"Error: {e}")
            break

    return ids_found

def main():
    total_ids = set() # Usamos set para evitar duplicados (algunos animes salen en varias temps)
    
    # Cargar IDs previos si existen
    try:
        with open(OUTPUT_FILE, "r") as f:
            for line in f:
                total_ids.add(int(line.strip()))
        print(f"📂 Cargados {len(total_ids)} IDs previos.")
    except FileNotFoundError:
        pass

    print(f"🚀 Iniciando descubrimiento de IDs ({START_YEAR}-{END_YEAR})...")

    for year in range(START_YEAR, END_YEAR + 1):
        for season in SEASONS:
            new_ids = get_ids_from_season(year, season)
            
            # Guardar en el set
            total_ids.update(new_ids)
            
            # Guardado incremental en archivo (por seguridad)
            with open(OUTPUT_FILE, "w") as f:
                for mid in sorted(total_ids):
                    f.write(f"{mid}\n")
            
            print(f"💾 Total acumulado: {len(total_ids)} IDs únicos.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Detenido. Los IDs recolectados están guardados.")