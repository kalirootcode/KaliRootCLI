#!/usr/bin/env python3
"""
Test script to verify payment system configuration
"""

import sys
sys.path.insert(0, '.')

from kalirootcli.config import CREDIT_PACKAGES, SUBSCRIPTION_PRICE_USD, SUBSCRIPTION_BONUS_CREDITS

print("=" * 60)
print("🧪 VERIFICACIÓN DE CONFIGURACIÓN DE PAGOS")
print("=" * 60)

print("\n📦 PAQUETES DE CRÉDITOS:")
print("-" * 60)
for i, pkg in enumerate(CREDIT_PACKAGES, 1):
    print(f"{i}. {pkg['name']:15} | {pkg['credits']:>5} créditos | ${pkg['price']:>5.0f} USD")

print("\n👑 SUSCRIPCIÓN PREMIUM:")
print("-" * 60)
print(f"Precio: ${SUBSCRIPTION_PRICE_USD:.0f} USD/mes")
print(f"Créditos mensuales: {SUBSCRIPTION_BONUS_CREDITS}")

print("\n✅ VALIDACIÓN:")
print("-" * 60)

# Verify API server pricing matches
expected_server_map = {
    10: 500,   # Starter
    20: 1200,  # Hacker Pro
    35: 2500   # Elite
}

all_valid = True
for pkg in CREDIT_PACKAGES:
    expected_credits = expected_server_map.get(int(pkg['price']))
    if expected_credits == pkg['credits']:
        print(f"✓ ${pkg['price']:.0f} → {pkg['credits']} créditos (Correcto)")
    else:
        print(f"✗ ${pkg['price']:.0f} → {pkg['credits']} créditos (Esperado: {expected_credits})")
        all_valid = False

if all_valid:
    print("\n🎉 ¡Toda la configuración es correcta!")
else:
    print("\n⚠️  Hay discrepancias en la configuración")
    sys.exit(1)

print("\n📊 RESUMEN PARA USUARIOS:")
print("-" * 60)
print("FREE: 500 créditos iniciales")
print("PREMIUM: 1200 créditos/mes + herramientas ($20/mes)")
print("Packs adicionales: 500 ($10), 1200 ($20), 2500 ($35)")
print("=" * 60)
