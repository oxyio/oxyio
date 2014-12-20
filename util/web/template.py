# Oxypanel
# File: util/template.py
# Desc: template functions

from os import path
from itertools import chain
from hashlib import md5

from flask import Markup, g, url_for
from webassets import Bundle

import config
from app import app, assets, module_map, object_map


from .flashes import get_flashed_request
app.jinja_env.globals['get_flashed_request'] = get_flashed_request


from .user import (
    get_current_user,
    has_permission, has_permissions,
    has_object_permission, has_object_permissions,
    has_own_objects_permission, has_any_objects_permission,
    has_global_objects_permission
)
app.jinja_env.globals['current_user'] = get_current_user
app.jinja_env.globals['has_permission'] = has_permission
app.jinja_env.globals['has_permissions'] = has_permissions
app.jinja_env.globals['has_object_permission'] = has_object_permission
app.jinja_env.globals['has_object_permissions'] = has_object_permissions
app.jinja_env.globals['has_own_objects_permission'] = has_own_objects_permission
app.jinja_env.globals['has_any_objects_permission'] = has_any_objects_permission
app.jinja_env.globals['has_global_objects_permission'] = has_global_objects_permission


def get_config():
    return config

app.jinja_env.globals['get_config'] = get_config


def prettify_relation_field(field):
    return field.replace('_id', '').replace('_', ' ')

app.jinja_env.globals['prettify_relation'] = prettify_relation_field


def modules_nav():
    '''Generate dropdown for modules changing the active/current one'''
    # Active module link
    add_dashboard = False
    add_admin = True
    module_name = None
    name = 'Dashboard'
    color = 'green'
    icon = 'dashboard'
    url = url_for('dashboard')

    if hasattr(g, 'module'):
        module_name = g.module
        add_dashboard = True

        if module_name == 'admin':
            url = url_for('admin_dashboard')
            color = 'red'
            icon = 'cog'
            name = 'Admin'
            add_admin = False
        else:
            module = module_map[module_name]
            name = module.config.TITLE
            color = module.config.COLOR
            icon = module.config.ICON
            url = url_for('{}.dashboard'.format(module_name))

    out = '''
    <a href="{0}" class="{1}">
        <span class="icon icon-{2}"></span> {3} <span class="icon icon-arrow-down"></span>
    </a>
    '''.format(url, color, icon, name)

    # Other module links
    links = []
    for name, module in module_map.iteritems():
        if name != module_name:
            color = module.config.COLOR
            icon = module.config.ICON
            display_name = module.config.TITLE

            links.append('<li><a href="{0}" class="{1}"><span class="icon icon-{2}"></span> {3}</a></li>'.format(
                url_for('{0}.dashboard'.format(name)),
                color,
                icon,
                display_name
            ))

    if add_dashboard:
        links.append('<li><a href="{0}" class="green"><span class="icon icon-dashboard"></span> Dashboard</a></li>'.format(url_for('dashboard')))

    if add_admin == True and has_permission('Admin'):
        links.append('<li><a href="{0}" class="red"><span class="icon icon-cog"></span> Admin</a></li>'.format(url_for('admin_dashboard')))

    out = '{0}<ul>{1}</ul>'.format(out, ''.join(links))
    return Markup(out)

app.jinja_env.globals['modules_nav'] = modules_nav


def module_nav():
    '''Generate nav for current module (objects/etc)'''
    if not hasattr(g, 'module'):
        return ''

    objects_type = g.object if hasattr(g, 'object') else None

    objects = object_map[g.module]
    links = []
    for object_name, object_class in objects.iteritems():
        name = object_class.TITLES
        url = url_for('list_objects', module_name=g.module, objects_type=object_name)
        links.append('<li class="{0}"><a href="{1}">{2}</a></li>'.format(('active' if object_name==objects_type else ''), url, name))

    return Markup(''.join(links))

app.jinja_env.globals['module_nav'] = module_nav


#
def bundle_assets(*files, **options):
    '''
    Sadly webassets has no way to auto-generate outfile names
    this allows dynamically building bundles, only needing to fiddle with template code
    currently supports: JS, CSS(+Less)
    '''
    extension = options.pop('extension', '')
    filters = options.pop('filters', [])
    # For css
    rel = options.pop('rel', 'screen')

    # Debug? just print out the file includes
    if assets.debug:
        files = ['/'.join([f[0], 'static', f[1]]) if isinstance(f, tuple) else '/'.join(['static', f]) for f in files]
        outfiles = []
        for f in files:
            ext = f.split('.')[-1:][0]
            if ext == 'js':
                outfiles.append('<script type="text/javascript" src="/{0}"></script>'.format(f))
            elif ext == 'css':
                outfiles.append('<link rel="stylesheet" type="text/css" rel="{0}" href="/{1}" />'.format(rel, f))
            elif ext == 'less':
                outfiles.append('<link rel="stylesheet/less" type="text/css" rel="{0}" href="/{1}" />'.format(rel, f))

        return Markup('\n'.join(outfiles))

    files = [
        (path.join(*f), path.join('modules', f[0], 'static', f[1]))
        if isinstance(f, tuple) else
        (f, 'static/{0}'.format(f))
        for f in files
    ]

    # Build a key based off the files in question
    outfile = ''.join(chain.from_iterable((f[0], f[1]) for f in files))
    outfile = md5(outfile).hexdigest()

    bundle = None
    # Does the bundle already exist?
    if outfile not in assets:
        bundle = Bundle(*[f[1] for f in files],
            output='static/cache/{0}.{1}'.format(outfile, extension),
            filters=filters
        )
        assets.register(outfile, bundle)
    else:
        bundle = assets[outfile]

    # Trigger the bundle to be built
    urls = bundle.urls()

    if extension == 'js':
        outfile = ''.join(['<script type="text/javascript" src="{0}"></script>'.format(url) for url in urls])
    elif extension == 'css':
        outfile = ''.join(['<link rel="stylesheet" rel="{0}" href="{1}" />'.format(rel, url) for url in urls])

    return Markup(outfile)

app.jinja_env.globals['assets'] = bundle_assets
