import datetime
import re
from tabulate import tabulate

folio_actual = 0

class Nota:
    def __init__(self, cliente, fecha):
        global folio_actual
        folio_actual += 1
        self.folio = folio_actual
        self.fecha = fecha
        self.cliente = cliente
        self.servicios = []
        self.cancelada = False

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
      elif not (bool(re.search('^[a-zA-Z]+$', cliente))):
        print ("\n* NOMBRE NO VALIDO, INGRESE NUEVAMENTE *")
        continue
      else:
        break
      
    nota = Nota(cliente,fecha)

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
        elif not (bool(re.search('^[a-zA-Z]+$', nombre_servicio))):
          print ("\n* SERVICIO NO VALIDO, INGRESE NUEVAMENTE *")
          continue

        while True:
            costo_servicio = input("\nCosto del servicio: ")

            if costo_servicio == "":
                print ("\n* NO SE PERIMTE LA OMICION DEL COSTO *")
                continue
            elif not (bool(re.match("^[0-9]+(\.[0-9]+)?$", costo_servicio))):
                print ("\n* COSTO NO VALIDO, INGRESE NUEVAMENTE *")
                continue
            costo_servicio = float(costo_servicio)
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
        try:
            fecha_inicial = input("\nIngresa la fecha inicial (dd/mm/aaaa): ")
            fecha_final = input("Ingresa la fecha final (dd/mm/aaaa): ")
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, "%d/%m/%Y").date()
            fecha_final = datetime.datetime.strptime(fecha_final, "%d/%m/%Y").date()
        except Exception:
            print("\n* LAS FECHAS INGRESADAS DEBEN ESTAR EN FORMATO dd/mm/yyyy *")
        else: 
            notas_no_canceladas = [n for n in notas if not n.cancelada]
            notas_por_periodo = [n for n in notas_no_canceladas if fecha_inicial <= n.fecha  <= fecha_final]
            if notas_por_periodo:
                print("\n---------NOTAS POR PERIODO---------")
                informacion = [[n.folio, n.fecha, n.cliente] for n in notas_por_periodo]
                titulos = ["Folio", "Fecha", "Cliente"]
                print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
            else:
                print("\n* NO SE ENCUENTRAN NOTAS EN PERIODO SOLICITADO *")
            break

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
        try:
            folio = int(folio)
        except Exception:
            print("\n* FOLIO DEBE SER NUMERO, INGRESE NUEVAMENTE")
            continue
        nota_encontrada = False
        for nota in notas:
            if nota.folio == int(folio) and not nota.cancelada:
                imprimir_nota(nota)
                nota_encontrada = True
            if not nota_encontrada:
                print("\n* EL FOLIO INDICADO NO EXISTE O CORRESPONDE A UNA NOTA CANCELADA *")
                break
        break

def cancelar_nota():
    while True:
        cancelado = input("\nIngresa el folio de la nota a cancelar: ")
        try:
            cancelado = int(cancelado)
        except Exception:
            print("\n* FOLIO DEBE SER UN NUMERO, INGRESA NUEVAMENTE *")
            continue
        nota_a_cancelar = None 
        for nota in notas:
            if nota.folio == cancelado:
                nota_a_cancelar = nota
                break
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
        informacion = [[n.folio, n.fecha, n.cliente] for n in notas_canceladas]
        titulos = ["Folio", "Fecha", "Cliente"]
        print(tabulate(informacion, titulos, tablefmt="fancy_grid"))
        
    while True:
        folio_a_recuperar = input("\nIngresa el folio de la nota a recuperar ('No' para salir): ")
        if (folio_a_recuperar.lower() == "no"):
            print("\nNo se realizará ninguna recuperación.")
            break
        elif folio_a_recuperar == "":
            print("\n* FOLIO OMITIDO, INGRESE FOLIO *")
            continue
        try:
            folio_a_recuperar = int(folio_a_recuperar)
        except Exception:
            print("\n* FOLIO DEBE SER UN NUMERO, INGRESA NUEVAMENTE *")
            continue
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
                print("1. Consulta por periodo\n2. Consulta por folio\n3. Regresar al menu principal ")
                sub_opcion = input("Elige una opcion: ")
                if sub_opcion == "1":
                    consulta_por_periodo()
                elif sub_opcion == "2":
                    consulta_por_folio()
                elif sub_opcion == "3":
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
            ("\nDe acuerdo. Saliendo del programa...")
            break
    else:
        print("\n* OPCION NO VALIDA, INGRESE NUEVAMENTE *")
        continue