"""
Market Updates Module
Handles real-time market data and finance news
"""
import requests
from datetime import datetime
import random

class MarketUpdates:
    def __init__(self):
        # Sample market data (in production, you would use real APIs like Alpha Vantage, Yahoo Finance, etc.)
        self.sample_indices = {
            'SENSEX': {'value': 71234.56, 'change': 234.12, 'change_percent': 0.33},
            'NIFTY': {'value': 21456.78, 'change': -45.67, 'change_percent': -0.21},
            'BANK NIFTY': {'value': 46789.12, 'change': 123.45, 'change_percent': 0.26}
        }
        
        self.sample_stocks = [
            {'symbol': 'RELIANCE', 'price': 2456.78, 'change': 12.34, 'change_percent': 0.50},
            {'symbol': 'TCS', 'price': 3890.12, 'change': -23.45, 'change_percent': -0.60},
            {'symbol': 'HDFCBANK', 'price': 1654.32, 'change': 8.90, 'change_percent': 0.54},
            {'symbol': 'INFY', 'price': 1523.67, 'change': 5.67, 'change_percent': 0.37},
            {'symbol': 'ICICIBANK', 'price': 987.45, 'change': -3.21, 'change_percent': -0.32}
        ]
        
        self.finance_news = [
            {
                'title': 'Stock Market Hits New High Amid Positive Economic Indicators',
                'summary': 'The market continues its upward trend with strong corporate earnings and stable economic growth.',
                'source': 'Financial Times',
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'title': 'RBI Announces Interest Rate Decision',
                'summary': 'The Reserve Bank of India maintains current interest rates, signaling economic stability.',
                'source': 'Economic Times',
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'title': 'Mutual Fund Industry Sees Record Inflows',
                'summary': 'Systematic Investment Plans continue to attract retail investors, showing growing financial awareness.',
                'source': 'Business Standard',
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'title': 'Tech Stocks Lead Market Rally',
                'summary': 'Technology sector stocks show strong performance driven by digital transformation trends.',
                'source': 'Mint',
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'title': 'Gold Prices Stabilize After Recent Volatility',
                'summary': 'Precious metals market finds balance as investors seek safe-haven assets.',
                'source': 'Financial Express',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        ]
    
    def get_market_indices(self):
        """Get market indices data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'indices': self.sample_indices,
            'note': 'For real-time data, integrate with market data APIs like Alpha Vantage, Yahoo Finance, or NSE/BSE APIs'
        }
    
    def get_stock_prices(self, symbols=None):
        """Get stock prices for given symbols or top stocks"""
        if symbols:
            return [stock for stock in self.sample_stocks if stock['symbol'] in symbols]
        return self.sample_stocks[:5]  # Return top 5 stocks
    
    def get_finance_news(self, limit=5):
        """Get latest finance news"""
        return self.finance_news[:limit]
    
    def get_market_summary(self):
        """Get overall market summary"""
        indices = self.get_market_indices()
        top_stocks = self.get_stock_prices()  # Already returns top 5 by default
        news = self.get_finance_news(limit=3)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'market_status': 'Market is trading',
            'indices': indices['indices'],
            'top_stocks': top_stocks,
            'latest_news': news
        }
    
    # In production, you would add methods to fetch real data from APIs:
    # def fetch_real_market_data(self, api_key):
    #     """Fetch real market data from Alpha Vantage or similar API"""
    #     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=RELIANCE.BSE&apikey={api_key}"
    #     response = requests.get(url)
    #     return response.json()

