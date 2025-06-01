# REGLAS DEL SISTEMA EXPERTPO

# CAMBIOS REALIZADOS:
# Ahora regla_encriptar_contrasenas solo se ejecuta si se han configurado contraseñas.
# Se sustituyo regla_ip_router por regla_interfaces_router para manejar múltiples interfaces.
# Se seccionaron las reglas preguntas en reglas generales y especificas para cada dispositivo

# COSAS A REVISAR:
# Modificar regla_ip_switch para manejar múltiples interfaces si es necesario.
# Modificar regla_ip_switch para solo solictar numero de VLAN
# Añadir reglas para aplicar las VLANs en los switches si es necesario.


# Reglas para ambos dispositivos
def regla_hostname(hechos, config):
    if hechos.get("hostname"):
        config.append(f"hostname {hechos['hostname']}")


def regla_consola(hechos, config):
    if hechos.get("console_pw"):
        config += [
            "line console 0",
            f" password {hechos['console_pw']}",
            " login",
            " exit"
        ]


def regla_vty(hechos, config):
    if hechos.get("vty_pw"):
        config += [
            "line vty 0 4",
            f" password {hechos['vty_pw']}",
            " login",
            " exit"
        ]


def regla_enable_secret(hechos, config):
    if hechos.get("enable_secret"):
        config.append(f"enable secret {hechos['enable_secret']}")

def regla_encriptar_contrasenas(hechos, config):
    # Solo añade el comando si la clave existe y es True
    if hechos.get("encriptar_contrasenas") is True: 
        config.append("service password-encryption")
    # Un mensaje si el usuario explícitamente dijo que no
    elif hechos.get("encriptar_contrasenas") is False:
        print("[DEBUG] El usuario eligió no encriptar las contraseñas.")

def regla_banner_motd(hechos, config):
    if hechos.get("banner_motd"):
        print("[DEBUG] Ejecutando regla_banner_motd")
        config.append(f"banner motd #{hechos['banner_motd']}#")
###


# Reglas de switches
#EN MODIFICACION
def regla_ip_switch(hechos, config):
    if hechos.get("ip_switch") and hechos.get("mascara_switch"):
        config.append(f"interface {hechos['interface']}")
        config.append(f" ip address {hechos['ip_switch']} {hechos['mascara_switch']}")
        config.append(" no shutdown")
        config.append(" exit")

####
###


# Reglas de routers
def regla_interfaces_router(hechos, config):
    if "interfaces_router" in hechos and hechos["interfaces_router"]:
        for interfaz_data in hechos["interfaces_router"]:
            nombre_interfaz = interfaz_data.get("interface")
            if not nombre_interfaz:
                print(f"[AVISO] Se omitió una interfaz porque no tiene nombre: {interfaz_data}")
                continue

            config.append(f"interface {nombre_interfaz}")

            descripcion = interfaz_data.get("descripcion")
            if descripcion:
                config.append(f" description {descripcion}")

            ip_v4 = interfaz_data.get("ip")
            mascara_v4 = interfaz_data.get("mascara")
            if ip_v4 and mascara_v4:
                config.append(f" ip address {ip_v4} {mascara_v4}")
            elif ip_v4 or mascara_v4: # Si solo uno de los dos está presente
                print(f"[AVISO] Para la interfaz {nombre_interfaz}, se proporcionó IP o máscara IPv4, pero no ambos. Se omitirá la configuración IPv4.")

            ip_v6 = interfaz_data.get("ipv6")
            prefijo_v6 = interfaz_data.get("ipv6_prefix") # ej. "/64" o "64"
            if ip_v6 and prefijo_v6:
                # Aseguramos que el prefijo tenga el formato correcto (ej. /64)
                if not prefijo_v6.startswith('/'):
                    prefijo_v6_completo = f"/{prefijo_v6}"
                else:
                    prefijo_v6_completo = prefijo_v6
                config.append(f" ipv6 address {ip_v6}{prefijo_v6_completo}")
                config.append(" ipv6 enable") # Generalmente se requiere para activar IPv6 en la interfaz
            elif ip_v6 or prefijo_v6: # Si solo uno de los dos está presente
                print(f"[AVISO] Para la interfaz {nombre_interfaz}, se proporcionó dirección o prefijo IPv6, pero no ambos. Se omitirá la configuración IPv6.")

            config.append(" no shutdown")
            config.append(" exit")
        config.append("") # Añade una línea en blanco después de configurar todas las interfaces para mayor legibilidad

def regla_ospf(hechos, config):
    # Verificar si existe el process_id y la lista de redes OSPF
    if hechos.get("ospf_process_id") and "ospf_networks" in hechos and hechos["ospf_networks"]:
        process_id = hechos["ospf_process_id"]
        config.append(f"router ospf {process_id}")
        
        # Iterar sobre cada red en la lista de redes OSPF
        for red_info in hechos["ospf_networks"]:
            network_ip = red_info.get("network")
            wildcard = red_info.get("wildcard")
            area = red_info.get("area")
            
            # Asegurarse de que todos los detalles de la red están presentes
            if network_ip and wildcard and area:
                config.append(f" network {network_ip} {wildcard} area {area}")
            else:
                # registrar un aviso si una red está incompleta
                print(f"[AVISO] Red OSPF incompleta para el proceso {process_id}: {red_info}. Omitiendo.")
                
        config.append(" exit")

def regla_nat(hechos, config):
    tipo_nat = hechos.get("tipo_nat")

    if hechos.get("nat_inside_interface") and hechos.get("nat_outside_interface"):
        # Marcar interfaces NAT
        config.append(f"interface {hechos['nat_inside_interface']}")
        config.append(" ip nat inside")
        config.append(" exit")

        config.append(f"interface {hechos['nat_outside_interface']}")
        config.append(" ip nat outside")
        config.append(" exit")

    if tipo_nat == "dinamico":
        if hechos.get("nat_acl_num") and hechos.get("nat_red_local") and hechos.get("nat_wildcard"):
            config.append(f"access-list {hechos['nat_acl_num']} permit {hechos['nat_red_local']} {hechos['nat_wildcard']}")
            config.append(f"ip nat inside source list {hechos['nat_acl_num']} interface {hechos['nat_outside_interface']} overload")

    elif tipo_nat == "estatico":
        if hechos.get("ip_privada") and hechos.get("ip_publica"):
            config.append(f"ip nat inside source static {hechos['ip_privada']} {hechos['ip_publica']}")
###

def regla_guardar(hechos, config):
    if "wr" in hechos:
        config.append("end")
        config.append("wr")

def aplicar_reglas(hechos):
    config = []
    reglas = [
        regla_hostname,
        regla_consola,
        regla_vty,
        regla_enable_secret,
        regla_encriptar_contrasenas,
        regla_banner_motd,
        regla_interfaces_router,
        regla_ip_switch,
        regla_ospf,
        regla_nat,
        regla_guardar #Esta regla se ejecuta al final
    ]

    for regla in reglas:
        regla(hechos, config)

    return config


def guardar_configuracion(config, nombre_archivo):
    with open(nombre_archivo, 'w') as f:
        f.write('enable\n')
        f.write('configure terminal\n')
        f.write("\n".join(config))
        f.write("\n")
    print(f" Configuración guardada en: {nombre_archivo}")
