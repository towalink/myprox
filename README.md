# MyProx

A simple web frontend for accessing and managing VMs running on Proxmox VE. It is targeted on end-users.

---

## Main Features

- List all VMs a user has permissions on
- Manage VM state, e.g. starting and stopping
- Open SPICE console (virt-viewer)
- Authentication against Proxmox
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
