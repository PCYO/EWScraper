from scrapers import earnings_whispers_scraper
from services.earnings_service import set_earnings
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    scraper = earnings_whispers_scraper.EarningsWhispersScraper()
    earnings_list = scraper.scrape()

    for earnings in earnings_list:
        set_earnings(earnings)
