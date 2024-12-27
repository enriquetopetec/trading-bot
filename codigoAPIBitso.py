import requests
import hmac
import hashlib
import time
import pandas as pd
import numpy as np

# Configuración de la API de Bitso
API_KEY = "bitsoenriquetopete"
API_SECRET = "hWcSHHvrGw"
API_URL = "https://api.bitso.com/v3/"

# Configuración inicial
INITIAL_INVESTMENT = 30.63  # Monto inicial en USD
USD_BALANCE = INITIAL_INVESTMENT  # Saldo en USD
BTC_AMOUNT = 0.0          # BTC disponibles
RSI_PERIOD = 14  # Período del RSI
OVERSOLD = 35    # Umbral de sobreventa (compra)
OVERBOUGHT = 70  # Umbral de sobrecompra (venta)
TARGET_RETURN = 0.02  # Rendimiento mensual deseado (2%)
AMOUNT_PER_TRADE = 0.01  # Cantidad fija de BTC por operación

# Función para generar encabezados de autenticación
def create_auth_headers(http_method, request_path, payload=""):
    nonce = str(int(time.time() * 1000))
    message = nonce + http_method + request_path + payload
    signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    
    headers = {
        "Authorization": f"Bitso {API_KEY}:{nonce}:{signature}"
    }
    return headers

# Obtener el precio actual de BTC en USD
def get_btc_price():
    response = requests.get(f"{API_URL}ticker/?book=btc_usd")
    if response.status_code == 200:
        data = response.json()
        return float(data['payload']['last'])
    else:
        print("Error al obtener precio de BTC:", response.text)
        return None

# Obtener historial de precios (simulado)
def get_price_history():
    return np.random.uniform(25000, 30000, 50)  # 50 precios aleatorios entre $25,000 y $30,000 USD

# Calcular RSI
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi

# Registrar operaciones
def log_trade(trade_data):
    file_name = "bitso_trades_usd.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "side", "amount", "price", "total", "usd_balance", "btc_balance"])
    
    df = pd.concat([df, pd.DataFrame([trade_data])], ignore_index=True)
    df.to_csv(file_name, index=False)
    print("Operación registrada en el archivo CSV.")

# Estrategia de trading optimizada
def trading_strategy():
    global USD_BALANCE, BTC_AMOUNT
    prices = get_price_history()
    rsi = calculate_rsi(prices, RSI_PERIOD)
    current_price = get_btc_price()

    if current_price:
        print(f"Precio actual de BTC: ${current_price:.2f} USD")
        print(f"RSI actual: {rsi[-1]:.2f}")

        # Comprar si RSI indica sobreventa
        if rsi[-1] < OVERSOLD and USD_BALANCE > 0:
            # Comprar una cantidad fija de BTC
            amount_to_buy = AMOUNT_PER_TRADE
            USD_BALANCE -= amount_to_buy * current_price
            BTC_AMOUNT += amount_to_buy
            trade_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "side": "buy",
                "amount": amount_to_buy,
                "price": current_price,
                "total": amount_to_buy * current_price,
                "usd_balance": USD_BALANCE,
                "btc_balance": BTC_AMOUNT
            }
            log_trade(trade_data)
            print(f"Compra realizada: {amount_to_buy:.6f} BTC a ${current_price:.2f} USD")

        # Vender si RSI indica sobrecompra
        elif rsi[-1] > OVERBOUGHT and BTC_AMOUNT > 0:
            # Vender una cantidad fija de BTC
            amount_to_sell = AMOUNT_PER_TRADE
            USD_BALANCE += amount_to_sell * current_price
            BTC_AMOUNT -= amount_to_sell
            trade_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "side": "sell",
                "amount": amount_to_sell,
                "price": current_price,
                "total": amount_to_sell * current_price,
                "usd_balance": USD_BALANCE,
                "btc_balance": BTC_AMOUNT
            }
            log_trade(trade_data)
            print(f"Venta realizada: {amount_to_sell:.6f} BTC a ${current_price:.2f} USD")

# Ejecución del bot en ciclos
if __name__ == "__main__":
    while True:
        trading_strategy()
        time.sleep(30)  # Espera 30 segundos antes del siguiente ciclo
