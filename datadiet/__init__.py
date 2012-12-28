from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('register', '/register')
    config.add_route('test_create_user', '/test_create_user')
    config.add_route('cpost', '/cpost')
    config.add_route('test_add_post', '/test_add_post')
    config.scan()
    return config.make_wsgi_app()
