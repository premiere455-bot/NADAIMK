import requests
import time
import random
import string
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Manus AI Account Creator API")

# Adicionar suporte a CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAIL_TM_API = "https://api.mail.tm"

class AccountResponse(BaseModel):
    email: str
    password: str
    token: str
    account_id: str

class VerificationResponse(BaseModel):
    code: Optional[str]
    subject: Optional[str]
    from_address: Optional[str]

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_mail_tm_account():
    username = f"manus_{generate_random_string(8)}"
    password = generate_random_string(12)
    
    # Get domain
    domains = requests.get(f"{MAIL_TM_API}/domains").json()
    if not domains.get('hydra:member'):
        raise Exception("No domains available from Mail.tm")
    domain = domains['hydra:member'][0]['domain']
    
    email = f"{username}@{domain}"
    
    # Create account
    payload = {
        "address": email,
        "password": password
    }
    response = requests.post(f"{MAIL_TM_API}/accounts", json=payload)
    if response.status_code != 201:
        raise Exception(f"Failed to create email account: {response.text}")
    
    account_data = response.json()
    
    # Get Token
    token_payload = {"address": email, "password": password}
    token_response = requests.post(f"{MAIL_TM_API}/token", json=token_payload)
    token = token_response.json().get('token')
    
    return {
        "email": email,
        "password": password,
        "token": token,
        "account_id": account_data.get('id')
    }

@app.post("/create-temp-email", response_model=AccountResponse)
async def create_email():
    """Cria um novo e-mail temporário no Mail.tm"""
    try:
        account = create_mail_tm_account()
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check-verification-code/{token}")
async def check_code(token: str):
    """Verifica a caixa de entrada em busca do código da Manus AI"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # List messages
        messages_response = requests.get(f"{MAIL_TM_API}/messages", headers=headers)
        messages = messages_response.json().get('hydra:member', [])
        
        if not messages:
            return {"status": "waiting", "message": "Nenhum e-mail recebido ainda."}
        
        # Get latest message
        latest_msg = messages[0]
        msg_id = latest_msg['id']
        
        # Get message content
        msg_detail = requests.get(f"{MAIL_TM_API}/messages/{msg_id}", headers=headers).json()
        content = msg_detail.get('text', '') or msg_detail.get('intro', '')
        
        # Extract 6-digit code (common for verification)
        import re
        code_match = re.search(r'\b\d{6}\b', content)
        code = code_match.group(0) if code_match else None
        
        return {
            "status": "received",
            "from": latest_msg.get('from', {}).get('address'),
            "subject": latest_msg.get('subject'),
            "code": code,
            "full_content": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "Manus AI Account Automation API",
        "instructions": "1. Use /create-temp-email para obter um e-mail. 2. Use esse e-mail no link de convite. 3. Use /check-verification-code/{token} para pegar o código."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
