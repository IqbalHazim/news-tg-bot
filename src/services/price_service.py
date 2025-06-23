import pandas as pd
import requests
import logging

from config import DEFIDIVE_API_URL

logger = logging.getLogger(__name__)

class PriceService:
    def __init__(self):
        pass

    def prepare_price_data(self, data):
        """
        Prepares the price data for storage.
        """
        if not data:
            # raise ValueError("No data provided for preparation.")
            return []

        try:
            # Convert the data to a DataFrame
            # TODO: Add more robust error handling and data validation
            # TODO: determine if time is using unix timestamp or datetime
            prepared_data = pd.DataFrame(data)
        except Exception as e:
            logger.error(f"⚠️ Error preparing price data: {e}")
            return []
        return prepared_data
    
    def get_price(self, token: str, timeframe: str = "1w"):
        """
        Retrieves the price of a product by its ticker symbol.
        """
        # get data from defidive api
        url = f"{DEFIDIVE_API_URL}/chart/{token.upper()}/price?timeframe={timeframe}"
        try:
            token_price_json = requests.get(url).json()
            # prepare data for analysis
            return self.prepare_price_data(token_price_json.get("prices", {}))
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request Error: {e}")
            return None
    
    def get_top_tokens(self, limit=3, page="1", sort_by="rank", sort_order="asc"):
        """
        Retrieves the top tokens by market cap.
        """
        try:
            url = f"{DEFIDIVE_API_URL}/coin/info/all?page={page}&sort_field{sort_by}&sort_direction={sort_order}"
            response = requests.get(url).json()
            data = response.get('data', [])
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request Error: {e}")
            return []
        
        top_token_list = data[:limit] if len(data) > limit else data
        top_tokens = [token.get('symbol') for token in top_token_list]
        return top_tokens