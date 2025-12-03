import flet as ft
from motor_reglas import aplicar_reglas, guardar_configuracion
from utils import cidr_to_mask, ip_and_cidr_to_network_wildcard

# Importar las Vistas Modulares
from vistas.tab_general import obtener_tab_general
from vistas.tab_interfaces import obtener_tab_interfaces
from vistas.tab_enrutamiento import obtener_tab_enrutamiento
from vistas.tab_consejos import obtener_tab_consejos
from vistas.tab_generar import obtener_tab_generar

def main(page: ft.Page): 
    # CONFIGURACIÓN
    page.title = "SERCI - Sistema Experto en Redes Cisco"
    page.window_width = 950
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.padding = 20

    # REFERENCIAS (Estado Global)
    refs = {
        'device_type': ft.Ref[ft.RadioGroup](),
        'hostname': ft.Ref[ft.TextField](),
        'banner_motd': ft.Ref[ft.TextField](),
        'console_pw': ft.Ref[ft.TextField](),
        'vty_pw': ft.Ref[ft.TextField](),
        'enable_secret': ft.Ref[ft.TextField](),
        'encrypt_passwords': ft.Ref[ft.Checkbox](),
        'password_controls': ft.Ref[ft.Column](),
        'router_interfaces_col': ft.Ref[ft.Column](),
        'switch_interfaces_col': ft.Ref[ft.Column](),
        'router_interface_panel': ft.Ref[ft.Column](),
        'switch_interface_panel': ft.Ref[ft.Column](),
        'ospf_process_id': ft.Ref[ft.TextField](),
        'ospf_networks_col': ft.Ref[ft.Column](),
        'ospf_default_area': ft.Ref[ft.TextField](),
        'nat_type': ft.Ref[ft.RadioGroup](),
        'nat_dynamic_controls': ft.Ref[ft.Column](),
        'nat_static_controls': ft.Ref[ft.Column](),
        'save_config_check': ft.Ref[ft.Checkbox](),
        'output_textfield': ft.Ref[ft.TextField](),
        'filename_input': ft.Ref[ft.TextField]()
    }

    # CONTROLADORES DE EVENTOS
    
    def on_password_change(e):
        refs['password_controls'].current.visible = e.control.value
        page.update()

    def on_device_change(e):
        is_router = refs['device_type'].current.value == "router"
        refs['router_interface_panel'].current.visible = is_router
        refs['switch_interface_panel'].current.visible = not is_router
        # Accedemos a las pestañas por índice. Si cambia el orden, ajustar aquí.
        if len(tabs.tabs) > 2:
            tabs.tabs[2].disabled = not is_router
        page.update()

    def on_add_interface(e, type):
        def remove_row(e):
            target_column = refs['router_interfaces_col'].current if type == "router" else refs['switch_interfaces_col'].current
            target_column.controls.remove(e.control.data)
            page.update()
        
        interface_row_controls = [ft.IconButton(icon=ft.Icons.DELETE_FOREVER, icon_color="red", on_click=remove_row, tooltip="Eliminar")]
        
        if type == "router":
            interface_row_controls.extend([
                ft.TextField(label="Interfaz", hint_text="g0/0", width=120, border_radius=8, text_size=12),
                ft.TextField(label="Descripción", expand=True, border_radius=8, text_size=12),
                ft.TextField(label="IPv4", width=130, border_radius=8, text_size=12),
                ft.TextField(label="CIDR", hint_text="24", width=70, border_radius=8, text_size=12),
                ft.TextField(label="IPv6", width=180, border_radius=8, text_size=12),
                ft.TextField(label="/Prefix", hint_text="/64", width=80, border_radius=8, text_size=12)])
        else: 
            interface_row_controls.extend([
                ft.TextField(label="VLAN ID", hint_text="VLAN1", width=120, border_radius=8),
                ft.TextField(label="Descripción", expand=True, border_radius=8),
                ft.TextField(label="IP Gestión", width=150, border_radius=8),
                ft.TextField(label="CIDR", hint_text="24", width=80, border_radius=8)])
        
        new_row = ft.Row(controls=interface_row_controls, alignment=ft.MainAxisAlignment.START, spacing=5)
        new_row.controls[0].data = new_row
        target_col = refs['router_interfaces_col'].current if type == "router" else refs['switch_interfaces_col'].current
        target_col.controls.append(new_row)
        page.update()

    def on_add_ospf_network(e, network_val="", wildcard_val="", area_val=""):
        def remove_row(e):
            refs['ospf_networks_col'].current.controls.remove(e.control.data)
            page.update()

        new_row = ft.Row(controls=[
            ft.TextField(label="Red", value=network_val, hint_text="192.168.1.0", expand=True, border_radius=8),
            ft.TextField(label="Wildcard", value=wildcard_val, hint_text="0.0.0.255", expand=True, border_radius=8),
            ft.TextField(label="Área", value=area_val, hint_text="0", width=100, border_radius=8),
            ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=remove_row)
        ])
        new_row.controls[3].data = new_row
        refs['ospf_networks_col'].current.controls.append(new_row) 
        page.update()

    def on_discover_ospf_networks(e):
        default_area = refs['ospf_default_area'].current.value or "0" 
        for row in refs['router_interfaces_col'].current.controls:
            ip_val = row.controls[3].value
            cidr_val = row.controls[4].value
            if ip_val and cidr_val:
                network, wildcard = ip_and_cidr_to_network_wildcard(ip_val, cidr_val)
                if network and wildcard:
                    on_add_ospf_network(None, network_val=network, wildcard_val=wildcard, area_val=default_area)
        page.snack_bar = ft.SnackBar(content=ft.Text("Redes OSPF descubiertas y añadidas."), open=True)
        page.update()

    def on_toggle_nat(e):
        is_dynamic = refs['nat_type'].current.value == "dinamico"
        refs['nat_dynamic_controls'].current.visible = is_dynamic
        refs['nat_static_controls'].current.visible = not is_dynamic
        page.update()

    def on_generate_config(e):
        # Recolección de Hechos
        hechos = {}
        hechos["tipo"] = refs['device_type'].current.value
        if refs['hostname'].current.value: hechos["hostname"] = refs['hostname'].current.value
        if refs['banner_motd'].current.value: hechos["banner_motd"] = refs['banner_motd'].current.value
        if refs['console_pw'].current.value: hechos["console_pw"] = refs['console_pw'].current.value
        if refs['vty_pw'].current.value: hechos["vty_pw"] = refs['vty_pw'].current.value
        if refs['enable_secret'].current.value: hechos["enable_secret"] = refs['enable_secret'].current.value
        
        if any([refs['console_pw'].current.value, refs['vty_pw'].current.value, refs['enable_secret'].current.value]):
            hechos["encriptar_contrasenas"] = refs['encrypt_passwords'].current.value
        
        # Interfaces
        if hechos["tipo"] == "router":
            interfaces = []
            for row in refs['router_interfaces_col'].current.controls:
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
            for row in refs['switch_interfaces_col'].current.controls:
                cidr_val = row.controls[4].value
                mascara_val = cidr_to_mask(cidr_val)
                interfaz = {
                    "interface": row.controls[1].value,
                    "descripcion": row.controls[2].value,
                    "ip_switch": row.controls[3].value,
                    "mascara_switch": mascara_val}
                if interfaz["interface"]: interfaces.append(interfaz)
            if interfaces: hechos["interfaces_switch"] = interfaces

        # OSPF y NAT
        if hechos["tipo"] == "router":
            if refs['ospf_process_id'].current.value:
                hechos["ospf_process_id"] = refs['ospf_process_id'].current.value
            redes = []
            for row in refs['ospf_networks_col'].current.controls:
                red = {"network": row.controls[0].value, "wildcard": row.controls[1].value, "area": row.controls[2].value}
                if all(red.values()): redes.append(red)
            if redes: hechos["ospf_networks"] = redes

            if refs['nat_type'].current.value:
                hechos["tipo_nat"] = refs['nat_type'].current.value
                panel = refs['nat_dynamic_controls'].current if hechos["tipo_nat"] == "dinamico" else refs['nat_static_controls'].current
                if hechos["tipo_nat"] == "dinamico":
                    hechos["nat_inside_interface"] = panel.controls[0].value
                    hechos["nat_outside_interface"] = panel.controls[1].value
                    hechos["nat_acl_num"] = panel.controls[2].value
                    hechos["nat_red_local"] = panel.controls[3].value
                    hechos["nat_wildcard"] = panel.controls[4].value
                else: 
                    hechos["nat_inside_interface"] = panel.controls[0].value
                    hechos["nat_outside_interface"] = panel.controls[1].value
                    hechos["ip_privada"] = panel.controls[2].value
                    hechos["ip_publica"] = panel.controls[3].value

        if refs['save_config_check'].current.value:
            hechos["wr"] = ''
            
        config_list = aplicar_reglas(hechos)
        config_text = "enable\nconfigure terminal\n" + "\n".join(config_list)
        refs['output_textfield'].current.value = config_text
        refs['output_textfield'].current.update()
        
        user_filename = refs['filename_input'].current.value
        filename = f"{user_filename.strip()}.txt" if user_filename else f"{hechos['tipo']}_config.txt"
        
        guardar_configuracion(config_list, filename)
        page.snack_bar = ft.SnackBar(content=ft.Text(f"¡Guardado en {filename}!"), open=True)
        page.update()

    # CONSTRUCCIÓN DE LA APP
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            obtener_tab_general(page, refs, on_device_change, on_password_change),
            obtener_tab_interfaces(page, refs, on_add_interface),
            obtener_tab_enrutamiento(page, refs, on_add_ospf_network, on_discover_ospf_networks, on_toggle_nat),
            obtener_tab_generar(refs, on_generate_config),
            obtener_tab_consejos()
        ],
        expand=1,
    )

    page.add(tabs)
    on_device_change(None) # Inicializar estado visual

if __name__ == "__main__":
    ft.app(target=main)