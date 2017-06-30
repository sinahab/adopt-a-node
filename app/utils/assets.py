from flask_assets import Bundle

bundles = {
    'js': Bundle(
        'js/vendor/jquery-3.2.1.min.js',
        'js/adopt.js',
        output='dist/main.js'),

    'css': Bundle(
        'css/vendor/normalize.css',
        'css/vendor/basscss.css',
        'css/vendor/_font-family.css',
        'css/colors.styl',
        'css/utils.styl',
        'css/fonts.styl',
        'css/forms.styl',
        'css/main.styl',
        'css/node.styl',
        'css/landing.styl',
        filters='stylus',
        output='dist/site.css')
}
