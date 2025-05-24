from binance import Client
from config import Settings
from logger import logger

class Basic:
    def __init__(self,settings: Settings):
        self.settings = settings
        self.client = Client(settings.api_key, settings.api_secret, testnet=settings.testnet)
        self.client.API_URL = 'https://testnet.binancefutures.com'
    
    def place_market_order(self, symbol: str, side: str, quantity: float):
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=quantity
            )
            logger.info(f"Market order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise e
        
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float):
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce='GTC'
            )
            logger.info(f"Limit order placed: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            raise e
        
    def get_positions(self):
        try:
            positions = self.client.futures_position_information()
            logger.info(f"Current positions: {positions}")
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise e
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float):
        """
        Place a STOP-LIMIT order: triggers a limit order at `price` once `stop_price` is reached
        """
        logger.info(f"Stop-Limit order → {side} {quantity}@{price} stopPrice={stop_price}")
        mark = float(self.client.futures_mark_price(symbol=symbol)["markPrice"])
        if side == "BUY":
            if stop_price <= mark:
                raise ValueError(f"stopPrice ({stop_price}) must exceed markPrice ({mark}) for a BUY")
            if price < stop_price:
                raise ValueError(f"limit price ({price}) must be ≥ stopPrice ({stop_price})")
        else:  # SELL
            if stop_price >= mark:
                raise ValueError(f"stopPrice ({stop_price}) must be below markPrice ({mark}) for a SELL")
            if price > stop_price:
                raise ValueError(f"limit price ({price}) must be ≤ stopPrice ({stop_price})")
        if quantity * stop_price < 20:
            raise ValueError("order notional must be at least 20 USDT")
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type="STOP",
                timeInForce="GTC",
                quantity=quantity,
                price=price,
                stopPrice=stop_price
            )
            logger.info(f"Stop-Limit Response: {order}")
            return order
        except Exception as e:
            logger.error(f"Stop-Limit order failed: {e}")
            raise
    
    def place_oco_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float):
        """
        Place an OCO (One Cancels Other) order: combines a LIMIT and a STOP-LIMIT order
        """
        logger.info(f"OCO order → {side} {quantity}@{price} stopPrice={stop_price}")
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type="OCO",
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                stopLimitPrice=stop_price,  # This is the limit price for the stop-limit part
                stopLimitTimeInForce="GTC"
            )
            logger.info(f"OCO Response: {order}")
            return order
        except Exception as e:
            logger.error(f"OCO order failed: {e}")
            raise e