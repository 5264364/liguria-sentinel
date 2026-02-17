"""
Scrapers per diverse fonti di bandi
Ogni scraper è una classe che implementa il metodo scrape()
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class ScraperFILSEPrivati:
    """Scraper per FILSE Bandi Online - Privati"""
    
    def __init__(self):
        self.nome = "FILSE Privati"
        self.url_base = "https://bandifilse.regione.liguria.it"
        self.url_bandi = "https://bandifilse.regione.liguria.it/"
    
    def scrape(self):
        bandi = []
        url_visti = set()
        
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
            
            # Cerca SOLO gli elementi <li> che contengono i bandi
            elementi_li = soup.find_all('li')
            
            for elem in elementi_li:
                testo = elem.get_text(strip=True)
                
                # Salta elementi troppo corti o troppo lunghi
                if len(testo) < 10 or len(testo) > 500:
                    continue
                
                # Pulisci il titolo (rimuovi testo dei link tipo "Clicca qui per...")
                titolo = re.sub(r'Clicca qui per.*', '', testo).strip()
                titolo = re.sub(r'\s+', ' ', titolo).strip()
                
                if len(titolo) < 10:
                    continue
                
                # Usa URL univoco per evitare duplicati
                # Crea un ID univoco basato sul titolo
                url_univoco = self.url_bandi + "#" + titolo[:50].replace(' ', '-').lower()
                
                if url_univoco in url_visti:
                    continue
                url_visti.add(url_univoco)
                
                bando = {
                    'titolo': titolo,
                    'url': url_univoco,
                    'ente': self.nome,
                    'testo': testo,
                    'tipo': 'bando',
                    'data_trovato': datetime.now().isoformat()
                }
                
                bandi.append(bando)
                print(f"  ✓ {titolo[:70]}...")
            
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
        bandi = []
        
        try:
            print(f"🔍 Scansione {self.nome}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'it-IT,it;q=0.9',
            }
            
            response = requests.get(self.url_bandi, headers=headers, timeout=15)
            response.encoding = 'ISO-8859-1'  # La pagina usa encoding vecchio
            
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # La pagina ha bandi in <strong> con testo lungo
            # Seguiti da righe con "dal XX-XX-XXXX al XX-XX-XXXX"
            testo_pagina = soup.get_text(separator='\n')
            
            # Dividi per righe
            righe = [r.strip() for r in testo_pagina.split('\n') if r.strip()]
            
            i = 0
            while i < len(righe):
                riga = righe[i]
                
                # Cerca righe lunghe che sembrano titoli di bandi (> 30 char)
                # e che sono seguite da una riga con date
                if len(riga) > 30 and i + 1 < len(righe):
                    prossima = righe[i + 1] if i + 1 < len(righe) else ''
                    dopo = righe[i + 2] if i + 2 < len(righe) else ''
                    
                    # Controlla se le prossime righe contengono date
                    testo_vicino = prossima + ' ' + dopo
                    match_date = re.search(
                        r'dal\s+(\d{2}-\d{2}-\d{4})\s*al\s+(\d{2}-\d{2}-\d{4})',
                        testo_vicino,
                        re.IGNORECASE
                    )
                    
                    if match_date:
                        data_inizio = match_date.group(1)
                        data_fine = match_date.group(2)
                        
                        # Crea URL univoco basato sul titolo
                        url_univoco = self.url_bandi + "#" + riga[:50].replace(' ', '-').lower()
                        
                        bando = {
                            'titolo': riga,
                            'url': url_univoco,
                            'ente': self.nome,
                            'testo': f"Domande dal {data_inizio} al {data_fine}. {riga}",
                            'tipo': 'bando',
                            'data_scadenza': data_fine,
                            'data_trovato': datetime.now().isoformat()
                        }
                        
                        bandi.append(bando)
                        print(f"  ✓ {riga[:60]}... (scade {data_fine})")
                        i += 3  # Salta le righe delle date
                        continue
                
                i += 1
            
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
        print(f"⏭️ {self.nome} - Non ancora implementato")
        return []


class ScraperRegione:
    """Scraper per Regione Liguria"""
    
    def __init__(self):
        self.nome = "Regione Liguria"
        self.url_base = "https://www.regione.liguria.it"
        self.url_bandi = "https://www.regione.liguria.it/homepage-bandi-e-avvisi"
    
    def scrape(self):
        print(f"⏭️ {self.nome} - Non ancora implementato")
        return []
