"""
Liguria Sentinel Bot - Main Orchestrator
Coordina tutti gli scraper e invia notifiche Telegram
"""

import os
from database import Database
from scrapers import ScraperFILSEPrivati, ScraperFILSEImprese
from keywords import filtra_keywords, calcola_score, estrai_keywords_match
import requests
import time

def invia_notifica_telegram(bando, db):
    """Invia notifica Telegram per un bando"""
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Token o Chat ID Telegram non configurati")
        return
    
    score = bando.get('score', 0)
    
    # Emoji rilevanza
    if score >= 70:
        emoji_score = "⭐⭐⭐⭐⭐"
        priorita = "🔴 ALTA"
    elif score >= 50:
        emoji_score = "⭐⭐⭐⭐"
        priorita = "🟡 MEDIA"
    else:
        emoji_score = "⭐⭐⭐"
        priorita = "🟢 BASSA"
    
    messaggio = f"""
🆕 NUOVO BANDO

{bando['titolo']}

🏢 Ente: {bando['ente']}
📊 Rilevanza: {score}/100 {emoji_score}
{priorita}

🔗 {bando['url']}
🏷️ Keywords: {bando.get('keywords_match', 'N/A')}
"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': messaggio,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Notifica inviata per: {bando['titolo'][:50]}...")
        else:
            print(f"⚠️ Errore invio notifica: {response.status_code}")
    except Exception as e:
        print(f"❌ Errore Telegram: {e}")


def invia_riepilogo_telegram(totale_trovati, totale_nuovi, totale_db):
    """Invia riepilogo finale"""
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        return
    
    from datetime import datetime
    ora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    messaggio = f"""
✅ Scansione Completata
📅 {ora}
🔍 Bandi analizzati: {totale_trovati}
🆕 Nuovi bandi: {totale_nuovi}
📊 Database: {totale_db} bandi totali

Prossimo controllo tra 6 ore.
"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': messaggio
    }
    
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass


def main():
    """Main execution"""
    print("=" * 60)
    print("🤖 LIGURIA SENTINEL BOT")
    print("=" * 60)
    
    # Inizializza database
    db = Database()
    
    # Lista scrapers attivi
    scrapers = [
        ScraperFILSEPrivati(),
        ScraperFILSEImprese(),
        # ScraperALFA(),  # Attiva dopo
        # ScraperRegione()  # Attiva dopo
    ]
    
    totale_trovati = 0
    totale_nuovi = 0
    
    # Esegui tutti gli scraper
    for scraper in scrapers:
        try:
            bandi = scraper.scrape()
            totale_trovati += len(bandi)
            
            for bando in bandi:
                # Controlla se esiste già
                if db.bando_esiste(bando['url']):
                    print(f"⏭️ Già presente: {bando['titolo'][:50]}...")
                    continue
                
                # Filtra keywords negative
                if not filtra_keywords(bando['titolo'], bando.get('testo', '')):
                    print(f"❌ Filtrato (keyword negativa): {bando['titolo'][:50]}...")
                    continue
                
                # Calcola score
                score = calcola_score(bando)
                bando['score'] = score
                
                # Estrai keywords match
                keywords = estrai_keywords_match(bando['titolo'], bando.get('testo', ''))
                bando['keywords_match'] = ', '.join(keywords) if keywords else None
                
                # Salva in database
                db.salva_bando(bando)
                totale_nuovi += 1
                
                print(f"💾 Salvato: {bando['titolo'][:50]}... (Score: {score})")
                
                # Invia notifica se score >= 40
                if score >= 40:
                    invia_notifica_telegram(bando, db)
        
        except Exception as e:
            print(f"❌ Errore scraper {scraper.nome}: {e}")
            import traceback
            traceback.print_exc()
    
    # Riepilogo finale
    totale_db = db.conta_bandi()
    print("\n" + "=" * 60)
    print(f"✅ Scansione completata!")
    print(f"🔍 Bandi trovati: {totale_trovati}")
    print(f"🆕 Nuovi bandi: {totale_nuovi}")
    print(f"📊 Totale database: {totale_db}")
    print("=" * 60)
    
    # Invia riepilogo Telegram
    invia_riepilogo_telegram(totale_trovati, totale_nuovi, totale_db)


if __name__ == "__main__":
    main()
