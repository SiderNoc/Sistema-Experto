# utils.py
import flet as ft
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
    try:
        interface = ipaddress.IPv4Interface(f"{ip_str}/{cidr_str}")
        network = interface.network
        network_address = str(network.network_address)
        wildcard_mask = str(network.hostmask)
        return network_address, wildcard_mask
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return None, None

def mostrar_ayuda(page, titulo, mensaje):
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
            ft.ElevatedButton("Entendido", on_click=lambda e: page.close(dlg), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=12),
    )
    page.open(dlg)

def crear_boton_ayuda(page, titulo, mensaje, tooltip_corto):
    return ft.IconButton(
        icon=ft.Icons.HELP, 
        icon_color=ft.Colors.INDIGO_500, 
        icon_size=24,
        tooltip=tooltip_corto,
        on_click=lambda e: mostrar_ayuda(page, titulo, mensaje)
    )