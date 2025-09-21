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
            self._config = cfg
        except Exception as e:
            logger.warning('Config file [{0}] could not be read [{1}], using defaults'.format(self.filename, str(e)))
            self._config = dict()

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
    def nodes(self):
        """Return a dictionary of nodes (config sections except 'myprox') with their captions"""
        nodes = dict()
        for section in self.config.sections():
            if section != 'myprox':
                nodes[section] = self.config[section].get('caption', '[unnamed node]')
        return nodes

    def get(self, itemname, default=None, node=None):
        """Return a specific item from the configuration or the provided default value if not present; section 'myprox' provides defaults"""
        value = None
        if node is not None:
            if node in self.nodes:
                value = self.config[node].get(itemname, None)
            else:
                logger.warn(f'Attempt to get config item [{itemname}] for an undefined node [{node}]')
        if value is None:
            value = self.config['myprox'].get(itemname, default)
        return value

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
        return self.get('socket_host', '::')

    @property
    def socket_port(self):
        """The port to listen on"""
        return int(self.get('socket_port', 8080))

    @property
    def webserver_user(self):
        """In case MyProx is started as root, drop privileges to the given user for increased security"""
        return self.get('webserver_user', 'myprox')

    @property
    def webserver_group(self):
        """In case MyProx is started as root, drop privileges to the given group for increased security"""
        return self.get('webserver_group', 'myprox')

    @property
    def environment(self):
        """Defines the CherryPy runtime environment"""
        return self.get('environment', 'development')

    def proxmox_api(self, node):
        """The hostname/IP address of the Proxmox API"""
        return self.get('proxmox_api', 'localhost', node)

    def proxmox_api_withport(self, node):
        """The hostname/IP address of the Proxmox API including port number"""
        result = self.proxmox_api(node)
        # Note: The following won't work with IPv6 addresses; we currently don't care since hostnames are usually used anyway
        if ':' not in result:
            result += ':8006'
        return result

    def proxmox_api_verifyssl(self, node):
        """Whether to check the ssl certificate of the Proxmox API"""
        return self.is_true(self.get('proxmox_api_verifyssl', 0, node))

    def proxmox_default_auth_domain(self, node):
        """Default authentication domain for the case that no domain is explicitly provided"""
        return self.get('proxmox_default_auth_domain', 'pve', node)
        
    def cookie_auth_domain(self, node):
        """The joint domain of MyProx and Proxmox to be set in an authentication cookie (used for authentication Proxmox' VNC client)"""
        domain = self.get('cookie_auth_domain', 'auto', node)
        if domain == 'auto':
            domain = self.proxmox_api # e.g. "myprox.prox.mydomain.com" or "192.168.1.0"
            parts = domain.rsplit('.', 2) # e.g. ['myprox.prox', 'mydomain', 'com'] or ['192.168', '1', '0']
            if not parts[-1].isnumeric(): # no IP address?
                domain = '.'.join(parts[-2:]) # e.g. "mydomain.com"
            # Don't set domain in case the default "localhost" is set
            if domain == 'localhost':
                domain = None
        return domain

    def shortcut_user(self, node):
        """The user to be used in case '.' is provided as username"""
        return self.get('shortcut_user', '', node)

    def shortcut_password(self, node):
        """The password to be used in case '.' is provided as username and no password given"""
        return self.get('shortcut_password', '', node)

    def machine_creation_url(self, node):
        """Email URL to be used for creating a machine"""
        return self.get('machine_creation_url', 'mailto:myadmin@mydomain.local?subject=New machine request&body=User: {username}', node)

    def expiry_prolongation_days(self, node):
        """Number of days from today when setting a new expiry date"""
        return int(self.get('expiry_prolongation_days', 365, node))

    def dryrun(self, node):
        """Define whether to disable sending any writing/changing requests to Proxmox API"""
        return self.is_true(self.get('dryrun', 0, node))
