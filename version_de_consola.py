# CAMBIOS REALIZADOS:
# Se modifico todo el pedo para que ahora puedan configurarse varias interfaces en los switches



from sistema_experto import aplicar_reglas, guardar_configuracion

def preguntar(texto):
    return input(texto).strip().lower()

def main():
    hechos = {}

    tipo = preguntar("¿El dispositivo es un Router o un Switch? (router/switch): ")
    hechos["tipo"] = tipo

    # CONFIGURACIONES PARA AMBOS DISPOSITIVOS

    if preguntar("¿Deseas establecer un nombre para el dispositivo? (s/n): ") == 's':
        hechos["hostname"] = input("Nombre del dispositivo: ").strip()

    if preguntar("¿Deseas configurar contraseñas? (s/n): ") == 's':
        if preguntar("¿Contraseña de consola? (s/n): ") == 's':
            hechos["console_pw"] = input("Contraseña para consola: ").strip()

        if preguntar("¿Contraseña de acceso remoto (VTY)? (s/n): ") == 's':
            hechos["vty_pw"] = input("Contraseña para VTY: ").strip()

        if preguntar("¿Deseas establecer enable secret? (s/n): ") == 's':
            hechos["enable_secret"] = input("Contraseña para enable secret: ").strip()

    if hechos.get("enable_secret") or hechos.get("console_pw") or hechos.get("vty_pw"):
        if preguntar("¿Deseas encriptar las contraseñas? (s/n): ") == 's':
            hechos["encriptar_contrasenas"] = True
        else:
            hechos["encriptar_contrasenas"] = False
    
    if preguntar("¿Deseas establecer un banner MOTD? (s/n): ") == 's':
        hechos["banner_motd"] = input("Escribe el mensaje para el banner MOTD: ").strip()

###


    # CONFIGURACIONES ESPECÍFICAS PARA SWITCHES
    if tipo == "switch":
        if preguntar("¿Deseas configurar las interfaces del switch? (s/n): ") == 's':
            cantidad_interfaces = 0
            interfaces = []
            # Preguntar cuántas interfaces se desean configurar
            while True:
                try:
                    cantidad_interfaces_str = input("¿Cuántas interfaces deseas configurar en el switch? ")
                    cantidad_interfaces = int(cantidad_interfaces_str)
                    if cantidad_interfaces >= 0:
                        break
                    else:
                        print("Por favor, ingresa un número válido.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingresa un número.")

            for i in range(cantidad_interfaces):
                print(f"\n--- Configurando Interfaz de Switch #{i + 1} ---")
                interfaz = {}
                interfaz["interface"] = input(f"Interfaz {i + 1} (ej. VLAN1, GigabitEthernet0/1): ").strip()

                if preguntar("¿Deseas configurar una dirección IP y máscara para esta interfaz? (s/n): ") == 's':
                    interfaz["ip_switch"] = input(f"Dirección IP del switch para la interfaz {i + 1}: ").strip()
                    interfaz["mascara_switch"] = input(f"Máscara de subred del switch para la interfaz {i + 1}: ").strip()

                if preguntar("¿Deseas establecer una descripción para la interfaz? (s/n): ") == 's':
                    interfaz["descripcion"] = input(f"Descripción de la interfaz {i + 1}: ")

                interfaces.append(interfaz)

            if interfaces:
                hechos["interfaces_switch"] = interfaces
    
    # CONFIGURACIONES ESPECÍFICAS PARA ROUTERS

    if tipo == "router":

        if preguntar("¿Deseas configurar las interfaces? (s/n): ") == 's':
            cantidad_interfaces = 0
            interfaces= []
            # Preguntar cuántas interfaces se desean configurar
            while True:
                try:
                    cantidad_interfaces_str = input("¿Cuántas interfaces deseas configurar? ")
                    cantidad_interfaces = int(cantidad_interfaces_str)
                    if cantidad_interfaces >= 0: # Permitir 0 si el usuario cambia de opinión o para flexibilidad
                        break
                    else:
                        print("Por favor, ingresa un número valido.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingresa un número.")

            for i in range(cantidad_interfaces):
                print(f"\n--- Configurando Interfaz #{i + 1} ---")
                interfaz = {}
                interfaz["interface"] = input(f"Interfaz {i + 1} (ej. GigabitEthernet0/0): ").strip()
                if preguntar("¿Deseas configurar ipv4 en esta interfaz? (s/n): ") == 's':
                    interfaz["ip"] = input(f"Dirección IP de la interfaz {i + 1}: ").strip()
                    interfaz["mascara"] = input(f"Máscara de subred de la interfaz {i + 1}: ").strip()
                if preguntar("¿Deseas configurar ipv6 en esta interfaz? (s/n): ") == 's':
                    interfaz["ipv6"] = input(f"Dirección IPv6 de la interfaz {i + 1}: ").strip()
                    interfaz["ipv6_prefix"] = input(f"Prefijo IPv6 de la interfaz {i + 1} (ej. /64): ").strip()
                if preguntar("¿Deseas establecer una descripción para la interfaz? (s/n): ") == 's':
                    interfaz["descripcion"] = input(f"Descripción de la interfaz {i + 1}: ")
                interfaces.append(interfaz)
            if interfaces: 
                hechos["interfaces_router"] = interfaces



        if preguntar("¿Deseas configurar OSPF? (s/n): ") == 's':
            hechos["ospf_process_id"] = input("Identificador del proceso OSPF (ej. 1): ").strip() # Pedir una sola vez
            
            redes_ospf = [] # Inicializar una lista para las redes
            cantidad_redes = 0
            while True:
                try:
                    cantidad_redes_str = input("¿Cuántas redes deseas agregar para este proceso OSPF? ")
                    cantidad_redes = int(cantidad_redes_str)
                    if cantidad_redes >= 0: # Permitir 0 si el usuario cambia de opinión o para flexibilidad
                        break
                    else:
                        print("Por favor, ingresa un número no negativo.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingresa un número.")

            for i in range(cantidad_redes):
                print(f"\n--- Configurando Red OSPF #{i + 1} ---")
                red = {} # Diccionario para esta red específica
                red["network"] = input(f"Red OSPF [{i + 1}] (ej. 192.168.1.0): ").strip()
                red["wildcard"] = input(f"Wildcard OSPF [{i + 1}] (ej. 0.0.0.255): ").strip()
                red["area"] = input(f"Área OSPF [{i + 1}] (ej. 0): ").strip()
                redes_ospf.append(red)
            
            if redes_ospf: 
                hechos["ospf_networks"] = redes_ospf


        if preguntar("¿Deseas configurar NAT? (s/n): ") == 's':
            tipo_nat = preguntar("¿Qué tipo de NAT deseas configurar? (dinamico/estatico): ")
            hechos["tipo_nat"] = tipo_nat

            if tipo_nat == "dinamico":
                hechos["nat_inside_interface"] = input("Interfaz interna (ej. GigabitEthernet0/0): ").strip()
                hechos["nat_outside_interface"] = input("Interfaz externa (ej. GigabitEthernet0/1): ").strip()
                hechos["nat_acl_num"] = input("Número de lista de acceso estándar para NAT (ej. 1): ").strip()
                hechos["nat_red_local"] = input("Red interna para NAT (ej. 192.168.1.0): ").strip()
                hechos["nat_wildcard"] = input("Wildcard de la red interna (ej. 0.0.0.255): ").strip()

            elif tipo_nat == "estatico":
                hechos["nat_inside_interface"] = input("Interfaz interna (ej. GigabitEthernet0/0): ").strip()
                hechos["nat_outside_interface"] = input("Interfaz externa (ej. GigabitEthernet0/1): ").strip()
                hechos["ip_privada"] = input("Dirección IP privada (ej. 192.168.1.10): ").strip()
                hechos["ip_publica"] = input("Dirección IP pública (ej. 200.1.1.10): ").strip()
###

    if preguntar("Deseas guardar la configuracion? (s/n): ") == 's':
        hechos["wr"] = ''


    config = aplicar_reglas(hechos)
    guardar_configuracion(config, f"{tipo}_config.txt")


if __name__ == "__main__":
    main()
