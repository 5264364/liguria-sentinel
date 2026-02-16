import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

class ScraperFILSE:
    """Scraper per FILSE - Usa API alternativa"""
    
    def __init__(self):
        self.nome = "FILSE"
        self.url_base = "https://www.filse.it"
        # Usiamo la pagina aggiornamenti che è HTML statico
        self.url_bandi = "https://www.filse.it/it/bandi-avvisi-gare/aggiornamenti.html"
        self.url = self.url_bandi
    
    def scrape(self):
        """
        Scarica bandi da FILSE aggiornamenti
        (pagina più semplice senza JS)
        """
        bandi = []
        
        try:
            print(f"🔍 Scansione {self.nome}...")
            
            headers = {
                'User-Agent': 'LiguriaSentinel/1.0'
            }
            
            response = requests.get(self.url_bandi, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca tutti i link e titoli nella pagina aggiornamenti
            contenuto = soup.find('div', class_='item-page') or soup.find('main') or soup.find('article')
            
            if not contenuto:
                print(f"⚠️ {self.nome} - Struttura pagina non trovata")
                return []
            
            # Trova tutti i paragrafi e link
            elementi = contenuto.find_all(['p', 'div', 'h2', 'h3', 'h4'])
            
            print(f"📄 Trovati {len(elementi)} elementi in {self.nome}")
            
            for elem in elementi:
                try:
                    # Cerca link dentro l'elemento
                    link = elem.find('a')
                    if not link:
                        continue
                    
                    titolo = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    if not titolo or len(titolo) < 10:
                        continue
                    
                    if url and not url.startswith('http'):
                        url = self.url_base + url
                    
                    # Filtra solo cose che sembrano bandi
                    parole_chiave = ['bando', 'avviso', 'contributo', 'finanziamento', 'voucher', 'fondo']
                    if any(parola in titolo.lower() for parola in parole_chiave):
                        
                        # Estrai testo intorno
                        testo = elem.get_text(strip=True)
                        
                        bando = {
                            'titolo': titolo,
                            'url': url,
                            'ente': self.nome,
                            'testo': testo,
                            'tipo': 'bando',
                            'data_trovato': datetime.now().isoformat()
                        }
                        bandi.append(bando)
                
                except Exception as e:
                    continue
            
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
            
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
        
        return bandi


class ScraperALFA:
    """Scraper per ALFA - Da implementare"""
    
    def __init__(self):
        self.nome = "ALFA"
        self.url = "https://www.alfaliguria.it/"
    
    def scrape(self):
        """TODO: Implementare dopo test FILSE"""
        print(f"⏭️ {self.nome} - Da implementare")
        return []


class ScraperRegione:
    """Scraper per Regione Liguria - Da implementare"""
    
    def __init__(self):
        self.nome = "Regione Liguria"
        self.url = "https://www.regione.liguria.it/homepage-bandi-e-avvisi"
    
    def scrape(self):
        """TODO: Implementare dopo test FILSE"""
        print(f"⏭️ {self.nome} - Da implementare")
        return []


def get_all_scrapers():
    """Ritorna lista di tutti gli scraper attivi"""
    return [
        ScraperFILSE(),
        # ScraperALFA(),  # Commentato, da attivare dopo
        # ScraperRegione(),  # Commentato, da attivare dopo
    ]
