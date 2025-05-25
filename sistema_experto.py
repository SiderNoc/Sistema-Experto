#REGLAS DEL SISTEMA EXPERTPO

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

def regla_banner_motd(hechos, config):
    if hechos.get("banner_motd"):
        print("[DEBUG] Ejecutando regla_banner_motd")
        config.append(f"banner motd #{hechos['banner_motd']}#")

def regla_ip_router(hechos, config):
    if hechos.get("ip_router") and hechos.get("mascara_router"):
        config.append(f"interface {hechos['interface']}")
        config.append(f" ip address {hechos['ip_router']} {hechos['mascara_router']}")
        config.append(" no shutdown")
        config.append(" exit")

def regla_ip_switch(hechos, config):
    if hechos.get("ip_switch") and hechos.get("mascara_switch"):
        config.append(f"interface {hechos['interface']}")
        config.append(f" ip address {hechos['ip_switch']} {hechos['mascara_switch']}")
        config.append(" no shutdown")
        config.append(" exit")

def regla_guardar(hechos, config):
    if "wr" in hechos:
        config.append("end")
        config.append("wr")

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


def aplicar_reglas(hechos):
    config = []
    reglas = [
        regla_hostname,
        regla_consola,
        regla_vty,
        regla_enable_secret,
        regla_banner_motd,
        regla_ip_router,
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
