# -*- coding: utf-8 -*-

import configparser
import logging
import os
import textwrap


logger = logging.getLogger(__name__)

config_filename = '/etc/myprox/myprox.conf'


class Configuration():
    """Class for reading/writing the configuration file"""
    _config = None

    def exists(self):
        """Checks whether the config file exists"""
        return os.path.isfile(self.filename)
  
    def read_config(self):
        """Reads the config file"""
        try:
            logger.debug('Attempting to read config file [{0}]'.format(self.filename))
            cfg = configparser.ConfigParser()
            cfg.read(self.filename)
            self._config = dict(cfg['myprox'])
        except Exception as e:
            logger.warning('Config file [{0}] could not be read [{1}], using defaults'.format(self.filename, str(e)))
            self._config = dict()
    
#    def write_config(self, configfile=''):
#        """Writes a new config file with the given attributes"""
#        # Set default values
#        if not configfile.strip():
#            configfile = '/etc/myprox/myprox.conf'
#        # Config file content
#        config_content = textwrap.dedent(f'''\
#            ### MyProx config file ###
#            [general]
#            # *** use templates/myprox.conf instead ***
#        ''')
#        # Write to file system
#        try:
#            with open(self.filename, 'w') as config_file:
#                config_file.write(config_content)
#        except OSError as e:
#            logger.error('Could not write config file [{0}], [{1}]'.format(self.filename, str(e)))

    def is_true(self, value):
        """Checks whether the given value evaluates to True"""
        value = str(value).lower()
        return value not in ['0', 'false']

    @property
    def filename(self):
        """Return the name of the config file (incl. path)"""
        return config_filename

    @property
    def config(self):
        """Return the config dictionary"""
        if self._config is None:
            self.read_config()
        return self._config

    @property
    def sslcertfile(self):
        """The filename incl. path for the server certificate"""
        return os.path.join(os.path.dirname(self.filename), 'server.pem')

    @property
    def sslkeyfile(self):
        """The filename incl. path for the server private key"""
        return os.path.join(os.path.dirname(self.filename), 'key.pem')

    @property
    def socket_host(self):
        """The address to bind to"""
        return self.config.get('socket_host', '::')

    @property
    def socket_port(self):
        """The port to listen on"""
        return int(self.config.get('socket_port', 8080))

    @property
    def proxmox_api(self):
        """The hostname/IP address of the Proxmox API"""
        return self.config.get('proxmox_api', 'localhost')

    @property
    def proxmox_api_withport(self):
        """The hostname/IP address of the Proxmox API including port number"""
        result = self.proxmox_api
        # Note: The following won't work with IPv6 addresses; we currently don't care since hostnames are usually used anyway
        if ':' not in result:
            result += ':8006'
        return result

    @property
    def proxmox_api_verifyssl(self):
        """Whether to check the ssl certificate of the Proxmox API"""
        return self.is_true(self.config.get('proxmox_api_verifyssl', 0))

    @property
    def proxmox_default_auth_domain(self):
        """Whether to check the ssl certificate of the Proxmox API"""
        return self.config.get('proxmox_default_auth_domain', 'pve')
        
    @property
    def cookie_auth_domain(self):
        """The joint domain of MyProx and Proxmox to be set in an authentication cookie (used for authentication Proxmox' VNC client)"""
        domain = self.config.get('cookie_auth_domain', 'auto')
        if domain == 'auto':
            domain = self.proxmox_api # e.g. "myprox.prox.mydomain.com" or "192.168.1.0"
            parts = domain.rsplit('.', 2) # e.g. ['myprox.prox', 'mydomain', 'com'] or ['192.168', '1', '0']
            if not parts[-1].isnumeric(): # no IP address?
                domain = '.'.join(parts[-2:]) # e.g. "mydomain.com"
            # Don't set domain in case the default "localhost" is set
            if domain == 'localhost':
                domain = None
        return domain

    @property
    def webserver_user(self):
        """In case MyProx is started as root, drop privileges to the given user for increased security"""
        return self.config.get('webserver_user', 'myprox')

    @property
    def webserver_group(self):
        """In case MyProx is started as root, drop privileges to the given group for increased security"""
        return self.config.get('webserver_group', 'myprox')

    @property
    def shortcut_user(self):
        """The user to be used in case '.' is provided as username"""
        return self.config.get('shortcut_user', '')

    @property
    def shortcut_password(self):
        """The password to be used in case '.' is provided as username and no password given"""
        return self.config.get('shortcut_password', '')

    @property
    def machine_creation_url(self):
        """Email URL to be used for creating a machine"""
        return self.config.get('machine_creation_url', 'mailto:myadmin@mydomain.local?subject=New machine request&body=User: {username}')

    @property
    def expiry_prolongation_days(self):
        """Number of days from today when setting a new expiry date"""
        return int(self.config.get('expiry_prolongation_days', 365))

    @property
    def dryrun(self):
        """Define whether to disable sending any writing/changing requests to Proxmox API"""
        return self.is_true(self.config.get('dryrun', 0))
