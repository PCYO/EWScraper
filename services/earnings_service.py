import logging
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

fs_config_file = os.getenv('fs_config_file', None)
if fs_config_file:
    fs_config = fs_config_file
else:
    fs_config = {
        'type': os.getenv('fs_type', None),
        'project_id': os.getenv('fs_project_id', None),
        'private_key_id': os.getenv('fs_private_key_id', None),
        'private_key': os.getenv('fs_private_key', None),
        'client_email': os.getenv('fs_client_email', None),
        'client_id': os.getenv('fs_client_id', None),
        'auth_uri': os.getenv('fs_auth_uri', None),
        'token_uri': os.getenv('fs_token_uri', None),
        'auth_provider_x509_cert_url': os.getenv('fs_auth_provider_x509_cert_url', None),
        'client_x509_cert_url': os.getenv('fs_client_x509_cert_url', None)
    }

    fs_config['private_key'] = fs_config['private_key'].replace('\\n', '\n')

    for k, v in fs_config.items():
        if not v:
            logging.error('Firebase init error, invalid config env %s', k)
            sys.exit(1)

try:
    cred = credentials.Certificate(fs_config)
except:
    logging.error('Firebase init error, check config')
    for k, v in fs_config.items():
        logging.error('%s => %s', k, v)
    sys.exit(1)

firebase_admin.initialize_app(cred)
db = firestore.client()


def get_earnings_by_ticker(ticker):
    docs = db.collection('earnings').where('ticker', '==', ticker).stream()
    return [doc.to_dict() for doc in docs]


def get_earnings_by_date(date):
    docs = db.collection('earnings').where('date', '==', date).stream()
    return [doc.to_dict() for doc in docs]


def set_earnings(earnings):
    docs = list(db
                .collection('earnings')
                .where('ticker', '==', earnings['ticker'])
                .where('date', '==', earnings['date'])
                .limit(1)
                .stream())
    if not docs:
        doc = db.collection('earnings').document()
        doc.set(earnings)
        logging.info('[FS] Add earnings %s, ticker %s date %s', doc.id, earnings['ticker'], earnings['date'])
    else:
        doc = docs[0]
        if doc.to_dict() != earnings:
            db.collection('earnings').document(doc.id).update(earnings)
            logging.info('[FS] Update earnings %s, ticker %s date %s', doc.id, earnings['ticker'], earnings['date'])
        else:
            logging.info('[FS] Unmodified earnings %s, ticker %s date %s', doc.id, earnings['ticker'], earnings['date'])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    earnings = {
        'ticker': 'TESTLA',
        'company': 'TESTLALALA',
        'actestimate': '$5.05',
        'actrevest': '$3.92 B',
        'actual': '$5.46',
        'date': '20210101',
        'epsgrowthfull': '85.1%',
        'epssurpfull': '8.1%',
        'revactual': '$3.94 B',
        'revgrowthfull': '20.6%',
        'revsurpfull': '0.6%',
        'popularity': 1
    }
    # set_earnings(earnings)

    es = get_earnings_by_date('20210205')
    for e in es:
        print(e)
