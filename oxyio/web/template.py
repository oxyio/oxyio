# oxy.io
# File: oxyio/includes/web/template.py
# Desc: template functions

from werkzeug.routing import BuildError
from flask import Markup, g, url_for, request

from oxyio import settings
from oxyio.app import web_app, module_map, object_map


# Attach data accessors
from oxyio.data import get_object_class
web_app.jinja_env.globals['get_object_class'] = get_object_class


# Attach the has_module function
from oxyio.app.module_loader import has_module
web_app.jinja_env.globals['has_module'] = has_module


# Attach the get_flashed_request & get_flashed_task_subscribes function
from oxyio.web.flashes import get_flashed_request, get_flashed_task_subscribes
web_app.jinja_env.globals['get_flashed_request'] = get_flashed_request
web_app.jinja_env.globals['get_flashed_task_subscribes'] = get_flashed_task_subscribes


# Attach the user functions to our global jinja env
from oxyio.web.user import (
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


# Helper for checking for list
web_app.jinja_env.globals['is_list'] = lambda arg: isinstance(arg, list)

# Make settings accessible within templates
web_app.jinja_env.globals['get_settings'] = lambda: settings

# Helper for making relations pretty
web_app.jinja_env.globals['prettify_relation'] = lambda field: (
    field.replace('_ids', '')
    .replace('_id', '')
    .replace('_', ' ')
)


# Local in-Python cache of webpack JSON data
WEBPACK_BUILD = None

def _get_webpack_build():
    global WEBPACK_BUILD

    if WEBPACK_BUILD is None:
        WEBPACK_BUILD = {}

    return WEBPACK_BUILD


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
        url = url_for('{0}.dashboard'.format(module_name))

    return name, color, icon, url


def modules_nav():
    '''
    Generate dropdown for modules changing the active/current one.
    '''

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
        if not has_permission(name):
            continue

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

    if add_admin is True and has_permission('admin'):
        links.append('''
            <li><a href="{0}" class="red">
                <span class="icon icon-cog"></span> Admin
            </a></li>
        '''.format(url_for('admin_dashboard')))

    out = '{0}<ul>{1}</ul>'.format(out, ''.join(links))

    return Markup(out)

web_app.jinja_env.globals['modules_nav'] = modules_nav


def module_nav():
    '''
    Generate nav for current module (objects/etc).
    '''

    if not hasattr(g, 'module'):
        return ''

    _, color, _, _ = _module_data()
    objects_type = g.object if hasattr(g, 'object') else None

    objects = object_map[g.module]
    links = []
    for object_name, object_class in objects.iteritems():
        name = object_class.TITLES
        url = None

        # If object is ownable, default to all view if allowed, otherwise just own
        if object_class.OWNABLE:
            if has_any_objects_permission(g.module, object_name, 'view'):
                url = url_for('.list_all_{0}s'.format(object_name))

            elif has_own_objects_permission(g.module, object_name, 'view'):
                url = url_for('.list_own_{0}s'.format(object_name))

        # Unowned objects just have a single, global, list view
        elif has_global_objects_permission(g.module, object_name, 'view'):
            url = url_for('.list_{0}s'.format(object_name))

        if url:
            links.append('<li class="{0} {1}"><a href="{2}">{3}</a></li>'.format(
                ('active' if object_name == objects_type else ''), color, url, name
            ))

    return Markup(''.join(links))

web_app.jinja_env.globals['module_nav'] = module_nav


def get_api_url():
    if '.' in request.endpoint:
        module, endpoint = request.endpoint.split('.')

        try:
            return url_for('{0}_api.{1}'.format(module, endpoint), **request.view_args)

        except BuildError:
            pass

web_app.jinja_env.globals['get_api_url'] = get_api_url


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

    module_name = ''
    if '/' in outname:
        module_name, outname = outname.split('/')
        module_name = '/{0}'.format(module_name)

    if extension == 'js':
        return Markup('''
            <script type="text/javascript" src="{0}/static/dist/{1}.js"></script>
        '''.format(module_name, outname))

    if extension == 'css':
        return Markup('''
            <link rel="stylesheet" href="{0}/static/dist/{1}.css" />
        '''.format(module_name, outname))


# Attach webpack_js and webpack_css wrappers
web_app.jinja_env.globals['webpack_js'] = lambda name: webpack(name, 'js')
web_app.jinja_env.globals['webpack_css'] = lambda name: webpack(name, 'css')
