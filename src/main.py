"""
Punto de entrada principal para el inicio y control del software "Academia de Héroes".

Se encarga de levantar y mapear el menú interactivo para la consola de comandos 
proveyendo acceso a la creación, lectura, actualización y combate interactivo 
mediante los modelos predefinidos.
"""
import sys
from db.db_config import get_connection
from models import Personaje, Guerrero, Mago, Arquero
from repository import insertar, actualizar, borrar, obtener_por_id, listar

def mostrar_menu():
    """
    Despliega las opciones navegables del menú principal por consola.
    Presenta una interfaz de texto plana.
    """
    print("\n" + "="*50)
    print("ACADEMIA DE HÉROES - MENÚ PRINCIPAL")
    print("="*50)
    print("1. Crear personaje")
    print("2. Listar personajes")
    print("3. Simular combate")
    print("4. Entrenar personaje")
    print("5. Eliminar personaje")
    print("0. Salir")
    print("="*50)

def crear_personaje(conn):
    """
    Asistente interactivo para generar e inyectar un nuevo personaje a la base de datos.
    Pregunta paso a paso por todos los atributos indispensables según la clase elegida.

    Args:
        conn (sqlite3.Connection): Conexión activa a la base de datos.
    """
    print("\n--- Crear Personaje ---")
    nombre = input("Nombre: ")
    try:
        nivel_input = input("Nivel (mín 1, default 1): ")
        nivel = int(nivel_input) if nivel_input.strip() else 1
    except ValueError:
        nivel = 1
    
    print("Tipos disponibles: 1. Guerrero, 2. Mago, 3. Arquero, 4. Personaje Base")
    tipo_sel = input("Selecciona tipo (1-4): ")
    
    try:
        if tipo_sel == "1":
            armadura_input = input("Armadura (default 5): ")
            armadura = int(armadura_input) if armadura_input.strip() else 5
            p = Guerrero(nombre, nivel, armadura=armadura)
        elif tipo_sel == "2":
            mana_input = input("Mana (default 50): ")
            mana = int(mana_input) if mana_input.strip() else 50
            p = Mago(nombre, nivel, mana=mana)
        elif tipo_sel == "3":
            precision_input = input("Precisión (0-100, default 80): ")
            precision = int(precision_input) if precision_input.strip() else 80
            p = Arquero(nombre, nivel, precision=precision)
        else:
            p = Personaje(nombre, nivel)
        
        insertar(conn, p)
        print(f"Personaje creado exitosamente bajo el ID: {p.id}")
    except ValueError as e:
        print(f"Error de validación durante la creación: {e}")

def listar_personajes(conn) -> list:
    """
    Pide todos los personajes registrados en el repositorio y los imprime en consola.

    Args:
        conn (sqlite3.Connection): Conexión activa a la base de datos.

    Returns:
        list: Colección de objetos recuperados del catálogo y listados localmente.
    """
    personajes = listar(conn)
    if not personajes:
        print("\nNo existen personajes registrados actualmente.")
        return []
    
    print("\n--- Lista Exhaustiva de Personajes ---")
    for p in personajes:
        print(f"[{p.id}] {p}")
    return personajes

def simular_combate(conn):
    """
    Motor interactivo de simulación para batallas 1vs1 controladas por menú.
    Permite turnos alternados procesando estados individuales de salud o maná 
    hasta la total liquidación de uno de los participantes.

    Args:
        conn (sqlite3.Connection): Conexión estructurada a SQLite.
    """
    personajes = listar_personajes(conn)
    if len(personajes) < 2:
        print("El modo combate requiere obligatoriamente de al menos dos participantes disponibles.")
        return

    try:
        id1 = int(input("\nInserte el ID asignado para el rol de Atacante Inicial: "))
        id2 = int(input("Inserte el ID asignado para el rol de Defensor: "))
        
        p1 = obtener_por_id(conn, id1)
        p2 = obtener_por_id(conn, id2)
        
        if not p1 or not p2:
            print("Datos corruptos: Uno o ambos IDs ingresados no están referenciados.")
            return

        print(f"\n¡INICIA LA SIMULACIÓN DE COMBATE: {p1.nombre} contra {p2.nombre}!")
        
        turno = 1
        while p1.esta_vivo() and p2.esta_vivo():
            print(f"\n--- Turno Secuencial {turno} ---")
            
            # Etapa del atacante P1
            danio = 0
            if isinstance(p1, Mago) and p1.mana >= 10:
                usar_especial = input(f"¿Atacante {p1.nombre} canalizará la habilidad mágica superior? (s/n): ").lower() == 's'
                if usar_especial:
                    danio = p1.ataque_especial()
                else:
                    danio = p1.ataque()
            else:
                danio = p1.ataque()
            
            if danio > 0:
                p2.recibir_danio(danio)
            
            if not p2.esta_vivo():
                print(f"Incapacitación crítica: {p2.nombre} ha caído al recibir trauma grave.")
                break
                
            # Etapa de contraofensiva de P2
            danio2 = p2.ataque()
            if danio2 > 0:
                p1.recibir_danio(danio2)
                
            if not p1.esta_vivo():
                print(f"Incapacitación crítica: El contraataque acabó con {p1.nombre}.")
                break
            
            turno += 1
            input("Presione la tecla <Enter> para iterar el siguiente paso del proceso...")

        print("\nResultado estandarizado: Fin concluyente del transcurso del duelo.")
        guardar = input("¿Se solicita archivar esta nueva variación de integridad física en Base de Datos? (s/n): ").lower() == 's'
        if guardar:
            actualizar(conn, p1)
            actualizar(conn, p2)
            print("Sistema de archivo sincronizado: los valores se persistieron internamente.")

    except ValueError:
        print("Excepción atrapada: Solo se admiten transacciones y selecciones numéricas íntegras.")

def entrenar_personaje(conn):
    """
    Focaliza a una unidad del sistema y asciende artificialmente su nivel.

    Args:
        conn (sqlite3.Connection): Conexión activa a la base de datos.
    """
    listar_personajes(conn)
    try:
        pid = int(input("\nID técnico del personaje elegido para el adiestramiento intensivo: "))
        p = obtener_por_id(conn, pid)
        if p:
            p.subir_nivel()
            actualizar(conn, p)
            print(f"Certificación exitosa: {p.nombre} ha modificado su categorización jerárquica a nivel {p.nivel}.")
        else:
            print("Consulta fallada, ID huérfano.")
    except ValueError:
        print("La denominación ID resulta de naturaleza errónea.")

def eliminar_personaje(conn):
    """
    Selecciona y destruye enteramente una fila y entidad correspondiente al ID objetivo.

    Args:
        conn (sqlite3.Connection): Conexión activa a la base de datos.
    """
    listar_personajes(conn)
    try:
        pid = int(input("\nIdentificador estricto a solicitar su purgado del registro central: "))
        p = obtener_por_id(conn, pid)
        if p:
            confirm = input(f"Se precisa confirmación ineludible para desintegrar a {p.nombre} del plano (s/n): ").lower() == 's'
            if confirm:
                borrar(conn, pid)
                print("Línea suprimida del formato relacional con saldo eficiente.")
        else:
            print("Puntero de selección nulo, no se ha operado modificación alguna.")
    except ValueError:
        print("Input corrupto, el flujo requiere números para el control interno de la BD.")

def main():
    """
    Bucle principal del frontend textual de la aplicación.
    Sostiene la conexión viva y evalúa la entrada principal del usuario
    hasta solicitar el comando de salida programada.
    """
    conn = get_connection()
    while True:
        mostrar_menu()
        opcion = input("Instrucción seleccionada por código: ")
        
        if opcion == "1":
            crear_personaje(conn)
        elif opcion == "2":
            listar_personajes(conn)
        elif opcion == "3":
            simular_combate(conn)
        elif opcion == "4":
            entrenar_personaje(conn)
        elif opcion == "5":
            eliminar_personaje(conn)
        elif opcion == "0":
            print("Secuencia de cerrado iniciada, ejecución terminada.")
            break
        else:
            print("Opción fuera de índice matricial, reinténtalo.")
    
    conn.close()

if __name__ == "__main__":
    main()
