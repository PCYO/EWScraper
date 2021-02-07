from .earnings_reply import EarningsReply


class EarningsBot:
    def get_reply_instance(self, type):
        if type == 'earnings':
            return EarningsReply()
