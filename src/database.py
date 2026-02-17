import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_path='bandi.db'):
        self.db_path = db_path
        self.crea_tabelle()
    
    def crea_tabelle(self):
        """Crea tutte le tabelle del database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella principale bandi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bandi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titolo TEXT NOT NULL,
                ente TEXT NOT NULL,
                url TEXT NOT NULL,
                tipo TEXT,
                data_pubblicazione DATE,
                data_scadenza DATE,
                dgr_riferimento TEXT,
                hash_pagina TEXT,
                pdf_scaricati TEXT,
                keywords_match TEXT,
                score INTEGER DEFAULT 0,
                stato TEXT DEFAULT 'nuovo',
                ultimo_check DATETIME,
                note TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella aggiornamenti
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aggiornamenti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bando_id INTEGER,
                data_aggiornamento DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo TEXT,
                descrizione TEXT,
                url TEXT,
                FOREIGN KEY (bando_id) REFERENCES bandi(id)
            )
        ''')
        
        # Tabella controlli
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS controlli (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT NOT NULL,
                url TEXT NOT NULL,
                ultimo_controllo DATETIME DEFAULT CURRENT_TIMESTAMP,
                esito TEXT,
                errore_dettaglio TEXT,
                hash_attuale TEXT
            )
        ''')
        
        # Tabella PDF archivio
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdf_archivio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bando_id INTEGER,
                nome_file TEXT NOT NULL,
                percorso TEXT NOT NULL,
                hash_file TEXT,
                data_download DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bando_id) REFERENCES bandi(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database completo inizializzato (4 tabelle)")
    
    def bando_esiste(self, url):
    """Controlla se un bando esiste già nel database tramite URL"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM bandi WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
    
    def aggiungi_bando(self, titolo, url, ente, tipo=None, keywords=None):
        """Aggiunge un nuovo bando"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calcola hash della pagina
            hash_pagina = hashlib.md5(f"{titolo}{url}".encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO bandi (
                    titolo, url, ente, tipo, hash_pagina, 
                    keywords_match, stato, ultimo_check
                )
                VALUES (?, ?, ?, ?, ?, ?, 'nuovo', ?)
            ''', (titolo, url, ente, tipo, hash_pagina, keywords, datetime.now()))
            
            conn.commit()
            bando_id = cursor.lastrowid
            conn.close()
            
            print(f"✅ Bando salvato: {titolo}")
            return bando_id
            
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Errore salvataggio: {e}")
            return None
    
    def registra_controllo(self, sito, url, esito, hash_pagina=None, errore=None):
        """Registra un controllo effettuato"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO controlli (
                sito, url, esito, hash_attuale, errore_dettaglio
            )
            VALUES (?, ?, ?, ?, ?)
        ''', (sito, url, esito, hash_pagina, errore))
        
        conn.commit()
        conn.close()
    
    def conta_bandi(self):
        """Conta quanti bandi ci sono"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM bandi')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def statistiche(self):
        """Ritorna statistiche del database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conta bandi per ente
        cursor.execute('''
            SELECT ente, COUNT(*) 
            FROM bandi 
            GROUP BY ente
        ''')
        per_ente = cursor.fetchall()
        
        # Conta controlli
        cursor.execute('SELECT COUNT(*) FROM controlli')
        tot_controlli = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'per_ente': per_ente,
            'tot_controlli': tot_controlli

       def get_tutti_bandi(self):
    """Ritorna tutti i bandi nel database"""
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bandi ORDER BY data_trovato DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]     
        }
