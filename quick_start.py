#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 09:32:41 2020

@author: nautica
"""

from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
