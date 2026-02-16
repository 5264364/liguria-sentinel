"""
Sistema di keywords e scoring per filtrare i bandi
"""

# Keywords positive con peso
KEYWORDS_POSITIVE = {
    'formazione': 20,
    'accreditamento': 20,
    'FSE': 15,
    'fondo sociale europeo': 15,
    'turismo': 15,
    'hotel': 10,
    'albergo': 10,
    'ristorazione': 10,
    'ristorante': 10,
    'voucher': 10,
    'contributo a fondo perduto': 15,
    'fondo perduto': 15,
    'concessione demaniale': 15,
    'demanio': 10,
    'spiaggia': 10,
    'stabilimento balneare': 15,
    'manifestazione di interesse': 10,
    'manifestazione interesse': 10,
    'innovazione': 10,
    'digitale': 8,
    'digitalizzazione': 10,
    'startup': 10,
    'impresa': 8,
    'PMI': 10,
    'piccola media impresa': 10,
    'sviluppo': 8,
    'investimento': 10,
}

# Keywords negative (escludono automaticamente)
KEYWORDS_NEGATIVE = [
    'esiti',
    'graduatoria definitiva',
    'graduatoria provvisoria',
    'nomina commissione',
    'commissione giudicatrice',
    'appalto lavori',
    'lavori pubblici',
    'gara d\'appalto',
    'aggiudicazione',
    'verbale',
    'rettifica graduatoria',
]


def filtra_keywords(titolo, testo=''):
    """
    Filtra i bandi con keywords negative
    Ritorna True se il bando è OK, False se deve essere scartato
    """
    contenuto = (titolo + ' ' + testo).lower()
    
    for keyword in KEYWORDS_NEGATIVE:
        if keyword.lower() in contenuto:
            return False
    
    return True


def estrai_keywords_match(titolo, testo=''):
    """
    Estrae le keywords positive trovate nel bando
    Ritorna una lista di keywords
    """
    contenuto = (titolo + ' ' + testo).lower()
    keywords_trovate = []
    
    for keyword in KEYWORDS_POSITIVE.keys():
        if keyword.lower() in contenuto:
            keywords_trovate.append(keyword)
    
    return keywords_trovate


def calcola_score(bando):
    """
    Calcola uno score 0-100 in base a:
    1. Keywords match (max 50 punti)
    2. Ente prioritario (max 20 punti)
    3. Scadenza ragionevole (max 15 punti)
    4. Budget significativo (max 15 punti)
    """
    score = 0
    
    titolo = bando.get('titolo', '').lower()
    testo = bando.get('testo', '').lower()
    ente = bando.get('ente', '').lower()
    contenuto = titolo + ' ' + testo
    
    # 1. Keywords match (max 50 punti)
    for keyword, peso in KEYWORDS_POSITIVE.items():
        if keyword.lower() in contenuto:
            score += peso
    
    # Cap a 50 punti
    if score > 50:
        score = 50
    
    # 2. Ente prioritario (+20 punti)
    enti_prioritari = ['filse', 'alfa', 'regione liguria']
    for ente_prioritario in enti_prioritari:
        if ente_prioritario in ente:
            score += 20
            break
    
    # 3. Scadenza ragionevole (+15 punti)
    # TODO: implementare parsing data scadenza
    # Per ora diamo punti di default
    score += 10
    
    # 4. Budget significativo (+15 punti)
    # Cerca importi nel testo
    if '€' in contenuto or 'euro' in contenuto:
        # Cerca pattern tipo "1.000.000" o "1000000"
        if '1.000.000' in contenuto or '1000000' in contenuto or 'milione' in contenuto:
            score += 15
        elif '500.000' in contenuto or '500000' in contenuto:
            score += 10
        else:
            score += 5
    
    # Assicura che lo score sia tra 0 e 100
    if score > 100:
        score = 100
    
    return score
