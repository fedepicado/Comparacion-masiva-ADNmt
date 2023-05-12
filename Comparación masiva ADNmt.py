#!/usr/bin/env python
# coding: utf-8

# In[1]:


#PRONTO READme JUNTO AL SCRIPT DONDE SE DARAN TODOS LOS DETALLES DEL PROGRAMA.
import pandas as pd
import os
import glob
import re
import itertools
import timeit


# In[2]:


# Estas funciones reorganizan el dataframe, Unen todas las mutaciones en una sola columna como una lista de strings
def cantColsDf(df):
    cant_cols=(len(df.columns)-2) #le resto la columna del nombre y del rango
    cols=[]
    for i in range(cant_cols):
        cols.append(i)
    return cols

#concateno las columnas de mutaciones
def concatCols(df,cols):
    df_copy=df.copy()
    df_copy["Secuencia"] = df_copy[cols].apply(lambda x: ",".join(x.dropna()), axis=1)
    df_copy=df_copy.reset_index()
    x=[]
    for i in df_copy["Secuencia"]:
        x.append(i.split(","))
    df_copy["Secuencia_lista"]=x    
    df_copy=df_copy[['Sample Name','Rango de lectura','Secuencia_lista']]
    return df_copy

def extraerFilas(df):
    Sample_Name = df['Sample Name'].tolist()
    Rango = df['Rango de lectura'].tolist()
    Sec = df['Secuencia_lista'].tolist()
    return Sample_Name, Rango, Sec

### para ver si quedo bien
def data(Sample_Name,rango_entero,Sec):
      data={
      "Sample Name": Sample_Name,
      "Rango de lectura": rango_entero,
      "Sec": Sec
  }
        
def limpiarEspacios(lista):
    for i in range(len(lista)):
        lista[i] = lista[i].strip()
    return lista

def data(Sample_Name, rango_entero, Sec):
    return pd.DataFrame({'Sample Name': Sample_Name, 'Rango de lectura': rango_entero, 'Sec': Sec})


# In[3]:


#Estas funciones trabajan con los rangos de lectura.
# Hay dos tipos de formas de expresar el rango de lectura:
# Rango completo -> 16024-576
# HV1 y HV2 -> 16024-16480/50-430 
# En este segundo caso es importante respetar el "-" para marcar donde empieza y termina una region y el "/" para separar regiones

def rangoSplitUno(Rango):
    Rango_split=[]
    Rango_completo="16024-576"
    if(Rango == Rango_completo):
        Rango_split.append([1,576])
        Rango_split.append([16024,16569])
    else:
        numeros=extraer_numeros_rango(Rango)
        Rango_split.append([numeros[0],numeros[1]])
        Rango_split.append([numeros[2],numeros[3]])
    return Rango_split

#aux de rangoSplitUno
def extraer_numeros_rango(cadena):
    return list(map(int, re.findall(r'\d+', cadena)))

def extraer_numeros_rango1(cadena):
    numeros = []
    for elemento in cadena:
        if isinstance(elemento, int):
            numeros.append(elemento)
        elif isinstance(elemento, list):
            numeros.extend(extraer_numeros_rango1(elemento))
        elif isinstance(elemento, str):
            numeros.extend(map(int, re.findall(r'\d+', elemento)))
    numeros.sort(reverse=False)
    return numeros


def combinar_rangos(rango1, rango2):
    rangoLectura = []
    rangoLectura.append([max(rango1[0], rango2[0]), min(rango1[1], rango2[1])])
    rangoLectura.append([max(rango1[2], rango2[2]), min(rango1[3], rango2[3])])
    return rangoLectura


# In[4]:


#Estas funciones sirven en para descartar mutaciones que caigan fuera del rango determinado, excluye mutaciones de regiones homopolimericas y tienen en cuenta las heteroplasmias

def extract_numbers(lst):
    numbers = []
    pattern = r"\d+(\.\d+)?"
    for s in lst:
        match = re.search(pattern, s)
        if match:
            number = match.group()
            if '.' in number:
                numbers.append(float(number))
            else:
                numbers.append(int(number))
    return numbers

def repetidos(l1):
    nueva=[]
    repetidos=[]
    no_repetidos=[]
    for i in l1:
        if(i not in nueva):
            nueva.append(i)
        else:
            repetidos.append(i)
    return repetidos

def descartarNumFloat(difer_num, difer_string):
    # Encontrar los índices de los números enteros en la lista de números
    indices_enteros = [i for i, x in enumerate(difer_num) if isinstance(x, int)]
    
    # Eliminar los elementos correspondientes en la lista de strings
    difer_string1 = [difer_string[i] for i in indices_enteros]
    
    return list(filter(lambda x: isinstance(x, int), difer_num)), difer_string1


def pertenece_rango(rango_lectura,difer_num,difer_string):
    difer_int = list(map(int,difer_num))
    pos=[]
    i=0 
    while i < len(difer_int):
        a= rango_lectura[0]
        if (difer_int[i] >= a[0] and difer_int[i] <= a[1]):
            pos.append(i)
        b= rango_lectura[1]
        if (difer_int[i] >= b[0] and difer_int[i] <= b[1]):
            pos.append(i)
        i=i+1  
    dif_int1=[]
    dif_string1=[]
    for i in pos:
        dif_int1.append(difer_num[i])
        dif_string1.append(difer_string[i])
    return dif_int1,dif_string1

def find_duplicate_positions(lst):
    seen = {}
    duplicates = []
    for i, x in enumerate(lst):
        if x in seen:
            duplicates.append(seen[x])
            duplicates.append(i)
        else:
            seen[x] = i
    return duplicates

def encontrarMut(numero, dif,dif_num):
    mivar=[]
    for x in numero:
        for ind,r in enumerate(dif_num):
            if(r==x):
                mivar.append(dif[ind])
    return mivar

def esDiferencia(letras):
    flat_list=[]
    for item in letras:
    # appending elements to the flat_list
        flat_list += item
    nueva=[]
    repetidos=[]
    for i in flat_list:
        if(i not in nueva):
            nueva.append(i)
        else:
            repetidos.append(i)
    if(len(repetidos)!=0):
        return True
    else:
        return False

def unique_positions(lst):
    unique = {}
    for i, x in enumerate(lst):
        if x not in unique:
            unique[x] = [i]
        else:
            unique[x].append(i)
    return [v[0] for k, v in unique.items() if len(v) == 1]

def extraerHeteroplasmias(dif_string1,rep):
    return [x for ind,x in enumerate(dif_string1) if ind in rep]

def translate_heteroplasmy_unica(lista,unicos):
    # create a dictionary of IUPAC nomenclature and corresponding mutations
    iupac_dict = {'R': ['A', 'G'], 'Y': ['C', 'T'], 'S': ['G', 'C'], 'W': ['A', 'T'], 'K': ['G', 'T'], 'M': ['A', 'C']}
    cant_dif=0
    for i in unicos:
        repetidas=[]
        mut1=lista[i]
        ultima1=mut1[-1]
        primera1=mut1[0]
        if(ultima1 in iupac_dict.keys()):
            hetero1=iupac_dict[ultima1]
            repetidas.append(hetero1)
            repetidas.append(primera1)
        else:
            repetidas.append(ultima1)  
        a= esDiferencia(repetidas)
        if (a == True):
            None
        else:
            cant_dif+=1
    return cant_dif

def translate_heteroplasmy(lista):
    # create a dictionary of IUPAC nomenclature and corresponding mutations
    iupac_dict = {'R': ['A', 'G'], 'Y': ['C', 'T'], 'S': ['G', 'C'], 'W': ['A', 'T'], 'K': ['G', 'T'], 'M': ['A', 'C']}
    cant_dif=0
    x=0
    while x < len(lista):
        repetidas=[]
        mut1=lista[x]
        mut2=lista[x+1]
        ultima1=mut1[-1]
        ultima2=mut2[-1]
        if(ultima1 in iupac_dict.keys()):
            hetero1=iupac_dict[ultima1]
            repetidas.append(hetero1)
        else:
            repetidas.append(ultima1)  
        if (ultima2 in iupac_dict.keys()):
            hetero2=iupac_dict[ultima2]
            repetidas.append(hetero2)
        else:     
            repetidas.append(ultima2)
        a= esDiferencia(repetidas)
        if (a == True):
            None
        else:
            cant_dif+=1
        x+=2
    return cant_dif


# In[5]:


# funcion general que agrupa todas las funciones ya presentadas para que al ir iterando sobre el dataframe sea sencillo de hacer.
def GENERAL(sec1,sec2,rango_sec1,rango_sec2,nombre1,nombre2):
    rango_int1=rangoSplitUno(rango_sec1)
    rango_int2=rangoSplitUno(rango_sec2)
    num_rango1=extraer_numeros_rango1(rango_int1)
    num_rango2=extraer_numeros_rango1(rango_int2)
    rango_lectura=combinar_rangos(num_rango1,num_rango2)
    ### DIFERENCIAS
    a1= list(set(sec1) - set(sec2))
    b1= list(set(sec2) - set(sec1))
    dif=list(a1+b1)# diferencias como string
    dif_num= extract_numbers(dif)#diferecncias como numeros.
    dif2 = descartarNumFloat(dif_num, dif)## descarto regiones homopolimericas
    quedan_dif= pertenece_rango(rango_lectura,dif2[0],dif2[1])#descarto por rango 
    ## encontrar los numeros que no estan repetidos
    unicos=unique_positions(quedan_dif[0])
    ### de estos valores unicos hay alguno que tenga alguna heteroplasmia? 
    primeras_diferencias=translate_heteroplasmy_unica(quedan_dif[1],unicos)
    rep=find_duplicate_positions(quedan_dif[0])#posiciones de las mutaciones repetidas, heteroplasmias que se encuentran en ambas secuencias
    analizar=extraerHeteroplasmias(quedan_dif[1],rep)
    segundas_diferencias=translate_heteroplasmy(analizar)
    diferencias=primeras_diferencias + segundas_diferencias
    return nombre1,nombre2,diferencias,rango_lectura


# In[6]:





# In[7]:


#Funcion aux de extraerDatosMASIVA()
def extraerFilas_extra(df):
    Sample_Name=[]
    Rango=[]
    Sec=[]
    for index,row in df.iterrows():
        Sample_Name.append(row['Sample Name'])
        Rango.append(row["Rango de lectura"])
        Sec.append(row["Sec"])
    return Sample_Name,Rango,Sec

# Permite ir extrayendo cada par de muestras del df y se le aplica la funcion general que hace a la comparacion en si.
def extraerDatosMASIVA(df_corregido,lista_general):
    Sample_Name,Rango,Sec= extraerFilas_extra(df_corregido)
    i=0
    while i < (len(Sample_Name)-1):
        Nombre1=Sample_Name[i]
        Rango1=Rango[i]
        Sec1=Sec[i]
        for x in range(i+1,len(Sample_Name)):
            Nombre2=Sample_Name[x]
            Rango2=Rango[x]
            Sec2=Sec[x]
            resultado=GENERAL(Sec1,Sec2,Rango1,Rango2,Nombre1,Nombre2)## funcion que compara
            if(resultado[2]<=1):
                lista_general.append(resultado)
        i+=1
    return lista_general


# In[8]:


# Organiza el dataframe, hace la comparacion y organiza los resultados para que esten en el formato correcto
def Masiva(df_base):
    print("Se ejecutara una Comparacion Masiva, esto puede demorar unos minutos")
    print("\n")
    cols=cantColsDf(df_base)
    df_unido=concatCols(df_base,cols)
    Sample_Name,Rango,Sec=extraerFilas(df_unido)
    Rango_limpio=limpiarEspacios(Rango)
    df_corregido=data(Sample_Name,Rango_limpio,Sec)
    lista_general=[]
    extraerDatosMASIVA(df_corregido,lista_general)
    df_resultados= pd.DataFrame(lista_general, columns =['INDIVIDUO 1', 'INDIVIDUO 2', 'Diferencias',"Rango de lectura"])
    ## cambio el formato del rango de lectura. 
    rango_lista=df_resultados["Rango de lectura"].tolist()
    rango_completo="16024-576"
    for ind,x in enumerate(rango_lista):
        rang=[[1, 576], [16024, 16569]]
        if (x==rang):
            rango_lista[ind]=rango_completo
        else:
            a=x[1]
            b=x[0]
            a_str = "-".join(str(num) for num in a)
            b_str = "-".join(str(num) for num in b)
            rango_lista[ind]= a_str + "/" + b_str
    df_resultados["Rango de lectura"]=rango_lista
    df_resultados.set_index(["INDIVIDUO 1", "INDIVIDUO 2"], inplace=True)
    df_resultados.sort_values(by=["INDIVIDUO 1",'Diferencias'],axis=0, na_position="last",inplace=True)
    return  df_resultados.style.applymap(lambda x: 'text-align: center').to_excel("Comparacion Masiva.xlsx")


# In[9]:


# Leemos la base de datos que se va a comparar
df = pd.read_excel("Base de datos.xlsx")

# pasamos todos los datos a str y le sacamos los espacios en blanco
for col in df.iloc[:,:]:
    df[col] = df[col].astype(str)
    df[col] = df[col].str.strip()


# In[10]:


# Medimos el tiempo que tarda en ejecutarse la comparacion
start = timeit.default_timer()
Masiva(df)
stop = timeit.default_timer()

print('Tiempo de procesamiento: ', stop - start, "seg") 
print("Los resultados se encuentran en la misma carpeta donde se corrio el script bajo el nombre Comparacion Masiva")
print("\n")


# In[ ]:




