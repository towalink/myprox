#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""myprox.py: easy-to-use web-based user interface for Proxmox VE."""

"""
Copyright (C) 2022 Dirk Henrici

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Dirk Henrici"
__license__ = "AGPL3" # + author has right to release in parallel under different licenses
__email__ = "myprox@henrici.name"


from . import config
from . import webapp


def main():
    cfg = config.Configuration()
    webapp.run_webapp(cfg)


if __name__ == '__main__':
    main()
