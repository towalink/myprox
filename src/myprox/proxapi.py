#!/usr/bin/env python3

# ProxmoxAPI documentation: see https://pve.proxmox.com/pve-docs/api-viewer/

import proxmoxer


class ProxAPI():

    def __init__(self, host, user, password, verify_ssl = True):
        """Object initialization: set API parameters"""
        self.proxmox = proxmoxer.ProxmoxAPI(host, user=user, password=password, verify_ssl=verify_ssl)

    def int2human(self, value, decimal_places = -1):
        """Convert integer value to human readable one with 'K'/'M'/'G'/'T'"""
        letter = ''
        if value >= 1024:
            value /= 1024
            letter = 'K'
        if value >= 1024:
            value /= 1024
            letter = 'M'
        if value >= 1024:
            value /= 1024
            letter = 'G'
        if value >= 1024:
            value /= 1024
            letter = 'T'
        if decimal_places == -1: # automatically choose based on detail assumed to be needed
            decimal_places = 0 if value >= 10 else 1
        value = round(value, decimal_places)
        format = f'.{decimal_places}f'
        return f'{value:{format}}{letter}'
    
    def uptime2human(self, value, decimal_places = -1, lang = 'en'):
        """Convert uptime value to human readable one with 'seconds'/'minutes'/'hours'/'days'"""
        if value == 0:
            return 'n/a'
        unit = 'Sekunden' if lang == 'de' else 'seconds'
        if value >= 60:
            value /= 60
            unit = 'Minuten' if lang == 'de' else 'minutes'
        if value >= 60:
            value /= 60
            unit = 'Stunden' if lang == 'de' else 'hours'
            if value >= 24:
                value /= 24
                unit = 'Tage' if lang == 'de' else 'days'
        if decimal_places == -1: # automatically choose based on detail assumed to be needed
            decimal_places = 0 if value >= 10 else 1
        value = round(value, decimal_places)
        format = f'.{decimal_places}f'
        return f'{value:{format}} {unit}'
    
    def decompose_id(self, id):
        """Returns the vmid and node part of the provided id (format: 'vmid@node')"""
        if id is None:
            raise ValueError('No vmid provided')
        vmid, _, node = id.partition('@')
        if (node is not None) and (not len(node)):
            node = None    
        return vmid, node
    
    def get_role(self, role):
        """Gets data regarding the specified role"""
        try:
            # all roles: proxmox.access.roles.get()
            # single role: proxmox.access.roles(role).get())
            result = self.proxmox.access.roles(role).get()
        except proxmoxer.core.ResourceException as e:
            err = str(e) # proxmoxer.core.ResourceException: 500 Internal Server Error: role 'MyRole' does not exist
            if 'does not exist' in err:
                return False
            raise
        return result
    
    def get_nodes(self):
        return self.proxmox.nodes.get()

    def get_virtual_machines(self, node=None, vmid=None, full=False):
        """Return the data of the available virtual machines (or filter to return data of VMs on single node or just the data of a single VM)"""
        result = dict()
        for current_node in ([{'node': node}] if node is not None else self.proxmox.nodes.get()):
            if current_node.get('status', 'online') != 'online': # one can't query non-online nodes
                continue
            # Works similarly for LXC:
            # for vm in self.proxmox.nodes(current_node["node"]).lxc.get():
            #     print("{0}: {1} => {2}".format(vm["vmid"], vm["name"], vm["status"]))
            #     print('Uptime:', uptime2human(vm['uptime']))
            for vm in self.proxmox.nodes(current_node['node']).qemu.get(full=(1 if full else 0)):
                item = vm.copy() #item = { key: value for key, value in vm.items() }
                item['node'] = current_node['node']
                item['mem_human'] = self.int2human(vm['mem'])
                item['maxmem_human'] = self.int2human(vm['maxmem'])
                if (item['mem_human'] == item['maxmem_human']) or (vm['mem'] == 0):
                    item['memrange'] = item['maxmem_human']
                else:
                    item['memrange'] = item['mem_human'] + ' of ' + item['maxmem_human']
                item['maxdisk_human'] = self.int2human(vm['maxdisk'])
                item['uptime_human'] = self.uptime2human(vm['uptime'])
                if item['status'] == 'running':
                    item['status_uptime'] = item['status'] + ' for ' + item['uptime_human']
                elif item['status'] == 'stopped':
                    item['status_uptime'] = item['status']
                else:
                    item['status_uptime'] = item['status'] + ', up for ' + item['uptime_human']
                result[vm['vmid']] = item
        if vmid is not None:
            return result[int(vmid)]
        return result            

    def get_virtual_machine(self, id, full=False):
        """Return the data of the given virtual machine (id format: 'vmid@node')"""
        vmid, node = self.decompose_id(id)
        result = self.get_virtual_machines(node=node, vmid=vmid, full=full)
        return result

    def get_spice(self, id):
        """Gets the content of a SPICE connection file"""
        vmid, node = self.decompose_id(id)        
        try:
            result = self.proxmox.nodes(node).qemu(vmid).spiceproxy.post()
        except proxmoxer.core.ResourceException as e:
            err = str(e)
            if 'not running' in err:
                raise Exception(f'VM {vmid} on {node} not running [{err}]')
            elif 'no spice port' in err:
                raise Exception(f'VM {vmid} on {node} does not use SPICE [{err}]')
            else:
                raise
        return result

    def trigger_vm_action(self, id, action):
        """Triggers an action (status change) on the given VM"""
        vmid, node = self.decompose_id(id)
        if action == 'start':
            self.proxmox.nodes(node).qemu(vmid).status.start.post()
        elif action == 'reboot':
            self.proxmox.nodes(node).qemu(vmid).status.reboot.post()
        elif action == 'shutdown':
            self.proxmox.nodes(node).qemu(vmid).status.shutdown.post()
        elif action == 'reset':
            self.proxmox.nodes(node).qemu(vmid).status.reset.post()
        elif action == 'stop':
            self.proxmox.nodes(node).qemu(vmid).status.stop.post()
        elif action == 'suspend':
            self.proxmox.nodes(node).qemu(vmid).status.suspend.post()
        elif action == 'resume':
            self.proxmox.nodes(node).qemu(vmid).status.resume.post()
