import flet as ft
from utils import crear_boton_ayuda

def obtener_tab_general(page, refs, on_device_change, on_password_change):
    return ft.Tab(
        text="General",
        icon=ft.Icons.SETTINGS,
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.TUNE, color=ft.Colors.BLUE_700),
                        ft.Text("Configuración Básica", style=ft.TextThemeStyle.HEADLINE_SMALL, color=ft.Colors.BLUE_GREY_800),
                        crear_boton_ayuda(page, "Configuración Básica", 
                            "Define la identidad y seguridad del dispositivo:\n\n• Hostname: Nombre único.\n• VTY: Acceso remoto.\n• Secret: Contraseña root.", "Ayuda")
                    ]), margin=ft.margin.only(bottom=15)
                ),
                
                ft.RadioGroup(
                    ref=refs['device_type'],
                    content=ft.Row([
                        ft.Radio(value="router", label="Router"),
                        ft.Radio(value="switch", label="Switch")
                    ]),
                    value="router",
                    on_change=on_device_change
                ),
                
                ft.TextField(ref=refs['hostname'], label="Hostname", hint_text="R1", border_radius=8, prefix_icon=ft.Icons.COMPUTER),
                ft.TextField(ref=refs['banner_motd'], label="Banner MOTD", border_radius=8, prefix_icon=ft.Icons.WARNING_AMBER),
                
                ft.Checkbox(label="Configurar contraseñas", on_change=on_password_change),
                
                ft.Container(
                    ref=refs['password_controls'],
                    visible=False,
                    bgcolor=ft.Colors.BLUE_50,
                    padding=15,
                    border_radius=10,
                    content=ft.Column(controls=[
                        ft.Text("Seguridad", weight=ft.FontWeight.BOLD),
                        ft.TextField(ref=refs['console_pw'], label="Pass Consola", password=True, can_reveal_password=True, border_radius=8),
                        ft.TextField(ref=refs['vty_pw'], label="Pass VTY", password=True, can_reveal_password=True, border_radius=8),
                        ft.TextField(ref=refs['enable_secret'], label="Enable Secret", password=True, can_reveal_password=True, border_radius=8),
                        ft.Checkbox(ref=refs['encrypt_passwords'], label="Encriptar claves", value=True),
                    ])
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=30
        )
    )