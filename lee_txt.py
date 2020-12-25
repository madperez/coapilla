#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 19:44:19 2020

@author: nautica

"""
import subprocess
from bs4 import BeautifulSoup
  
subprocess.call(["tesseract", "./ife/ife1.jpg","text_result"])
flagp=False
flagm=False
flagn=False
flag_ciudad=False
flag_colonia=False
flag_domicilio=False
flag_curp=False
flag_nacimiento=False
paterno=''
with open('text_result.txt') as f:
    lines = f.readlines()
    print(lines)
    for i in lines:
        soup=BeautifulSoup(i)
        text=soup.get_text()
        tokens=text.split()
        if flagn==True:
            if len(i)>1:
                nombre=i
                flagn=False
        if flagm==True:
            if len(i)>1:
                materno=i
                flagm=False
                flagn=True
        if flagp==True:
            if len(i)>1:
                paterno=i
                flagp=False
                flagm=True
        if flag_ciudad==True:
            if len(i)>1:
                ciudad=i
                flag_ciudad=False
        if flag_colonia==True:
            if len(i)>1:
                colonia=i
                flag_colonia=False
                flag_ciudad=True
        if flag_domicilio==True:
            if len(i)>1:
                direccion=i
                flag_domicilio=False
                flag_colonia=True
        if flag_curp==True:
            if len(i)>1:
                curp=tokens[0]
                ano_registro=tokens[1]
                flag_curp=False
        if 'nombre' in i.lower():
            flagp=True
        if i.lower()=='domicilio\n'.lower():
            flag_domicilio=True
        if 'elector' in i.lower():
            for palabras in tokens:
                if 'elector' not in palabras.lower():
                    clave_elector=palabras
        if flag_nacimiento==True:
            fecha_nacimiento=tokens[0]
            seccion=tokens[1]
            vigencia=tokens[2]+'-'+tokens[3]
            flag_nacimiento=False
        if 'nacimiento' in i.lower():
            flag_nacimiento=True
        if 'curp' in i.lower():
            flag_curp=True
print(paterno,materno,nombre)
print(direccion,colonia,ciudad)
print(clave_elector)
print(curp,ano_registro)
print(fecha_nacimiento,seccion,vigencia)