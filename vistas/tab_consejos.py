# vistas/tab_consejos.py
import flet as ft

def obtener_tab_consejos():
    return ft.Tab(
        text="Consejos",
        icon=ft.Icons.LIGHTBULB_OUTLINE,
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.PURPLE_700, size=30),
                        ft.Text("Guía Rápida y Conceptos", style=ft.TextThemeStyle.HEADLINE_SMALL, color=ft.Colors.BLUE_GREY_900),
                    ]), margin=ft.margin.only(bottom=20)
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("¿Cómo calcular la Wildcard?", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text("Esencial para OSPF y ACLs"),
                    leading=ft.Icon(ft.Icons.CALCULATE_OUTLINED, color=ft.Colors.INDIGO),
                    controls=[
                        ft.Container(padding=20, bgcolor=ft.Colors.GREY_50, border_radius=10, content=ft.Column([
                            ft.Text("La Wildcard es la 'inversa' de la máscara de subred."),
                            ft.Text("Fórmula: 255.255.255.255 - Máscara", style=ft.TextThemeStyle.BODY_LARGE, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_700),
                            ft.Divider(),
                            ft.Text("Ejemplo Práctico (/24):"),
                            ft.Text("   255.255.255.255", font_family="Consolas"),
                            ft.Text(" - 255.255.255.  0  (Máscara /24)", font_family="Consolas"),
                            ft.Text(" ------------------", font_family="Consolas"),
                            ft.Text("     0.  0.  0.255  (Wildcard)", font_family="Consolas", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ]))
                    ]
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("Subneteo Básico", weight=ft.FontWeight.BOLD),
                    leading=ft.Icon(ft.Icons.GRID_ON, color=ft.Colors.TEAL),
                    controls=[
                        ft.Container(padding=20, bgcolor=ft.Colors.GREY_50, border_radius=10, content=ft.Column([
                            ft.Text("Prefijos comunes en redes LAN/WAN:"),
                            ft.ListTile(leading=ft.Text("/24", weight=ft.FontWeight.BOLD), title=ft.Text("Máscara: 255.255.255.0"), subtitle=ft.Text("Hosts: 254. (LAN Típica)")),
                            ft.ListTile(leading=ft.Text("/30", weight=ft.FontWeight.BOLD), title=ft.Text("Máscara: 255.255.255.252"), subtitle=ft.Text("Hosts: 2. (Enlaces Punto a Punto)")),
                            ft.ListTile(leading=ft.Text("/32", weight=ft.FontWeight.BOLD), title=ft.Text("Máscara: 255.255.255.255"), subtitle=ft.Text("Hosts: 1. (Loopbacks / Host específico)")),
                        ]))
                    ]
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("Conceptos OSPF", weight=ft.FontWeight.BOLD),
                    leading=ft.Icon(ft.Icons.SHARE, color=ft.Colors.ORANGE),
                    controls=[
                        ft.Container(padding=20, bgcolor=ft.Colors.GREY_50, border_radius=10, content=ft.Column([
                            ft.Text("• OSPF es un protocolo de Estado de Enlace (Link-State)."),
                            ft.Text("• Área 0 (Backbone): Todas las áreas deben conectarse física o virtualmente al Área 0."),
                            ft.Text("• Process ID: Es local al router. R1 puede usar ID 1 y R2 usar ID 100 y aun así se comunican."),
                            ft.Text("• Hello/Dead Timers: Deben coincidir en ambos extremos para establecer adyacencia."),
                        ]))
                    ]
                )
            ], scroll=ft.ScrollMode.AUTO), padding=30
        )
    )