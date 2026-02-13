import requests
from datetime import datetime

print("===========================================")
print("LIGURIA SENTINEL - TEST")
print("===========================================")
print(f"Data/Ora esecuzione: {datetime.now()}")
print("")

# Prova a scaricare la pagina di FILSE
try:
    url = "https://www.filse.it/"
    print(f"Sto provando a connettermi a: {url}")
    
    risposta = requests.get(url, timeout=10)
    
    if risposta.status_code == 200:
        print("✅ SUCCESSO! Sono riuscito a scaricare la pagina!")
        print(f"   La pagina è lunga {len(risposta.text)} caratteri")
    else:
        print(f"⚠️  La pagina ha risposto con codice: {risposta.status_code}")
        
except Exception as errore:
    print(f"❌ ERRORE: {errore}")

print("")
print("===========================================")
print("Fine del test")
print("===========================================")
