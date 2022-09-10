#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import grp
import os
import pwd


def is_root():
    """Returns whether this script is run with user id 0 (root)"""
    return os.getuid() == 0

def get_uid_gid(uid_name='nobody', gid_name='nogroup'):
    """Returns uid and gid for the given username and groupname"""
    uid = pwd.getpwnam(uid_name).pw_uid
    gid = grp.getgrnam(gid_name).gr_gid
    return uid, gid
