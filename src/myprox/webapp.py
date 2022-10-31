#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cherrypy
import jinja2
import logging
import os
import random
import string
from urllib.parse import urlencode

import proxmoxer
from . import myproxapi
from . import setupenv


class WebApp():

    def __init__(self, cfg):
        """Instance initialization"""
        self.cfg = cfg
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')))

    @cherrypy.expose
    def index(self, action=None, id=None, action_selection=None):
        """Show a list of existing machines"""
        vms = cherrypy.session['proxmox'].get_virtual_machines()
        #cherrypy.log(str(vms), context='WEBAPP', severity=logging.INFO, traceback=False)
        tmpl = self.jinja_env.get_template('index.html')
        return tmpl.render(sessiondata=cherrypy.session, machines=vms)

    @cherrypy.expose
    def manage(self, action=None, id=None, action_selection=None):
        """Manage a machine"""
        machine_data = None
        message = None
        if id:
            action_results = {
              'start': 'start triggered',
              'reboot': 'reboot triggered',
              'shutdown': 'shutdown triggered',
              'reset': 'reset triggered', 
              'stop': 'stop (switch-off) triggered',
              'suspend': 'suspension (hibernation) triggered',
              'resume': 'resume triggered'
            }
            if action_selection in action_results.keys():
                if not self.cfg.dryrun:
                    cherrypy.session['proxmox'].trigger_vm_action(id, action_selection)
                message = f'Machine {action_results[action_selection]}.'
            elif action_selection == 'console':
                raise cherrypy.HTTPRedirect(f'/console?id={id}')
            elif action_selection == 'console_vnc':
                raise cherrypy.HTTPRedirect(f'/console_vnc?id={id}')
            elif action_selection == 'extend':
                cherrypy.session['proxmox'].set_tag_expiry_bydays(id, self.cfg.expiry_prolongation_days)
                message = 'The expiry data of this machine has been set according to the prolongation policy of your organization.'
            elif action_selection == 'destroy':
                message = 'The functionality to destroy a machine is not yet implemented. . Contact support to do this.'
            elif action_selection == 'refresh':
                pass # nothing to do
            elif action_selection is None: # no action triggered at all
                pass # nothing to do
            else: # unknown action
                message = 'Error: invalid action specified'
        else:
            message = 'Error: no identifier given'
        if not machine_data and id:
            machine_data = cherrypy.session['proxmox'].get_virtual_machine_with_tags(id)
        if machine_data is None:
            machine_data = dict()
        #cherrypy.log(str(machine_data), context='WEBAPP', severity=logging.WARNING, traceback=False)
        tmpl = self.jinja_env.get_template('manage.html')
        return tmpl.render(sessiondata=cherrypy.session, itemdata=machine_data, message=message)

    @cherrypy.expose
    def create(self, action=None, id=None):
        """Trigger creation of a VM"""
        raise cherrypy.HTTPRedirect(self.cfg.machine_creation_url.format(username=cherrypy.session['username']))

    @cherrypy.expose
    def console(self, id=None):
        """Provide a connection file for download"""
        cherrypy.log(f'Attempting to download connection file for [{id}] by user [{cherrypy.session["username"]}]', context='WEBAPP', severity=logging.INFO, traceback=False)
        try:
            file_dict = cherrypy.session['proxmox'].get_spice(id)
            file_data = '[virt-viewer]\n'
            for key, value in file_dict.items():
                file_data += f'{key}={value}\n'
            cherrypy.log(str(file_data), context='WEBAPP', severity=logging.INFO, traceback=False)
            filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
            #cherrypy.response.headers['Content-Disposition'] = f'attachment; filename={filename}.vv'
            cherrypy.response.headers['Content-Disposition'] = f'inline; filename={filename}.vv'
            cherrypy.response.headers['Content-Type'] = 'application/x-virt-viewer'
            return file_data.encode('utf-8')
        except Exception as e:
            return str(e)

    @cherrypy.expose
    def console_vnc(self, id=None):
        """Open a VNC console for the provided VM using Proxmox' web console"""
        token = cherrypy.session['proxmox'].proxmox.get_tokens()[0]
        cherrypy.response.cookie['PVEAuthCookie'] = token        
        cherrypy.response.cookie['PVEAuthCookie']._coded_value = token # automatic encoding adds quotes; since these break Proxmox authentication, override automatic quoting
        cherrypy.response.cookie['PVEAuthCookie']['path'] = '/'
        domain = self.cfg.cookie_auth_domain
        if domain is not None:
            cherrypy.response.cookie['PVEAuthCookie']['domain'] = domain
        cherrypy.response.cookie['PVEAuthCookie']['max-age'] = 60
        cherrypy.response.cookie['PVEAuthCookie']['samesite'] = 'Strict' # other values would be 'Lax' and 'None'
        if cherrypy.server.ssl_certificate is not None: # are we running on ssl/tls?
            cherrypy.response.cookie['PVEAuthCookie']['secure'] = 'true'
        cherrypy.response.cookie['PVEAuthCookie']['httponly'] = 'true'
        cherrypy.log(f'Auth cookie set: {cherrypy.response.cookie["PVEAuthCookie"].output()}', context='WEBAPP', severity=logging.DEBUG)
        # Proxmox does e.g. https://192.168.202.16:8006/?console=kvm&novnc=1&vmid=112&vmname=dh-testvm&node=dh-nas6&resize=off&cmd='
        prox = self.cfg.proxmox_api_withport
        vmid, node = cherrypy.session['proxmox'].decompose_id(id)
        raise cherrypy.HTTPRedirect(f'https://{prox}/?console=kvm&novnc=1&vmid={vmid}&node={node}&resize=off&cmd=')

    @cherrypy.expose
    def start(self, id=None):
        """Trigger start of the provided VM"""
        raise cherrypy.HTTPRedirect('./manage?action_selection=start&' + urlencode([('id', id)]))

    def check_username_and_password(self, username, password):
        """Check whether provided username and password are valid when authenticating"""
        # Shortcut user
        if username == '.':
            username = self.cfg.shortcut_user
            if not len(password):
                password = self.cfg.shortcut_password
        # Add default domain in case no domain provided
        if '@' not in username:
            username += '@' + self.cfg.proxmox_default_auth_domain
        # Connect to ProxmoxAPI with provided credentials and store reference in session
        try:
            try:
                cherrypy.session['proxmox'] = myproxapi.MyProxAPI(self.cfg.proxmox_api, username, password, self.cfg.proxmox_api_verifyssl)
            except proxmoxer.backends.https.AuthenticationError as e:
                cherrypy.log(f'Wrong credentials for user ["{username}"]', context='WEBAPP', severity=logging.INFO, traceback=False)
                return 'invalid username/password'
        except Exception as e:
            cherrypy.log(f'Error accessing ProxmoxAPI by user ["{username}"]: {str(e)}', context='WEBAPP', severity=logging.WARNING, traceback=False)
            #raise # for debugging
            return 'login not possible - please try again later'
        cherrypy.log(f'User ["{username}"] logged in', context='WEBAPP', severity=logging.INFO, traceback=False)
        return # credentials ok; all set

    def login_screen(self, from_page='..', username='', error_msg='', **kwargs):
        """Shows a login form"""
        tmpl = self.jinja_env.get_template('login.html')
        return tmpl.render(from_page=from_page, username=username, error_msg=error_msg).encode('utf-8')

    @cherrypy.expose
    def logout(self):
        """Ends the currently logged-in user's session"""
        username = cherrypy.session['username']
        cherrypy.session.clear()
        cherrypy.response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        cherrypy.response.headers['Pragma'] = 'no-cache'
        cherrypy.response.headers['Expires'] = '0'
        raise cherrypy.HTTPRedirect('/', 302)
        return f'"{username}" has been logged out'

    def on_change_func(self):
        """React on config changes"""
        pass
        cherrypy.log('Error calling on_change_command', context='WEBAPP', severity=logging.ERROR, traceback=False)


def run_webapp(cfg):
    """Runs the CherryPy web application with the provided configuration data"""
    script_path = os.path.dirname(os.path.abspath(__file__))
    app = WebApp(cfg)
    # Configure the web application
    app_conf = {
      'global': {
         'environment' : 'production'
       },
       '/': {
            'tools.sessions.on': True,
            'tools.sessions.secure': (cherrypy.server.ssl_certificate is not None),
            'tools.sessions.httponly': True,
            'tools.staticdir.root': os.path.join(script_path, 'webroot'),
            'tools.session_auth.on': True,
            'tools.session_auth.login_screen': app.login_screen,
            'tools.session_auth.check_username_and_password': app.check_username_and_password,
            },
        '/static': {
            'tools.session_auth.on': False,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        },
        '/favicon.ico':
        {
            'tools.session_auth.on': False,
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(script_path, 'webroot', 'static', 'favicon.ico')
        }
    }
    # Use SSL if certificate files exist
    if os.path.exists(cfg.sslcertfile) and os.path.exists(cfg.sslkeyfile):
        # Use ssl/tls if certificate files are present
        cherrypy.server.ssl_module = 'builtin'
        cherrypy.server.ssl_certificate = cfg.sslcertfile
        cherrypy.server.ssl_private_key = cfg.sslkeyfile
    else:
        cherrypy.log(f'Not using SSL/TLS due to certificate files [{cfg.sslcertfile}] and [{cfg.sslkeyfile}] not being present', context='SETUP', severity=logging.WARNING, traceback=False)
    # Define socket parameters
    cherrypy.config.update({'server.socket_host': cfg.socket_host,
                            'server.socket_port': cfg.socket_port,
                           })
    # Select environment
    cherrypy.config.update({'staging':
                             {
                               'environment' : 'production'
                             }
                           })
    # Start CherryPy
    cherrypy.tree.mount(app, config=app_conf)
    if setupenv.is_root():
        # Drop privileges
        cherrypy.log(f'MyProx was started as root; attempting to drop privileges to user "{cfg.webserver_user}" and group "{cfg.webserver_group}"', context='SETUP', severity=logging.INFO, traceback=False)
        try:
            uid, gid = setupenv.get_uid_gid(cfg.webserver_user, cfg.webserver_group)
        except KeyError:
            cherrypy.log(f'Error dropping privileges to user "{cfg.webserver_user}" and group "{cfg.webserver_group}"; do they exist on your machine? Aborting.', context='SETUP', severity=logging.ERROR, traceback=False)
            exit(1)
        cherrypy.process.plugins.DropPrivileges(cherrypy.engine, umask=0o022, uid=uid, gid=gid).subscribe()
    cherrypy.engine.start()
    cherrypy.engine.signals.subscribe()
    cherrypy.engine.block()


if __name__ == '__main__':
    pass
