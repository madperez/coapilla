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
from difflib import get_close_matches

class ife():
    def __init__(self,image):
        self.image=image
        self.image_cv = numpy.array(self.image)
        self.corrige_orientacion()
        self.image_bin=self.binariza_imagen()
        self.result_gray=pytesseract.image_to_string(self.image)
        self.result_bin=pytesseract.image_to_string(self.image_bin)
        self.result_dict = pytesseract.image_to_data(self.image, output_type=Output.DICT)
        self.anio_registro=''
        self.seccion=''
        self.vigencia=''
        self.identidad={}
        self.identidad['fecha_nacimiento']=self.busca_fecha_nacimiento()
        self.identidad['sexo']=self.busca_sexo()
        self.identidad['paterno'],self.identidad['materno'],self.identidad['nombre']=self.busca_nombre()
        #self.identidad['nombre']={'nombre':self.nombre,'paterno':self.apellido_paterno,'materno':self.apellido_materno}
        self.dict_documento,self.list_relaciones=self.crea_lineas()
        self.identidad['direccion'],self.identidad['colonia'],self.identidad['codigo_postal'],self.identidad['municipio'],self.identidad['estado']=self.busca_direccion()
        self.identidad['clave_elector']=self.busca_clave_elector()
        self.identidad['curp'],tmp=self.busca_curp()
        self.identidad['folio']=self.busca_folio()
        self.identidad['estado_id']=self.busca_estado()
        self.identidad['anio_registro']=self.busca_registro()
        self.identidad['municipio_id']=self.busca_municipio()
        self.identidad['localidad']=self.busca_localidad()
        self.identidad['seccion']=self.busca_seccion()
        self.identidad['emision']=self.busca_emision()
        self.identidad['vigencia']=self.busca_vigencia()
    def busca_registro(self):
        # se busca algo que suene similar por si falla el ocr
        # el año a veces viene en otro renglon, False
        # el año se pega con el 01, False
        # la palabra año se pega con la palabra de
        registro=''
        flag=False
        for i,value in self.dict_documento.items():
            similar_estado=get_close_matches('registro',value.split())
            if len(similar_estado)>0:
                words=value.split()
                for word in words:
                    if len(word)==4 and word.isdigit():
                        flag=True
                        registro=word
        # lo busca en el renglon de abajo
        if flag==False:
            for relaciones in self.list_relaciones:
                similar_ano=get_close_matches('ano',relaciones[0])
                if len(similar_ano)>0:
                    registro=relaciones[1]
        print(registro)
        return registro
    def busca_municipio(self):
        municipio=''
        regex = re.compile('munici')
        flag=False
        for i,value in self.dict_documento.items():
            for j in value.split():
                similar_municipio=get_close_matches('municipio',j)
                if flag==True:
                    municipio=j
                    flag=False
                if re.match(regex,j):
                    flag=True
                if len(similar_municipio)>0:
                    flag=True
        return municipio
    def busca_vigencia(self):
        # hay tres posibilidades, no hay, solo vigencia o vigencia hasta
        # se buscaran 4 digitos y se buscará el mayor
        anio_actual=datetime.date.today().strftime("%Y")
        municipio=''
        regex = re.compile('vi.encia')
        flag=False
        # busca abajo
        for i in self.list_relaciones:
            similar_localidad=get_close_matches('vigencia',i)
            if len(similar_localidad)>0:
                municipio=i[1]
        # busca a la derecha
        for i,value in self.dict_documento.items():
            for j in value.split():
                if len(j)==4:
                    if j.isdigit():
                        if j>anio_actual:
                            municipio=j
                similar_municipio=get_close_matches('vigencia',j)
                similar_vigencia=get_close_matches('hasta',j)
                if flag==True:
                    if j.isdigit():
                        municipio=j
                    flag=False
                if re.match(regex,j):
                    flag=True
                if len(similar_municipio)>0 or len(similar_vigencia)>0:
                    flag=True
        return municipio
    def busca_emision(self):
        municipio=''
        regex = re.compile('emision')
        flag=False
        for i,value in self.dict_documento.items():
            for j in value.split():
                similar_municipio=get_close_matches('emision',j)
                if flag==True:
                    municipio=j
                    flag=False
                if re.match(regex,j):
                    flag=True
                if len(similar_municipio)>0:
                    flag=True
        return municipio
    def busca_localidad(self):
        localidad=''
        regex = re.compile('.oca...ad')
        flag=False
        for i,value in self.dict_documento.items():
            for j in value.split():
                similar_localidad=get_close_matches('localidad',j)
                if flag==True:
                    localidad=j
                    flag=False
                if re.match(regex,j):
                    flag=True
                if len(similar_localidad)>0:
                    flag=True
        return localidad
    def busca_seccion(self):
        # puede estar a la derecha o abajo de la palabra seccion
        localidad=''
        regex = re.compile('seccion')
        flag=False
        # busca abajo
        for i in self.list_relaciones:
            similar_localidad=get_close_matches('seccion',i)
            if len(similar_localidad)>0:
                localidad=i[1]
        # busca a la derecha
        for i,value in self.dict_documento.items():
            for j in value.split():
                similar_localidad=get_close_matches('seccion',j)
                if flag==True:
                    if j.isdigit():
                        localidad=j
                    flag=False
                if re.match(regex,j):
                    flag=True
                if len(similar_localidad)>0:
                    flag=True
        return localidad
    def busca_estado(self):
        estado=''
        for i,value in self.dict_documento.items():
            similar_estado=get_close_matches('estado',value.split())
            if len(similar_estado)>0:
                words=value.split()
                for word in words:
                    if len(word)==2:
                        estado=word
        return estado
    def busca_folio(self):
        # el folio tiene 13 caracteres de largo
        # todos son numeros
        folio=''
        rango=len(self.result_dict['text'])
        for i in range(rango):
            palabra=self.result_dict['text'][i].lower()
            if len(palabra)==13:
                if palabra.isdigit():
                    folio=palabra
        return folio
    def busca_curp(self):
        # modelo 1 en un renglon solo la curp
        # modelo 2 curp y año de registro en el mismo renglon
        # modelo 3 leyendas curp y año de registro en un renglon y los datos en el siguiente renglon
        # 29/12/20 se busca por el tamaño de la cadena y la regla de la creación de la curp
        # se puede aprovechar la clave de elector obtenida aqui, pero hay que validar que este correcta
        # el sexo se puede obtener de la curp
        # no todas las ifes tienen el campo fecha de nacimiento
        curp=''
        clave_elector=''
        rango=len(self.result_dict['text'])
        for i in range(rango):
            palabra=self.result_dict['text'][i].lower()
            if len(palabra)==18:
                if palabra[1]=="a" or palabra[1]=="e" or palabra[1]=="i" or palabra[1]=="o" or palabra[1]=="u":
                    curp=palabra
                    sexo=palabra[10]
                    if sexo=='h' or sexo=='m':
                        self.identidad['sexo']=sexo
                else:
                    clave_elector=palabra
                if self.identidad['fecha_nacimiento']=='':
                    anio=int(palabra[4:6])
                    if anio<=21:
                        self.identidad['fecha_nacimiento']=palabra[8:10]+'/'+palabra[6:8]+'/20'+palabra[4:6]
                    else:
                        self.identidad['fecha_nacimiento']=palabra[8:10]+'/'+palabra[6:8]+'/19'+palabra[4:6]
                
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
        try:
            result=pytesseract.image_to_osd(self.image)
        except:
            scale_percent = 30
            #calculate the 50 percent of original dimensions
            print(self.image_cv.shape)
            width = int(self.image_cv.shape[1] * scale_percent / 100)
            height = int(self.image_cv.shape[0] * scale_percent / 100)
            # dsize
            dsize = (width, height)
            print(dsize)
            resize_img = cv.resize(self.image_cv, dsize, interpolation=cv.INTER_CUBIC)
            print(resize_img.shape)
            self.image_cv=resize_img.copy()
            print(self.image_cv.shape)
            result=pytesseract.image_to_osd(self.image_cv)
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
        fecha_nacimiento=''
        regex = re.compile('../../....')
        qty_data=len(self.result_dict['text'])
        for i in range(qty_data):
            palabra=self.result_dict['text'][i]
            if re.match(regex,palabra):
                date_time_obj=datetime.datetime.strptime(palabra+' 7:40AM','%d/%m/%Y %I:%M%p')
                fecha_nacimiento=palabra
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
        # 01/01/2021 se establece la relación entre palabras de lineas consecutivas
        top_direccion=0
        qty_data=len(self.result_dict['text'])
        # construyendo lineas
        frase=''
        documento={}
        linea_anterior={}
        linea_actual={}
        relaciones=[]
        palabra_anterior=''
        for i in range(qty_data):
            #checa si hay un cambio de linea
            if self.result_dict['top'][i]>=top_direccion-10 and self.result_dict['top'][i]<=top_direccion+10:
                palabra=self.result_dict['text'][i].lower()
                frase+=' '+palabra
                if len(palabra)>0:
                    linea_actual[self.result_dict['left'][i]]=palabra
                    for keys,values in linea_anterior.items():
                        if keys>=self.result_dict['left'][i]-10 and keys<=self.result_dict['left'][i]+10:
                            relaciones.append([values,palabra,palabra_anterior])
                    palabra_anterior=palabra
                documento[top_direccion]=frase
            else:
                print(linea_anterior,linea_actual)
                linea_anterior=linea_actual
                linea_actual={}
                frase=''
                top_direccion=self.result_dict['top'][i]
        print(documento)
        print(relaciones)
        return documento,relaciones

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
            if 'domicilio' in palabra:
                flag=True
                left_nombre=self.result_dict['left'][i]
        return direccion,colonia,codigo_postal,municipio,estado

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
  parameters.append(miife.identidad)
  return miife.identidad
