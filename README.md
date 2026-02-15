# Manus AI Account Creator API

Esta API automatiza a criação de e-mails temporários e a captura de códigos de verificação para facilitar o registro no link de convite da Manus AI.

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn
- Requests

## Como Executar

1. Instale as dependências:
   ```bash
   pip install fastapi uvicorn requests
   ```

2. Inicie a API:
   ```bash
   python main.py
   ```

A API estará disponível em `http://localhost:8000`.

## Endpoints

### 1. Criar E-mail Temporário
**POST** `/create-temp-email`

Retorna um novo endereço de e-mail, senha e um token de acesso.

### 2. Verificar Código de Verificação
**GET** `/check-verification-code/{token}`

Verifica a caixa de entrada do e-mail associado ao token e extrai automaticamente o código de 6 dígitos enviado pela Manus AI.

## Fluxo de Uso Sugerido

1. Chame `/create-temp-email` para obter um e-mail.
2. Acesse o link de convite da Manus AI e insira o e-mail gerado.
3. Resolva o desafio do Cloudflare (necessário manualmente ou via automação de navegador).
4. Chame `/check-verification-code/{token}` repetidamente até receber o código.
5. Insira o código no site da Manus AI para concluir o registro.

---
*Nota: Esta API utiliza o serviço Mail.tm para e-mails temporários.*
