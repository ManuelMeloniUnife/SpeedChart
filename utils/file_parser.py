import re
from datetime import datetime

def parse_race_file(file_content, wheel_circumference=1.52):
    """
    Parsa il contenuto di un file del computer di bordo.
    
    Args:
        file_content (str): Contenuto del file txt
        wheel_circumference (float): Circonferenza della ruota in metri
        
    Returns:
        dict: Dizionario con informazioni sulla corsa e lista di punti dati
    """
    lines = file_content.strip().split('\n')
    
    # Estrai informazioni dall'intestazione
    header_info = {}
    header_pattern = r"Il giroruota misura: (\d+) mm"
    date_pattern = r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})"
    
    for i, line in enumerate(lines[:5]):
        wheel_match = re.search(header_pattern, line)
        date_match = re.search(date_pattern, line)
        
        if wheel_match:
            header_info['wheel_diameter_mm'] = float(wheel_match.group(1))
            header_info['wheel_circumference'] = header_info['wheel_diameter_mm'] / 1000  # converti in metri
        
        if date_match:
            date_str = date_match.group(1)
            time_str = date_match.group(2)
            header_info['datetime'] = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
    
    # Se la circonferenza della ruota non è specificata nel file, usa il valore di default
    wheel_circumference = header_info.get('wheel_circumference', wheel_circumference)
    
    # Estrai punti dati (velocità)
    data_points = []
    distance = 0.0
    
    for line in lines:
        # Salta righe di intestazione e vuote
        if not line.strip() or any(word in line for word in ["giroruota", "misura", "/"]):
            continue
            
        try:
            # Converti al formato con decimale
            speed_str = line.strip().replace(',', '.')
            # A volte il formato è 00,0 - lo convertiamo in float
            if speed_str:
                speed = float(speed_str)
                
                # Salta velocità zero ripetute all'inizio
                if not data_points and speed == 0.0:
                    continue
                    
                data_points.append({
                    'distance': distance,
                    'speed': speed
                })
                
                # Incrementa la distanza per il prossimo punto
                distance += wheel_circumference
        except ValueError:
            # Salta righe che non possono essere convertite in float
            continue
    
    # Calcola accelerazione e tempo
    calculate_acceleration_and_time(data_points)
    
    return {
        'header_info': header_info,
        'data_points': data_points
    }

def calculate_acceleration_and_time(data_points):
    """Calcola accelerazione e tempo per ogni punto dati"""
    if not data_points:
        return
    
    # Il primo punto ha tempo e accelerazione zero
    data_points[0]['acceleration'] = 0.0
    data_points[0]['time'] = 0.0
    
    total_time = 0.0
    
    for i in range(1, len(data_points)):
        prev = data_points[i-1]
        curr = data_points[i]
        
        # Calcola la differenza di distanza in metri
        distance_diff = curr['distance'] - prev['distance']
        
        # Converti velocità da km/h a m/s per i calcoli
        prev_speed_ms = prev['speed'] / 3.6
        curr_speed_ms = curr['speed'] / 3.6
        
        # Calcola il tempo per percorrere questo segmento (in secondi)
        if prev_speed_ms + curr_speed_ms > 0:  # Evita divisione per zero
            segment_time = (2 * distance_diff) / (prev_speed_ms + curr_speed_ms)
        else:
            segment_time = 0
            
        # Aggiorna il tempo totale
        total_time += segment_time
        curr['time'] = total_time
        
        # Calcola l'accelerazione media su questo segmento (m/s²)
        if segment_time > 0:
            curr['acceleration'] = (curr_speed_ms - prev_speed_ms) / segment_time
        else:
            curr['acceleration'] = 0.0