# oxy.io
# File: setup.py
# Desc: oxy.io is a package?

from setuptools import setup


install_requires = (
    'gevent',
    'uwsgi>=2',

    # (micro) Framework
    'flask==0.10.1',
    'flask-uwsgi-websocket==0.5.0',
    'flask-debugtoolbar==0.9.0',
    'flask-script==2.0.5',
    'flask-sqlalchemy==2.0',

    # Database
    'mysqlclient==1.3.7',
    'alembic==0.7.4.',

    # Services
    'redis==2.10.3',
    'requests==2.7.0',
    'elasticsearch==2.2.0',
    'elasticquery==2.3',

    # Hashing
    'bcrypt==1.0.2',

    # Logging
    'coloredlogs==0.5',

    # CLI
    'docopt'
)


# oxy.io Python, see MANIFEST.in for HTML/etc
packages = (
    'oxyio',
    'oxyio.app',
    'oxyio.models',
    'oxyio.scripts',
    'oxyio.settings',
    'oxyio.tasks',
    'oxyio.web',
    'oxyio.web.templates',
    'oxyio.web.views',
    'oxyio.web.views.admin',
    'oxyio.websockets'
)


if __name__ == '__main__':
    setup(
        name='oxy.io',
        version=0,
        author='Oxygem',
        author_email='hello@oxygem.com',
        url='',
        description='',
        packages=packages,
        package_dir={'oxyio': 'oxyio'},
        install_requires=install_requires,
        scripts=(
            'bin/oxyio',
        ),
        license='MIT',
        include_package_data=True
    )
