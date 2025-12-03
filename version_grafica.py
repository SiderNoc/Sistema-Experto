# gui.py (Versión con nombre de archivo personalizado)
import flet as ft
from sistema_experto import aplicar_reglas, guardar_configuracion
import ipaddress

def cidr_to_mask(cidr_str):
    try:
        cidr = int(cidr_str)
        if not 0 <= cidr <= 32: return ""
        mask_int = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
        octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF, (mask_int >> 8) & 0xFF, mask_int & 0xFF]
        return ".".join(map(str, octets))
    except (ValueError, TypeError): return ""

def ip_and_cidr_to_network_wildcard(ip_str, cidr_str):
    """Calcula la red y la wildcard a partir de una IP y un CIDR."""
    try:
        interface = ipaddress.IPv4Interface(f"{ip_str}/{cidr_str}")
        network = interface.network
        network_address = str(network.network_address)
        wildcard_mask = str(network.hostmask)
        return network_address, wildcard_mask
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return None, None

def main(page: ft.Page):
    """
    Función principal que construye y gestiona la interfaz gráfica con Flet. 
    """
    page.title = "Generador de Configuración de Red"
    page.window_width = 800
    page.window_height = 750 # Aumenté un poco la altura para el nuevo campo

    # --- REFERENCIAS A CONTROLES ---
    device_type = ft.Ref[ft.RadioGroup]()
    hostname = ft.Ref[ft.TextField]()
    banner_motd = ft.Ref[ft.TextField]()
    console_pw = ft.Ref[ft.TextField]()
    vty_pw = ft.Ref[ft.TextField]()
    enable_secret = ft.Ref[ft.TextField]()
    encrypt_passwords = ft.Ref[ft.Checkbox]()
    password_controls = ft.Ref[ft.Column]()
    router_interfaces_col = ft.Ref[ft.Column]()
    switch_interfaces_col = ft.Ref[ft.Column]()
    router_interface_panel = ft.Ref[ft.Column]()
    switch_interface_panel = ft.Ref[ft.Column]()
    ospf_process_id = ft.Ref[ft.TextField]()
    ospf_networks_col = ft.Ref[ft.Column]()
    ospf_default_area = ft.Ref[ft.TextField]()
    nat_type = ft.Ref[ft.RadioGroup]()
    nat_dynamic_controls = ft.Ref[ft.Column]()
    nat_static_controls = ft.Ref[ft.Column]()
    save_config_check = ft.Ref[ft.Checkbox]()
    output_textfield = ft.Ref[ft.TextField]()
    
    # --- NUEVA REFERENCIA ---
    filename_input = ft.Ref[ft.TextField]() 

    # --- LÓGICA DE LA INTERFAZ ---
    def toggle_password_fields(e):
        password_controls.current.visible = e.control.value
        page.update()

    def toggle_device_panels(e):
        is_router = device_type.current.value == "router"
        router_interface_panel.current.visible = is_router
        switch_interface_panel.current.visible = not is_router
        tabs.tabs[2].disabled = not is_router
        page.update()

    def add_interface(e, type):
        def remove_row(e):
            target_column = router_interfaces_col.current if type == "router" else switch_interfaces_col.current
            target_column.controls.remove(e.control.data)
            page.update()
        
        interface_row_controls = [ft.IconButton(icon=ft.icons.DELETE_FOREVER, icon_color="red", on_click=remove_row, tooltip="Eliminar Interfaz")]
        if type == "router":
            interface_row_controls.extend([
                ft.TextField(label="Interfaz", hint_text="GigabitEthernet0/0", width=160),
                ft.TextField(label="Descripción", expand=True),
                ft.TextField(label="IP IPv4", width=140),
                ft.TextField(label="Prefijo CIDR", hint_text="24", width=100),
                ft.TextField(label="IP IPv6", width=200),
                ft.TextField(label="Prefijo", hint_text="/64", width=80)])
        else: # switch
            interface_row_controls.extend([
                ft.TextField(label="Interfaz", hint_text="VLAN1", width=160),
                ft.TextField(label="Descripción", expand=True),
                ft.TextField(label="Dirección IP", width=160),
                ft.TextField(label="Prefijo CIDR", hint_text="24", width=110),])
        new_row = ft.Row(controls=interface_row_controls)
        new_row.controls[0].data = new_row
        target_col = router_interfaces_col.current if type == "router" else switch_interfaces_col.current
        target_col.controls.append(new_row)
        page.update()

    def add_ospf_network(e, network_val="", wildcard_val="", area_val=""):
        def remove_row(e):
            ospf_networks_col.current.controls.remove(e.control.data)
            page.update()

        new_row = ft.Row(
            controls=[
                ft.TextField(label="Red", value=network_val, hint_text="192.168.1.0", expand=True),
                ft.TextField(label="Wildcard", value=wildcard_val, hint_text="0.0.0.255", expand=True),
                ft.TextField(label="Área", value=area_val, hint_text="0", width=100),
                ft.IconButton(icon=ft.icons.DELETE, on_click=remove_row, tooltip="Eliminar Red")]) 
        new_row.controls[3].data = new_row
        ospf_networks_col.current.controls.append(new_row) 
        page.update()

    def discover_ospf_networks(e):
        default_area = ospf_default_area.current.value or "0" 
        for row in router_interfaces_col.current.controls:
            ip_val = row.controls[3].value
            cidr_val = row.controls[4].value
            if ip_val and cidr_val:
                network, wildcard = ip_and_cidr_to_network_wildcard(ip_val, cidr_val)
                if network and wildcard:
                    add_ospf_network(None, network_val=network, wildcard_val=wildcard, area_val=default_area)
        page.snack_bar = ft.SnackBar(content=ft.Text("Redes OSPF descubiertas y añadidas."), open=True)
        page.update()

    def toggle_nat_panels(e):
        is_dynamic = nat_type.current.value == "dinamico"
        nat_dynamic_controls.current.visible = is_dynamic
        nat_static_controls.current.visible = not is_dynamic
        page.update()
        
    def generate_config(e):
        hechos = {}
        hechos["tipo"] = device_type.current.value
        if hostname.current.value: hechos["hostname"] = hostname.current.value
        if banner_motd.current.value: hechos["banner_motd"] = banner_motd.current.value
        if console_pw.current.value: hechos["console_pw"] = console_pw.current.value
        if vty_pw.current.value: hechos["vty_pw"] = vty_pw.current.value
        if enable_secret.current.value: hechos["enable_secret"] = enable_secret.current.value
        if any([console_pw.current.value, vty_pw.current.value, enable_secret.current.value]):
            hechos["encriptar_contrasenas"] = encrypt_passwords.current.value
        
        if hechos["tipo"] == "router":
            interfaces = []
            for row in router_interfaces_col.current.controls:
                cidr_val = row.controls[4].value
                mascara_val = cidr_to_mask(cidr_val)
                interfaz = {
                    "interface": row.controls[1].value,
                    "descripcion": row.controls[2].value,
                    "ip": row.controls[3].value,
                    "mascara": mascara_val,
                    "ipv6": row.controls[5].value,
                    "ipv6_prefix": row.controls[6].value}
                if interfaz["interface"]: interfaces.append(interfaz)
            if interfaces: hechos["interfaces_router"] = interfaces
        else: # switch
            interfaces = []
            for row in switch_interfaces_col.current.controls:
                cidr_val = row.controls[4].value
                mascara_val = cidr_to_mask(cidr_val)
                interfaz = {
                    "interface": row.controls[1].value,
                    "descripcion": row.controls[2].value,
                    "ip_switch": row.controls[3].value,
                    "mascara_switch": mascara_val}
                if interfaz["interface"]: interfaces.append(interfaz)
            if interfaces: hechos["interfaces_switch"] = interfaces

        # 3. Recopilar datos de Router (OSPF, NAT)
        if hechos["tipo"] == "router":
            # Recoger OSPF Process ID
            if ospf_process_id.current.value:
                hechos["ospf_process_id"] = ospf_process_id.current.value
            
            # Recoger redes OSPF (de forma independiente al Process ID)
            redes = []
            for row in ospf_networks_col.current.controls:
                red = {"network": row.controls[0].value, "wildcard": row.controls[1].value, "area": row.controls[2].value}
                if all(red.values()):
                    redes.append(red)
            if redes:
                hechos["ospf_networks"] = redes

            # Recoger NAT
            if nat_type.current.value:
                hechos["tipo_nat"] = nat_type.current.value
                panel = nat_dynamic_controls.current if nat_type.current.value == "dinamico" else nat_static_controls.current
                if nat_type.current.value == "dinamico":
                    hechos["nat_inside_interface"] = panel.controls[0].value
                    hechos["nat_outside_interface"] = panel.controls[1].value
                    hechos["nat_acl_num"] = panel.controls[2].value
                    hechos["nat_red_local"] = panel.controls[3].value
                    hechos["nat_wildcard"] = panel.controls[4].value
                else: #estatico
                    hechos["nat_inside_interface"] = panel.controls[0].value
                    hechos["nat_outside_interface"] = panel.controls[1].value
                    hechos["ip_privada"] = panel.controls[2].value
                    hechos["ip_publica"] = panel.controls[3].value

        if save_config_check.current.value:
            hechos["wr"] = ''
            
        config_list = aplicar_reglas(hechos)
        config_text = "enable\nconfigure terminal\n" + "\n".join(config_list)
        output_textfield.current.value = config_text
        
        # --- LÓGICA MODIFICADA PARA EL NOMBRE DEL ARCHIVO ---
        user_filename = filename_input.current.value
        if user_filename:
            user_filename = user_filename.strip() # Quitar espacios
            if not user_filename.endswith(".txt"):
                filename = f"{user_filename}.txt"
            else:
                filename = user_filename
        else:
            # Nombre por defecto si está vacío
            filename = f"{hechos['tipo']}_config.txt"
        
        guardar_configuracion(config_list, filename)

        page.snack_bar = ft.SnackBar(content=ft.Text(f"¡Configuración generada y guardada en {filename}!"), open=True)
        page.update()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="1. General",
                icon=ft.icons.TUNE,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Paso 1: Elige el tipo de dispositivo y las configuraciones básicas.", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.RadioGroup(
                            ref=device_type,
                            content=ft.Row([
                                ft.Radio(value="router", label="Router"),
                                ft.Radio(value="switch", label="Switch"),
                            ]),
                            value="router",
                            on_change=toggle_device_panels,
                        ),
                        ft.TextField(ref=hostname, label="Hostname", hint_text="Ej: R1-Oficina"),
                        ft.TextField(ref=banner_motd, label="Banner MOTD", hint_text="Acceso no autorizado prohibido"),
                        ft.Checkbox(label="Configurar contraseñas", on_change=toggle_password_fields),
                        ft.Column(
                            ref=password_controls,
                            visible=False,
                            controls=[
                                ft.TextField(ref=console_pw, label="Contraseña de Consola", password=True, can_reveal_password=True),
                                ft.TextField(ref=vty_pw, label="Contraseña VTY (telnet/ssh)", password=True, can_reveal_password=True),
                                ft.TextField(ref=enable_secret, label="Enable Secret", password=True, can_reveal_password=True),
                                ft.Checkbox(ref=encrypt_passwords, label="Encriptar todas las contraseñas (service password-encryption)", value=True),
                            ]
                        )
                    ]),
                    padding=20,
                )
            ),
            ft.Tab(
                text="Interfaces",
                icon=ft.icons.ROUTER_OUTLINED,
                content=ft.Container(
                    content=ft.Column([
                        ft.Column(
                            ref=router_interface_panel,
                            visible=True,
                            controls=[
                                ft.Text("Configuración de Interfaces de Router", style=ft.TextThemeStyle.TITLE_MEDIUM),
                                ft.ElevatedButton("Añadir Interfaz de Router", icon=ft.icons.ADD, on_click=lambda e: add_interface(e, "router")),
                                ft.Column(ref=router_interfaces_col),
                            ]
                        ),
                        ft.Column(
                            ref=switch_interface_panel,
                            visible=False,
                            controls=[
                                ft.Text("Configuración de Interfaces de Switch", style=ft.TextThemeStyle.TITLE_MEDIUM),
                                ft.ElevatedButton("Añadir Interfaz de Switch", icon=ft.icons.ADD, on_click=lambda e: add_interface(e, "switch")),
                                ft.Column(ref=switch_interfaces_col),
                            ]
                        )
                    ]),
                    padding=20
                )
            ),
            ft.Tab(
                text="3. Configuración de Router",
                icon=ft.icons.HUB_OUTLINED,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("OSPF", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.TextField(ref=ospf_process_id, label="ID del Proceso OSPF", hint_text="Ej: 1", width=200),
                        ft.Row([
                            ft.ElevatedButton("Añadir Red Manualmente", icon=ft.icons.ADD, on_click=add_ospf_network),
                            ft.ElevatedButton("Descubrir Interfaces", icon=ft.icons.ADD_LINK, on_click=discover_ospf_networks, tooltip="Añadir redes desde la pestaña de interfaces"),
                            ft.TextField(ref=ospf_default_area, label="Área por defecto", value="0", width=120)
                        ]),
                        ft.Column(ref=ospf_networks_col),
                        ft.Divider(),

                        ft.Divider(),
                        ft.Text("NAT", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.RadioGroup(
                            ref=nat_type,

                            value="dinamico",
                            on_change=toggle_nat_panels,
                            content=ft.Row([
                                ft.Radio(value="dinamico", label="Dinámico"),
                                ft.Radio(value="estatico", label="Estático"),
                            ])
                        ),

                        ft.Column(
                            ref=nat_dynamic_controls,
                            visible=True,  # Inicia visible porque el valor por defecto es "dinamico"
                            controls=[
                                ft.TextField(label="Interfaz Interna", hint_text="GigabitEthernet0/0"),
                                ft.TextField(label="Interfaz Externa", hint_text="GigabitEthernet0/1"),
                                ft.TextField(label="Número de ACL", hint_text="1", width=150),
                                ft.TextField(label="Red Interna", hint_text="192.168.1.0"),
                                ft.TextField(label="Wildcard", hint_text="0.0.0.255"),
                            ]
                        ),

                        ft.Column(
                            ref=nat_static_controls,
                            visible=False, # Inicia oculto
                            controls=[
                                ft.TextField(label="Interfaz Interna", hint_text="GigabitEthernet0/0"),
                                ft.TextField(label="Interfaz Externa", hint_text="GigabitEthernet0/1"),
                                ft.TextField(label="IP Privada Interna", hint_text="192.168.1.10"),
                                ft.TextField(label="IP Pública Global", hint_text="200.1.1.10"),
                            ]
                        )
                    ]),
                    padding=20
                )
            ),
            ft.Tab(
                text="Generar",
                icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE_OUTLINED,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Paso Final: Genera y guarda tu configuración.", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        
                        # --- NUEVO CAMPO DE TEXTO ---
                        ft.TextField(
                            ref=filename_input, 
                            label="Nombre del archivo (Opcional)", 
                            hint_text="Ej: router_principal", 
                            suffix_text=".txt"
                        ),
                        # ----------------------------

                        ft.Checkbox(ref=save_config_check, label="Guardar configuración en el dispositivo (wr)", value=True),
                        ft.ElevatedButton(
                            text="Generar Archivo de Configuración",
                            icon=ft.icons.SAVE, 
                            on_click=generate_config, 
                            bgcolor=ft.colors.BLUE_700, 
                            color=ft.colors.WHITE 
                        ),
                        ft.TextField(ref=output_textfield, multiline=True, read_only=True, label="Resultado de la Configuración", expand=True)
                    ], expand=True, spacing=15),
                    padding=20
                )
            )
        ],
        expand=1,
    )

    page.add(tabs)
    toggle_device_panels(None)

if __name__ == "__main__":
    ft.app(target=main)