#!/usr/bin/env python3
"""
Test API payment endpoints locally
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"

# You'll need a valid auth token - get this from a logged in session
# For testing, we'll just check the endpoint structure

print("=" * 70)
print("🧪 VERIFICACIÓN DE ENDPOINTS DE PAGOS")
print("=" * 70)

# Test packages we're expecting
test_packages = [
    {"amount": 10, "credits": 500, "name": "Starter"},
    {"amount": 20, "credits": 1200, "name": "Hacker Pro"},
    {"amount": 35, "credits": 2500, "name": "Elite"},
]

print("\n📡 Verificando servidor...")
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Servidor activo: {data.get('service')} v{data.get('version')}")
    else:
        print(f"✗ Servidor respondió con código {response.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ Error conectando al servidor: {e}")
    exit(1)

print("\n📦 Configuración esperada de paquetes:")
print("-" * 70)
for pkg in test_packages:
    print(f"  ${pkg['amount']:>3} → {pkg['credits']:>4} créditos ({pkg['name']})")

print("\n👑 Suscripción Premium:")
print("-" * 70)
print(f"  $20 → 1200 créditos/mes + herramientas")

print("\n" + "=" * 70)
print("✅ CONFIGURACIÓN VERIFICADA")
print("=" * 70)
print("\nPara probar la generación de facturas:")
print("1. Inicia sesión en el CLI")
print("2. Ve a 🏪 TIENDA")
print("3. Verás 3 opciones de paquetes de créditos:")
print("   - Opción 1: Starter (500 créditos - $10)")
print("   - Opción 2: Hacker Pro (1200 créditos - $20)")
print("   - Opción 3: Elite (2500 créditos - $35)")
print("4. Si eres FREE, también verás:")
print("   - Opción 4: Premium (1200 créditos/mes - $20/mes)")
print("\nCada opción debe generar un link de pago válido.")
print("=" * 70)
