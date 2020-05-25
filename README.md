# T2

## Bug

Actualmente no se puede tener un B < cant de bytes de un nodo

## Notación

Este codigo permite crear, insertar y buscar en Arboles B.

Los árboles se almacenan en archivos de texto de la siguiente manera:

Sea k la máxima cantidad de punteros que hay en un nodo del árbol(implica k-1 valores como máximo), 
cada nodo se anota en una linea por separado de la forma "p1 ,v1 ,p2 ,v2 ,p3 ,v3 ,p4 ... ,vk-1 ,pk\n". 
Donde pi es un puntero a un hijo y vi un valor. Cada pi corresponde a un valor que indica una posición en el archivo
donde se encuentra el comienzo del nodo hijo. 
Además la forma en que se construye el archivo deja el nodo raíz en la última linea del archivo.

Por otro lado, el codigo presenta la estructura BTree la que va leyendo los nodos del archivo y va almacenando sus
valores y sus punteros en los campos values y ptrs de otra estructura llamada nodo. 

## Usos

Primero es necesario crear la estructura del B arbol, la cual tiene como paŕametros el valor k de la máxima cantidad
de punteros y B correspondiente al tamaño del bloque de lectura. Por ejemplo, T = BTree('test9.txt',3,128) lee el 
BTree almacenado en test9.txt que tiene k = 3, además se indica que el tamaño de los bloques de lectura es 128. 

### Insertar
Mediante T.insert(element) se inserta el elemento en la posición adecuada adentro del archivo de texto.
(Actualmente es necesario que el archivo este vacío para llamar al primer insertar(primer insertar desde crear 
la estuctura BTree))

### Buscar
Mediante T.search(element) se busca el elemento dentro del archivo de texto. Retorna un bool dependiendo si se 
encuentra o no.
