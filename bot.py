import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import time
import requests

# =========================
# API KEYS
# =========================

API_KEY = "YOUR_NEW_API_KEY"
API_SECRET = "YOUR_NEW_SECRET_KEY"

# =========================
# TELEGRAM
# =========================

TELEGRAM_TOKEN = "8399819376:AAHmPvTDEWikQG0zqF4vyY5n4QiEAUTcXx8",
CHAT_ID = "7610833426"

# =========================
# EXCHANGE SETUP
# =========================

exchange = ccxt.delta({
    "apiKey": "OZsM0U3PW4XeDMD8CfQ7OFVUFmLCrB",
    "secret": "OPIptyWsI24mzU1HQls5UDJXZtePf5RfDxoS2NllhUqN8ny9dYGkQmnIbZwz",
    "enableRateLimit": True,
})

# =========================
# SETTINGS
# =========================

symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "DOGEUSDT"
]

timeframe = "1h"
cooldown_seconds = 3600

last_trade_times = {}

# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot8399819376:AAFOtqU2JjTQQm4OHio6Uf-np5P54NU5NUY/sendMessage"

    data = {
        "chat_id": "7610833426",
        "text": message
}
    requests.post(url, data=data)

# =========================
# START MESSAGE
# =========================

send_telegram_message("BOT ONLINE")

# =========================
# POSITION TRACKING
# =========================

in_position = {}

position_type = {}

entry_price = {}

# =========================
# BOT LOOP
# =========================

while True:

    try:

        for symbol in symbols:

            try:

                print(f"\nChecking {symbol}...")

                candles = exchange.fetch_ohlcv(
                    symbol,
                    timeframe=timeframe,
                    limit=300
                )

                df = pd.DataFrame(
                    candles,
                    columns=[
                        "time",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume"
                    ]
                )

                close = df["close"]

                ema20 = EMAIndicator(
                    close,
                    window=20
                ).ema_indicator()

                ema50 = EMAIndicator(
                    close,
                    window=50
                ).ema_indicator()

                ema200 = EMAIndicator(
                    close,
                    window=200
               ).ema_indicator()

                current_price = close.iloc[-1]

                current_ema20 = ema20.iloc[-2]
                current_ema50 = ema50.iloc[-2]
                current_ema200 = ema200.iloc[-2]

                previous_ema20 = ema20.iloc[-3]
                previous_ema50 = ema50.iloc[-3]

                print(f"Price : {current_price:.2f}")
                print(f"EMA20 : {current_ema20:.2f}")
                print(f"EMA50 : {current_ema50:.2f}")

                if symbol not in in_position:

                    in_position[symbol] = False

                # =========================
                # LONG ENTRY
                # =========================

                long_signal = (
    previous_ema20 <= previous_ema50
    and current_ema20 > current_ema50
    and current_ema50 > current_ema200
)

                # =========================
                # SHORT ENTRY
                # =========================

                short_signal = (
    previous_ema20 >= previous_ema50
    and current_ema20 < current_ema50
    and current_ema50 < current_ema200
)
                # =========================
                # LONG BUY
                # =========================

                if long_signal and not in_position[symbol]:

                    in_position[symbol] = True

                    position_type[symbol] = "LONG"

                    entry_price[symbol] = current_price

                    message = (
    f"LONG BUY SIGNAL\n\n"
    f"Coin: {symbol}\n"
    f"Entry: {current_price:.2f}\n"
    f"EMA20 > EMA50 > EMA200"
)

                    print(message)

                    send_telegram_message(message)

                # =========================
                # SHORT SELL
                # =========================

                elif short_signal and not in_position[symbol]:

                    in_position[symbol] = True

                    position_type[symbol] = "SHORT"

                    entry_price[symbol] = current_price

                    message = (
    f"SHORT SELL SIGNAL\n\n"
    f"Coin: {symbol}\n"
    f"Entry: {current_price:.2f}\n"
    f"EMA20 < EMA50 < EMA200"
)

                    print(message)

                    send_telegram_message(message)

                # =========================
                # POSITION MANAGEMENT
                # =========================

                if in_position[symbol]:

                    entry = entry_price[symbol]

                    trade_type = position_type[symbol]

                    # LONG PNL

                    if trade_type == "LONG":

                        profit_percent = (
                            (current_price - entry)
                            / entry
                        ) * 100

                    # SHORT PNL

                    else:

                        profit_percent = (
                            (entry - current_price)
                            / entry
                        ) * 100

                    print(f"Position : {trade_type}")
                    print(f"PnL : {profit_percent:.2f}%")

                    # =========================
                    # EXIT CONDITIONS
                    # =========================

                    take_profit_hit = (
                        profit_percent >= take_profit_percent
                    )

                    stop_loss_hit = (
                        profit_percent <= -stop_loss_percent
                    )

                    # LONG EXIT

                    if trade_type == "LONG":

                        ema_reverse = (
                            current_ema20 < current_ema50
                        )

                    # SHORT EXIT

                    else:

                        ema_reverse = (
                            current_ema20 > current_ema50
                        )

                    # =========================
                    # CLOSE POSITION
                    # =========================

                    if (
                        take_profit_hit
                        or stop_loss_hit
                        or ema_reverse
                    ):

                        if take_profit_hit:

                            reason = "TAKE PROFIT HIT"

                        elif stop_loss_hit:

                            reason = "STOP LOSS HIT"

                        else:

                            reason = "EMA REVERSAL EXIT"

                        message = (
                            f"{reason}\n\n"
                            f"Coin: {symbol}\n"
                            f"Type: {trade_type}\n"
                            f"Exit Price: {current_price:.2f}\n"
                            f"PnL: {profit_percent:.2f}%"
                        )

                        print(message)

                        send_telegram_message(message)

                        in_position[symbol] = False

                else:

                    print("No active trade")

            except Exception as coin_error:

                print(f"{symbol} ERROR: {coin_error}")

        print("\nWaiting 60 seconds\n")

        time.sleep(60)

    except Exception as e:

        print("MAIN ERROR:", e)

        time.sleep(60)

last_candle_time = df["time"].iloc[-2]

