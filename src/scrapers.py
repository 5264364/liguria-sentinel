"""
Scrapers per diverse fonti di bandi
Ogni scraper è una classe che implementa il metodo scrape()
"""

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
import time


class ScraperFILSE:
    """Scraper per FILSE - Versione DEFINITIVA con Selenium"""
    
    def __init__(self):
        self.nome = "FILSE"
        self.url_base = "https://www.filse.it"
        self.url_bandi = "https://www.filse.it/it/bandi-avvisi-gare/bandi-attivi/publiccompetitions/"
        self.url = self.url_bandi
    
    def scrape(self):
        """
        Scarica bandi da FILSE usando Selenium
        per gestire il caricamento JavaScript
        """
        bandi = []
        driver = None
        
        try:
            print(f"🔍 Scansione {self.nome} con Selenium...")
            
            # Configura Chrome in modalità headless
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Avvia il browser
            driver = webdriver.Chrome(options=chrome_options)
            
            # Vai alla pagina
            print(f"📡 Caricamento pagina...")
            driver.get(self.url_bandi)
            
            # Aspetta che la pagina carichi (fino a 10 secondi)
            time.sleep(5)
            
            # Ottieni l'HTML completo dopo che JS ha caricato tutto
            html = driver.page_source
            
            # Ora parsa l'HTML con BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Cerca i bandi - FILSE usa diverse strutture possibili
            articoli = (
                soup.find_all('div', class_='public-competition-item') or
                soup.find_all('article', class_='item') or
                soup.find_all('div', class_='item-list') or
                soup.find_all('div', class_=['competition-item', 'bando-item']) or
                soup.find_all('article') or
                soup.find_all('div', class_='item')
            )
            
            print(f"📄 Trovati {len(articoli)} elementi in {self.nome}")
            
            # Se non troviamo articoli, stampa l'HTML per debug
            if len(articoli) == 0:
                print("⚠️ Nessun articolo trovato. Debug HTML:")
                # Cerca tutti i div con classe che contiene "item"
                tutti_div = soup.find_all('div', class_=True)
                classi_trovate = set()
                for div in tutti_div[:20]:  # Prime 20 per non spammare
                    classi = div.get('class', [])
                    for c in classi:
                        if 'item' in c.lower() or 'bando' in c.lower() or 'competition' in c.lower():
                            classi_trovate.add(c)
                print(f"Classi rilevanti trovate: {classi_trovate}")
            
            for articolo in articoli:
                try:
                    # Cerca titolo
                    titolo_elem = (
                        articolo.find('h2') or 
                        articolo.find('h3') or 
                        articolo.find('h4') or
                        articolo.find('a', class_=['title', 'titolo'])
                    )
                    
                    if not titolo_elem:
                        continue
                    
                    titolo = titolo_elem.get_text(strip=True)
                    
                    # Cerca link
                    link_elem = articolo.find('a')
                    if not link_elem:
                        continue
                    
                    url = link_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = self.url_base + url
                    
                    # Estrai tutto il testo
                    testo = articolo.get_text(strip=True)
                    
                    if titolo and url and len(titolo) > 10:
                        bando = {
                            'titolo': titolo,
                            'url': url,
                            'ente': self.nome,
                            'testo': testo,
                            'tipo': 'bando',
                            'data_trovato': datetime.now().isoformat()
                        }
                        bandi.append(bando)
                        print(f"  ✓ {titolo[:60]}...")
                
                except Exception as e:
                    print(f"⚠️ Errore parsing elemento: {e}")
                    continue
            
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
            
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Chiudi sempre il browser
            if driver:
                driver.quit()
        
        return bandi


class ScraperALFA:
    """Scraper per ALFA Liguria"""
    
    def __init__(self):
        self.nome = "ALFA"
        self.url_base = "https://www.alfaliguria.it"
        self.url_bandi = "https://www.alfaliguria.it/"
    
    def scrape(self):
        """Placeholder - da implementare"""
        print(f"⏭️ {self.nome} - Non ancora implementato")
        return []


class ScraperRegione:
    """Scraper per Regione Liguria"""
    
    def __init__(self):
        self.nome = "Regione Liguria"
        self.url_base = "https://www.regione.liguria.it"
        self.url_bandi = "https://www.regione.liguria.it/homepage-bandi-e-avvisi"
    
    def scrape(self):
        """Placeholder - da implementare"""
        print(f"⏭️ {self.nome} - Non ancora implementato")
        return []
