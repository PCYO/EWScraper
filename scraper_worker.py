from scrapers import earnings_whispers_scraper
from services.earnings_service import set_earnings
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = earnings_whispers_scraper.EarningsWhispersScraper()
    earnings_list = scraper.scrape()
    logging.info('Scrap %d earnings', len(earnings_list))

    for earnings in earnings_list:
        set_earnings(earnings)

    logging.info('Scraper exit')
