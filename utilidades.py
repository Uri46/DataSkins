# -*- coding: utf-8 -*-


import sys
import os
import re

if os.name == "nt":
    import msvcrt
    termios = None
    tty = None
else:
    import termios
    import tty

def limpiar():
    comando_limpiar = "cls" if os.name == "nt" else "clear"
    os.system(comando_limpiar)

def _leer_tecla_windows():
    k = msvcrt.getch()
    if isinstance(k, bytes):
        try:
            return k.decode('latin-1')
        except Exception:
            return chr(k[0])
    return k

def gestion_menu(opcion_seleccionada, opciones, menu_activo = True):
    for indice in range(len(opciones)):
        if indice == opcion_seleccionada:
            print("\033[92m> \033[0m" + opciones[indice])
        else:
            print("  " + opciones[indice])
            
    print("\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if sys.platform.startswith("win"):
        tecla = _leer_tecla_windows()
        if tecla == '\xe0':
            tecla = _leer_tecla_windows()
            if tecla == 'H':  # Flecha arriba
                opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
            elif tecla == 'P':  # Flecha abajo
                opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)
        elif tecla == '\r':  # ENTER
            menu_activo = False
    else:
        entrada = sys.stdin.fileno()
        configuracion_anterior = termios.tcgetattr(entrada)
        try:
            tty.setraw(entrada)
            tecla1 = sys.stdin.read(1)

            if tecla1 == '\x1b':  # Secuencias que empiezan con ESC
                tecla2 = sys.stdin.read(1)
                tecla3 = sys.stdin.read(1)

                if tecla2 == '[':
                    if tecla3 == 'A':  # Flecha arriba
                        opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                    elif tecla3 == 'B':  # Flecha abajo
                        opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)

                elif tecla2 == 'O' and tecla3 == 'M':  # Enter del keypad
                    menu_activo = False

            elif tecla1 in ('\n', '\r'):  # Enter
                menu_activo = False

        finally:
            termios.tcsetattr(entrada, termios.TCSADRAIN, configuracion_anterior)
            
    
    return menu_activo, opcion_seleccionada

def mostrar_menu(titulo, opciones, sesion_iniciada=None, nombre_usuario=""):
    opcion_seleccionada = 0
    menu_activo = True

    while menu_activo:
        limpiar()
        print("<<<<<<<<<<<<<<<<<<< " + titulo + " >>>>>>>>>>>>>>>>>>>")
        print("\nUse las flechas para moverse y ENTER para seleccionar:\n")

        if sesion_iniciada:
            print("Sesion iniciada como:", nombre_usuario, "\n")
        elif not sesion_iniciada and sesion_iniciada != None:
            print("Sesion no iniciada.\n")

        menu_activo, opcion_seleccionada = gestion_menu(opcion_seleccionada, opciones)

    return opcion_seleccionada

def mostrar_menu_cajas(titulo, lista):
    indice_seleccionado = 0
    opciones = [lista[i][1] for i in range(len(lista))]
    menu_activo = True
    while menu_activo:
        limpiar()
        print("<<<<<<<<<<<<<<<<<<<<<<<<<< " + titulo + " >>>>>>>>>>>>>>>>>>>>>>")
        print("\nUse las flechas para moverse y ENTER para seleccionar:\n")
        encabezado = "Nombre | Descripcion | Precio"
        regex_ansi = re.compile(r'\x1b\[[0-9;]*m')
        opciones_ajustadas = reservacion_de_espacio([encabezado] + opciones, regex_color=regex_ansi, separador=" | ")
        encabezado_ajustado = opciones_ajustadas[0]
        opciones = opciones_ajustadas[1:]
        print("\n  " + encabezado_ajustado)
        menu_activo, indice_seleccionado = gestion_menu(indice_seleccionado, opciones)
        
    return indice_seleccionado

def mostrar_menu_filtrado(titulo, inventario, opciones_filtros, tipo, regex_color=None, orden_rareza=None):
    opcion_filtro = 0
    menu_activo = True

    while menu_activo:
        limpiar()
        print("<<<<<<<<<<<<<<<<<<<<<< " + titulo + " >>>>>>>>>>>>>>>>>>>>>>>>")

        print("\nUse las flechas para cambiar filtros o ENTER para salir\n")
        
        if tipo == "completo" or tipo == "camuflajes":
            encabezado = "Nombre | Precio | Rareza | Cantidad"
        elif tipo == "armas":
            encabezado = "Nombre | Precio | Cantidad"

        datos_ordenados = []

        for clave, datos in inventario.items():
            if tipo == "completo":
                nombre, precio, rareza, cantidad = datos
                nombre_limpio = regex_color.sub('', nombre)
                rareza_limpia = regex_color.sub('', rareza)

                if opcion_filtro in (0, 1):  # Nombre
                    datos_ordenados.append((nombre_limpio, nombre, precio, rareza, cantidad))
                elif opcion_filtro in (2, 3):  # Precio
                    datos_ordenados.append((precio, nombre, rareza, cantidad))
                elif opcion_filtro in (4, 5):  # Rareza
                    datos_ordenados.append((orden_rareza.index(rareza_limpia), nombre, precio, rareza, cantidad))
                elif opcion_filtro in (6, 7):  # Cantidad
                    datos_ordenados.append((cantidad, nombre, precio, rareza))

            elif tipo == "camuflajes":
                nombre, precio, rareza, cantidad = datos
                nombre_limpio = regex_color.sub('', nombre)
                rareza_limpia = regex_color.sub('', rareza)

                if opcion_filtro in (0, 1):  # Nombre
                    datos_ordenados.append((nombre_limpio, nombre, precio, rareza, cantidad))
                elif opcion_filtro in (2, 3):  # Precio
                    datos_ordenados.append((precio, nombre, rareza, cantidad))
                elif opcion_filtro in (4, 5):  # Rareza
                    datos_ordenados.append((orden_rareza.index(rareza_limpia), nombre, precio, rareza, cantidad))
                elif opcion_filtro in (6, 7):  # Cantidad
                    datos_ordenados.append((cantidad, nombre, precio, rareza))

            elif tipo == "armas":
                nombre, precio, cantidad = datos
                nombre_limpio = regex_color.sub('', nombre)

                if opcion_filtro in (0, 1):  # Nombre
                    datos_ordenados.append((nombre_limpio, nombre, precio, cantidad))
                elif opcion_filtro in (2, 3):  # Precio
                    datos_ordenados.append((precio, nombre, cantidad))
                elif opcion_filtro in (4, 5):  # Cantidad
                    datos_ordenados.append((cantidad, nombre, precio))

        if opcion_filtro % 2 == 1:  # impares son DESCENDENTES
            datos_ordenados.sort(reverse=True)
        else:
            datos_ordenados.sort()
        lineas = []
        for datos in datos_ordenados:
            if tipo == "completo":
                if opcion_filtro in (0, 1):
                    nombre_limpio, nombre, precio, rareza, cantidad = datos
                elif opcion_filtro in (2, 3):
                    precio, nombre, rareza, cantidad = datos
                elif opcion_filtro in (4, 5):
                    orden, nombre, precio, rareza, cantidad = datos
                elif opcion_filtro in (6, 7):
                    cantidad, nombre, precio, rareza = datos
                lineas.append(f"{nombre} | {precio} | {rareza} | {cantidad}")

            elif tipo == "camuflajes":
                if opcion_filtro in (0, 1):
                    nombre_limpio, nombre, precio, rareza, cantidad = datos
                elif opcion_filtro in (2, 3):
                    precio, nombre, rareza, cantidad = datos
                elif opcion_filtro in (4, 5):
                    orden, nombre, precio, rareza, cantidad = datos
                elif opcion_filtro in (6, 7):
                    cantidad, nombre, precio, rareza = datos
                lineas.append(f"{nombre} | {precio} | {rareza} | {cantidad}")

            elif tipo == "armas":
                if opcion_filtro in (0, 1):
                    nombre_limpio, nombre, precio, cantidad = datos
                elif opcion_filtro in (2, 3):
                    precio, nombre, cantidad = datos
                elif opcion_filtro in (4, 5):
                    cantidad, nombre, precio = datos
                lineas.append(f"{nombre} | {precio} | {cantidad}")

        lineas_con_encabezado = [encabezado] + lineas
        lineas_ajustadas = reservacion_de_espacio(lineas_con_encabezado, regex_color=regex_color, separador=" | ")
        print(lineas_ajustadas[0])
        for linea in lineas_ajustadas[1:]:
            print(linea)

        print("\n")
        menu_activo, opcion_filtro = gestion_menu(opcion_filtro, opciones_filtros)
    return opcion_filtro

def mostrar_menu_enciclopedia(titulo, diccionario, opciones_filtros, tipo, regex_color=None, orden_rareza=None):
    opcion_filtro = 0
    menu_activo = True

    while menu_activo:
        limpiar()
        print("<<<<<<<<<<<<<<<<<<<<<< " + titulo + " >>>>>>>>>>>>>>>>>>>>>>>>")

        print("\nUse las flechas para cambiar filtros o ENTER para salir\n")

        if tipo == "camuflajes":
            encabezado = "Nombre | Precio | Rareza | Probabilidad"
        elif tipo == "armas":
            encabezado = "Nombre | Precio | Probabilidad"
        
        lineas_con_encabezado = [encabezado]

        datos_ordenados = []

        for clave, datos in diccionario.items():
            if tipo == "camuflajes":
                nombre, rareza, precio, probabilidad = datos
                nombre_limpio = regex_color.sub('', nombre) if regex_color else nombre
                rareza_limpia = regex_color.sub('', rareza) if regex_color else rareza

                if opcion_filtro in (0, 1):  # Nombre
                    datos_ordenados.append((nombre_limpio, nombre, precio, rareza, probabilidad))
                elif opcion_filtro in (2, 3):  # Precio
                    datos_ordenados.append((precio, nombre, rareza, probabilidad))
                elif opcion_filtro in (4, 5):  # Rareza
                    indice_rareza = orden_rareza.index(rareza_limpia) if (orden_rareza and rareza_limpia in orden_rareza) else 0
                    datos_ordenados.append((indice_rareza, nombre, precio, rareza, probabilidad))
                elif opcion_filtro in (6, 7):  # Probabilidad
                    datos_ordenados.append((probabilidad, nombre, precio, rareza))

            elif tipo == "armas":
                nombre, precio, probabilidad = datos
                nombre_limpio = regex_color.sub('', nombre) if regex_color else nombre

                if opcion_filtro in (0, 1):  # Nombre
                    datos_ordenados.append((nombre_limpio, nombre, precio, probabilidad))
                elif opcion_filtro in (2, 3):  # Precio
                    datos_ordenados.append((precio, nombre, probabilidad))
                elif opcion_filtro in (4, 5):  # Probabilidad
                    datos_ordenados.append((probabilidad, nombre, precio))

        if opcion_filtro % 2 == 1:  # impares son DESC
            datos_ordenados.sort(reverse=True)
        else:
            datos_ordenados.sort()
        lineas = []
        for datos in datos_ordenados:
            if tipo == "camuflajes":
                if opcion_filtro in (0, 1):
                    nombre_limpio, nombre, precio, rareza, probabilidad = datos
                elif opcion_filtro in (2, 3):
                    precio, nombre, rareza, probabilidad = datos
                elif opcion_filtro in (4, 5):
                    orden, nombre, precio, rareza, probabilidad = datos
                elif opcion_filtro in (6, 7):
                    probabilidad, nombre, precio, rareza = datos
                lineas.append(f"{nombre} | {precio} | {rareza} | {str(probabilidad * 100)}%")

            elif tipo == "armas":
                if opcion_filtro in (0, 1):
                    nombre_limpio, nombre, precio, probabilidad = datos
                elif opcion_filtro in (2, 3):
                    precio, nombre, probabilidad = datos
                elif opcion_filtro in (4, 5):
                    probabilidad, nombre, precio = datos
                lineas.append(f"{nombre} | {precio} | {str(probabilidad * 100)}%")

        lineas_con_encabezado = [encabezado] + lineas
        lineas_ajustadas = reservacion_de_espacio(lineas_con_encabezado, regex_color=regex_color, separador=" | ")
        print(lineas_ajustadas[0])
        for linea in lineas_ajustadas[1:]:
            print(linea)

        print("\n")
        menu_activo, opcion_filtro = gestion_menu(opcion_filtro, opciones_filtros)
    return opcion_filtro

def cargar_diccionario(nombre):
    try:
        with open("diccionarios/" + nombre + ".dat", "r") as archivo:
            return eval(archivo.read())
    except:
        return {}

def guardar_diccionario(nombre, datos):
    try:
        with open("diccionarios/" + nombre + ".dat", "w") as archivo:
            archivo.write(repr(datos))
    except:
        print("ERROR: No se pudo guardar el diccionario", nombre)

def reservacion_de_espacio(datos, cantidad = 4, regex_color = None, separador = " | "):
    if isinstance(datos, dict):
        flag = True
        diccionario_limpio = {}
        for code, valores in datos.items():
            if isinstance(valores, (list, tuple)):
                n = min(cantidad, len(valores))
                if n == 0:
                    continue
                dato1 = str(valores[0])
                dato2 = str(valores[1]) if n > 1 else ""
                dato3 = str(valores[2]) if n > 2 else ""
                if cantidad == 4:
                    dato4 = str(valores[3]) if n > 3 else ""
                    tamanio_texto4 = len(dato4)

                if regex_color != None:
                    dato1 = regex_color.sub('', dato1) if regex_color else dato1
                    dato2 = regex_color.sub('', dato2) if regex_color else dato2

                tamanio_texto1 = len(dato1)
                tamanio_texto2 = len(dato2)
                tamanio_texto3 = len(dato3)

                if flag:
                    mayor1 = tamanio_texto1
                    mayor2 = tamanio_texto2
                    mayor3 = tamanio_texto3
                    if cantidad == 4:
                        mayor4 = tamanio_texto4
                    flag = False
                else:
                    if mayor1 < tamanio_texto1:
                        mayor1 = tamanio_texto1
                    if mayor2 < tamanio_texto2:
                        mayor2 = tamanio_texto2
                    if mayor3 < tamanio_texto3:
                        mayor3 = tamanio_texto3
                    if cantidad == 4:
                        if mayor4 < tamanio_texto4:
                            mayor4 = tamanio_texto4

        for code, valores in datos.items():
            if isinstance(valores, (list, tuple)):
                n = min(cantidad, len(valores))
                if n == 0:
                    continue
                dato1 = str(valores[0])
                dato2 = str(valores[1]) if n > 1 else ""
                dato3 = str(valores[2]) if n > 2 else ""
                if cantidad == 4:
                    dato4 = str(valores[3]) if n > 3 else ""
                    tamanio_texto4 = len(dato4)
                    restante4 = mayor4 - tamanio_texto4

                if regex_color != None:
                    dato1_visible = regex_color.sub('', dato1) if regex_color else dato1
                    dato2_visible = regex_color.sub('', dato2) if regex_color else dato2
                else:
                    dato1_visible = dato1
                    dato2_visible = dato2

                tamanio_texto1 = len(dato1_visible)
                tamanio_texto2 = len(dato2_visible)
                tamanio_texto3 = len(dato3)

                restante1 = mayor1 - tamanio_texto1
                restante2 = mayor2 - tamanio_texto2
                restante3 = mayor3 - tamanio_texto3

                for i in range(restante1):
                    dato1 += " "
                for j in range(restante2):
                    dato2 += " "
                for k in range(restante3):
                    dato3 += " "
                if cantidad == 4:
                    for y in range(restante4):
                        dato4 += " "

                if cantidad == 3:
                    diccionario_limpio[code] = [dato1, dato2, dato3]
                elif cantidad == 4:
                    diccionario_limpio[code] = [dato1, dato2, dato3, dato4]
        return diccionario_limpio

    elif isinstance(datos, list):
        partes_lista = []
        mayores = []
        for item in datos:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                texto = str(item[1])
            else:
                texto = str(item)
            partes = texto.split(separador)
            partes_lista.append(partes)
            for i in range(len(partes)):
                visible = partes[i]
                if regex_color != None:
                    visible = regex_color.sub('', visible) if regex_color else visible
                largo = len(visible)
                if i >= len(mayores):
                    mayores.append(largo)
                else:
                    if mayores[i] < largo:
                        mayores[i] = largo

        salida = []
        for idx in range(len(partes_lista)):
            partes = partes_lista[idx]
            nuevas = []
            for i in range(len(partes)):
                p = partes[i]
                visible = p
                if regex_color != None:
                    visible = regex_color.sub('', visible) if regex_color else visible
                restante = mayores[i] - len(visible)
                for r in range(restante):
                    p += " "
                nuevas.append(p)
            texto_nuevo = separador.join(nuevas)
            item_original = datos[idx]
            if isinstance(item_original, (list, tuple)) and len(item_original) == 2:
                salida.append((item_original[0], texto_nuevo))
            else:
                salida.append(texto_nuevo)
        return salida
    else:
        return datos