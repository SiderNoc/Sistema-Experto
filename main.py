from sistema_experto import aplicar_reglas, guardar_configuracion

def preguntar(texto):
    return input(texto).strip().lower()

def main():
    hechos = {}

    tipo = preguntar("¿El dispositivo es un Router o un Switch? (router/switch): ")
    hechos["tipo"] = tipo

    if preguntar("¿Deseas establecer un nombre para el dispositivo? (s/n): ") == 's':
        hechos["hostname"] = input("Nombre del dispositivo: ").strip()

    if preguntar("¿Deseas configurar contraseñas? (s/n): ") == 's':
        if preguntar("¿Contraseña de consola? (s/n): ") == 's':
            hechos["console_pw"] = input("Contraseña para consola: ").strip()

        if preguntar("¿Contraseña de acceso remoto (VTY)? (s/n): ") == 's':
            hechos["vty_pw"] = input("Contraseña para VTY: ").strip()

        if preguntar("¿Deseas establecer enable secret? (s/n): ") == 's':
            hechos["enable_secret"] = input("Contraseña para enable secret: ").strip()
    
    if preguntar("¿Deseas establecer un banner MOTD? (s/n): ") == 's':
        hechos["banner_motd"] = input("Escribe el mensaje para el banner MOTD: ").strip()

    if preguntar("Deseas establecer una dirección IPv4? (s/n): ") == 's':
        if tipo == "router":
            hechos["interface"] = input("Interfaz (ej. GigabitEthernet0/0): ").strip()
            hechos["ip_router"] = input("Dirección IP del router: ").strip()
            hechos["mascara_router"] = input("Máscara de subred del router: ").strip()
        elif tipo == "switch":
            hechos["interface"] = input("Interfaz (ej. VLAN1): ").strip()
            hechos["ip_switch"] = input("Dirección IP del switch: ").strip()
            hechos["mascara_switch"] = input("Máscara de subred del switch: ").strip()

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

#TERMINAR LA REGLA DE NAT
#REVISAR LA PREGUNTA DE NAT
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
