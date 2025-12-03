# gui.py (Versión Estilizada y Corregida)
import flet as ft
from motor_reglas import aplicar_reglas, guardar_configuracion
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
    # Calcula la red y la wildcard a partir de una IP y un CIDR.
    try:
        interface = ipaddress.IPv4Interface(f"{ip_str}/{cidr_str}")
        network = interface.network
        network_address = str(network.network_address)
        wildcard_mask = str(network.hostmask)
        return network_address, wildcard_mask
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return None, None

def main(page: ft.Page): 
    
    # CONFIGURACIÓN DE TEMA Y PÁGINA
    page.title = "Generador de Configuración de Red"
    page.window_width = 900
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.padding = 20

    # --- FUNCIÓN DE AYUDA ESTILIZADA ---
    def mostrar_ayuda(e, titulo, mensaje):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_700, size=30),
                ft.Text(titulo, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900)
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            content=ft.Container(
                content=ft.Text(mensaje, size=15, color=ft.Colors.GREY_800),
                padding=10,
                width=400,
            ),
            actions=[
                ft.ElevatedButton(
                    "Entendido", 
                    on_click=lambda e: page.close(dlg),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    elevation=2
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        page.open(dlg)

    # --- HELPER PARA BOTONES DE AYUDA ---
    def crear_boton_ayuda(titulo, mensaje, tooltip_corto):
        return ft.IconButton(
            icon=ft.Icons.HELP, 
            icon_color=ft.Colors.INDIGO_500, 
            icon_size=24,
            tooltip=tooltip_corto,
            on_click=lambda e: mostrar_ayuda(e, titulo, mensaje)
        )

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
        
        interface_row_controls = [ft.IconButton(icon=ft.Icons.DELETE_FOREVER, icon_color="red", on_click=remove_row, tooltip="Eliminar Interfaz")]
        
        if type == "router":
            interface_row_controls.extend([
                ft.TextField(label="Interfaz", hint_text="GigabitEthernet0/0", width=160, border_radius=8, tooltip="Nombre físico de la interfaz"),
                ft.TextField(label="Descripción", expand=True, border_radius=8),
                ft.TextField(label="IP IPv4", width=140, border_radius=8, tooltip="Ej: 192.168.1.1"),
                ft.TextField(label="Prefijo", hint_text="24", width=80, border_radius=8, tooltip="CIDR (Ej: 24)"),
                ft.TextField(label="IP IPv6", width=200, border_radius=8, tooltip="Ej: 2001:db8::1"),
                ft.TextField(label="Prefijo v6", hint_text="/64", width=100, border_radius=8)])
        else: # switch
            interface_row_controls.extend([
                ft.TextField(label="Interfaz", hint_text="VLAN1", width=160, border_radius=8, tooltip="Interfaz virtual del Switch (SVI)"),
                ft.TextField(label="Descripción", expand=True, border_radius=8),
                ft.TextField(label="Dirección IP", width=160, border_radius=8, tooltip="IP de gestión para el Switch"),
                ft.TextField(label="Prefijo", hint_text="24", width=110, border_radius=8),])
        
        new_row = ft.Row(controls=interface_row_controls, alignment=ft.MainAxisAlignment.START)
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
                ft.TextField(label="Red", value=network_val, hint_text="192.168.1.0", expand=True, border_radius=8),
                ft.TextField(label="Wildcard", value=wildcard_val, hint_text="0.0.0.255", expand=True, border_radius=8, tooltip="Máscara inversa"),
                ft.TextField(label="Área", value=area_val, hint_text="0", width=100, border_radius=8, tooltip="Area OSPF"),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=remove_row, tooltip="Eliminar Red")
            ]
        ) 
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

        if hechos["tipo"] == "router":
            if ospf_process_id.current.value:
                hechos["ospf_process_id"] = ospf_process_id.current.value
            
            redes = []
            for row in ospf_networks_col.current.controls:
                red = {"network": row.controls[0].value, "wildcard": row.controls[1].value, "area": row.controls[2].value}
                if all(red.values()):
                    redes.append(red)
            if redes:
                hechos["ospf_networks"] = redes

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
        
        user_filename = filename_input.current.value
        if user_filename:
            user_filename = user_filename.strip() 
            if not user_filename.endswith(".txt"):
                filename = f"{user_filename}.txt"
            else:
                filename = user_filename
        else:
            filename = f"{hechos['tipo']}_config.txt"
        
        guardar_configuracion(config_list, filename)

        page.snack_bar = ft.SnackBar(content=ft.Text(f"¡Configuración generada y guardada en {filename}!"), open=True)
        page.update()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=ft.Colors.BLUE_700,
        label_color=ft.Colors.BLUE_900,
        unselected_label_color=ft.Colors.GREY_500,
        tabs=[
            ft.Tab(
                text="1. General",
                icon=ft.Icons.SETTINGS,
                content=ft.Container(
                    content=ft.Column([
                        # HEADER ESTILIZADO
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.TUNE, color=ft.Colors.BLUE_700),
                                ft.Text("Configuración Básica", style=ft.TextThemeStyle.HEADLINE_SMALL, color=ft.Colors.BLUE_GREY_800),
                                crear_boton_ayuda("Configuración Básica", 
                                    "Define la identidad y seguridad del dispositivo:\n\n"
                                    "• Hostname: Nombre en la consola (ej. Router1).\n"
                                    "• VTY: Contraseña para acceso remoto (SSH/Telnet).\n"
                                    "• Enable Secret: Contraseña encriptada privilegiada.", 
                                    "Ayuda General")
                            ]),
                            margin=ft.margin.only(bottom=15)
                        ),
                        
                        ft.RadioGroup(
                            ref=device_type,
                            content=ft.Row([
                                ft.Radio(value="router", label="Router"),
                                ft.Radio(value="switch", label="Switch"),
                            ]),
                            value="router",
                            on_change=toggle_device_panels,
                        ),
                        ft.TextField(ref=hostname, label="Hostname", hint_text="Ej: R1-Oficina", border_radius=8, prefix_icon=ft.Icons.COMPUTER),
                        ft.TextField(ref=banner_motd, label="Banner MOTD", hint_text="Acceso prohibido", border_radius=8, prefix_icon=ft.Icons.WARNING_AMBER),
                        
                        ft.Container(height=10), 

                        ft.Checkbox(label="Configurar contraseñas", on_change=toggle_password_fields),
                        ft.Container(
                            ref=password_controls,
                            visible=False,
                            bgcolor=ft.Colors.BLUE_50, 
                            padding=15,
                            border_radius=10,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Seguridad", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                                    ft.TextField(ref=console_pw, label="Contraseña Consola", password=True, can_reveal_password=True, border_radius=8, prefix_icon=ft.Icons.USB),
                                    ft.TextField(ref=vty_pw, label="Contraseña VTY", password=True, can_reveal_password=True, border_radius=8, prefix_icon=ft.Icons.WIFI_LOCK),
                                    ft.TextField(ref=enable_secret, label="Enable Secret", password=True, can_reveal_password=True, border_radius=8, prefix_icon=ft.Icons.SECURITY),
                                    ft.Checkbox(ref=encrypt_passwords, label="Encriptar todas (Service Password-Encryption)", value=True),
                                ]
                            )
                        )
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=30,
                )
            ),
            ft.Tab(
                text="Interfaces",
                icon=ft.Icons.CABLE,
                content=ft.Container(
                    content=ft.Column([
                        ft.Column(
                            ref=router_interface_panel,
                            visible=True,
                            controls=[
                                ft.Row([
                                    ft.Text("Interfaces de Router", style=ft.TextThemeStyle.HEADLINE_SMALL, color=ft.Colors.BLUE_GREY_800),
                                    crear_boton_ayuda("Interfaces Router", 
                                            "Configura las puertas de enlace.\n\n"
                                            "• CIDR: Notación abreviada de máscara (/24 = 255.255.255.0).\n"
                                            "• IPv6: Direcciones de nueva generación (Hexadecimal).",
                                            "Ayuda Interfaces")
                                ]),
                                ft.ElevatedButton("Añadir Interfaz", icon=ft.Icons.ADD, on_click=lambda e: add_interface(e, "router"), bgcolor=ft.Colors.TEAL_600, color="white"),
                                ft.Column(ref=router_interfaces_col, spacing=10),
                            ]
                        ),
                        ft.Column(
                            ref=switch_interface_panel,
                            visible=False,
                            controls=[
                                ft.Text("Interfaces de Switch (VLANs)", style=ft.TextThemeStyle.HEADLINE_SMALL),
                                ft.ElevatedButton("Añadir SVI / VLAN", icon=ft.Icons.ADD, on_click=lambda e: add_interface(e, "switch"), bgcolor=ft.Colors.TEAL_600, color="white"),
                                ft.Column(ref=switch_interfaces_col, spacing=10),
                            ]
                        )
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=30
                )
            ),
            ft.Tab(
                text="Enrutamiento y NAT",
                icon=ft.Icons.ROUTER,
                content=ft.Container(
                    content=ft.Column([
                        # SECCION OSPF
                        ft.Container(
                            padding=15,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.SHARE, color=ft.Colors.ORANGE_700),
                                    ft.Text("Protocolo OSPF", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
                                    crear_boton_ayuda("OSPF (Open Shortest Path First)", 
                                        "Protocolo de enrutamiento dinámico.\n\n"
                                        "• Process ID: Identificador local (1-65535).\n"
                                        "• Wildcard: Máscara invertida. (0 verifica, 255 ignora).\n"
                                        "• Área: Típicamente 0 para Backbone.",
                                        "Ayuda OSPF")
                                ]),
                                ft.TextField(ref=ospf_process_id, label="ID del Proceso", hint_text="Ej: 1", width=200, border_radius=8),
                                ft.Row([
                                    ft.ElevatedButton("Añadir Red", icon=ft.Icons.ADD, on_click=add_ospf_network),
                                    ft.ElevatedButton("Auto-Descubrir", icon=ft.Icons.AUTO_MODE, on_click=discover_ospf_networks, bgcolor=ft.Colors.AMBER_700, color="white", tooltip="Calcula redes desde tus interfaces"),
                                    ft.TextField(ref=ospf_default_area, label="Área Default", value="0", width=120, border_radius=8)
                                ]),
                                ft.Column(ref=ospf_networks_col),
                            ])
                        ),

                        ft.Divider(height=30, thickness=2),

                        # SECCION NAT
                        ft.Container(
                            padding=15,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.PUBLIC, color=ft.Colors.GREEN_700),
                                    ft.Text("NAT (Traducción de Direcciones)", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
                                    crear_boton_ayuda("Ayuda NAT", 
                                        "Permite la salida a Internet:\n\n"
                                        "• Dinámico (PAT): Múltiples equipos salen por una IP pública (Requiere ACL).\n"
                                        "• Estático: Mapeo 1 a 1 (Ej: Servidores Web).", 
                                        "Ayuda NAT")
                                ]),
                                ft.RadioGroup(
                                    ref=nat_type,
                                    value="dinamico",
                                    on_change=toggle_nat_panels,
                                    content=ft.Row([
                                        ft.Radio(value="dinamico", label="Dinámico (PAT)"),
                                        ft.Radio(value="estatico", label="Estático"),
                                    ])
                                ),
                                ft.Column(
                                    ref=nat_dynamic_controls,
                                    visible=True,  
                                    controls=[
                                        ft.TextField(label="Interfaz Interna (LAN)", hint_text="g0/0", border_radius=8, prefix_icon=ft.Icons.LOGIN),
                                        ft.TextField(label="Interfaz Externa (WAN)", hint_text="g0/1", border_radius=8, prefix_icon=ft.Icons.LOGOUT),
                                        ft.TextField(label="ACL ID", hint_text="1", width=150, border_radius=8, helper_text="ACL Estándar (1-99)"),
                                        ft.TextField(label="Red Interna", hint_text="192.168.1.0", border_radius=8),
                                        ft.TextField(label="Wildcard", hint_text="0.0.0.255", border_radius=8),
                                    ]
                                ),
                                ft.Column(
                                    ref=nat_static_controls,
                                    visible=False, 
                                    controls=[
                                        ft.TextField(label="Interfaz Interna", hint_text="g0/0", border_radius=8),
                                        ft.TextField(label="Interfaz Externa", hint_text="g0/1", border_radius=8),
                                        ft.TextField(label="IP Privada", hint_text="192.168.1.10", border_radius=8),
                                        ft.TextField(label="IP Pública", hint_text="200.1.1.10", border_radius=8),
                                    ]
                                )
                            ])
                        )
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=30
                )
            ),
            ft.Tab(
                text="Generar",
                icon=ft.Icons.SAVE_ALT,
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Generar y Guardar", style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=ft.Colors.BLUE_GREY_900),
                        
                        ft.Container(
                            padding=20,
                            bgcolor=ft.Colors.BLUE_GREY_50,
                            border_radius=10,
                            content=ft.Column([
                                ft.TextField(
                                    ref=filename_input, 
                                    label="Nombre del archivo", 
                                    hint_text="ej: configuracion_final", 
                                    suffix_text=".txt",
                                    border_radius=8,
                                    prefix_icon=ft.Icons.FILE_PRESENT
                                ),
                                ft.Checkbox(ref=save_config_check, label="Agregar comando de guardado (write memory)", value=True),
                                ft.ElevatedButton(
                                    text="GENERAR SCRIPT",
                                    icon=ft.Icons.ROCKET_LAUNCH, 
                                    on_click=generate_config, 
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE_800,
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    width=300
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        ),
                        
                        ft.Container(
                            content=ft.Text("Vista Previa:", weight=ft.FontWeight.BOLD),
                            margin=ft.margin.only(top=20)
                        ),
                        
                        ft.TextField(
                            ref=output_textfield, 
                            multiline=True, 
                            read_only=True, 
                            text_style=ft.TextStyle(font_family="Consolas", size=14), # Fuente monoespaciada tipo terminal
                            border_color=ft.Colors.BLUE_GREY_200,
                            expand=True
                        )
                    ], expand=True),
                    padding=30
                )
            )
        ],
        expand=1,
    )

    page.add(tabs)
    toggle_device_panels(None)

if __name__ == "__main__":
    ft.app(target=main)