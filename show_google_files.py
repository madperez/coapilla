#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 09:54:14 2020

@author: nautica
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# Rename the downloaded JSON file to client_secrets.json
# The client_secrets.json file needs to be in the same directory as the script.
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
# List files in Google Drive
#file1 = drive.CreateFile({'title': 'Hello.txt'})
#file1.SetContentString('Hello')
#file1.Upload() # Files.insert()
#file2 = drive.CreateFile({'id': '1TfpYBdJyjHiTMlvYJi0t759CsgwkpbKL'})
#file2.GetContentString('Hello.txt')
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
  print('title: %s, id: %s' % (file1['title'], file1['id']))
  