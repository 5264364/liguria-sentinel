"""
Liguria Sentinel Bot - Main Orchestrator
"""

import os
import requests
from datetime import datetime
from database import Database
from scrapers import ScraperFILSEPrivati, ScraperFILSEImprese
from keywords import filtra_keywords, calcola_score, estrai_keywords_match


def invia_notifica_telegram(testo):
    """Invia messaggio Telegram generico"""
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Token o Chat ID Telegram non configurati")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': testo,
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Notifica inviata")
        else:
            print(f"⚠️ Errore invio notifica: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Errore Telegram: {e}")


def notifica_nuovo_bando(bando):
    """Notifica per un singolo bando nuovo"""
    keywords = bando.get('keywords_match', '') or 'N/A'
    scadenza = bando.get('data_scadenza', '') or 'N/A'
    
    messaggio = f"""🆕 NUOVO BANDO

{bando['titolo']}

🏢 Ente: {bando['ente']}
📅 Scadenza: {scadenza}
🏷️ Keywords: {keywords}

🔗 {bando['url']}"""
    
    invia_notifica_telegram(messaggio)


def invia_riepilogo_quindicinale(db):
    """Ogni 15 giorni invia TUTTI i bandi nel database"""
    bandi = db.get_tutti_bandi()
    
    if not bandi:
        return
    
    ora = datetime.now().strftime("%d/%m/%Y")
    
    messaggio = f"📋 RIEPILOGO QUINDICINALE - {ora}\n"
    messaggio += f"Tutti i {len(bandi)} bandi attivi nel database:\n\n"
    
    for i, bando in enumerate(bandi, 1):
        scadenza = bando.get('data_scadenza', 'N/A') or 'N/A'
        messaggio += f"{i}. {bando['titolo'][:80]}\n"
        messaggio += f"   🏢 {bando['ente']} | 📅 Scade: {scadenza}\n\n"
    
    # Telegram ha limite di 4096 caratteri per messaggio
    # Dividi in più messaggi se necessario
    if len(messaggio) <= 4096:
        invia_notifica_telegram(messaggio)
    else:
        # Invia a blocchi
        righe = messaggio.split('\n')
        chunk = ""
        for riga in righe:
            if len(chunk) + len(riga) + 1 > 4000:
                invia_notifica_telegram(chunk)
                chunk = riga + '\n'
            else:
                chunk += riga + '\n'
        if chunk:
            invia_notifica_telegram(chunk)
    
    print(f"✅ Riepilogo quindicinale inviato ({len(bandi)} bandi)")


def invia_riepilogo_giornaliero(totale_trovati, totale_nuovi, totale_db):
    """Riepilogo giornaliero"""
    ora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if totale_nuovi == 0:
        messaggio = f"""✅ Scansione completata
📅 {ora}
🔍 Bandi analizzati: {totale_trovati}
🆕 Nessun bando nuovo
📊 Database: {totale_db} bandi totali"""
    else:
        messaggio = f"""✅ Scansione completata
📅 {ora}
🔍 Bandi analizzati: {totale_trovati}
🆕 Nuovi bandi trovati: {totale_nuovi}
📊 Database: {totale_db} bandi totali"""
    
    invia_notifica_telegram(messaggio)


def main():
    print("=" * 60)
    print("🤖 LIGURIA SENTINEL BOT")
    print("=" * 60)
    
    db = Database()
    
    scrapers = [
        ScraperFILSEPrivati(),
        ScraperFILSEImprese(),
    ]
    
    totale_trovati = 0
    totale_nuovi = 0
    
    for scraper in scrapers:
        try:
            bandi = scraper.scrape()
            totale_trovati += len(bandi)
            
            for bando in bandi:
                if db.bando_esiste(bando['url']):
                    print(f"⏭️ Già presente: {bando['titolo'][:50]}...")
                    continue
                
                if not filtra_keywords(bando['titolo'], bando.get('testo', '')):
                    print(f"❌ Filtrato: {bando['titolo'][:50]}...")
                    continue
                
                # Calcola keywords ma NON score
                keywords = estrai_keywords_match(bando['titolo'], bando.get('testo', ''))
                bando['keywords_match'] = ', '.join(keywords) if keywords else None
                bando['score'] = 0  # Non usato
                
                db.salva_bando(bando)
                totale_nuovi += 1
                
                print(f"💾 Salvato: {bando['titolo'][:50]}...")
                
                # Notifica TUTTI i bandi nuovi senza score
                notifica_nuovo_bando(bando)
        
        except Exception as e:
            print(f"❌ Errore scraper {scraper.nome}: {e}")
            import traceback
            traceback.print_exc()
    
    # Riepilogo giornaliero
    totale_db = db.conta_bandi()
    print("\n" + "=" * 60)
    print(f"✅ Scansione completata!")
    print(f"🔍 Bandi trovati: {totale_trovati}")
    print(f"🆕 Nuovi bandi: {totale_nuovi}")
    print(f"📊 Totale database: {totale_db}")
    print("=" * 60)
    
    invia_riepilogo_giornaliero(totale_trovati, totale_nuovi, totale_db)
    
    # Riepilogo quindicinale (ogni 1° e 16° del mese)
    giorno = datetime.now().day
    if giorno in [1, 16]:
        print("📋 Invio riepilogo quindicinale...")
        invia_riepilogo_quindicinale(db)


if __name__ == "__main__":
    main()
