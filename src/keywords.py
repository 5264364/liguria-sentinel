# Keywords dal PRD - Sistema di filtraggio intelligente

KEYWORDS_POSITIVE = {
    # Tua attività core
    "formazione": 20,
    "corsi": 15,
    "accreditamento": 20,
    "ente formativo": 20,
    "FSE": 15,
    "PNRR formazione": 15,
    "formatore": 10,
    "docente": 10,
    
    # Settori clienti
    "turismo": 15,
    "hospitality": 15,
    "hotel": 10,
    "ristorazione": 10,
    "bed and breakfast": 10,
    "B&B": 10,
    "agriturismo": 10,
    
    # Tipo agevolazioni
    "voucher": 10,
    "contributo a fondo perduto": 15,
    "partita IVA": 10,
    "micro impresa": 10,
    "forfettari": 15,
    "piccola impresa": 10,
    
    # Immobili e concessioni
    "concessione demaniale": 15,
    "stabilimento balneare": 10,
    "manifestazione di interesse": 10,
    "gestione immobile": 10,
    "chiosco bar": 10,
    "valorizzazione patrimonio": 10,
}

KEYWORDS_NEGATIVE = [
    "esiti",
    "graduatoria definitiva",
    "graduatoria finale",
    "nomina commissione",
    "appalto lavori",
    "gara d'appalto forniture",
    "esclusivamente enti pubblici",
    "riservato dipendenti",
]

ENTI_PRIORITARI = ["FILSE", "ALFA", "Regione Liguria", "Comune Genova"]

def calcola_score(bando_dict):
    """
    Calcola score di rilevanza 0-100
    
    Args:
        bando_dict: dizionario con chiavi: titolo, testo, ente, scadenza, budget
    
    Returns:
        int: Score 0-100
    """
    score = 0
    testo_completo = f"{bando_dict.get('titolo', '')} {bando_dict.get('testo', '')}".lower()
    
    # 1. Match keywords (max 50 punti)
    for keyword, punti in KEYWORDS_POSITIVE.items():
        if keyword.lower() in testo_completo:
            score += punti
    
    score = min(score, 50)  # Cap a 50
    
    # 2. Ente prioritario (max 20 punti)
    if bando_dict.get('ente') in ENTI_PRIORITARI:
        score += 20
    
    # 3. Tempistiche ragionevoli (max 15 punti)
    giorni_mancanti = bando_dict.get('giorni_scadenza', 0)
    if giorni_mancanti >= 30:
        score += 15
    elif giorni_mancanti >= 15:
        score += 10
    elif giorni_mancanti >= 7:
        score += 5
    
    # 4. Budget significativo (max 15 punti)
    budget = bando_dict.get('budget', 0)
    if budget >= 1000000:
        score += 15
    elif budget >= 500000:
        score += 10
    elif budget >= 100000:
        score += 5
    
    return min(score, 100)

def ha_keywords_negative(testo):
    """Controlla se il testo contiene keywords negative"""
    testo_lower = testo.lower()
    for keyword in KEYWORDS_NEGATIVE:
        if keyword.lower() in testo_lower:
            return True
    return False

def estrai_keywords_match(testo):
    """Ritorna lista keywords trovate nel testo"""
    keywords_trovate = []
    testo_lower = testo.lower()
    
    for keyword in KEYWORDS_POSITIVE.keys():
        if keyword.lower() in testo_lower:
            keywords_trovate.append(keyword)
    
    return keywords_trovate
