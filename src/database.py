"""
Database SQLite per Liguria Sentinel
"""

import sqlite3
import os


class Database:
    
    def __init__(self, db_path='data/sentinel.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.inizializza()
    
    def inizializza(self):
        """Crea le tabelle se non esistono"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bandi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titolo TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                ente TEXT,
                tipo TEXT,
                data_scadenza TEXT,
                keywords_match TEXT,
                score INTEGER DEFAULT 0,
                stato TEXT DEFAULT 'attivo',
                data_trovato TEXT,
                data_aggiornamento TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aggiornamenti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bando_id INTEGER,
                tipo_aggiornamento TEXT,
                descrizione TEXT,
                data_aggiornamento TEXT,
                FOREIGN KEY (bando_id) REFERENCES bandi(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS controlli (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fonte TEXT,
                data_controllo TEXT,
                bandi_trovati INTEGER,
                bandi_nuovi INTEGER,
                esito TEXT,
                note TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdf_archivio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bando_id INTEGER,
                url_pdf TEXT,
                nome_file TEXT,
                data_download TEXT,
                versione INTEGER DEFAULT 1,
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
    
    def salva_bando(self, bando):
        """Salva un nuovo bando nel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO bandi (titolo, url, ente, tipo, data_scadenza, keywords_match, score, data_trovato)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bando.get('titolo'),
                bando.get('url'),
                bando.get('ente'),
                bando.get('tipo', 'bando'),
                bando.get('data_scadenza'),
                bando.get('keywords_match'),
                bando.get('score', 0),
                bando.get('data_trovato')
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def conta_bandi(self):
        """Conta i bandi nel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM bandi')
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_tutti_bandi(self):
        """Ritorna tutti i bandi nel database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bandi ORDER BY data_trovato DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
