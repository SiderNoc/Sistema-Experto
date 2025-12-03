import flet as ft
from utils import crear_boton_ayuda

def obtener_tab_interfaces(page, refs, on_add_interface):
    return ft.Tab(
        text="Interfaces",
        icon=ft.Icons.CABLE,
        content=ft.Container(
            content=ft.Column([
                # Panel Router
                ft.Column(
                    ref=refs['router_interface_panel'],
                    visible=True,
                    controls=[
                        ft.Row([
                            ft.Text("Interfaces de Router", style=ft.TextThemeStyle.HEADLINE_SMALL),
                            crear_boton_ayuda(page, "Interfaces", "Configura IPs y Máscaras.\nCIDR /24 = 255.255.255.0", "Ayuda")
                        ]),
                        ft.ElevatedButton(
                            "Añadir Interfaz", 
                            icon=ft.Icons.ADD, 
                            on_click=lambda e: on_add_interface(e, "router"), 
                            bgcolor=ft.Colors.TEAL_600, 
                            color="white"
                        ),
                        ft.Column(ref=refs['router_interfaces_col'], spacing=10),
                    ]
                ),
                # Panel Switch
                ft.Column(
                    ref=refs['switch_interface_panel'],
                    visible=False,
                    controls=[
                        ft.Text("Interfaces Switch (SVI)", style=ft.TextThemeStyle.HEADLINE_SMALL),
                        ft.ElevatedButton(
                            "Añadir VLAN", 
                            icon=ft.Icons.ADD, 
                            on_click=lambda e: on_add_interface(e, "switch"), 
                            bgcolor=ft.Colors.TEAL_600, 
                            color="white"
                        ),
                        ft.Column(ref=refs['switch_interfaces_col'], spacing=10),
                    ]
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=30
        )
    )