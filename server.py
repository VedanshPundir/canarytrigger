# server.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests  # Only needed if using geolocation
from colorama import Fore, Style  # For colored output
app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('canary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tokens
                 (id TEXT PRIMARY KEY, creator TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS triggers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  token_id TEXT, ip TEXT, user_agent TEXT,
                  timestamp TEXT, FOREIGN KEY(token_id) REFERENCES tokens(id))''')
    conn.commit()
    conn.close()

# Email alert function
def send_alert(token_id, ip, user_agent):
    try:
        # Get creator email from database
        conn = sqlite3.connect('canary.db')
        c = conn.cursor()
        c.execute("SELECT creator FROM tokens WHERE id = ?", (token_id,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            print(f"{Fore.RED}[!] No creator found for token {token_id}{Style.RESET_ALL}")
            return False
            
        recipient_email = result[0]
        
        # Email configuration
        SMTP_USER = "pundirved09@gmail.com"
        SMTP_PASSWORD = "nzpklxrlxnguhsmz"
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        
        msg = MIMEMultipart()
        msg['Subject'] = f'Canary Token Trigger: {token_id[:8]}...'
        msg['From'] = SMTP_USER
        msg['To'] = recipient_email
        
        body = f"""Canary Token Triggered!

Details:
- Token ID: {token_id}
- IP Address: {ip}
- User Agent: {user_agent}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            
        print(f"{Fore.GREEN}[+] Alert sent to {recipient_email}{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}[!] Email error: {str(e)}{Style.RESET_ALL}")
        return False
@app.route('/register', methods=['POST'])
def register_token():
    data = request.json
    token_id = data.get('token_id')
    creator = data.get('creator')
    
    conn = sqlite3.connect('canary.db')
    c = conn.cursor()
    c.execute("INSERT INTO tokens VALUES (?, ?, ?)", 
              (token_id, creator, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "token_id": token_id})

@app.route('/trigger/<token_id>', methods=['GET'])
def token_triggered(token_id):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    conn = sqlite3.connect('canary.db')
    c = conn.cursor()
    c.execute("INSERT INTO triggers (token_id, ip, user_agent, timestamp) VALUES (?, ?, ?, ?)",
              (token_id, ip, user_agent, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    # Send alert
    send_alert(token_id, ip, user_agent)
    
    # Return a benign image
    return app.send_static_file('pixel.png')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
