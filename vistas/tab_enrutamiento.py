import flet as ft
from utils import crear_boton_ayuda

def obtener_tab_enrutamiento(page, refs, on_add_ospf, on_discover_ospf, on_toggle_nat):
    return ft.Tab(
        text="Enrutamiento",
        icon=ft.Icons.ROUTER,
        content=ft.Container(
            content=ft.Column([
                # Sección OSPF
                ft.Container(
                    padding=15, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=10,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SHARE, color=ft.Colors.ORANGE_700),
                            ft.Text("OSPF", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
                            crear_boton_ayuda(page, "OSPF", "Protocolo dinámico.\nWildcard = Inversa de máscara.\nArea 0 = Backbone", "Ayuda")
                        ]),
                        ft.TextField(ref=refs['ospf_process_id'], label="ID Proceso", hint_text="1", width=100, border_radius=8),
                        ft.Row([
                            ft.ElevatedButton("Añadir Red", icon=ft.Icons.ADD, on_click=on_add_ospf),
                            ft.ElevatedButton("Auto-Descubrir", icon=ft.Icons.AUTO_MODE, on_click=on_discover_ospf, bgcolor=ft.Colors.AMBER_700, color="white"),
                            ft.TextField(ref=refs['ospf_default_area'], label="Área Default", value="0", width=100, border_radius=8)
                        ]),
                        ft.Column(ref=refs['ospf_networks_col']),
                    ])
                ),
                
                ft.Divider(height=30),
                
                # Sección NAT
                ft.Container(
                    padding=15, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=10,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PUBLIC, color=ft.Colors.GREEN_700),
                            ft.Text("NAT", style=ft.TextThemeStyle.TITLE_LARGE, weight=ft.FontWeight.BOLD),
                            crear_boton_ayuda(page, "NAT", "Salida a Internet.\nDinámico requiere ACL.\nEstático es 1 a 1.", "Ayuda")
                        ]),
                        ft.RadioGroup(
                            ref=refs['nat_type'],
                            value="dinamico",
                            on_change=on_toggle_nat,
                            content=ft.Row([
                                ft.Radio(value="dinamico", label="Dinámico"),
                                ft.Radio(value="estatico", label="Estático")
                            ])
                        ),
                        # NAT Dinámico
                        ft.Column(
                            ref=refs['nat_dynamic_controls'],
                            visible=True,
                            controls=[
                                ft.TextField(label="Int. Interna", hint_text="g0/0", border_radius=8),
                                ft.TextField(label="Int. Externa", hint_text="g0/1", border_radius=8),
                                ft.TextField(label="ACL ID", hint_text="1", width=100, border_radius=8),
                                ft.TextField(label="Red Interna", hint_text="192.168.1.0", border_radius=8),
                                ft.TextField(label="Wildcard", hint_text="0.0.0.255", border_radius=8)
                            ]
                        ),
                        # NAT Estático
                        ft.Column(
                            ref=refs['nat_static_controls'],
                            visible=False,
                            controls=[
                                ft.TextField(label="Int. Interna", hint_text="g0/0", border_radius=8),
                                ft.TextField(label="Int. Externa", hint_text="g0/1", border_radius=8),
                                ft.TextField(label="IP Privada", hint_text="192.168.1.10", border_radius=8),
                                ft.TextField(label="IP Pública", hint_text="200.1.1.10", border_radius=8)
                            ]
                        )
                    ])
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=30
        )
    )