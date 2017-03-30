from sso import context_processors


def test_sso_user_middleware_plugged_in(settings):
    assert 'sso.middleware.SSOUserMiddleware' in settings.MIDDLEWARE_CLASSES


def test_sso_user_processor_plugged_in(settings):
    context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
    assert 'sso.context_processors.sso_user_processor' in context_processors


def test_sso_logged_in(request_logged_in):
    context = context_processors.sso_user_processor(request_logged_in)
    assert context['sso_is_logged_in'] is True


def test_sso_logged_out(request_logged_out):
    context = context_processors.sso_user_processor(request_logged_out)
    assert context['sso_is_logged_in'] is False


def test_sso_login_url(request_logged_in, settings):
    settings.SSO_LOGIN_URL = 'http://www.example.com/login/'
    expected = 'http://www.example.com/login/?next=http://testserver/'
    context = context_processors.sso_user_processor(request_logged_in)
    assert context['sso_login_url'] == expected


def test_sso_profile_url(request_logged_in, settings):
    settings.SSO_PROFILE_URL = expected = 'http://www.example.com/profile/'
    context = context_processors.sso_user_processor(request_logged_in)
    assert context['sso_profile_url'] == expected


def test_sso_register_url_url(request_logged_in, settings):
    settings.SSO_SIGNUP_URL = expected = 'http://www.example.com/signup/'
    context = context_processors.sso_user_processor(request_logged_in)
    assert context['sso_register_url'] == expected


def test_sso_logout_url(request_logged_in, settings):
    settings.SSO_LOGOUT_URL = expected = 'http://www.example.com/logout/'
    context = context_processors.sso_user_processor(request_logged_in)
    assert context['sso_logout_url'] == expected


def test_sso_user(request_logged_in, sso_user):
    context = context_processors.sso_user_processor(request_logged_in)

    assert context['sso_user'] == sso_user


def test_sso_reset_password_url(request_logged_in, settings):
    context = context_processors.sso_user_processor(request_logged_in)

    assert context['sso_password_reset_url'] == settings.SSO_PASSWORD_RESET_URL
