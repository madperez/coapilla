#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 12:49:03 2020

@author: nautica
"""

def ocr_ife(media_image):
    
  pil_image=Image.open(BytesIO(media_image.get_bytes()))
  d = pytesseract.image_to_string(pil_image)
  print(d)
  # Get verbose data including boxes, confidences, line and page numbers
  print('image_to_data \n')
  print(pytesseract.image_to_data(pil_image))

  # Get information about orientation and script detection
  print('image_to_osd \n')
  result=pytesseract.image_to_osd(pil_image)
  print(result)
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
        print('elector encontrado',palabra)
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
