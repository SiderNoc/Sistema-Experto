# vistas/tab_consejos.py
import flet as ft


def obtener_tab_consejos(page):
    return ft.Tab(
        text="Consejos",
        icon=ft.Icons.LIGHTBULB_OUTLINE,
        content=ft.Container(
            padding=30,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[

                    #  TÍTULO PRINCIPAL
                    ft.Container(
                        margin=ft.margin.only(bottom=20),
                        content=ft.Row(
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    ft.Icons.SCHOOL,
                                    color=ft.Colors.PURPLE_700,
                                    size=32
                                ),
                                ft.Text(
                                    "Guía Rápida y Conceptos",
                                    style=ft.TextThemeStyle.HEADLINE_SMALL,
                                    color=ft.Colors.BLUE_GREY_900,
                                ),
                            ],
                        )
                    ),

                    #  BOTÓN DE MÁS INFORMACIÓN
                    ft.Container(
                    alignment=ft.alignment.center_left,
                    margin=ft.margin.only(bottom=20),
                    content=ft.ElevatedButton(
                        text="Más información (Documentación Cisco)",
                        icon=ft.Icons.OPEN_IN_NEW,
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                        # [CORRECCIÓN] Usamos page.launch_url
                        on_click=lambda _: page.launch_url(
                            "https://www.cisco.com/c/es_mx/support/ios-nx-os-software/ios-xe-17/products-command-reference-list.html"
                        )
                    )
                ),

                    #  CONTRASEÑAS (CONSOLE, ENABLE SECRET, VTY)
                    ft.ExpansionTile(
                        leading=ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.RED_700),
                        title=ft.Text("Buenas prácticas de contraseñas en Cisco IOS", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Consola, enable secret y líneas VTY"),
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                content=ft.Column([
                                    ft.Text("• Usa siempre 'enable secret' en lugar de 'enable password' (va cifrado)."),
                                    ft.Text("• En line console 0: usar 'login' y 'password <clave>' si no hay usuarios locales."),
                                    ft.Text("• Si existen usuarios locales, usar 'login local'."),
                                    ft.Text("• En VTY: preferir 'login local' y limitar acceso con 'transport input ssh'."),
                                    ft.Text("• No usar contraseñas triviales; Cisco recomienda mínimo 10 caracteres."),
                                ])
                            )
                        ]
                    ),

                    #  INTERFACES IPv4 / IPv6
                    ft.ExpansionTile(
                        leading=ft.Icon(ft.Icons.DEVICE_HUB, color=ft.Colors.BLUE_600),
                        title=ft.Text("Consejos para configurar interfaces IPv4 e IPv6", weight=ft.FontWeight.BOLD),
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                content=ft.Column([
                                    ft.Text("• Cada interfaz debe estar activa: 'no shutdown'."),
                                    ft.Text("• Para IPv4: asignar dirección con prefijo (/CIDR) y evitar direcciones de broadcast o red."),
                                    ft.Text("• Verificación rápida: 'show ip interface brief'."),
                                    ft.Text("• Para IPv6: usar 'ipv6 enable' para activar link-local automáticamente."),
                                    ft.Text("• Direcciones globales: 'ipv6 address <ip>/<prefijo>'."),
                                    ft.Text("• Buena práctica: documentar la interfaz usando 'description'."),
                                ])
                            )
                        ]
                    ),

                    #  CIDR / MÁSCARAS / WILDCARD
                    ft.ExpansionTile(
                        leading=ft.Icon(ft.Icons.CALCULATE_OUTLINED, color=ft.Colors.INDIGO),
                        title=ft.Text("CIDR, máscaras y wildcard", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Máscaras / prefijos usados y cálculo rápido"),
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                content=ft.Column([
                                    ft.Text("• Más bits → menos hosts; menos bits → más hosts."),
                                    ft.Text("• Prefijos más comunes:"),
                                    ft.Text("   /24 → 254 hosts (LAN típica)"),
                                    ft.Text("   /30 → 2 hosts (punto a punto)"),
                                    ft.Text("   /32 → 1 host (loopbacks)"),
                                    ft.Divider(),
                                    ft.Text("• Wildcard (para OSPF) = 255.255.255.255 - Máscara"),
                                    ft.Text("Ejemplo /24:", weight=ft.FontWeight.BOLD),
                                    ft.Text("  255.255.255.255", font_family="Consolas"),
                                    ft.Text("- 255.255.255.  0", font_family="Consolas"),
                                    ft.Text("------------------", font_family="Consolas"),
                                    ft.Text("    0.  0.  0.255", font_family="Consolas",
                                            weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                                ])
                            )
                        ]
                    ),

                    #  OSPF
                    ft.ExpansionTile(
                        leading=ft.Icon(ft.Icons.SHARE, color=ft.Colors.ORANGE),
                        title=ft.Text("Conceptos esenciales de OSPF", weight=ft.FontWeight.BOLD),
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                content=ft.Column([
                                    ft.Text("• OSPF es un protocolo de estado de enlace (Link-State)."),
                                    ft.Text("• Process ID es local al router; no necesita coincidir."),
                                    ft.Text("• Todas las áreas deben conectarse al Área 0."),
                                    ft.Text("• Los Hello y Dead Timers deben coincidir para adyacencia."),
                                    ft.Text("• Comando clave: 'network <ip> <wildcard> area <n>'."),
                                ])
                            )
                        ]
                    ),

                    #  NAT ESTÁTICO
                    ft.ExpansionTile(
                        leading=ft.Icon(ft.Icons.SWAP_HORIZ, color=ft.Colors.GREEN_700),
                        title=ft.Text("NAT estático", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Traducción 1 a 1"),
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                content=ft.Column([
                                    ft.Text("• Asigna una IP pública fija a un host interno."),
                                    ft.Text("• Se usa para servidores que deben ser accesibles desde Internet."),
                                    ft.Text("• Ejemplo típico:"),
                                    ft.Text("  ip nat inside source static 192.168.1.10 200.10.10.5",
                                            font_family="Consolas"),
                                    ft.Text("• Siempre marcar interfaces con 'ip nat inside' / 'ip nat outside'."),
                                ])
                            )
                        ]
                    ),

                    #  NAT DINÁMICO (POOL)=
                    ft.ExpansionTile(
                        leading=ft.Icon(ft.Icons.SHUFFLE_OUTLINED, color=ft.Colors.TEAL_700),
                        title=ft.Text("NAT dinámico", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Uso de pools de direcciones públicas"),
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                content=ft.Column([
                                    ft.Text("• Se usa cuando varios hosts necesitan salir usando un pool de IP públicas."),
                                    ft.Text("• Requiere:"),
                                    ft.Text("   - Crear pool con 'ip nat pool'."),
                                    ft.Text("   - ACL para tráfico interno permitido."),
                                    ft.Text("   - Interfaces inside/outside definidas."),
                                    ft.Text("• Si falla: revisar ACL, rutas y conectividad de la interfaz de salida."),
                                ])
                            )
                        ]
                    ),

                ],
            ),
        ),
    )
