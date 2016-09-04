def includeme(config):
    # config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home_test', '/')
    config.add_route('single_stock_info_test', '/single_stock_info_test')
    config.add_route('login', '/login')
