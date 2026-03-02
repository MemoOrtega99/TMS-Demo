import asyncio
import httpx
from datetime import datetime
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config import settings

async def main():
    print(f"Key activa: {settings.OPENROUTER_API_KEY[:10]}...")
    
    messages = [
        {"role": "system", "content": "Eres un asistente de demo. Di hola."},
        {"role": "user", "content": "Hola."}
    ]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Enviando petición a OpenRouter...")
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:3002",
                    "X-Title": "Soluciones-TMS",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": messages,
                    "max_tokens": 1500,
                },
            )

            print(f"Status HTTP: {response.status_code}")
            if response.status_code != 200:
                print("Error Response:")
                print(response.text)
            else:
                data = response.json()
                print("Exito:")
                print(data["choices"][0]["message"]["content"])
                
    except Exception as e:
        print("Exception:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
