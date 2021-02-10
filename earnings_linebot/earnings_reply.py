from services.earnings_service import get_earnings_by_date, get_earnings_by_ticker
from linebot.models import FlexSendMessage, TextSendMessage


class EarningsReply:
    def _eps2float(self, eps):
        try:
            if eps[0] == '$':
                return float(eps[1:])
            elif eps[0] == '(' and eps[1] == '$' and eps[-1] == ')':
                return -float(eps[2:-1])
            else:
                return None
        except:
            return None

    def _rev2float(self, rev):
        try:
            if rev[0] == '$':
                return float(rev[1:-1])
            elif rev[0] == '(' and rev[1] == '$' and rev[-1] == ')':
                return -float(rev[2:-2])
            else:
                return None
        except:
            return None

    def _get_bubble_container(self, earnings):
        green = '#599F59'
        red = '#BD5959'
        black = "#323232"

        color = dict()
        try:
            estimate = self._eps2float(earnings['actestimate'])
            actual = self._eps2float(earnings['actual'])
            color['acteps'] = red if actual < estimate else green
        except:
            color['acteps'] = black

        try:
            estimate = self._rev2float(earnings['actrevest'])
            actual = self._rev2float(earnings['revactual'])
            color['actrev'] = red if actual < estimate else green
        except:
            color['actrev'] = black

        try:
            color['growtheps'] = red if earnings['epsgrowthfull'][0] == '-' else green
        except:
            color['growtheps'] = black

        try:
            color['growthrev'] = red if earnings['revgrowthfull'][0] == '-' else green
        except:
            color['growthrev'] = black

        try:
            color['surpeps'] = red if earnings['epssurpfull'][0] == '-' else green
        except:
            color['surpeps'] = black

        try:
            color['surprev'] = red if earnings['revsurpfull'][0] == '-' else green
        except:
            color['surprev'] = black

        return {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"#{earnings.get('popularity', '00')} {earnings.get('ticker', '???')}",
                        "size": "xl",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": earnings.get('company', '<unknown company>')
                    },
                    {
                        "type": "text",
                        "text": earnings.get('date', '<unknown date>')
                    },
                    {
                        "type": "text",
                        "text": earnings.get('bmoamc', '<all>')
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": " "
                            },
                            {
                                "type": "text",
                                "text": "EPS"
                            },
                            {
                                "type": "text",
                                "text": "REV"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Estimate"
                            },
                            {
                                "type": "text",
                                "text": earnings.get('actestimate', '..')
                            },
                            {
                                "type": "text",
                                "text": earnings.get('actrevest', '..')
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Actual"
                            },
                            {
                                "type": "text",
                                "text": earnings.get('actual', '..'),
                                "color": color['acteps']
                            },
                            {
                                "type": "text",
                                "text": earnings.get('revactual', '..'),
                                "color": color['actrev']
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Growth"
                            },
                            {
                                "type": "text",
                                "text": earnings.get('epsgrowthfull', '..'),
                                "color": color['growtheps']
                            },
                            {
                                "type": "text",
                                "text": earnings.get('revgrowthfull', '..'),
                                "color": color['growthrev']
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Surprise"
                            },
                            {
                                "type": "text",
                                "text": earnings.get('epssurpfull', '..'),
                                "color": color['surpeps']
                            },
                            {
                                "type": "text",
                                "text": earnings.get('revsurpfull', '..'),
                                "color": color['surprev']
                            }
                        ]
                    }
                ]
            }
        }

    def _get_carousel_container(self, earnings_list):
        return {
            "type": "carousel",
            "altText": "earnings carousel",
            "contents": [self._get_bubble_container(earnings) for earnings in earnings_list]
        }

    def _get_reply_by_ticker(self, ticker):
        earnings_list = get_earnings_by_ticker(ticker)[:12]
        if earnings_list:
            return FlexSendMessage(
                alt_text='ticker carousel',
                contents=self._get_carousel_container(earnings_list))
        else:
            return TextSendMessage(text='Ticker ' + ticker + ' not found')

    def _get_reply_by_date(self, date, start_at=None, limit=None):
        earnings_list = get_earnings_by_date(date, start_at=start_at, limit=limit)

        if not earnings_list:
            return TextSendMessage(text='Date ' + date + ' not found')

        groups = [earnings_list[i:i+12] for i in range(0, len(earnings_list), 12)]
        reply = [FlexSendMessage(alt_text='ticker carousel', contents=self._get_carousel_container(group))
                 for group in groups]
        return reply

    def get_reply_message(self, type, ticker='', date='', start_at=None, limit=None):
        if start_at and not isinstance(start_at, int):
            raise TypeError('args: start_at must be an int')

        if limit and not isinstance(limit, int):
            raise TypeError('args: limit must be an int')

        if not limit or limit > 60:
            limit = 60

        if type == 'ticker':
            return self._get_reply_by_ticker(ticker)
        else:
            return self._get_reply_by_date(date, start_at=start_at, limit=limit)
