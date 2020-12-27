#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 12:49:03 2020

@author: nautica
"""
import pytesseract
from PIL import Image
from io import BytesIO
import datetime
from bs4 import BeautifulSoup
import re
import cv2 as cv
import numpy
class ife():
    def __init__(self,image):
        self.image=image
        self.image_cv = numpy.array(self.image)
        self.image_bin=self.binariza_imagen()
        self.result=''
        self.apellido_paterno=''
        self.apellido_materno=''
        self.nombre=''
        self.ciudad=''
        self.colonia=''
        self.domicilio=''
        self.curp=''
        self.fecha_nacimiento=datetime.date.today()
        self.clave_elector=''
        self.anio_registro=''
        self.seccion=''
        self.vigencia=''
        self.corrige_orientacion()
        self.lee_caracteres()
        self.busca_fecha_nacimiento()
        self.busca_sexo()
        self.sexo=''
    def binariza_imagen(self):
        # Otsu's thresholding
        ret2,th2 = cv.threshold(self.image_cv,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        #cv.imshow('binarizacion',th2)
        #cv.waitKey()
        return th2
    def corrige_orientacion(self):
        result=pytesseract.image_to_osd(self.image)
        soup=BeautifulSoup(result)
        text=soup.get_text()
        tokens=text.split()
        flag=False
        for i in tokens:
            if flag==True:
                angle_rotation=int(i)
                flag=False
            if 'degrees' in i:
                flag=True
        angle_to_modify=0
        if angle_rotation==270:
            angle_to_modify=90
        elif angle_rotation==180:
            angle_to_modify=0
        self.image=self.image.rotate(angle_to_modify,expand=True)
        self.image.show()
        return(angle_rotation)
    def lee_caracteres(self):
        self.result=pytesseract.image_to_string(self.image_bin)
        #print(self.result)
    def busca_fecha_nacimiento(self):
        regex = re.compile('../../....')
        palabra=''
        for word in self.result:
            if word=='\n' or word==' ':
                palabra=''
            else:
                palabra+=word
            if re.match(regex, palabra):
                self.fecha_nacimiento=palabra
    def busca_sexo(self):
        regex = re.compile('sexo')
        palabra=''
        flag=False
        for word in self.result:
            if word=='\n' or word==' ':
                palabra=''
            else:
                palabra+=word.lower()
            if palabra=='sexo':
                flag=True
            if flag==True and (palabra=='h' or palabra=='m'):
                self.sexo=palabra
                flag=False

def ocr_ife(media_image):
    
  pil_image=Image.open(BytesIO(media_image.get_bytes())).convert('L')
  miife=ife(pil_image)
  #miife.corrige_orientacion()
  #miife.lee_caracteres()
  d = miife.result
  print(d)

  flagp=False
  flagm=False
  flagn=False
  flag_ciudad=False
  flag_colonia=False
  flag_domicilio=False
  flag_curp=False
  flag_nacimiento=False
  flag_elector=False
  paterno=''
  materno=''
  nombre=''
  direccion=''
  colonia=''
  ciudad=''
  clave_elector=''
  palabra=''
  curp=''
  ano_registro=''
  fecha_nacimiento=datetime.date.today()
  seccion=''
  vigencia=''
  cp=''
  for word in d:
    #se juntan las letras
    if word=='\n':
      flag_start=True
    else:
      palabra+=word
      flag_start=False
    if flag_start==True:
      print(palabra)
      i=palabra
      soup=BeautifulSoup(i)
      text=soup.get_text()
      tokens=text.split()
      if flagn==True:
        if len(i)>1:
            nombre=i
            flagn=False
            palabra=''
      if flagm==True:
        if len(i)>1:
            materno=i
            flagm=False
            flagn=True
            palabra=''
      if flagp==True:
        if len(i)>1:
            paterno=i
            flagp=False
            flagm=True
            palabra=''
      if flag_ciudad==True:
        if len(i)>1:
            ciudad=i
            flag_ciudad=False
            palabra=''
      if flag_colonia==True:
        if len(i)>1:
          largo=len(tokens)
          for palabras in range(largo-1):
            colonia+=tokens[palabras]+' '
          cp=tokens[largo-1]
          flag_colonia=False
          flag_ciudad=True
          palabra=''
      if flag_domicilio==True:
        if len(i)>1:
            direccion=i
            flag_domicilio=False
            flag_colonia=True
            palabra=''
      if flag_curp==True:
        if len(i)>1:
            curp=tokens[0]
            ano_registro=tokens[1]
            flag_curp=False
            palabra=''
      if 'nombre' in i.lower():
        flagp=True
        palabra=''
      if 'domicilio' in i.lower():
        flag_domicilio=True
        palabra=''
      if 'elector' in i.lower():
        flag_elector=True
        for palabras in tokens:
          print('--',palabras)
          if 'elector' not in palabras.lower():
             clave_elector=palabras
        palabra=''
      if flag_nacimiento==True:
        fecha_nacimiento=tokens[0]
        seccion=tokens[1]
        vigencia=tokens[2]+'-'+tokens[3]
        flag_nacimiento=False
      if 'vigencia' in i.lower():
        flag_nacimiento=True
        palabra=''
      if 'registro' in i.lower():
        flag_curp=True
        palabra=''
  print(paterno,materno,nombre)
  print(direccion,colonia,ciudad)
  print(clave_elector)
  print(curp,ano_registro)
  print(fecha_nacimiento,seccion,vigencia)
  date_time_obj=datetime.datetime.strptime(fecha_nacimiento+' 7:40AM','%d/%m/%Y %I:%M%p')
  if len(clave_elector)>1:
    app_tables.dbclientes.add_row(anio_registro=ano_registro,ciudad=ciudad,clave_elector=clave_elector,colonia=colonia,curp=curp,direccion=direccion,
                                  fecha_nacimiento=date_time_obj.date(),materno=materno,nombre=nombre,paterno=paterno,seccion=seccion,vigencia=vigencia,ife=media_image,codigo_postal=cp)
    status=True
    anvil.server.call('save_ife',media_image,clave_elector)
  else:
    status=False
  return status, paterno+materno+nombre
