# MyProx

A simple web frontend for accessing and managing VMs running on Proxmox VE. It is targeted on end-users.

---

## Main Features

- List all VMs a user has permissions on
- Manage VM state, e.g. starting and stopping
- Open SPICE console (virt-viewer)
- Authentication against Proxmox (username/password, OIDC)
- Support connecting to multiple Proxmox nodes/clusters
- Web frontend has responsive design
- Does not require root privileges
- Built on light-weight CherryPy framework
- No JavaScript bloat; no external font/JS includes
- Simple installation using pip, few dependencies

---

## Installation

Install using PyPi:

```shell
pip3 install myprox
```

---

## Quickstart

After installing "MyProx" as shown above, just execute the tool to get it running:

```shell
myprox
```

Configuration can be done in the file `/etc/myprox/myprox.conf`. A commented example file can be downloaded at <a href="https://github.com/towalink/myprox/blob/main/src/myprox/templates/myprox.conf" target="_blank">https://github.com/towalink/myprox/blob/main/src/myprox/templates/myprox.conf</a>.

---

## Screenshots

<img src="https://raw.githubusercontent.com/towalink/myprox/main/screenshots/list-machines.png" width="450" alt="screenshot: show list of VMs">

See additional screenshots in the "screenshots" folder.

---

## Special features

### Support for OIDC authentication

If your Proxmox installation is set up to authenticate against an OIDC provider like Keycloak, you can still use MyProx. MyProx still authenticates against your Proxmox cluster but no longer based on username and password.

You need to set the URL of your MyProx installation as a valid redirect URL in the Proxmox client configuration of your identity provider, e.g. `https://myprox.mydomain.de/redirect_uri`. Then set the OIDC related options, at least the Proxmox realm to be used. Now you can leave username and password fields empty in the login form to authenticate against your OIDC provider.

---

## Reporting bugs

In case you encounter any bugs, please report the expected behavior and the actual behavior so that the issue can be reproduced and fixed.

---

## Developers

### Clone repository

Clone this repo to your local machine using `https://github.com/towalink/myprox.git`

Install the module temporarily to make it available in your Python installation:
```shell
pip3 install -e <path to directory with setup.py>
```

---

## License

[![License](http://img.shields.io/:license-agpl3-blue.svg?style=flat-square)](https://opensource.org/licenses/AGPL-3.0)

- **[AGPL3 license](https://opensource.org/licenses/AGPL-3.0)**
- Copyright 2022 © <a href="https://github.com/towalink/myprox" target="_blank">Dirk Henrici</a>.
- Note: This project is not affiliated with [Proxmox](https://www.proxmox.com/), it just accesses its REST API.
