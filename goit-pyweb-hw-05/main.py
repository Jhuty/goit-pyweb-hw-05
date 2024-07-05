import asyncio
import sys
import json
from datetime import datetime, timedelta
import aiohttp

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"

async def fetch_exchange_rates(session, date):
    url = API_URL.format(date=date.strftime("%d.%m.%Y"))
    async with session.get(url) as response:
        return await response.json()

async def get_currency_rates(days):
    async with aiohttp.ClientSession() as session:
        tasks = []
        today = datetime.today()
        
        for i in range(days):
            date = today - timedelta(days=i)
            task = fetch_exchange_rates(session, date)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def format_currency_rates(results):
    formatted_results = []
    
    for result in results:
        if 'exchangeRate' in result:
            date = result['date']
            eur_rate = next((item for item in result.get('exchangeRate', []) if item.get('currency') == 'EUR'), None)
            usd_rate = next((item for item in result.get('exchangeRate', []) if item.get('currency') == 'USD'), None)
            
            if eur_rate and usd_rate:
                formatted_result = {
                    date: {
                        'EUR': {
                            'sale': eur_rate.get('saleRate', eur_rate.get('saleRateNB')),
                            'purchase': eur_rate.get('purchaseRate', eur_rate.get('purchaseRateNB'))
                        },
                        'USD': {
                            'sale': usd_rate.get('saleRate', usd_rate.get('saleRateNB')),
                            'purchase': usd_rate.get('purchaseRate', usd_rate.get('purchaseRateNB'))
                        }
                    }
                }
                formatted_results.append(formatted_result)
    
    return formatted_results

async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        return
    
    try:
        days = int(sys.argv[1])
        if days < 1 or days > 10:
            print("Number of days must be between 1 and 10.")
            return
    except ValueError:
        print("Invalid number of days.")
        return
    
    try:
        results = await get_currency_rates(days)
        formatted_results = format_currency_rates(results)
        print(json.dumps(formatted_results, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error fetching data: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
