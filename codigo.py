# Formato nodos arbol B
# k-1 valores y k punteros a otros nodos
# Notacion en el archvio: p1 ,v1 ,p2 ,v2 ,p3 ,v3 ,p4 ... ,vk-1 ,pk\n } 1 nodo del arbol
# Notación en la clase: values = [v1.v2,v3...] ; ptrs = [p1,p2,p3...]
import os

class Node:
    def __init__(self, val, ptrs):
        self.__values = val
        self.__ptrs = ptrs

    def get_values(self):
        return self.__values

    def get_ptrs(self):
        return self.__ptrs

    @classmethod
    def from_text(cls, txt):
        values = []
        pointers = []
        relevant_txt = txt.split('\n')[0]
        relevant_txt = relevant_txt.split(',')
        elements = list(relevant_txt)
        pointers.append(int(elements[0].split('.')[0]))
        for i in range(1, len(elements) - 1, 2):
            values.append(int(elements[i]))
            puntero = int(elements[i+1].split('.')[0])
            pointers.append(puntero)
        return cls(values, pointers)

    def to_text(self):
        string = f"{self.__ptrs[0]}."
        for j in range(11 - len(str(self.__ptrs[0]))):
            string += "0"
        for i in range(len(self.__values)):
            string += f",{self.__values[i]}"
            string += f",{self.__ptrs[i+1]}."
            largo = len(str(self.__ptrs[i+1]))
            for j in range(11 - largo):
                string += "0"
        return f"{string}\n"

class BTree:
    def __init__(self, filename, k, B):
        self.__filename = filename
        self.__size = 0
        self.__B = B
        self.__k = k
        self.__root_ptr = 0

    def search(self,element):
        # vamos a asumir que la busqueda se hace en un archivo no vacio
        #if self.__size == 0:
        #    return False
        with open(self.__filename, 'r') as f:
            # Suponemos que tenemos el root pointer
            #ptr = self.__root_ptr
            # Suponemos que no tenemos el root pointer
            f.seek(0, 2)  # puntero al final del archivo, se usa para leer
            file_size = f.tell()
            offset = min(file_size, self.__B)
            f.seek(file_size - offset)
            buffer = f.read(offset)
            lines = buffer.split('\n')
            #print(lines) # para saber lo que se leyo
            # No cabe el nodo completo en B
            if len(lines) == 2 and offset < file_size:
                node_text = lines[0]
                # Se van agregando los pedazos que se leen a la lista, la inserción es de derecha a izq
                node_list = [node_text]
                # Se para de agregar cuando se encuentra el salto de linea o se llega al inicio
                while '\n' not in node_text:
                    offset += self.__B
                    f.seek(file_size - offset)
                    node_text = f.read(self.__B)
                    node_list.append(node_text)

                # quitar la informacion del penultimo nodo
                node_list[len(node_list) - 1] = node_list[len(node_list) - 1].split('\n')[1]
                node_text = ""
                # Leer la lista en orden inverso y sumar los strings
                for i, string in reversed(list(enumerate(node_list))):
                    node_text += string
                #print(node_text)
            else: # El nodo si cabe en B
                node_text = lines[len(lines) - 2]

            #ptr = file_size - len(node_text) - 1
            node = Node.from_text(node_text)
            v = 1
            while True:
                if not v:
                    f.seek(ptr)
                    node_text = f.read(self.__B)
                    while '\n' not in node_text:
                        node_text += f.read(self.__B)
                    node = Node.from_text(node_text)
                v = 0
                values = node.get_values()
                ptrs = node.get_ptrs()
                for i in range(len(values)):
                    if (values[i] == element):
                        return True
                    elif (values[i] > element):
                        if ptrs[i] != -1:
                            ptr = ptrs[i]
                        else:
                            return False
                        break # salir del for
                    elif (i == (len(values) - 1) and values[i] < element):
                        if (ptrs[i+1] != -1):
                            ptr = ptrs[i+1]
                        else:
                            return False

    # La idea es que el ultimo nodo del archivo corresponde al root, si un nodo se separa en 2 por overflow la mitad se queda
    # en el nodo original y el resto se va a un nuevo nodo que queda en el penultimo nodo del archivo
    def insert(self, element):
        prev_ptrs = [] # guardar los punteros de los bloques leidos
        found = 0 # se utiliza para indicar que el objeto se inserto y es necesario salir detener la busqueda(salir del while)
        if self.__size == 0:
            self.__size += 1
            with open(self.__filename, 'a+') as f: # appending and reading
                f.write(f"-1.00000,{element},-1.00000\n")
        else:
            self.__size += 1
            with open(self.__filename, 'r+') as f: # leer y escribir desde el comienzo
                # Primero se recorre el arbol buscando el lugar donde insertar el objeto
                ptr = self.__root_ptr # se parte desde el root
                while not found:
                    prev_ptrs.append(ptr) # indicar que se lee un nodo
                    f.seek(ptr) # dejar el fp antes del nodo
                    node_text = f.read(self.__B) # leer el nodo
                    while '\n' not in node_text: # se hace seek en el inset_corrct
                        node_text += f.read(self.__B)
                    node = Node.from_text(node_text) # transformar el texto a nodo
                    values = node.get_values() # obtener valores del nodo
                    ptrs = node.get_ptrs() # obtener punteros del nodo
                    # Recorrer los valores buscando donde insertar el nuevo elemento
                    for i in range(len(values)):
                        if ((element <= values[i]) or ((element > values[i]) and (i == len(values) - 1))): # comparar de izq a der
                            if ptrs[i] == -1: # Es hoja
                                if element > values[i]:
                                    values.insert(i+1, element)
                                else:
                                    values.insert(i, element)
                                #print(values) # permite saber los valores del nodo
                                ptrs.append(-1) # como es uno nodo hoja todos los punteros son placeholders y da lo mismo dd se inserta

                                # Escribir el nodo actualizado y mover las pos necesarias
                                self.insert_correct_pos(f, values, ptrs , ptr, ptr + len(node_text.split('\n')[0]) + 1, 10+len(str(element))) # len(ptr) + 2 comas + len(elem)

                                # Actualizar la pos de los punteros guardados
                                for q in range(len(prev_ptrs)):
                                    if prev_ptrs[q] >= ptr + len(node_text.split('\n')[0]) + 1:
                                        prev_ptrs[q] += 10+len(str(element))

                                j = 0  # variable para indicar que tan abajo uno se encuentra en el arbol,
                                # si j = 0 se esta ubicado en las hojas, sirve para saber los nodos padres
                                while len(values) == self.__k: # Existe un overflow, deberian haber maximo k - 1 valores por nodo
                                    j = j + 1
                                    #print("J:" + str(j))
                                    # Separamos el nodo en izq y der, el nodo original queda como el izq(1) y el der(2) se crea
                                    med = int(len(values)/2) # indice del valor de la mediana
                                    med_value = values[med] # valor que se inserta en el nodo padre
                                    values1 = values[:med] # 0 --- med - 1
                                    values2 = values[med+1:] # med + 1 --- len(values) - 1
                                    ptrs1 = ptrs[:med+1] # 0 --- med
                                    ptrs2 = ptrs[med + 1:] # med + 1 --- el resto

                                    ptr1 = ptr

                                    cant_bytes = len(Node.to_text(Node(values, ptrs))) - len(Node.to_text(Node(values1, ptrs1)))

                                    # Actualizar la pos de los punteros guardados
                                    for q in range(len(prev_ptrs)):
                                        if prev_ptrs[q] >= f.tell():
                                            prev_ptrs[q] -= cant_bytes

                                    # Actualizar los punteros del nodo nuevo
                                    for u in range(len(ptrs2)):
                                        if ptrs2[u] >= f.tell():
                                            ptrs2[u] -= cant_bytes

                                    # Actualizar el nodo que hace overflow(escribir mitad izq del nodo) y mover los nodos necesarios.
                                    # Todavia falta agregar el nuevo nodo(mitad der del nodo) y agregar la mediana al padre
                                    self.insert_correct_pos2(f, values, ptrs, values1, ptrs1, ptr, f.tell())

                                    if (prev_ptrs[0] == ptr):  # el overflow es en el nodo raiz
                                        ptr2 = f.tell()  # guardar en var ptr2 el lugar del final del archivo
                                        f.write(Node.to_text(Node(values2,ptrs2))) # escribir al final del archivo el lado der del nodo
                                        prev_ptrs[0] = f.tell() # actualizar raiz
                                        new_root_value = [med_value]
                                        new_root_ptrs = [ptr1, ptr2]
                                        root = Node.to_text(Node(new_root_value,new_root_ptrs))
                                        self.__root_ptr = f.tell()
                                        f.write(root)
                                        break # no seguir chequeando mas arriba del root
                                    else:
                                        # Insertar la mediana en el padre y actualizar posiciones
                                        dad = len(prev_ptrs) - 1 - j
                                        #print("Dad:" + str(dad))
                                        ptr = prev_ptrs[dad]  # puntero al nodo padre
                                        f.seek(ptr)
                                        node_text = f.read(self.__B)  # leer nodo padre
                                        while '\n' not in node_text:  # se hace seek dps
                                            node_text += f.read(self.__B)
                                        #print("NODO FATHER: " + node_text)
                                        node = Node.from_text(node_text)  # transformar texto a nodo
                                        values = node.get_values()  # actualizar values y ptrs asi poder chequear overflow en el padre
                                        ptrs = node.get_ptrs()
                                        # si el ptr1 esta en la posicion w de los punteros del padre, dejar el ptr2 en la pos w + 1
                                        # y agregar a los valores la med entre el ptr1 y ptr2 que equivale a la pos w
                                        for w in range(len(ptrs)):
                                            if ptr1 == ptrs[w]:
                                                ptr2 = self.__root_ptr # por ahora, todavia no se inserta en todo caso
                                                ptrs.insert(w + 1, ptr2)
                                                values.insert(w, med_value)
                                        pos_antigua = ptr + len(node_text.split('\n')[0]) + 1

                                        # Escribir el padre actualizado y mover los nodos correspondientes
                                        self.insert_correct_pos(f, values, ptrs, ptr, pos_antigua, 10 + len(str(med_value)))  # len(ptr) + 2 comas + len(med_value)
                                        end_ptr = f.tell() # para el siguiente ciclo while
                                        # el ptr es el mismo, y values/ptrs quedan actualizados para la proxima iter del while

                                        # Actualizar la pos de los punteros guardados
                                        for q in range(len(prev_ptrs)):
                                            if prev_ptrs[q] >= pos_antigua:
                                                prev_ptrs[q] += 10 + len(str(med_value))

                                        # Ahora añadir el nuevo nodo casi al final y mover el root
                                        # Guardar el root
                                        f.seek(self.__root_ptr)  # Ir al root_ptr
                                        root_text = f.read(
                                            self.__B)  # leer el root ¿que pasa si se lee hasta el final del archivo?
                                        while '\n' not in root_text:
                                            root_text += f.read(self.__B)
                                        root = Node.from_text(root_text)  # transformar el texto del root a nodo
                                        # Escribir el nodo der en la pos del root
                                        f.seek(self.__root_ptr)  # Ir al root_ptr
                                        f.write(Node.to_text(Node(values2, ptrs2)))
                                        self.__root_ptr = f.tell() # nueva pos del root
                                        f.write(Node.to_text(root))
                                        prev_ptrs[0] = self.__root_ptr
                                        # fp al final del archivo
                                        if dad == 0 and len(values) == self.__k:
                                            ptr = self.__root_ptr
                                            f.seek(ptr + len(Node.to_text(Node(values, ptrs))))

                                        else:
                                            f.seek(end_ptr) # lo dejamos al final del nodo padre, por si hay otro overflow
                                        # no estoy seguro que en la proxima iteracion del while queden bien los valores

                                found = 1 # parar la busqueda
                                break # parar de revisar los valores del bloque
                            else: # No es una hoja, hay que seguir buscando
                                if element > values[i]: # Caso del ultimo puntero
                                    ptr = ptrs[i+1]
                                else:
                                    ptr = ptrs[i]
                f.close()

    def insert_correct_pos(self, file, values_input, ptrs_input, pos_puntero, pos_antigua, cant_bytes):
        if self.__root_ptr > pos_puntero: # No mover en el caso que sea estemos en el root
            self.__root_ptr = self.__root_ptr + cant_bytes # indicar que el root se mueve
        file.seek(0, 2)# puntero al final del archivo, se usa para leer
        file_size = remaining_size = file.tell()
        offset = 0

        # Mover los nodos superiores de posicion y actualizar sus punteros
        while remaining_size > pos_antigua: # se mueve el remaining size
            #print("Remaining size: " + str(remaining_size))
            #print("Pos_antigua: " + str(pos_antigua)) # final del nodo no actualizado
            B = min(remaining_size - pos_antigua, self.__B) # podria darse que sean iguales y todo explota
            file.seek(file_size - offset - B)
            if B < self.__B:
                buffer = file.read(remaining_size - pos_antigua) # ??
            else:
                buffer = file.read(self.__B)
            lines = buffer.split('\n')
            #print(lines) # para saber lo que se leyo
            if len(lines) == 2 and B != remaining_size - pos_antigua: # No se recibió el nodo completo
                # falta actualizar el ramaining size para este caso
                node_text = lines[0]
                #print("Se recibio: " + node_text)
                # Se van agregando los pedazos que se leen a la lista, la inserción es de derecha a izq
                node_list = [node_text]
                # Se para de agregar cuando se encuentra el salto de linea o se llega al inicio
                offset2 = offset + B
                while '\n' not in node_text:
                    offset2 += self.__B
                    file.seek(file_size - offset2)
                    node_text = file.read(self.__B)
                    node_list.append(node_text)
                # Eliminar la info del nodo "anterior"(el que sigue en la busqueda de end to init)
                node_list[len(node_list) - 1] = node_list[len(node_list) - 1].split('\n')[1]
                node_text = ""
                for i, string in reversed(list(enumerate(node_list))):
                    node_text += string
                #print("El nodo completo corresponde a : " + node_text)
            else:
                #print('Multiples nodos leidos: ' + str(lines))
                node_text = lines[len(lines) - 2]

            offset += len(node_text) + 1
            remaining_size = file_size - offset
            aux = file_size - offset + cant_bytes # Se deja el fp apuntando al ultimo nodo + cant bytes a mover
            #print("Rem size act: " + str(remaining_size))
            file.seek(aux)
            #print("NODO A ESCRIBIR: " + node_text)
            node = Node.from_text(node_text)
            values = node.get_values()
            ptrs = node.get_ptrs()
            # Se actualizan los punteros del nodo superior
            for i in range(len(ptrs)):
                if ptrs[i] >= pos_antigua:
                    ptrs[i] += cant_bytes
            file.write(Node.to_text(Node(values,ptrs)))

        # Actualizar los punteros del nodo que se va a escribir
        for i in range(len(ptrs_input)):
            if ptrs_input[i] >= pos_antigua:
                ptrs_input[i] += cant_bytes
        # Escribir el nodo actualizado
        file.seek(pos_puntero)
        file.write(Node.to_text(Node(values_input,ptrs_input)))
        end_ptr = file.tell()

        # Actualizar los punteros de los nodos inferiores
        file.seek(0)
        while file.tell() < pos_puntero: # pos puntero deberia ser 20
            wp = file.tell()
            node_text = file.read(self.__B)  # leer el nodo
            # da lo mismo donde queda el puntero porque despues se vuelve al inicio.
            while '\n' not in node_text:
                node_text += file.read(self.__B)
            node = Node.from_text(node_text)  # transformar el texto a nodo
            values = node.get_values()  # obtener valores del nodo
            ptrs = node.get_ptrs()  # obtener punteros del nodo
            for j in range(len(ptrs)):
                if ptrs[j] >= pos_antigua:
                    ptrs[j] += cant_bytes
            file.seek(wp)
            file.write(Node.to_text(Node(values, ptrs)))
        file.seek(end_ptr)

    def insert_correct_pos2(self, file, values_prev, ptrs_prev, values_input, ptrs_input, pos_puntero, pos_antigua):
        cant_bytes = len(Node.to_text(Node(values_prev, ptrs_prev))) - len(Node.to_text(Node(values_input, ptrs_input)))
        if self.__root_ptr > pos_puntero: # No mover en el caso que sea estemos en el root
            self.__root_ptr = self.__root_ptr - cant_bytes # indicar que el root se mueve

        # Actualizar los punteros de los nodos inferiores
        file.seek(0)
        while file.tell() < pos_puntero:
            #print("No entrar aca pls")
            wp = file.tell()
            node_text = file.read(self.__B)  # leer el nodo
            # da lo mismo donde queda el puntero porque despues se vuelve al inicio.
            while '\n' not in node_text:
                node_text += file.read(self.__B)
            node = Node.from_text(node_text)  # transformar el texto a nodo
            values = node.get_values()  # obtener valores del nodo
            ptrs = node.get_ptrs()  # obtener punteros del nodo
            for j in range(len(ptrs)):
                if ptrs[j] >= pos_antigua:
                    ptrs[j] -= cant_bytes
            file.seek(wp) # escribir antes
            txt = Node.to_text(Node(values, ptrs))
            file.write(txt)

        # Actualizar los punteros del nodo que se va a escribir
        for i in range(len(ptrs_input)):
            if ptrs_input[i] >= pos_antigua: # no es necesario restar la cantidad de bytes
                ptrs_input[i] -= cant_bytes

        # Antes de modificar el tamaño del archivo, dejarlo en una var
        file.seek(0,2)
        end = file.tell()
        # Escribir el nodo actualizado
        file.seek(pos_puntero)
        file.write(Node.to_text(Node(values_input, ptrs_input)))
        end_ptr = file.tell() # se utiliza para dejar el fp despues del nodo actualizado

        # Actualizar la pos de los nodos superiores y sus punteros
        file.seek(pos_antigua) # comenzar a leer a partir de la pos antigua
        #print(pos_antigua) # la pos antigua no esta actualizada al añadir el nodo previo
        #print(end)
        # leer desde pos antigua hasta final antiguo
        while file.tell() < end:
            wp = file.tell()
            node_text = file.read(self.__B)  # leer el nodo
            # da lo mismo donde queda el puntero porque despues se vuelve al inicio.
            while '\n' not in node_text:
                node_text += file.read(self.__B)
            node = Node.from_text(node_text)  # transformar el texto a nodo
            values = node.get_values()  # obtener valores del nodo
            ptrs = node.get_ptrs()  # obtener punteros del nodo
            # Actualizar los punteros del nodo
            for j in range(len(ptrs)):
                if ptrs[j] >= pos_antigua:
                    ptrs[j] -= cant_bytes
            file.seek(wp - cant_bytes)
            file.write(Node.to_text(Node(values, ptrs)))
            new_read_pos = file.tell() + cant_bytes
            file.seek(new_read_pos)
        #print("TRUNCATE AT: " + str(end - cant_bytes)) # borrar la info extra
        file.truncate(end - cant_bytes)
        file.seek(end_ptr)

from random import randint
def make_BTree(lines, B, name_of_file_p2b, k):
    T = BTree(name_of_file_p2b, k, B)
    next_val = 1
    for i in range(lines - 1):
        if i%1000 == 0: print(i)
        next_val = next_val + randint(1, 10)
        T.insert(next_val)


#make_BTree(100000,2048,"ortuzarpls2.txt",200)

#T = BTree('hmmm2.txt',100,2048) # k , B

#for i in range(100000):
#    T.insert(i)
#T.insert(2)
#T.insert(5)
#T.insert(4)
#assert T.search(2) and not T.search(3) and T.search(4) and T.search(5) and not T.search(6) # Hasta aqui va bien
#T.insert(6)
#assert T.search(2) and not T.search(3) and T.search(4) and T.search(5) and T.search(6)# Hasta aqui va bien
#T.insert(8)
#T.insert(7)
#T.insert(9)
#assert T.search(2) and not T.search(3) and T.search(4) and T.search(5) and T.search(6) and T.search(7) and T.search(8) and T.search(9) and not T.search(10)# Hasta aqui va bien
#T.insert(10)
#T.insert(11)
#T.insert(12)
#T.insert(13)
#T.insert(17)
#T.insert(16)
#T.insert(14)
#T.insert(15)
#assert T.search(2) and not T.search(3) and T.search(4) and T.search(5) and T.search(6) and T.search(7) and T.search(8) and T.search(9) and T.search(10)
#assert T.search(11) and T.search(12) and T.search(13) and T.search(14) and T.search(15) and T.search(16) and T.search(17) and not T.search(18) and not T.search(19) and not T.search(20)# Hasta aqui va bien

# Para debuggear
#file.seek(0)
#t = file.read(numero grande)
#print("LECTURA: " + t)
#print("-----------------")