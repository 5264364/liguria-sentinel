import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time requests

print("=" * 60)
print("🚀 LIGURIA SENTINEL - Avvio Scansione")
print("=" * 60)
print(f"📅 Data/Ora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("")

# Configurazione Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Inizializza database
db = Database()

def invia_telegram(messaggio):
    """Invia messaggio su Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token o Chat ID mancanti!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dati = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": messaggio,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        risposta = requests.post(url, json=dati, timeout=10)
        if risposta.status_code == 200:
            return True
        else:
            print(f"⚠️ Errore Telegram: {risposta.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore invio Telegram: {e}")
        return False

def processa_bando(bando):
    """
    Processa un singolo bando:
    1. Controlla se esiste già
    2. Filtra con keywords
    3. Calcola score
    4. Salva se nuovo
    5. Notifica se rilevante
    """
    
    # Controlla se già esiste
    if db.bando_esiste(bando['titolo'], bando['url']):
        return None
    
    # Filtra keywords negative
    testo_completo = f"{bando['titolo']} {bando.get('testo', '')}"
    if ha_keywords_negative(testo_completo):
        print(f"⏭️ Saltato (keyword negativa): {bando['titolo'][:50]}...")
        return None
    
    # Calcola score
    score = calcola_score(bando)
    
    # Estrai keywords match
    keywords_trovate = estrai_keywords_match(testo_completo)
    keywords_str = ",".join(keywords_trovate) if keywords_trovate else None
    
    # Salva nel database
    bando_id = db.aggiungi_bando(
        titolo=bando['titolo'],
        url=bando['url'],
        ente=bando['ente'],
        tipo=bando.get('tipo'),
        keywords=keywords_str
    )
    
    if not bando_id:
        return None
    
    # Se score >= 40, notifica
    if score >= 40:
        return {
            'id': bando_id,
            'bando': bando,
            'score': score,
            'keywords': keywords_trovate
        }
    else:
        print(f"📊 Score basso ({score}): {bando['titolo'][:50]}...")
        return None

def formatta_notifica(risultato):
    """Formatta il messaggio Telegram per un bando"""
    bando = risultato['bando']
    score = risultato['score']
    keywords = risultato['keywords']
    
    # Determina priorità
    if score >= 70:
        priorita = "🔴 ALTA"
        stelle = "⭐⭐⭐⭐⭐"
    elif score >= 50:
        priorita = "🟡 MEDIA"
        stelle = "⭐⭐⭐"
    else:
        priorita = "🟢 BASSA"
        stelle = "⭐"
    
    messaggio = f"""🆕 <b>NUOVO BANDO</b>

<b>{bando['titolo']}</b>

🏢 Ente: {bando['ente']}
📊 Rilevanza: {score}/100 {stelle}
{priorita}

🔗 <a href="{bando['url']}">Vai al bando</a>

🏷️ Keywords: {', '.join(keywords[:5]) if keywords else 'N/A'}"""
    
    return messaggio

# === ESECUZIONE PRINCIPALE ===

try:
    print("🔄 Inizio scansione siti...")
    print("")
    
    bandi_nuovi = []
    totale_bandi_trovati = 0
    
    # Esegui tutti gli scraper
    scrapers = get_all_scrapers()
    
    for scraper in scrapers:
        try:
            bandi = scraper.scrape()
            totale_bandi_trovati += len(bandi)
            
            # Registra controllo
            db.registra_controllo(
                sito=scraper.nome,
                url=getattr(scraper, 'url_bandi', scraper.url),
                esito="OK",
                hash_pagina=None
            )
            
            # Processa ogni bando
            for bando in bandi:
                risultato = processa_bando(bando)
                if risultato:
                    bandi_nuovi.append(risultato)
        
        except Exception as e:
            print(f"❌ Errore scraper {scraper.nome}: {e}")
            db.registra_controllo(
                sito=scraper.nome,
                url=getattr(scraper, 'url_bandi', scraper.url),
                esito="ERRORE",
                errore=str(e)
            )
    
    print("")
    print("=" * 60)
    print("📊 RIEPILOGO SCANSIONE")
    print("=" * 60)
    print(f"🔍 Bandi analizzati: {totale_bandi_trovati}")
    print(f"🆕 Bandi nuovi trovati: {len(bandi_nuovi)}")
    print(f"📚 Totale bandi in DB: {db.conta_bandi()}")
    
    # Invia notifiche per bandi nuovi
    if bandi_nuovi:
        print("")
        print(f"📱 Invio {len(bandi_nuovi)} notifiche Telegram...")
        
        for risultato in bandi_nuovi:
            messaggio = formatta_notifica(risultato)
            if invia_telegram(messaggio):
                print(f"✅ Notificato: {risultato['bando']['titolo'][:50]}...")
            else:
                print(f"⚠️ Errore notifica: {risultato['bando']['titolo'][:50]}...")
    else:
        # Nessun bando nuovo - messaggio riepilogativo
        stats = db.statistiche()
        
        msg_riepilogo = f"""✅ <b>Scansione Completata</b>

📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔍 Bandi analizzati: {totale_bandi_trovati}
🆕 Nessun bando nuovo

📊 Database: {db.conta_bandi()} bandi totali

Prossimo controllo tra 6 ore."""
        
        # Invia solo se è la prima esecuzione o ogni 24h
        # (per non spammare "nessun bando nuovo" ogni 6 ore)
        if db.conta_bandi() == 0:
            invia_telegram(msg_riepilogo)
    
    print("")
    print("=" * 60)
    print("✅ Esecuzione completata con successo!")
    print("=" * 60)

except Exception as e:
    print("")
    print("=" * 60)
    print(f"❌ ERRORE CRITICO: {e}")
    print("=" * 60)
    
    # Notifica errore
    invia_telegram(f"❌ <b>ERRORE nel bot</b>\n\n{str(e)[:200]}")
