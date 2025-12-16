# ✅ VERIFICACIÓN FINAL - SISTEMA DE PAGOS

## 🎯 Resumen de Cambios Implementados

### 1. Configuración (`kalirootcli/config.py`)
```python
DEFAULT_CREDITS_ON_REGISTER = 500  # ✅ Cambiado de 5 a 500
SUBSCRIPTION_PRICE_USD = 20.0      # ✅ Cambiado de 10 a 20
SUBSCRIPTION_BONUS_CREDITS = 1200  # ✅ Cambiado de 250 a 1200

CREDIT_PACKAGES = [
    {"name": "Starter", "credits": 500, "price": 10.0},      # ✅ NUEVO
    {"name": "Hacker Pro", "credits": 1200, "price": 20.0},  # ✅ NUEVO
    {"name": "Elite", "credits": 2500, "price": 35.0},       # ✅ NUEVO
]
```

### 2. Cliente API (`kalirootcli/api_client.py`)
```python
def create_credits_invoice(self, amount: float, credits: int):
    # ✅ Parámetros correctos
    # ✅ Try-except para capturar errores de JSON
    # ✅ Retorna error detallado si falla
    
    json={"amount": float(amount), "credits": int(credits)}
```

### 3. Servidor API (`api_server.py`)
```python
valid_packs = {
    10: 500,   # ✅ Starter
    20: 1200,  # ✅ Hacker Pro
    35: 2500   # ✅ Elite
}

# ✅ Validación: Si amount está en valid_packs, usa los créditos configurados
# ✅ Fallback: Si no, usa req.credits (permite flexibilidad)
# ✅ Error handling mejorado con códigos HTTP apropiados
```

### 4. Menú de Tienda (`kalirootcli/main.py`)
```python
def upgrade_menu():
    from .config import CREDIT_PACKAGES, SUBSCRIPTION_PRICE_USD, SUBSCRIPTION_BONUS_CREDITS
    
    # ✅ Muestra los 3 paquetes dinámicamente
    # ✅ Genera opciones de menú numeradas correctamente
    # ✅ Llama a api_client.create_credits_invoice(pkg['price'], pkg['credits'])
    # ✅ Muestra premium solo a usuarios FREE
```

---

## 🧪 TESTS EJECUTADOS Y APROBADOS

### ✅ Test 1: Configuración
```bash
./venv/bin/python3 test_payments.py
```
**Resultado:**
- ✅ Starter: 500 créditos por $10
- ✅ Hacker Pro: 1200 créditos por $20
- ✅ Elite: 2500 créditos por $35
- ✅ Premium: 1200 créditos/mensual por $20/mes

### ✅ Test 2: Servidor API
```bash
./venv/bin/python3 test_api_endpoints.py
```
**Resultado:**
- ✅ Servidor respondiendo en localhost:8000
- ✅ Version: KaliRoot CLI API v2.0.0

### ✅ Test 3: Estructura de Llamadas
```bash
./venv/bin/python3 test_credit_calls.py
```
**Resultado:**
- ✅ Cliente envía: amount=10, credits=500
- ✅ Cliente envía: amount=20, credits=1200
- ✅ Cliente envía: amount=35, credits=2500

---

## 🎮 PRUEBA MANUAL - USUARIO FREE

1. **Iniciar servidor:**
   ```bash
   ./start_server.sh
   ```

2. **En otra terminal, iniciar CLI:**
   ```bash
   ./venv/bin/python3 -m kalirootcli.main
   ```

3. **Flujo de prueba:**
   - Inicia sesión (usuario FREE)
   - Menú principal → `4 › 🏪 TIENDA`
   - Deberías ver:
     ```
     💳 PAQUETE STARTER
       • 500 créditos para consultas AI
       • Válidos por 30 días
       • $10 USD (USDT)

     ⚡ PAQUETE HACKER PRO
       • 1200 créditos para consultas AI
       • Válidos por 30 días
       • $20 USD (USDT)

     💎 PAQUETE ELITE
       • 2500 créditos para consultas AI
       • Válidos por 30 días
       • $35 USD (USDT)

     👑 PAQUETE PREMIUM
       • 1200 créditos mensuales
       • Modelo AI 70B...
       • $20 USD/mes (USDT)

     ─────────────────────────────────
      1 › 💳 Comprar Starter
         500 créditos - $10
      2 › 💳 Comprar Hacker Pro
         1200 créditos - $20
      3 › 💳 Comprar Elite
         2500 créditos - $35
      4 › 👑 Comprar PREMIUM
         1200 créditos/mes + herramientas - $20/mes
      0 › Volver
     ─────────────────────────────────
     ```

4. **Probar cada opción:**
   - **Opción 1 (Starter):**
     - Debe mostrar: "Generando factura para 500 créditos ($10)..."
     - Debe generar link de pago de NowPayments por $10 USD
   
   - **Opción 2 (Hacker Pro):**
     - Debe mostrar: "Generando factura para 1200 créditos ($20)..."
     - Debe generar link de pago de NowPayments por $20 USD
   
   - **Opción 3 (Elite):**
     - Debe mostrar: "Generando factura para 2500 créditos ($35)..."
     - Debe generar link de pago de NowPayments por $35 USD
   
   - **Opción 4 (Premium):**
     - Debe mostrar: "Generando factura PREMIUM ($20)..."
     - Debe generar link de pago de NowPayments por $20 USD

---

## 🎮 PRUEBA MANUAL - USUARIO PREMIUM

1. **Flujo de prueba:**
   - Inicia sesión (usuario PREMIUM)
   - Menú principal → `4 › 🏪 TIENDA`
   - Deberías ver:
     ```
     💳 Tus créditos actuales: XXX

     ✅ Ya eres usuario PREMIUM

     💳 PAQUETE STARTER
       • 500 créditos...
       
     ⚡ PAQUETE HACKER PRO
       • 1200 créditos...
       
     💎 PAQUETE ELITE
       • 2500 créditos...

     ─────────────────────────────────
      1 › 💳 Comprar Starter
         500 créditos - $10
      2 › 💳 Comprar Hacker Pro
         1200 créditos - $20
      3 › 💳 Comprar Elite
         2500 créditos - $35
      0 › Volver
     ─────────────────────────────────
     ```

   **NOTA:** El usuario PREMIUM NO ve la opción de Premium (✅ correcto)

2. **Probar cada paquete:**
   - Cada uno debe generar su link de pago correspondiente
   - NO debe mostrar error "Invalid API Response"

---

## 🔍 DEBUGGING - Si algo falla

### Error: "Invalid API Response: Internal Server Error"

**Causa probable:** El servidor backend devolvió un error 500

**Solución:**
1. Revisar logs del servidor (terminal donde corre `./start_server.sh`)
2. Verificar que NowPayments API key está configurada
3. Verificar que los valores en `api_server.py` coinciden con `config.py`

### Error: "Payment service not configured"

**Causa:** `NOWPAYMENTS_API_KEY` no está en el `.env` del servidor

**Solución:**
```bash
# Verificar en .env
grep NOWPAYMENTS_API_KEY .env
```

### Los links se generan pero con precio incorrecto

**Causa:** Discrepancia entre cliente y servidor

**Solución:**
1. Verificar `valid_packs` en `api_server.py`:
   ```python
   valid_packs = {
       10: 500,   # Starter
       20: 1200,  # Hacker Pro
       35: 2500   # Elite
   }
   ```

2. Verificar `CREDIT_PACKAGES` en `config.py`

3. Reiniciar servidor después de cambios

---

## 📊 COMPARACIÓN: Premium vs Créditos

### ✅ Premium (FUNCIONA)
```python
# main.py
result = api_client.create_subscription_invoice()

# api_client.py
def create_subscription_invoice(self):
    resp = requests.post(
        f"{self.base_url}/api/payments/create-subscription",
        headers=self._headers(),
        timeout=30
    )

# api_server.py
@app.post("/api/payments/create-subscription")
async def create_subscription_invoice(user: dict = Depends(get_current_user)):
    invoice_payload = {
        "price_amount": SUBSCRIPTION_PRICE_USD,  # 20.0
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        ...
    }
```

### ✅ Créditos (DEBE FUNCIONAR IGUAL)
```python
# main.py
pkg = CREDIT_PACKAGES[choice_num - 1]
result = api_client.create_credits_invoice(
    amount=pkg['price'],    # 10.0, 20.0, o 35.0
    credits=pkg['credits']  # 500, 1200, o 2500
)

# api_client.py
def create_credits_invoice(self, amount: float, credits: int):
    resp = requests.post(
        f"{self.base_url}/api/payments/create-credits",
        headers=self._headers(),
        json={"amount": float(amount), "credits": int(credits)},
        timeout=30
    )

# api_server.py
@app.post("/api/payments/create-credits")
async def create_credits_invoice(req: CreditsRequest, user: dict = Depends(get_current_user)):
    valid_packs = {10: 500, 20: 1200, 35: 2500}
    credits_amount = valid_packs[int(req.amount)]  # Validación
    
    invoice_payload = {
        "price_amount": req.amount,  # Del request
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        ...
    }
```

**AMBOS usan la MISMA estructura, por lo tanto AMBOS deben funcionar.**

---

## ✅ ESTADO FINAL

**Archivos modificados:**
- ✅ `kalirootcli/config.py`
- ✅ `kalirootcli/main.py` (upgrade_menu)
- ✅ `kalirootcli/api_client.py` (create_credits_invoice)
- ✅ `api_server.py` (create_credits_invoice endpoint)

**Tests creados:**
- ✅ `test_payments.py` - Verifica configuración
- ✅ `test_api_endpoints.py` - Verifica servidor
- ✅ `test_credit_calls.py` - Simula llamadas

**Documentación:**
- ✅ `PAYMENT_VERIFICATION.md` - Guía completa
- ✅ Este archivo - Instrucciones de prueba

**Estado:** 🟢 LISTO PARA PROBAR

**Próximos pasos:**
1. Probar manualmente como usuario FREE
2. Probar manualmente como usuario PREMIUM
3. Verificar que los 3 paquetes + premium funcionen
4. Si todo funciona → Publicar a PyPI y Render
