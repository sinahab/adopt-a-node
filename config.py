
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

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SQLALCHEMY_ECHO = True

    BITPAY_URI = 'https://test.bitpay.com'
    BITPAY_PEM_FILE = 'instance/bitpay-key.pem'

    APP_BASE_URI = 'http://localhost:8000'
    # separate public uri for development, since needs to use ngrok (or something else) to make it accessible to Bitpay servers.
    APP_BASE_PUBLIC_URI = 'http://7f0a0ac3.ngrok.io'

class TestingConfig(Config):
    """
    Testing configurations
    """

    BITPAY_URI = 'https://test.bitpay.com'
    BITPAY_PEM_FILE = 'instance/bitpay-key.pem'

    TESTING = True

class ProductionConfig(Config):
    """
    Production configurations
    """
    SQLALCHEMY_ECHO = True
    DEBUG=False

    BITPAY_URI = 'https://bitpay.com'
    BITPAY_PEM_FILE = 'instance/bitpay-key-production.pem'

    APP_BASE_URI = 'https://adoptanode.com'
    APP_BASE_PUBLIC_URI = APP_BASE_URI

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestingConfig
}
