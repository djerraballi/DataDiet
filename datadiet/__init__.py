from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import log_check

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    authn_policy = AuthTktAuthenticationPolicy('sosecret', callback=log_check, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home_view', '/')
    config.add_route('login', '/login')
    config.add_route('register', '/register')
    config.add_route('test_create_user', '/test_create_user')
    config.add_route('cpost', '/cpost')
    config.add_route('logout', '/logout')
    config.add_route('likes', '/likes')
    config.add_route('comments', '/comments/{post_id}')
    config.add_route('add_tag', '/tags/{post_id}')
    config.scan()
    return config.make_wsgi_app()
