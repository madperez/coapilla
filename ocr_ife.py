#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 12:49:03 2020

@author: nautica
"""
import pytesseract
from pytesseract import Output

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
        self.corrige_orientacion()
        self.image_cv = numpy.array(self.image)
        self.image_bin=self.binariza_imagen()
        self.result_gray=pytesseract.image_to_string(self.image)
        self.result_bin=pytesseract.image_to_string(self.image_bin)
        self.result_dict = pytesseract.image_to_data(self.image, output_type=Output.DICT)
        self.ciudad=''
        self.colonia=''
        self.domicilio=''
        self.curp=''
        self.fecha_nacimiento=datetime.date.today()
        self.clave_elector=''
        self.anio_registro=''
        self.seccion=''
        self.vigencia=''
        self.busca_fecha_nacimiento()
        self.sexo=self.busca_sexo()
        self.apellido_paterno,self.apellido_materno,self.nombre=self.busca_nombre()
    def binariza_imagen(self):
        # Otsu's thresholding
        print('binarizando')
        ret2,th2 = cv.threshold(self.image_cv,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
        cv.imwrite('imbin.jpg',th2)
        #cv.imshow('binarizacion',th2)
        #cv.waitKey()
        return th2
    def corrige_orientacion(self):
        print('orientando')
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
    def busca_fecha_nacimiento(self):
        regex = re.compile('../../....')
        qty_data=len(self.result_dict['text'])
        for i in range(qty_data):
            palabra=self.result_dict['text'][i]
            if re.match(regex,palabra):
                date_time_obj=datetime.datetime.strptime(palabra+' 7:40AM','%d/%m/%Y %I:%M%p')
                self.fecha_nacimiento=date_time_obj.date()

    def busca_sexo(self):
        qty_data=len(self.result_dict['text'])
        flag=False
        sexo=''
        for i in range(qty_data):
            palabra=self.result_dict['text'][i].lower()
            if palabra=='sexo':
                flag=True
            if flag==True and palabra=='h' or palabra=='m':
                sexo=palabra
        return sexo
    def busca_nombre(self):
        # estos datos se encuentran cerca de la etiqueta nombre, se usa su coordenada para buscarlo
        qty_data=len(self.result_dict['text'])
        flag=False
        flag_paterno=False
        flag_materno=False
        flag_nombre=False
        paterno=''
        materno=''
        nombre=''
        for keys,value in self.result_dict.items():
            print(keys,value)
        for i in range(qty_data):
            palabra=self.result_dict['text'][i].lower()
            if flag==True:
                if self.result_dict['left'][i]>left_nombre-10 and self.result_dict['left'][i]<left_nombre+10:
                    if flag_nombre==False and flag_materno==True and palabra!='':
                        nombre=self.result_dict['text'][i]
                        flag_nombre=True
                    if flag_materno==False and flag_paterno==True and palabra!='':
                        materno=self.result_dict['text'][i]
                        flag_materno=True
                    if flag_paterno==False and palabra!='':
                        paterno=self.result_dict['text'][i]
                        flag_paterno=True
            if palabra=='nombre':
                flag=True
                print(self.result_dict['left'][i],self.result_dict['top'][i])
                left_nombre=self.result_dict['left'][i]
        return paterno,materno,nombre

    def busca_direccion(self):
        # estos datos se encuentran cerca de la etiqueta direccion, se usa su coordenada para buscarlo
        qty_data=len(self.result_dict['text'])
        flag=False
        flag_direccion=False
        flag_colonia=False
        flag_municipio=False
        direccion=''
        colonia=''
        municipio=''
        codigo_postal=''
        estado=''
        for i in range(qty_data):
            palabra=self.result_dict['text'][i].lower()
            if flag==True:
                if self.result_dict['left'][i]>left_nombre-10 and self.result_dict['left'][i]<left_nombre+10:
                    if flag_municipio==False and flag_colonia==True and palabra!='':
                        municipio+=self.result_dict['text'][i]
                        if self.result_dict['top'][i]>=top_direccion-10 and self.result_dict['top'][i]<=top_direccion-10:
                            pass
                        else:
                            print('municipio: ',municipio)
                            flag_municipio=True
                    if flag_colonia==False and flag_direccion==True and palabra!='':
                        colonia+=self.result_dict['text'][i]
                        if self.result_dict['top'][i]>=top_direccion-10 and self.result_dict['top'][i]<=top_direccion-10:
                            pass
                        else:
                            print('colonia: ',colonia)
                            flag_colonia=True
                            top_direccion=self.result_dict['top'][i]
                    if flag_direccion==False and palabra!='':
                        direccion+=self.result_dict['text'][i]
                        if self.result_dict['top'][i]>=top_direccion-10 and self.result_dict['top'][i]<=top_direccion-10:
                            pass
                        else:
                            print('direccion: ',direccion)
                            flag_direccion=True
                            top_direccion=self.result_dict['top'][i]
            if palabra=='domicilio':
                flag=True
                print('domicilio detectado', self.result_dict['left'][i],self.result_dict['top'][i])
                left_nombre=self.result_dict['left'][i]
                top_direccion=self.result_dict['top'][i]
        return direccion

def ocr_ife(media_image):
    
  pil_image=Image.open(BytesIO(media_image.get_bytes())).convert('L')
  miife=ife(pil_image)
  #miife.corrige_orientacion()
  #miife.lee_caracteres()
  print(miife.result_bin)
  d = miife.result_gray
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
      if 'vigencia' in i.lower():
        flag_nacimiento=True
        palabra=''
      if 'registro' in i.lower():
        flag_curp=True
        palabra=''
  print('resultado ',miife.fecha_nacimiento,miife.sexo)
  print('nombre',miife.apellido_paterno,miife.apellido_materno,miife.nombre)
  print('direccion',direccion,colonia,ciudad)
  print(clave_elector)
  print(curp,ano_registro)
  print(fecha_nacimiento,seccion,vigencia)
  if len(clave_elector)>1:
    app_tables.dbclientes.add_row(anio_registro=ano_registro,ciudad=ciudad,clave_elector=clave_elector,colonia=colonia,curp=curp,direccion=direccion,
                                  fecha_nacimiento=date_time_obj.date(),materno=materno,nombre=nombre,paterno=paterno,seccion=seccion,vigencia=vigencia,ife=media_image,codigo_postal=cp)
    status=True
    anvil.server.call('save_ife',media_image,clave_elector)
  else:
    status=False
  return status, paterno+materno+nombre
