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
    """Scraper per FILSE - Versione DEBUG"""
    
    def __init__(self):
        self.nome = "FILSE"
        self.url_base = "https://www.filse.it"
        self.url_bandi = "https://www.filse.it/it/bandi-avvisi-gare/bandi-attivi/publiccompetitions/"
        self.url = self.url_bandi
    
    def scrape(self):
        """Scarica bandi da FILSE usando Selenium"""
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
            
            # Aspetta MOLTO di più - 15 secondi
            print("⏳ Attendo 15 secondi per caricamento JavaScript...")
            time.sleep(15)
            
            # Scroll in fondo per triggerare lazy loading
            print("📜 Scroll della pagina...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Ottieni l'HTML completo
            html = driver.page_source
            
            # SALVA HTML per debug
            print("💾 Salvo HTML completo per debug...")
            with open('/tmp/filse_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"📄 HTML salvato ({len(html)} caratteri)")
            
            # Parsa con BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # MEGA DEBUG - Stampa TUTTE le classi presenti
            print("\n🔍 DEBUG - Prime 50 classi CSS trovate nella pagina:")
            tutti_elementi = soup.find_all(True, class_=True)  # Tutti gli elementi con classe
            classi_uniche = set()
            for elem in tutti_elementi[:200]:
                classi = elem.get('class', [])
                for c in classi:
                    classi_uniche.add(c)
            
            for i, classe in enumerate(sorted(classi_uniche)[:50]):
                print(f"  {i+1}. {classe}")
            
            print(f"\n📊 Totale classi uniche trovate: {len(classi_uniche)}")
            
            # Cerca TUTTI gli <a> (link)
            tutti_link = soup.find_all('a', href=True)
            print(f"\n🔗 Trovati {len(tutti_link)} link nella pagina")
            
            # Mostra i primi 10 link
            print("\n🔗 Primi 10 link:")
            for i, link in enumerate(tutti_link[:10]):
                href = link.get('href', '')
                testo = link.get_text(strip=True)[:60]
                print(f"  {i+1}. {testo} → {href[:80]}")
            
            # Cerca pattern comuni per bandi
            print("\n🎯 Cerco pattern comuni...")
            
            # Pattern 1: Qualsiasi div o article con testo lungo
            elementi_grandi = soup.find_all(['div', 'article'], recursive=True)
            candidati = []
            for elem in elementi_grandi:
                testo = elem.get_text(strip=True)
                # Se ha più di 50 caratteri e contiene un link, potrebbe essere un bando
                if len(testo) > 50 and elem.find('a'):
                    candidati.append(elem)
            
            print(f"📦 Trovati {len(candidati)} elementi candidati (con testo > 50 char e link)")
            
            # Processa i candidati
            for i, elem in enumerate(candidati[:10]):  # Max 10 per debug
                try:
                    link = elem.find('a')
                    if not link:
                        continue
                    
                    titolo = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    if not url or len(titolo) < 10:
                        continue
                    
                    if not url.startswith('http'):
                        url = self.url_base + url
                    
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
                    print(f"  ✓ Candidato {i+1}: {titolo[:60]}...")
                
                except Exception as e:
                    continue
            
            print(f"\n✅ {self.nome}: {len(bandi)} bandi estratti")
            
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
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
