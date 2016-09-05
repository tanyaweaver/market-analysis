import os
import sys
import transaction

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
from ..models import Users
from .fake_users import FAKEUSERS


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
        for line in FAKEUSERS:
            user =  Users(username=line[username],
                          first_name=line[first_name],
                          last_name=line[last_name],
                          email=line[email],
                          email_verified=line[email_verified],
                          date_joined=line[date_joined],
                          date_last_logged=line[date_last_logged],
                          pass_hash=line[pass_hash],
                          phone_number=line[phone_number],
                          phone_number_verified=line[phone_number_verified],
                          active=line[active],
                          password_last_changed=line[password_last_changed],
                          password_expired=line[password_expired],
                          )
            dbsession.add(user)
