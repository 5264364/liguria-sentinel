import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright
import time

class ScraperFILSE:
    """Scraper per FILSE - Versione DEFINITIVA con Playwright"""
    
    def __init__(self):
        self.nome = "FILSE"
        self.url_base = "https://www.filse.it"
        self.url_bandi = "https://www.filse.it/it/bandi-avvisi-gare/bandi-attivi/publiccompetitions/"
        self.url = self.url_bandi
    
    def scrape(self):
        """
        Scarica bandi da FILSE usando Playwright
        per gestire il caricamento JavaScript
        """
        bandi = []
        
        try:
            print(f"🔍 Scansione {self.nome} con Playwright...")
            
            with sync_playwright() as p:
                # Avvia browser headless
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Vai alla pagina
                print(f"📡 Caricamento pagina...")
                page.goto(self.url_bandi, wait_until='networkidle', timeout=30000)
                
                # Aspetta che i bandi si carichino
                time.sleep(3)
                
                # Ottieni l'HTML completo dopo che JS ha caricato tutto
                html = page.content()
                browser.close()
            
            # Ora parsa l'HTML con BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Cerca i bandi - FILSE usa una struttura specifica
            # Proviamo diversi selettori
            articoli = (
                soup.find_all('div', class_='public-competition-item') or
                soup.find_all('article', class_='item') or
                soup.find_all('div', class_='item-list') or
                soup.find_all('div', class_=['competition-item', 'bando-item'])
            )
            
            print(f"📄 Trovati {len(articoli)} elementi in {self.nome}")
            
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
