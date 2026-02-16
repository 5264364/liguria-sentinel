import requests
from datetime import datetime
import os

print("===========================================")
print("LIGURIA SENTINEL - VERSIONE TELEGRAM")
print("===========================================")
print(f"Data/Ora: {datetime.now()}")
print("")

# Prendi i dati da GitHub Secrets
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Funzione per inviare messaggio Telegram
def invia_telegram(messaggio):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Token o Chat ID mancanti!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dati = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": messaggio,
        "parse_mode": "HTML"
    }
    
    try:
        risposta = requests.post(url, json=dati, timeout=10)
        if risposta.status_code == 200:
            print("✅ Messaggio Telegram inviato!")
            return True
        else:
            print(f"⚠️ Errore Telegram: {risposta.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore invio: {e}")
        return False

# Test connessione FILSE
try:
    url = "https://www.filse.it/"
    print(f"Connessione a: {url}")
    
    risposta = requests.get(url, timeout=10)
    
    if risposta.status_code == 200:
        print("✅ FILSE raggiunto!")
        
        # Invia notifica Telegram
        messaggio = f"""🚀 <b>LIGURIA SENTINEL - TEST</b>

✅ Bot attivo e funzionante!
📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}

🌐 FILSE raggiunto correttamente
📊 Pagina: {len(risposta.text)} caratteri

Prossimo controllo tra 6 ore."""
        
        invia_telegram(messaggio)
    else:
        print(f"⚠️ Status code: {risposta.status_code}")
        
except Exception as errore:
    print(f"❌ ERRORE: {errore}")
    invia_telegram(f"❌ ERRORE nel bot:\n{errore}")

print("")
print("===========================================")
print("Esecuzione completata")
print("===========================================")
