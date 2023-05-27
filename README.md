# Comparacion-masiva-ADNmt

Este script permite realizar una comparación masiva de haplotipos de ADNmt a partir de un archivo .xlsx, teniendo en cuenta los rangos de lectura de las muestras, excluyendo de la comparacion regiones homopolimericas y teniendo en cuenta heteroplasmias. 

## Logica del algoritmo

Requiere una tabla en formato excel donde la primera columna contenga el nombre de las muestras (Sample Name), la segunda columna sea el rango de lectura de la muestra (Rango de lectura), y las columnas siguientes correspondan a los haplotipos, numeradas como 0,1,2,3,etc 

### Rango de lectura y regiones homopolimericas
Lo primero que hace es agrupar las columnas que contienen las mutaciones en una sola columna como una lista de strings, bajo el nombre secuencia. Se seleccionan las columnas Sample Name, Rango de lectura y secuencia. A esa nueva base de datos se le aplican un conjunto de funciones que hacen a la comparacion.
Lo primero que se tiene en cuenta es el rango de lectura. Si una muestra tiene secuenciado el D-Loop Completo (16024-576) y otra muestra solo tiene las regiones HV1 y HV2 (16024-16428/50-340) se tomara como rango de lectura consenso las regiones que ambas compartan. En este caso, (16024-16428/50-340).

Ahora si tenemos una muestra con rango de lectura (16024-16428/58-400) y otra con (16034-16430/50-340) el rango de lectura consenso sera (16034-16428/58-340).
Es importante que para el caso que tengamos un rango incompleto sigamos esta regla de escritura; donde "/" separa regiones y "-" separa donde arranca y donde termina una region. 

Una vez ya determinado el rango de lectura nos fijamos cuales son las mutaciones distintas entre ambas muestras. Lo que es igual no nos interesa, asi que solo nos quedamos con lo diferente. De esas diferencias descartamos regiones homopolimericas y mutaciones que caen fuera del rango de lectura determinado.

### Heteroplasmias

Podemos tener dos casos distintos de heteroplasmias;

Podriamos tener entre las diferencias numeros repetidos,por ejemplo: "A73G" y "A73Y". 
Esto significa que cada una de las muestras que se comparan tenia una de estas mutaciones. Bien y ahora como determino si es diferencia o no? 

En este caso nos fijamos en la ultima letra de los numero repetidos ya que la primera hace refencia a la base que se encuentra en la secuencia de referencia. La Y detona que en esa posicion podemos encontrar tanto una C como una T. Entonces creamos una lista donde se guardan las posibles bases en la ultima posicion. Para este caso de ejemplo seria ["G","C","T"]. Queda preguntarse si dentro de la lista hay alguna letra repetida, y como no hay letras repetidas se cuenta como diferencia. 

Una vez analizadas las mutaciones con numeros repetidos, nos fijamos si las mutaciones con numeros unicos en la ultima posicion hay una letra que muestre una heteroplasmia. Pongamos de ejemplo que se encuentra la siguiente mutacion: "C151S". "S" vale por "C" o "G" entonces volvemos a crear una lista en la que guardaremos la primera letra de la mutacion, en este caso "C" y las bases que corresponden a la heteroplasmia, que son "C" o "G". Nos volvemos a preguntar hay alguna base repetida? En este caso si, la base "C" por lo que esta heteroplasmia no se considera como una diferencia. 

## Resultados

Una vez ejecutado el script obtendremos una tabla con los resultados de la comparacion donde solo se tendran en cuenta el par de muestras que presenten cero o una diferencias. 
Esta tabla tendra 4 columnas, las dos primeras corresponden a los nombres de las secuencias que se compararon, la tercera sera las diferencias entre ambas muestras y la cuarta mostrara el rango de lectura analizado. 










