"""
Scrapers per diverse fonti di bandi
"""

import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ScraperFILSEPrivati:

    def __init__(self):
        self.nome = "FILSE Privati"
        self.url_base = "https://bandifilse.regione.liguria.it"
        self.url_bandi = "https://bandifilse.regione.liguria.it/"

    def scrape(self):
        bandi = []
        url_visti = set()
        try:
            print(f"🔍 Scansione {self.nome}...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url_bandi, headers=headers, timeout=15, verify=False)
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            for elem in soup.find_all('li'):
                testo = elem.get_text(strip=True)
                if len(testo) < 10 or len(testo) > 500:
                    continue
                titolo = re.sub(r'Clicca qui per.*', '', testo).strip()
                titolo = re.sub(r'\s+', ' ', titolo).strip()
                if len(titolo) < 10:
                    continue
                url_univoco = self.url_bandi + "#" + re.sub(r'[^a-z0-9]', '-', titolo[:50].lower())
                if url_univoco in url_visti:
                    continue
                url_visti.add(url_univoco)
                bandi.append({
                    'titolo': titolo,
                    'url': url_univoco,
                    'ente': self.nome,
                    'testo': testo,
                    'tipo': 'bando',
                    'data_trovato': datetime.now().isoformat()
                })
                print(f"  ✓ {titolo[:70]}...")
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
        return bandi


class ScraperFILSEImprese:

    def __init__(self):
        self.nome = "FILSE Imprese"
        self.url_base = "https://filseonline.regione.liguria.it"
        self.url_bandi = "https://filseonline.regione.liguria.it/FilseWeb/Home.do"

    def scrape(self):
        bandi = []
        try:
            print(f"🔍 Scansione {self.nome}...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url_bandi, headers=headers, timeout=15, verify=False)
            response.encoding = 'ISO-8859-1'
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            righe = [r.strip() for r in soup.get_text(separator='\n').split('\n') if r.strip()]
            i = 0
            while i < len(righe):
                riga = righe[i]
                if len(riga) > 30 and i + 1 < len(righe):
                    testo_vicino = (righe[i+1] if i+1 < len(righe) else '') + ' ' + (righe[i+2] if i+2 < len(righe) else '')
                    match_date = re.search(r'dal\s+(\d{2}-\d{2}-\d{4})\s*al\s+(\d{2}-\d{2}-\d{4})', testo_vicino, re.IGNORECASE)
                    if match_date:
                        data_fine = match_date.group(2)
                        url_univoco = self.url_bandi + "#" + re.sub(r'[^a-z0-9]', '-', riga[:50].lower())
                        bandi.append({
                            'titolo': riga,
                            'url': url_univoco,
                            'ente': self.nome,
                            'testo': f"Domande dal {match_date.group(1)} al {data_fine}. {riga}",
                            'tipo': 'bando',
                            'data_scadenza': data_fine,
                            'data_trovato': datetime.now().isoformat()
                        })
                        print(f"  ✓ {riga[:60]}... (scade {data_fine})")
                        i += 3
                        continue
                i += 1
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
        return bandi


class ScraperRegione:

    def __init__(self):
        self.nome = "Regione Liguria"
        self.url_base = "https://www.regione.liguria.it"
        self.url_bandi = "https://www.regione.liguria.it/homepage-bandi-e-avvisi/publiccompetitions/"

    def scrape(self):
        bandi = []
        try:
            print(f"🔍 Scansione {self.nome}...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url_bandi, headers=headers, timeout=15, verify=False)
            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            link_bandi = soup.find_all('a', href=re.compile(r'/publiccompetition/\d+:'))
            print(f"📄 Trovati {len(link_bandi)} link in {self.nome}")
            for link in link_bandi:
                try:
                    titolo = link.get_text(strip=True)
                    href = link.get('href', '')
                    if not titolo or len(titolo) < 10:
                        continue
                    url = self.url_base + href if not href.startswith('http') else href
                    testo = link.parent.get_text(strip=True) if link.parent else titolo
                    match_data = re.search(r'(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})', testo, re.IGNORECASE)
                    bandi.append({
                        'titolo': titolo,
                        'url': url,
                        'ente': self.nome,
                        'testo': testo,
                        'tipo': 'bando',
                        'data_scadenza': match_data.group(0) if match_data else None,
                        'data_trovato': datetime.now().isoformat()
                    })
                    print(f"  ✓ {titolo[:70]}...")
                except Exception:
                    continue
            print(f"✅ {self.nome}: {len(bandi)} bandi estratti")
        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
        return bandi


class ScraperALFA:

    def __init__(self):
        self.nome = "ALFA Liguria"
        self.url_base = "https://www.alfaliguria.it"
        self.url_bandi = "https://www.alfaliguria.it/index.php/avvisi-attivi-fse-e-altri-fondi"

    def scrape(self):
        bandi = []
        try:
            print(f"🔍 Scansione {self.nome}...")
            import certifi
            import ssl
            import socket

            # Test connessione diretta
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'it-IT,it;q=0.9',
            }

            session = requests.Session()
            session.verify = certifi.where()

            response = session.get(self.url_bandi, headers=headers, timeout=20)

            if response.status_code != 200:
                print(f"⚠️ {self.nome} - Status: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            link_bandi = soup.find_all('a', href=re.compile(r'/index\.php/avvisi-attivi-fse-e-altri-fondi/\d+'))
            print(f"📄 Trovati {len(link_bandi)} link in {self.nome}")

            for link in link_bandi:
                try:
                    titolo = link.get_text(strip=True)
                    href = link.get('href', '')
                    if not titolo or len(titolo) < 10:
                        continue
                    if titolo.lower() in ['avvisi attivi fse e altri fondi', 'vai alla pagina dedicata']:
                        continue
                    url = self.url_base + href if not href.startswith('http') else href
                    testo = link.parent.get_text(strip=True) if link.parent else titolo
                    match_data = re.search(r'(\d{1,2})[/\.](\d{1,2})[/\.](\d{4})', testo)
                    bandi.append({
                        'titolo': titolo,
                        'url': url,
                        'ente': self.nome,
                        'testo': testo,
                        'tipo': 'avviso FSE',
                        'data_scadenza': match_data.group(0) if match_data else None,
                        'data_trovato': datetime.now().isoformat()
                    })
                    print(f"  ✓ {titolo[:70]}...")
                except Exception:
                    continue

            print(f"✅ {self.nome}: {len(bandi)} avvisi estratti")

        except Exception as e:
            print(f"❌ Errore {self.nome}: {e}")
        return bandi
