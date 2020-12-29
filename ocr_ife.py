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
        self.curp=''
        self.clave_elector=''
        self.anio_registro=''
        self.seccion=''
        self.vigencia=''
        self.identidad={}
        self.identidad['fecha_nacimiento']=self.busca_fecha_nacimiento()
        self.identidad['sexo']=self.busca_sexo()
        self.apellido_paterno,self.apellido_materno,self.nombre=self.busca_nombre()
        self.identidad['nombre']={'nombre':self.nombre,'paterno':self.apellido_paterno,'materno':self.apellido_materno}
        self.dict_documento=self.crea_lineas()
        self.identidad['direccion']=self.busca_direccion()
        self.identidad['clave_elector']=self.busca_clave_elector()
        self.identidad['curp'],tmp=self.busca_curp()
    def busca_curp(self):
        # modelo 1 en un renglon solo la curp
        # modelo 2 curp y año de registro en el mismo renglon
        # modelo 3 leyendas curp y año de registro en un renglon y los datos en el siguiente renglon
        homoclave=self.identidad['fecha_nacimiento'].strftime("%Y")[-2:]+self.identidad['fecha_nacimiento'].strftime("%m")+self.identidad['fecha_nacimiento'].strftime("%d")
        homoclave_curp=self.identidad['fecha_nacimiento'].strftime("%Y")[-2:]+self.identidad['fecha_nacimiento'].strftime("%m")+self.identidad['fecha_nacimiento'].strftime("%d")+self.identidad['sexo']
        print('buscando homoclave:--',homoclave,homoclave_curp)
        curp=''
        clave_elector=''
        rango=len(self.result_dict['text'])
        for i in range(rango):
            palabra=self.result_dict['text'][i].lower()
            if len(palabra)==18:
                print(palabra,palabra[1])
                if palabra[1]=="a" or palabra[1]=="e" or palabra[1]=="i" or palabra[1]=="o" or palabra[1]=="u":
                    print('curp detectada')
                    curp=palabra
                else:
                    clave_elector=palabra
        print('curp, clave elector',curp,clave_elector)
        return curp,clave_elector
    def busca_clave_elector(self):
        documento=self.dict_documento
        clave_elector=''
        for keys,values in documento.items():
            print(keys,values)
            if 'elector' in values:
                clave_elector=values.split()[-1]
                if len(clave_elector)<18:
                    lista=values.split()[-2:]
                    clave_elector=''
                    for i in lista:
                        clave_elector+=i
                    
        return clave_elector
    def datos_ife(self):
        print('datos obtenidos\n')
        print(self.identidad)
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
        fecha_nacimiento=datetime.date.today()
        regex = re.compile('../../....')
        qty_data=len(self.result_dict['text'])
        for i in range(qty_data):
            palabra=self.result_dict['text'][i]
            if re.match(regex,palabra):
                date_time_obj=datetime.datetime.strptime(palabra+' 7:40AM','%d/%m/%Y %I:%M%p')
                fecha_nacimiento=date_time_obj.date()
        return fecha_nacimiento

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

    def crea_lineas(self):
        # transforma la cadena de caracteres con lineas e indicadores de referencia al inicio
        top_direccion=0
        qty_data=len(self.result_dict['text'])
        # construyendo lineas
        frase=''
        documento={}
        lista_top=[]
        for i in range(qty_data):
            if self.result_dict['top'][i]>=top_direccion-10 and self.result_dict['top'][i]<=top_direccion+10:
                frase+=' '+self.result_dict['text'][i].lower()
                documento[top_direccion]=frase
            else:
                frase=''
                lista_top.append(top_direccion)
                top_direccion=self.result_dict['top'][i]
        return documento

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
        top_direccion=0
        # construyendo lineas
        documento=self.dict_documento
        # buscando datos
        for i in range(qty_data):
            palabra=self.result_dict['text'][i].lower()
            if flag==True:
                if self.result_dict['left'][i]>left_nombre-10 and self.result_dict['left'][i]<left_nombre+10:
                    if flag_municipio==False and flag_colonia==True and palabra!='':
                        # busca el mas cercano en caso de que no encuentre el indice
                        top_referencia=self.result_dict['top'][i]
                        diferencia=1000
                        key_cercano=top_referencia
                        for keys,value in documento.items():
                            error=abs(keys-top_referencia)
                            if error<diferencia:
                                diferencia=error
                                key_cercano=keys
                        municipio_estado=documento[key_cercano].split()
                        estado=municipio_estado[-1]
                        municipio_estado.pop()
                        for i in municipio_estado:
                            municipio+=i+' '
                        flag_municipio=True
                    if flag_colonia==False and flag_direccion==True and palabra!='':
                        # busca el mas cercano en caso de que no encuentre el indice
                        top_referencia=self.result_dict['top'][i]
                        diferencia=1000
                        key_cercano=top_referencia
                        for keys,value in documento.items():
                            error=abs(keys-top_referencia)
                            if error<diferencia:
                                diferencia=error
                                key_cercano=keys
                        colonia_cp=documento[key_cercano].split()
                        codigo_postal=colonia_cp[-1]
                        colonia_cp.pop()
                        for i in colonia_cp:
                            colonia+=i+' '
                        flag_colonia=True
                    if flag_direccion==False and palabra!='':
                        print(documento[self.result_dict['top'][i]])
                        direccion=documento[self.result_dict['top'][i]]
                        flag_direccion=True
            if palabra=='domicilio':
                flag=True
                left_nombre=self.result_dict['left'][i]
        return {'direccion':direccion,'colonia':colonia,'cp':codigo_postal,'municipio':municipio,'estado':estado}

def ocr_ife(media_image):
    
  pil_image=Image.open(BytesIO(media_image.get_bytes())).convert('L')
  miife=ife(pil_image)
  #miife.corrige_orientacion()
  #miife.lee_caracteres()
  print(miife.result_bin)
  miife.datos_ife()
  #if len(miife.identidad['clave_elector'])>1:
    #app_tables.dbclientes.add_row(anio_registro=ano_registro,ciudad=ciudad,clave_elector=clave_elector,colonia=colonia,curp=curp,direccion=direccion,
     #                             fecha_nacimiento=date_time_obj.date(),materno=materno,nombre=nombre,paterno=paterno,seccion=seccion,vigencia=vigencia,ife=media_image,codigo_postal=cp)
   # status=True
    #anvil.server.call('save_ife',media_image,clave_elector)
  #else:
   # status=False
  parameters=[]
  return True,parameters.append(miife.identidad)
