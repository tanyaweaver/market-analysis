def includeme(config):
    # config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('details', '/details/{sym}')
    config.add_route('home_test', '/test')
    config.add_route('add', '/add/{name}/{id}')
    config.add_route('delete', '/delete/{sym}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('search', '/search')
    config.add_route('userinfo', '/userinfo')
    config.add_route('admin', '/admin')
    config.add_route('private', '/private')
    config.add_route('public', '/public')
    config.add_route('new_user', '/new_user')
    config.add_route('portfolio', '/portfolio')
