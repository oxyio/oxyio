# oxy.io
# File: oxyio/web/util/template.py
# Desc: template functions

from flask import Markup, g, url_for

from ... import settings
from ...app import web_app, module_map, object_map

# Attach the get_flashed_request function
from .flashes import get_flashed_request
web_app.jinja_env.globals['get_flashed_request'] = get_flashed_request

# Attach the user functions to our global jinja env
from .user import (
    get_current_user,
    has_permission, has_permissions,
    has_object_permission, has_object_permissions,
    has_own_objects_permission, has_any_objects_permission,
    has_global_objects_permission
)
web_app.jinja_env.globals['current_user'] = get_current_user
web_app.jinja_env.globals['has_permission'] = has_permission
web_app.jinja_env.globals['has_permissions'] = has_permissions
web_app.jinja_env.globals['has_object_permission'] = has_object_permission
web_app.jinja_env.globals['has_object_permissions'] = has_object_permissions
web_app.jinja_env.globals['has_own_objects_permission'] = has_own_objects_permission
web_app.jinja_env.globals['has_any_objects_permission'] = has_any_objects_permission
web_app.jinja_env.globals['has_global_objects_permission'] = has_global_objects_permission


# Make settings accessible within templates
web_app.jinja_env.globals['get_settings'] = lambda: settings


# Helper for making relations pretty
web_app.jinja_env.globals['prettify_relation'] = lambda field: (
    field.replace('_id', '')
    .replace('_', ' ')
)


# Local in-Python cache of webpack JSON data
_webpack_build = None

def _get_webpack_build():
    global _webpack_build

    if _webpack_build is None:
        _webpack_build = {}

    return _webpack_build


def _module_data():
    module_name = g.module

    if module_name == 'admin':
        url = url_for('admin_dashboard')
        color = 'red'
        icon = 'cog'
        name = 'Admin'
    else:
        module = module_map[module_name]
        name = module.config.TITLE
        color = module.config.COLOR
        icon = module.config.ICON
        url = url_for('{}.dashboard'.format(module_name))

    return name, color, icon, url


def modules_nav():
    '''Generate dropdown for modules changing the active/current one.'''
    # Active module link
    add_dashboard = False
    add_admin = True
    module_name = None

    name = 'Dashboard'
    color = 'green'
    icon = 'dashboard'
    url = url_for('dashboard')

    if hasattr(g, 'module'):
        name, color, icon, url = _module_data()
        module_name = g.module
        add_dashboard = True

        if module_name == 'admin':
            add_admin = False

    out = '''
        <a href="{0}" class="{1}">
            <span class="icon icon-{2}"></span> {3}
            <span class="icon icon-arrow-down"></span>
        </a>
    '''.format(url, color, icon, name)

    # Other module links
    links = []
    for name, module in module_map.iteritems():
        if name != module_name:
            color = module.config.COLOR
            icon = module.config.ICON
            display_name = module.config.TITLE

            links.append('''
                <li><a href="{0}" class="{1}">
                    <span class="icon icon-{2}"></span> {3}
                </a></li>
            '''.format(
                url_for('{0}.dashboard'.format(name)),
                color,
                icon,
                display_name
            ))

    if add_dashboard:
        links.append('''
            <li><a href="{0}" class="green">
                <span class="icon icon-dashboard"></span> Dashboard
            </a></li>
        '''.format(url_for('dashboard')))

    if add_admin is True and has_permission('Admin'):
        links.append('''
            <li><a href="{0}" class="red">
                <span class="icon icon-cog"></span> Admin
            </a></li>
        '''.format(url_for('admin_dashboard')))

    out = '{0}<ul>{1}</ul>'.format(out, ''.join(links))
    return Markup(out)

web_app.jinja_env.globals['modules_nav'] = modules_nav


def module_nav():
    '''Generate nav for current module (objects/etc).'''
    if not hasattr(g, 'module'):
        return ''

    _, color, _, _ = _module_data()
    objects_type = g.object if hasattr(g, 'object') else None

    objects = object_map[g.module]
    links = []
    for object_name, object_class in objects.iteritems():
        name = object_class.TITLES
        url = url_for('list_objects', module_name=g.module, objects_type=object_name)

        links.append('<li class="{0} {1}"><a href="{2}">{3}</a></li>'.format(
            ('active' if object_name == objects_type else ''), color, url, name
        ))

    return Markup(''.join(links))

web_app.jinja_env.globals['module_nav'] = module_nav


def webpack(name, extension):
    '''
    Gets the built/compiled filename for a given webpack entry point, reading filenames
    from oxyio/static/dist/webpack_build.json in production.
    '''

    if settings.DEBUG:
        outname = name
    else:
        # TODO: implement!
        outname = None

    if extension == 'js':
        return Markup('''
            <script type="text/javascript" src="/static/dist/{}.js"></script>
        '''.format(outname))

    if extension == 'css':
        return Markup('''
            <link rel="stylesheet" href="/static/dist/{}.css" />
        '''.format(outname))

# Attach webpack_js and webpack_css wrappers
web_app.jinja_env.globals['webpack_js'] = lambda name: webpack(name, 'js')
web_app.jinja_env.globals['webpack_css'] = lambda name: webpack(name, 'css')