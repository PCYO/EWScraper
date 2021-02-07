import os
import sys
from flask import Flask, render_template, request, abort
from flask.logging import create_logger
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from services.earnings_service import get_earnings_by_date, get_earnings_by_ticker
from earnings_linebot.earnings_bot import EarningsBot
from earnings_linebot.earnings_reply import EarningsReply
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

app = Flask(__name__,
            static_folder='./dist/static',
            template_folder='./dist')
logger = create_logger(app)

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)

if not channel_access_token:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if not channel_secret:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

try:
    line_bot_api = LineBotApi(channel_access_token)
    handler = WebhookHandler(channel_secret)
except:
    logger.error('Line api init failed')
    sys.exit(1)


@app.route('/')
def earnings():
    return render_template('index.html')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if text[0].upper() == 'T':
        ticker = text[1:].lstrip().upper()
        if ticker:
            line_bot_api.reply_message(
                event.reply_token,
                messages=EarningsBot().get_reply_instance('earnings').get_reply_message('ticker', ticker=ticker))
    elif text[0].upper() == 'D':
        date = text[1:].lstrip()
        if len(date) == 1:
            try:
                days = int(date)
            except:
                days = 0
            date = (datetime.now(ZoneInfo("America/New_York")) - timedelta(days=days)).strftime(r'%Y%m%d')

        if date:
            line_bot_api.reply_message(
                event.reply_token,
                messages=EarningsBot().get_reply_instance('earnings').get_reply_message('date', date=date))


if __name__ == "__main__":
    app.run()
