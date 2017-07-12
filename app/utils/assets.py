from flask_assets import Bundle

bundles = {
    'js': Bundle(
        'js/vendor/jquery-3.2.1.min.js',
        'js/vendor/iscroll.min.js',
        'js/vendor/drawer.min.js',
        'js/adopt.js',
        'js/main.js',
        'js/google-analytics.js',
        output='dist/main.js'),

    'css': Bundle(
        'css/vendor/normalize.css',
        'css/vendor/basscss.css',
        'css/vendor/_font-family.css',
        'css/vendor/drawer.css',
        'css/colors.styl',
        'css/utils.styl',
        'css/fonts.styl',
        'css/forms.styl',
        'css/header.styl',
        'css/main.styl',
        'css/node.styl',
        'css/landing.styl',
        filters='stylus',
        output='dist/site.css')
}
