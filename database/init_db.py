import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Получить путь к файлу БД"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'invoice_generator.db')

def init_database():
    """Инициализировать базу данных"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Таблица заказчиков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            inn TEXT,
            account TEXT,
            bik TEXT,
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица документов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT NOT NULL,
            number TEXT NOT NULL,
            date DATE NOT NULL,
            client_id INTEGER,
            route TEXT,
            start_date DATE,
            end_date DATE,
            amount REAL,
            nds_rate REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Получить подключение к БД"""
    db_path = get_db_path()
    return sqlite3.connect(db_path)

def add_client(name, inn, account, bik, address):
    """Добавить заказчика"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clients (name, inn, account, bik, address)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, inn, account, bik, address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_clients():
    """Получить всех заказчиков"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, inn, account, bik, address FROM clients ORDER BY name')
    clients = cursor.fetchall()
    conn.close()
    return clients

def get_client_by_id(client_id):
    """Получить заказчика по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, inn, account, bik, address FROM clients WHERE id = ?', (client_id,))
    client = cursor.fetchone()
    conn.close()
    return client

def delete_client(client_id):
    """Удалить заказчика"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

def save_document(doc_type, number, date, client_id, route, start_date, end_date, amount, nds_rate):
    """Сохранить документ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (doc_type, number, date, client_id, route, start_date, end_date, amount, nds_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (doc_type, number, date, client_id, route, start_date, end_date, amount, nds_rate))
    conn.commit()
    conn.close()

def get_all_documents():
    """Получить все документы"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, d.doc_type, d.number, d.date, c.name, d.amount, d.created_at
        FROM documents d
        LEFT JOIN clients c ON d.client_id = c.id
        ORDER BY d.created_at DESC
    ''')
    documents = cursor.fetchall()
    conn.close()
    return documents
