<h1 align="center">:dna:Comparación masiva ADNmt:dna:</h1>

Este script permite realizar una comparación masiva de haplotipos de ADNmt a partir de un archivo .xlsx, teniendo en cuenta los rangos de lectura de las muestras, excluyendo de la comparación regiones homopolimericas y teniendo en cuenta heteroplasmias. 

## Pre-requisitos :clipboard:

Para poder usar este script primero tienen que tener instalado Python en su computadora. Este script está en formato .py y .ipynb para correrlo en el entorno de desarrollo que prefiera. Si no está familiarizado con el lenguaje, puede utilizar Jupyter Notebook, el cual es de rápido aprendizaje. Visit https://www.anaconda.com/download. Luego deben descargar el repositorio y descomprimir la carpeta. Entre los archivos se brinda una Base de datos de prueba para que puedan correr el script por primera vez sin la necesidad de hacer ninguna modificación en el código.

En el caso de querer trabajar con otra base de datos, ir a la sección donde se lee la base de datos y cambiar el nombre del archivo. 
<p align="center" width="100%">
    <img width="70%" src="https://github.com/fedepicado/Comparacion-masiva-ADNmt/assets/89711061/467c60d7-9e73-45a2-bdac-e82d5d9b0d01"> 
</p>

Para ejecutarlo solo tienen que darle click al boton de “fast forward” que ejecuta todo el codigo.
<p align="center" width="90%">
    <img width="70%" src="https://github.com/fedepicado/Comparacion-masiva-ADNmt/assets/89711061/7267da66-98c7-44ae-91f0-1f4c671508cb"> 
</p>

## Lógica del algoritmo :gear:

Requiere una tabla en formato excel donde la primera columna contenga el nombre de las muestras (Sample Name), la segunda columna sea el rango de lectura de la muestra (Rango de lectura), y las columnas siguientes correspondan a los haplotipos, numeradas como 0,1,2,3,etc 

### Rango de lectura y regiones homopolimericas
Lo primero que hace es agrupar las columnas que contienen las mutaciones en una sola columna como una lista de strings, bajo el nombre “secuencia”. Se seleccionan las columnas Sample Name, Rango de lectura y secuencia. A esa nueva base de datos se le aplican un conjunto de funciones que hacen a la comparación.
Lo primero que se tiene en cuenta es el rango de lectura. Si una muestra tiene secuenciado el D-Loop Completo (16024-576) y otra muestra solo tiene las regiones HV1 y HV2 (16024-16428/50-340) se tomará como rango de lectura consenso las regiones que ambas compartan. En este caso, (16024-16428/50-340).

Ahora si tenemos una muestra con rango de lectura (16024-16428/58-400) y otra con (16034-16430/50-340) el rango de lectura consenso será (16034-16428/58-340).
Es importante que para el caso que tengamos un rango incompleto sigamos esta regla de escritura; donde "/" separa regiones y "-" separa dónde empieza y dónde termina una región. 

Una vez ya determinado el rango de lectura nos fijamos cuáles son las mutaciones distintas entre ambas muestras. Lo que es igual no nos interesa, así que solo nos quedamos con lo diferente. De esas diferencias descartamos regiones homopolimericas y mutaciones que caen fuera del rango de lectura determinado.

### Heteroplasmias

Podemos tener dos casos distintos de heteroplasmias;

Podríamos tener entre las diferencias números repetidos,por ejemplo: "A73G" y "A73Y". 
Esto significa que cada una de las muestras que se comparan tenía una de estas mutaciones. Bien y ahora cómo determino si es diferencia o no? 

En este caso nos fijamos en la última letra de los número repetidos ya que la primera hace referencia a la base que se encuentra en la secuencia de referencia. La Y detona que en esa posición podemos encontrar tanto una C como una T. Entonces creamos una lista donde se guardan las posibles bases en la última posición. Para este caso de ejemplo seria ["G","C","T"]. Queda preguntarse si dentro de la lista hay alguna letra repetida, y como no hay letras repetidas se cuenta como diferencia. 

Una vez analizadas las mutaciones con números repetidos, nos fijamos si las mutaciones con números únicos en la última posición hay una letra que muestre una heteroplasmia. Pongamos de ejemplo que se encuentra la siguiente mutación: "C151S". "S" vale por "C" o "G" entonces volvemos a crear una lista en la que guardaremos la primera letra de la mutación, en este caso "C" y las bases que corresponden a la heteroplasmia, que son "C" o "G". Nos volvemos a preguntar ¿hay alguna base repetida? En este caso si, la base "C" por lo que está heteroplasmia no se considera como una diferencia. 

## Resultados :bar_chart:

Una vez ejecutado el script obtendremos una tabla con los resultados de la comparación donde solo se tendrán en cuenta el par de muestras que presenten cero o una diferencias. 
Esta tabla tendrá 4 columnas, las dos primeras corresponden a los nombres de las secuencias que se compararon, la tercera será las diferencias entre ambas muestras y la cuarta mostrará el rango de lectura analizado. 











