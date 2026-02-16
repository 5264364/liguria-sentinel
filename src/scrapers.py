"""
Scrapers per diverse fonti di bandi
Ogni scraper è una classe che implementa il metodo scrape()
"""

import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
import re


class ScraperFILSEPrivati:
    """Scraper per FILSE Bandi Online - Privati"""
    
    def __init__(self):
        self.nome = "FILSE Privati"
        self.url_base = "https://bandifilse.regione.liguria.it"
        self.url_bandi = "https://bandifilse.regione.liguria.it/"
    
    def scrape(self):
        """Scarica bandi per privati da FILSE"""
        bandi = []
        
        try:
            print(f"🔍 Scansione {self.nome}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.url_bandi, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca tutti gli elementi che contengono bandi
            # La pagina ha liste puntate e paragrafi con nomi di bandi
            testo_completo = soup.get_text()
            
            # Lista bandi trovati nel testo
            bandi_noti = [
                "Nidi Gratis",
                "Specializzarsi per competere",
                "attività sportive",
                "bonus badanti",
                "baby sitter",
                "Swim and go",
                "Progetto di Vita",
                "Voucher Centri Estivi",
                "Fondo di garanzia",
                "Dote Sport"
            ]
            
            # Cerca liste <li> o <p> che contengono i nomi dei bandi
            elementi = soup.find_all(['li', 'p', 'div'])
            
            for elem in elementi:
                testo = elem.get_text(strip=True)
                
                # Se il testo contiene uno dei bandi noti
                for bando_nome in bandi_noti:
                    if bando_nome.lower() in testo.lower() and len(testo) > 15:
                        # Cerca un link associato
                        link = elem.find('a')
                        url = self.url_bandi  # Default alla home se non c'è link specifico
                        
                        if link:
                            href = link.get('href', '')
                            if href.startswith('http'):
                                url = href
                            elif href:
                                url = self.url_base + href
                        
                        # Usa il testo come titolo
                        titolo = testo[:200] if len(testo) <= 200 else testo[:200] + "..."
                        
                        bando = {
                            'titolo': titolo,
                            'url': url,
                            'ente': self.nome,
                            'testo': testo,
                            'tipo': 'bando',
                            'data_trovato': datetime.now().isoformat()
                        }
                        
                        # Evita duplicati nella stessa scansione
                        if not any(b['titolo'] == titolo for b in bandi):
                            bandi.append(bando)
                            print(f"  ✓ {titolo[:60]}...")
                        break
            
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
            
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
            import traceback
            traceback.print_exc()
        
        return bandi


class ScraperFILSEImprese:
    """Scraper per FILSE Bandi Online - Imprese ed Enti"""
    
    def __init__(self):
        self.nome = "FILSE Imprese"
        self.url_base = "https://filseonline.regione.liguria.it"
        self.url_bandi = "https://filseonline.regione.liguria.it/FilseWeb/Home.do"
    
    def scrape(self):
        """Scarica bandi per imprese da FILSE"""
        bandi = []
        
        try:
            print(f"🔍 Scansione {self.nome}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.url_bandi, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca la sezione "Bandi attivi"
            testo_completo = soup.get_text()
            
            # Ogni bando è in grassetto seguito da date
            # Cerchiamo tutti gli elementi in grassetto <strong> o <b>
            elementi_bold = soup.find_all(['strong', 'b'])
            
            for elem in elementi_bold:
                titolo = elem.get_text(strip=True)
                
                # Filtra solo titoli lunghi (probabilmente bandi)
                if len(titolo) < 30:
                    continue
                
                # Cerca date nel testo successivo
                parent = elem.parent
                if parent:
                    testo_parent = parent.get_text(strip=True)
                    
                    # Cerca pattern "dal XX-XX-XXXX al XX-XX-XXXX"
                    match_date = re.search(r'dal\s+(\d{2}-\d{2}-\d{4})\s+al\s+(\d{2}-\d{2}-\d{4})', testo_parent)
                    
                    if match_date:
                        data_inizio = match_date.group(1)
                        data_fine = match_date.group(2)
                        
                        bando = {
                            'titolo': titolo,
                            'url': self.url_bandi,
                            'ente': self.nome,
                            'testo': f"Domande dal {data_inizio} al {data_fine}. {testo_parent[:300]}",
                            'tipo': 'bando',
                            'data_scadenza': data_fine,
                            'data_trovato': datetime.now().isoformat()
                        }
                        
                        bandi.append(bando)
                        print(f"  ✓ {titolo[:60]}... (scade {data_fine})")
            
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
            
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
            import traceback
            traceback.print_exc()
        
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
