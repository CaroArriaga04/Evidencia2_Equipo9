import datetime
import re
from tabulate import tabulate
import pandas as pd
import csv
import os

folio_actual = 0

class Nota:
    def __init__(self, cliente, fecha, rfc, correo):
        global folio_actual
        folio_actual += 1
        self.folio = folio_actual
        self.fecha = fecha
        self.cliente = cliente
        self.rfc = rfc
        self.correo = correo
        self.servicios = []
        self.cancelada = False
        
    @staticmethod
    def guardar_notas_csv():
        with open('notas.csv', 'w', newline='') as csvfile:
            fieldnames = ['folio', 'fecha', 'cliente', 'rfc', 'correo', 'cancelada', 'servicios','precios', 'monto_total']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for nota in notas:
                servicios = ', '.join([servicio.nombre for servicio in nota.servicios])
                precios = ', '.join([str(servicio.costo) for servicio in nota.servicios])
                monto_total = nota.calcular_monto_total()
                writer.writerow({
                    'folio': nota.folio,
                    'fecha': nota.fecha.strftime("%Y-%m-%d"),
                    'cliente' : nota.cliente,
                    'rfc': nota.rfc, 
                    'correo': nota.correo,
                    'cancelada': nota.cancelada,
                    'servicios': servicios,
                    'precios': precios,
                    'monto_total': monto_total
                })

    @staticmethod
    def cargar_notas_csv():
        try:
            with open('notas.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    cliente = row['cliente']
                    fecha = datetime.datetime.strptime(row['fecha'], "%Y-%m-%d").date()
                    rfc = row['rfc']
                    correo = row['correo']
                    cancelada = row['cancelada'] == 'True'
                    servicios_nombres = row['servicios'].split(', ')
                    servicios_precios = map(float, row['precios'].split(', '))
                    servicios = [Servicio(nombre, precio) for nombre, precio in zip(servicios_nombres, servicios_precios)]
                    nota = Nota(cliente, fecha, rfc, correo)
                    nota.servicios = servicios
                    nota.cancelada = cancelada
                    notas.append(nota)
        except FileNotFoundError:
            print("\nNo hay ningun archivo CSV anterior por lo que se comenzara desde un estado vacio. ")
        else:
            print("\nSe han cargado las notas del archivo CVS anterior.")

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)

    def calcular_monto_total(self):
        total = sum(servicio.costo for servicio in self.servicios)
        return total
    
class Servicio:
    def __init__(self, nombre, costo):
        self.nombre = nombre
        self.costo = costo

def imprimir_nota(nota):
    monto_total = nota.calcular_monto_total()
    print("\n---------------NOTA-------------")
    print(f"Folio: {nota.folio}")
    print(f"Fecha: {nota.fecha}")
    print(f"Cliente: {nota.cliente}")
    print(f"RFC: {nota.rfc}")
    print(f"Correo: {nota.correo}")
    print("--------------------------------")
    print("Servicio:")
    for servicio in nota.servicios:
        print(f"- {servicio.nombre}: ${servicio.costo:.2f}")
    print("--------------------------------")
    print(f"Total a pagar: ${monto_total:.2f}")

def validar_continuidad(mensaje):
    while True:
        confirmar = input("\n" + mensaje + " (Solamente Sí/No)?: ")
        if confirmar == "":
            print("\nRespuesta omitida, ingrese nuevamente.")
            continue
        elif confirmar.upper() in ("N", "NO"):
            return False
        elif confirmar.upper() in ("S", "SI"):
            print("\nDe acuerdo.")
            return True
        else:
            print("\nLa respuesta ingresada debe ser 'Si' o 'No'.")

notas = []

rfc_registrados = set()
def registrar_nota():    

    hoy = datetime.date.today()

    while True:
        fecha = input("\nIngresa la fecha (dd/mm/aaaa): ")

        try:
            fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y").date()
            if fecha <= hoy:
                break
            else:
                print("\n* LA FECHA NO PUEDE SER POSTERIOR A LA ACTUAL, INGRESE NUEVAMENTE *")
        except Exception:
            print("\n* FECHA NO INGRESADA O INVALIDA, INGRESE NUEVAMENTE *")

    while True:
      cliente = input("\nNombre del cliente: ")

      if cliente == "":
        print ("\n* INGRESE UN NOMBRE PARA EL REGISTRO DE LA NOTA *")
        continue
      elif not (bool(re.search('^[a-zA-Z ]+$', cliente))):
        print ("\n* NOMBRE NO VALIDO, INGRESE NUEVAMENTE *")
        continue
      else:
        break
    
    while True:
        rfc = input("\nIngrese RFC del cliente: ")
        if rfc == "":
            print("\n* INGRESE UN RFC PARA EL REGISTRO DE LA NOTA *")
            continue
        elif re.search('^[A-Z]{3,4}[0-9]{6}[A-Z0-9]{3}$', rfc) is None:
            print("\n* RFC NO VALIDO, INGRESE NUEVAMENTE *")
            continue
        else:
            rfc_registrados.add(rfc)
            break
    
    while True:
        correo = input("\nIngrese el correo del cliente: ")
        if correo == "":
            print("\n* INGRESE UN CORREO PARA EL REGISTRO DE LA NOTA *")
            continue
        correo = correo.strip()
        if re.search('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', correo) is None:
            print("\n* CORREO NO VALIDO, INGRESE NUEVAMENTE *")
            continue
        else:
            break

    nota = Nota(cliente,fecha,rfc,correo)

    servicio_agregado = False
    while True:
        nombre_servicio = input("\nNombre del servicio requerido (f para finalizar)): ")

        if nombre_servicio.lower() == "f":
            if servicio_agregado:
                break
            else:
                print("\n* PARA FINALIZAR DEBE AGREGAR MINIMO UN SERVICIO *")
                continue
        elif nombre_servicio == "":
          print ("\n * INGRESE EL SERVICIO REQUERIDO * ")
          continue
        elif not (bool(re.search('^[a-zA-Z ]+$', nombre_servicio))):
          print ("\n* SERVICIO NO VALIDO, INGRESE NUEVAMENTE *")
          continue

        while True:
            costo_servicio = input("\nCosto del servicio: ")

            if costo_servicio == "":
                print ("\n* NO SE PERIMTE LA OMICION DEL COSTO *")
                continue
            try:
                costo_servicio = float(costo_servicio)
                if costo_servicio != float(f"{costo_servicio:.2f}"):
                    print("\n* NO SE PERMITEN MAS DE 2 DECIMALES, INGRESE NUEVAMENTE *")
                    continue
            except Exception:
                print ("\n* COSTO NO VALIDO, INGRESE NUEVAMENTE *")
                continue
            if costo_servicio <= 0:
                print("\n* EL COSTO DEL SERVICIO DEBE SER MAYOR A 0, INGRESE NUEVAMENTE *")
                continue
            else:
                servicio = Servicio(nombre_servicio, costo_servicio)
                nota.agregar_servicio(servicio)
                servicio_agregado = True
                break
    notas.append(nota)
    imprimir_nota(nota)


def consulta_por_periodo():
    confirmar = input("\n¿Deseas realizar una consulta por periodo? (Solamente Si/No): ")
    if confirmar.lower() != "si":
        print("\nNo se realizara ninguna consulta.")
        return
    
    while True:
        fecha_inicial = input("\nIngresa la fecha inicial (dd/mm/aaaa): ")
        if fecha_inicial == "":
            fecha_inicial = "01/01/2000"
            print("\nPor omision de fecha inicial se asume 01/01/2000.")
    
        fecha_final = input("\nIngresa la fecha final (dd/mm/aaaa): ")
        if fecha_final == "":
            fecha_final = datetime.date.today().strftime("%d/%m/%Y")
            print("\nPor omision de fecha final se asume la fecha actual. ")

        try:
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d/%m/%Y").date()
            fecha_final = datetime.datetime.strptime(fecha_final, "%d/%m/%Y").date()
        except Exception:
            print("\n* LAS FECHAS INGRESADAS DEBEN ESTAR EN FORMATO dd/mm/yyyy *")
            continue
        
        if fecha_final < fecha_inicial:
            print("\n* LA FECHA FINAL NO PUEDE SER ANTERIOR A LA FECHA INICIAL *")
            continue
        else:
            break
    
    notas_por_periodo = [n for n in notas if not n.cancelada and fecha_inicial <= n.fecha  <= fecha_final]
    if notas_por_periodo:
        print("\n---------------------------NOTAS POR PERIODO-------------------------")
        informacion = [[n.folio, n.fecha, n.cliente, n.rfc, n.correo] for n in notas_por_periodo]
        titulos = ["Folio", "Fecha", "Cliente", "RFC", "Correo"]
        print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
        monto = [servicios.costo for nota in notas_por_periodo for servicios in nota.servicios]
        monto_promedio = pd.Series(monto).mean()
        informacion = [["Monto promedio", monto_promedio]]
        print(tabulate(informacion, tablefmt="fancy_grid"))
    else:
        print("\n* NO SE ENCUENTRAN NOTAS EN EL PERIODO SOLICITADO *")

def consulta_por_folio():
    confirmar = input("\n¿Deseas realizar una consulta por folio? (Solamente Si/No): ")
    if confirmar.lower() != "si":
        print("\nNo se realizara ninguna consulta.")
        return
    while True:
        folio = input("\nIngresa el folio de la nota solicitada: ")
        if folio == "":
            print("\n* FOLIO OMITIDO, INGRESE PORFAVOR *")
            continue
        if not folio.isdigit():
            print("\n* FOLIO DEBE SER NUMERO, INGRESE NUEVAMENTE")
            continue
        nota_encontrada = None
        for nota in notas:
            if nota.folio == int(folio) and not nota.cancelada:
                nota_encontrada = nota
                break
        if nota_encontrada:
            imprimir_nota(nota_encontrada)
        else:
            print("\n* EL FOLIO INDICADO NO EXISTE O CORRESPONDE A UNA NOTA CANCELADA *")
        break

def imprimir_notas_rfc():
    notas_no_canceladas = [nota for nota in notas if not nota.cancelada]
    informacion = []

    if notas_no_canceladas:
        notas_no_canceladas.sort(key=lambda x: (x.rfc, x.folio))
        
        current_rfc = None  #esta variable tastreara el RFC actual en el for
        folio = 0

        for nota in notas_no_canceladas:
            if nota.rfc != current_rfc:
                folio += 1
                current_rfc = nota.rfc
                informacion.append([nota.rfc, folio])
        print(tabulate(informacion, headers=["RFC", "Folio"], tablefmt="fancy_grid"))
    else:
        print("\nNo hay notas disponibles para consultar.")
    return informacion

def consulta_por_cliente():
    confirmar = input("\n¿Deseas realizar una consulta por cliente? (Solamente Si/No): ")
    if confirmar.lower() != "si":
        print("\nNo se realizara ninguna consulta.")
        return
    informacion_notas = imprimir_notas_rfc()
    while True:
      folio_consultado = input("\nIngresa el folio referente al RFC deseado a consultar: ")
      if folio_consultado == "":
        print ("\n* NO OMITIR FOLIO, INGRESE POR FAVOR *")
        continue
      try:
          folio_consultado = int(folio_consultado)
      except Exception:
            print("\n* FOLIO DEBE SER NUMERO, INGRESE NUEVAMENTE *")
            continue
      rfc_seleccionado = None
      for informacion in informacion_notas:
          if folio_consultado == informacion[1]:
            rfc_seleccionado = informacion[0]
            break
      if rfc_seleccionado is None:
         print("\n* EL FOLIO PROPORCIONADO NO CORRESPONDE A UN RFC *")
         continue
      notas_seleccionadas = [nota for nota in notas if nota.rfc == rfc_seleccionado and not nota.cancelada]
      break
      
    informacion = []
    for nota in notas_seleccionadas:  
            imprimir_nota(nota)
            # Crear un DataFrame a partir de la información de la nota
            servicios = ', '.join([servicio.nombre for servicio in nota.servicios])
            costos = ', '.join([str(servicio.costo) for servicio in nota.servicios])
            total = sum([servicio.costo for servicio in nota.servicios])
            informacion.append([nota.folio, nota.fecha, nota.cliente, nota.rfc, nota.correo, servicios, costos, total])
                    
    if notas_seleccionadas:
        montos = [servicio.costo for nota in notas_seleccionadas for servicio in nota.servicios]
        monto_promedio = pd.Series(montos).mean()
        informacion_promedio = [["Monto promedio", monto_promedio]]
        print(tabulate(informacion_promedio, tablefmt="fancy_grid"))

    atributos = ["Folio", "Fecha", "Cliente", "RFC", "Correo", "Servicio", "Costo", "Monto total"]
    df = pd.DataFrame(informacion, columns=atributos)
    df['Monto total'] = df['Monto total'].astype(float)  
    
    # Preguntar al usuario si desea guardar la nota en un archivo Excel
    while True:
        pasar_excel = input("\n¿Deseas convertir esta nota en un archivo Excel? (Si/No): ")
        if pasar_excel.lower() == "si":
            fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y')
            archivo_excel = f"{nota.rfc}_{fecha_actual}.xlsx"

        if pasar_excel.lower() == "no":
            print ("\nOK")
            break
        # Guardar el DataFrame en el archivo de Excel
        df.to_excel(archivo_excel, index=False, engine='openpyxl')
        print(f"\n--- Los resultados se han guardado en el archivo con el nombre: '{archivo_excel}' ---")
        print(f"\nEl archivo '{archivo_excel}' se ha guardado en la ubicación: {os.path.abspath(archivo_excel)}")
        break

def cancelar_nota():
    while True:
        cancelado = input("\nIngresa el folio de la nota a cancelar: ")
        if cancelado == "":
            print ("\n* FOLIO OMITIDO, INGRESE NUEVAMENTE*")
            continue
        if not cancelado.isdigit():
            print("\n* FOLIO DEBE SER UN NUMERO, INGRESA NUEVAMENTE *")
            continue
        cancelado = int(cancelado)
        nota_a_cancelar = None 
        for nota in notas:
            if nota.folio == cancelado:
                nota_a_cancelar = nota
                break
        if nota_a_cancelar:
            if nota_a_cancelar.cancelada:
                print("\n* LA NOTA YA ESTÁ CANCELADA *")
                continue
            imprimir_nota(nota_a_cancelar)
        if nota_a_cancelar:
            imprimir_nota(nota_a_cancelar)
            while True:
                confirmacion = input("\n¿Estás seguro de que quieres cancelar esta nota? (Si/No): ")
                if confirmacion == "":
                    print("\n* RESPUESTA OMITIDA, INGRESE POR FAVOR *")
                elif confirmacion.upper() in ["SI", "S"]:
                    print("\nNota cancelada.")
                    nota_a_cancelar.cancelada = True
                    break
                elif confirmacion.upper() in ["NO", "N"]:
                    print("\nNota no cancelada.")
                    break
                else:
                    print("\nLa respuesta ingresada debe ser 'Si' o 'No'.")
        else:
            print("\n* LA NOTA INGRESADA NO SE ENCUENTRA EN EL SISTEMA *")
        break

def recuperar_nota():
    notas_canceladas = [nota for nota in notas if nota.cancelada]
    if notas_canceladas:
        print("\n---------NOTAS CANCELADAS---------")
        informacion = [[n.folio, n.fecha, n.cliente, n.rfc, n.correo] for n in notas_canceladas]
        titulos = ["Folio", "Fecha", "Cliente", "RFC", "Correo"]
        print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
        
    while True:
        folio_a_recuperar = input("\nIngresa el folio de la nota a recuperar ('No' para salir): ")
        if (folio_a_recuperar.lower() == "no"):
            print("\nNo se realizará ninguna recuperación.")
            break
        elif folio_a_recuperar == "":
            print("\n* FOLIO OMITIDO, INGRESE FOLIO *")
            continue
        if not folio_a_recuperar.isdigit():
            print("\n* FOLIO DEBE SER UN NUMERO, INGRESA NUEVAMENTE *")
            continue
        folio_a_recuperar = int(folio_a_recuperar)
        nota_recuperada = None 
        for nota in notas:
            if nota.folio == folio_a_recuperar:
                nota_recuperada = nota
                break
        if nota_recuperada:
            imprimir_nota(nota_recuperada)
            confirmacion = input("\n¿Desea recuperar esta nota? (Solamente Sí/No): ")
            if confirmacion.lower() == "si":
                nota_recuperada.cancelada = False
                print("\nLa nota ha sido recuperada con éxito.")
            else:
                print("\nLa nota no ha sido recuperada.")
        else:
            print("\nEl folio proporcionado no corresponde a una nota cancelada.")
        break

print("\n---------------TALLER MECANICO--------------")
print("   BIENVENIDO A NUESTRO SISTEMA DE NOTAS    ")
print("--------------------------------------------")

Nota.cargar_notas_csv()

while True:
    print("\nMENU")
    print("1. Registrar nota")
    print("2. Consultas y Reportes")
    print("3. Cancelar nota")
    print("4. Recuperar nota")
    print("5. Salir del sistema")

    opcion = input("Elige una opcion: ")
    if opcion == "":
        print("\n* OPCION OMITIDA, INGRESE UNA OPCION *")
        continue
    
    if opcion == "1":
        if validar_continuidad("¿Estas seguro de realizar un registro?"):
            registrar_nota()

    elif opcion == "2":
            while True:
                print("\n----CONSULTAS Y REPORTES----")
                print("1. Consulta por periodo\n2. Consulta por folio\n3. Consulta por cliente\n4. Regresar al menu")
                sub_opcion = input("Elige una opcion: ")
                if sub_opcion == "1":
                    consulta_por_periodo()
                elif sub_opcion == "2":
                    consulta_por_folio()
                elif sub_opcion == "3":
                    consulta_por_cliente()
                elif sub_opcion == "4":
                    print("\n* OK *")
                    break
                else:
                    print("\n* OPCION NO VALIDA, INGRESE NUEVAMENTE *")

    elif opcion == "3":
        if validar_continuidad("¿Estas seguro de que quieres cancelar una nota?"):
            cancelar_nota()

    elif opcion == "4":
         if validar_continuidad("\n¿Estas seguro de que quieres recuperar una nota?"):
            recuperar_nota()

    elif opcion == "5":
        if validar_continuidad("\n¿Deseas salir del programa?"):
            Nota.guardar_notas_csv()
            ("\nDe acuerdo. Saliendo del programa...")
            break
    else:
        print("\n* OPCION NO VALIDA, INGRESE NUEVAMENTE *")
        continue
