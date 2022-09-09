# -*- coding: utf-8 -*-

# Notes:
# - Tags: useful as meta information for e.g., provisioning or config management systems, see https://lists.proxmox.com/pipermail/pve-devel/2019-October/039967.html

import datetime

from . import proxapi


class MyProxAPI(proxapi.ProxAPI):

    def __init__(self, host, user, password, verify_ssl = True):
        """Instance initialization"""
        super().__init__(host, user, password, verify_ssl = verify_ssl)
        self.clear_tag_cache()

    def check_role_VMUserMyProx(self):
        """Check whether the role 'PVEVMUserMyProx' has the required permissions"""
        role = 'PVEVMUserMyProx'
        result = get_role(role)
        if not result:
            # See https://pve.proxmox.com/pve-docs/chapter-pveum.html#_privileges
            raise Exception(f'Proxmox role {role} does not yet exist. Please create it under "Datacenter"|"Permissions"|"Roles" and assign (at least) permissions "VM.Console", "VM.PowerMgmt", and "VM.Audit" to it.')
        if result.get('VM.PowerMgmt', 0) != 1: # needed to manage the status of the machine, e.g. start and stop it
            raise Exception(f'Proxmox role {role} needs to have "VM.PowerMgmt" permission assigned to it.')
        if result.get('VM.Console', 0) != 1: # needed to get access to the VM console
            raise Exception(f'Proxmox role {role} needs to have "VM.Console" permission assigned to it.')
        if result.get('VM.Audit', 0) != 1: # needed to read basic information
            raise Exception(f'Proxmox role {role} needs to have "VM.Audit" permission assigned to it.')

    def clear_tag_cache(self):
        """Clears the tag cache"""
        self._cache_id = None
        self._cache_tags = None

    def get_tags_direct(self, id):
        """Get a dictionary of all the tags assigned to a given virtual machine"""
        # Requires: ["perm","/vms/{vmid}",["VM.Audit"]]
        vmid, node = self.decompose_id(id)
        tags = self.proxmox.nodes(node).qemu(vmid).config.get().get('tags')
        if tags is None:
            tags = ''
        tags = tags.split(',')
        tags = [ tag.partition('.') for tag in tags ]
        tags = { key.strip(): value.strip() for key, _, value in tags }
        return tags        

    def get_tags(self, id):
        """Get a dictionary of all the tags assigned to a given virtual machine using tag cache"""
        if (self._cache_id is None) or (self._cache_tags is None) or (self._cache_id != id):
            self._cache_tags = self.get_tags_direct(id)
            self._cache_id = id
        return self._cache_tags 

    def set_tags(self, id, tags):
        """Overwrite the tags of a given virtual machine based on a dictionary of all the new tags"""
        # Requires permission: (/vms/{vmid}, VM.Config.Options)
        vmid, node = self.decompose_id(id)
        # Convert dict to string representation
        tags = [ {key} if (value is None) or (len(value) == 0) else f'{key}.{value}' for key, value in tags.items() ]
        tags = ', '.join(tags)
        self.proxmox.nodes(node).qemu(vmid).config.put(tags=tags)

    def ensure_tag_set(self, id, tag, value):
        """Make sure that the tags of a given virtual machine has the specified one set to a desired value"""
        tags = self.get_tags(id)
        tags[tag] = value
        return self.set_tags(id, tags)
        
    def ensure_tag_unset(self, id, tag):
        """Make sure that the tags of a given virtual machine don't include the specified one"""
        tags = self.get_tags(id)
        tags.pop(tag, None)
        return self.set_tags(id, tags)

    def get_tag_expiry(self, id):
        """Returns the value of the expiry tag"""
        tags = self.get_tags(id)
        expiry = tags.get('myprox_expiry')
        if expiry is not None:
            expiry = datetime.date.fromisoformat(expiry)
        return expiry

    def set_tag_expiry(self, id, newdate):
        """Sets the value of the expiry tag"""
        return self.ensure_tag_set(id, 'myprox_expiry', newdate.isoformat())

    def set_tag_expiry_bydays(self, id, days=365):
        """Sets the value of the expiry tag to the given number of days in the future"""
        newdate = datetime.date.today()+datetime.timedelta(days=days)
        return self.set_tag_expiry(id, newdate)

    def get_virtual_machine_with_tags(self, id):
        """Return the data of the given virtual machine (id format: 'vmid@node') incl. certain tags"""
        data = self.get_virtual_machine(id)
        if data is not None:
            self.clear_tag_cache()
            data['tag_expiry'] = self.get_tag_expiry(id)
        return data
