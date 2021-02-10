import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


class EarningsWhispersScraper:
    def __init__(self):
        self.url = "https://www.earningswhispers.com/calendar?sb=p&d=0&t=all&v=s"
        self.tags = ['company', 'ticker', 'actestimate', 'actrevest', 'actual',
                     'revactual', 'revsurpfull', 'revgrowthfull', 'epssurpfull', 'epsgrowthfull']

    def _parse_earnings(self, idx, date, earnings_tag):
        earnings = dict()
        for tag_name in self.tags:
            tag = earnings_tag.find(class_=tag_name)
            if tag:
                earnings[tag_name] = tag.string if tag.string else '?'
            else:
                earnings[tag_name] = '..'

        earnings['date'] = date
        earnings['popularity'] = idx
        if 'bmo' in earnings_tag['class']:
            earnings['bmoamc'] = 'bmo'
        elif 'amc' in earnings_tag['class']:
            earnings['bmoamc'] = 'amc'
        else:
            earnings['bmoamc'] = 'all'

        guidance_tag = earnings_tag.find(class_='guidance')
        if guidance_tag:
            if 'neg' in guidance_tag.attrs['class']:
                earnings['guidance'] = 'neg'
            elif 'neut' in guidance_tag.attrs['class']:
                earnings['guidance'] = 'neut'
            elif 'pos' in guidance_tag.attrs['class']:
                earnings['guidance'] = 'pos'
        return earnings

    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            date_str = soup.find(id='filedownload').get('href').split('=')[1]
        except:
            date_str = datetime.now(ZoneInfo("America/New_York")).strftime(r'%Y%m%d')

        calendar_tag = soup.find(id='epscalendar')
        earnings_tags = calendar_tag.find_all('li')[1:]
        earnings_list = [self._parse_earnings(idx, date_str, tag) for idx, tag in enumerate(earnings_tags)]

        for earnings in earnings_list:
            earnings['date'] = date_str

        return earnings_list


if __name__ == "__main__":
    scraper = EarningsWhispersScraper()
    earnings_list = scraper.scrape()

    for earnings in earnings_list:
        print(earnings)

    print('Total', len(earnings_list))
