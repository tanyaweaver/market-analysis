import os
import sys
import transaction
import datetime
from market_analysis.scripts.test_db import STOCKS_100

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import Users, Stocks, Association


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        user_test = [
                    'Tom',
                    'Linda',
                    'Sally',
                    'Harold'
                    ]

        for name in user_test:
            date = datetime.datetime.now()
            user = Users(username=name, first_name=name, last_name='', email='', email_verified=True, date_joined=date, date_last_logged=date, pass_hash='seekrit', phone_number='', phone_number_verified=True, active=True, password_last_changed=date, password_expired=False)
            dbsession.add(user)

        for line in STOCKS_100:
            stock = Stocks(symbol=line[0], name=line[1], exchange='NASDAQ')
            dbsession.add(stock)
        
        association_test = [
                            (1, 1, 10),
                            (1, 2, 10),
                            (1, 3, 10),
                            (1, 4, 13),
                            (1, 5, 12),
                            (2, 1, 9),
                            (2, 4, 9),
                            (2, 3, 9)]
        for tup in association_test:
            association = Association(user_id=tup[0], stock_id=tup[1], shares=tup[2])
            dbsession.add(association)
