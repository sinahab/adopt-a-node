from flask_assets import Bundle

bundles = {
    # 'home_js': Bundle(
    #     'js/lib/jquery-1.10.2.js',
    #     'js/home.js',
    #     output='gen/home.js'),

    'css': Bundle(
        'css/vendor/normalize.css',
        'css/vendor/basscss.css',
        'css/vendor/_font-family.css',
        'css/main.styl',
        filters='stylus',
        output='dist/site.css')
}
