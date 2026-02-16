import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

class ScraperFILSE:
    """Scraper per FILSE"""
    
    def __init__(self):
        self.nome = "FILSE"
        self.url_base = "https://www.filse.it"
        self.url_bandi = "https://www.filse.it/it/bandi-avvisi-gare/bandi-attivi/"
        self.url = self.url_bandi
    
    def scrape(self):
        """
        Scarica e parse la pagina bandi FILSE
        
        Returns:
            list: Lista di dizionari con i bandi trovati
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
            
            # FILSE ha una struttura con articoli
            articoli = soup.find_all('article', class_='item-list')
            
            if not articoli:
                # Prova struttura alternativa
                articoli = soup.find_all('div', class_='view-content')
            
            print(f"📄 Trovati {len(articoli)} elementi in {self.nome}")
            
            for articolo in articoli[:10]:  # Max 10 per test
                try:
                    # Estrai titolo
                    titolo_elem = articolo.find('h2') or articolo.find('h3') or articolo.find('a')
                    if not titolo_elem:
                        continue
                    
                    titolo = titolo_elem.get_text(strip=True)
                    
                    # Estrai link
                    link_elem = articolo.find('a')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = self.url_base + url
                    
                    # Estrai testo descrittivo
                    testo = articolo.get_text(strip=True)
                    
                    if titolo and url:
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
                    print(f"⚠️ Errore parsing elemento: {e}")
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
