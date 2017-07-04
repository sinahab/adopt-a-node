
class Config(object):
    """
    Common configurations
    """

    DEBUG = True

    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = False # Needs email setup
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORDLESS = False
    SECURITY_CHANGEABLE = False # Enable this in the future, to allow changing of passwords.

    SECURITY_SEND_REGISTER_EMAIL = False # Needs email setup.

    SECURITY_URL_PREFIX = None
    SECURITY_LOGIN_URL = '/sign_in'
    SECURITY_LOGOUT_URL = '/sign_out'
    SECURITY_REGISTER_URL = '/sign_up'
    SECURITY_RESET_URL = '/reset'
    SECURITY_CHANGE_URL = '/change'
    SECURITY_CONFIRM_URL = '/confirm'
    SECURITY_POST_LOGIN_VIEW = '/nodes'
    SECURITY_POST_LOGOUT_VIEW = '/'
    SECURITY_POST_REGISTER_VIEW = '/adopt'
    SECURITY_UNAUTHORIZED_VIEW = '/'

    SECURITY_FORGOT_PASSWORD_TEMPLATE = 'security/forgot_password.html'
    SECURITY_LOGIN_USER_TEMPLATE = 'security/login_user.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'security/register_user.html'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'security/reset_password.html'
    SECURITY_CHANGE_PASSWORD_TEMPLATE = 'security/change_password.html'
    SECURITY_SEND_CONFIRMATION_TEMPLATE = 'security/send_confirmation.html'
    SECURITY_SEND_LOGIN_TEMPLATE = 'security/send_login.html'

    SECURITY_MSG_LOGIN = ('Please sign in first.', 'info')

    BITPAY_PEM_FILE = 'instance/bitpay-key.pem'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SQLALCHEMY_ECHO = True

    APP_BASE_URI = 'http://localhost:5000'

    # separate public uri for development, since needs to use ngrok (or something else) to make it accessible to Bitpay servers.
    APP_BASE_PUBLIC_URI = 'http://27474f51.ngrok.io'

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

    # TODO: update this when site is launched.
    APP_BASE_URI = 'http://165.227.15.19'
    APP_BASE_PUBLIC_URI = APP_BASE_URI

class TestingConfig(Config):
    """
    Testing configurations
    """

    TESTING = True

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestingConfig
}
