import datetime

FAKEUSERS = {
    {
        "id": 1,
        "username": 'fake',
        "first_name": 'Fakie',
        "last_name": 'Fake',
        "email": 'fake@fake.com',
        "email_verified": False,
        "date_joined": datetime.datetime.now(),
        "date_last_logged": datetime.date_joined.now(),
        "pass_hash": '$6$rounds=592828$M3HGCVUVOFj82EZv$ABSn/sV75ZaYNSI.GN5Usebhbng8SmFJuYoEwc/bfacXuIqtFof3/w8Ya/ZCN60NPDeDFDH0kjDQo.LsQTEuL.',
        "phone_number": '123-123-1234',
        "phone_number_verified": False,
        "active": True,
        "password_last_changed": datetime.datetime.now(),
        "password_expired": False,
    },
}
