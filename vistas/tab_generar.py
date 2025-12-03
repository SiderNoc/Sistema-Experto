import flet as ft

def obtener_tab_generar(refs, on_generate_config):
    return ft.Tab(
        text="Generar",
        icon=ft.Icons.SAVE_ALT,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Generar y Guardar", style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=ft.Colors.BLUE_GREY_900),
                
                ft.Container(
                    padding=20, bgcolor=ft.Colors.BLUE_GREY_50, border_radius=10,
                    content=ft.Column([
                        ft.TextField(ref=refs['filename_input'], label="Nombre archivo", hint_text="config", suffix_text=".txt", border_radius=8, prefix_icon=ft.Icons.FILE_PRESENT),
                        ft.Checkbox(ref=refs['save_config_check'], label="Agregar 'write memory'", value=True),
                        ft.ElevatedButton(
                            text="GENERAR SCRIPT",
                            icon=ft.Icons.ROCKET_LAUNCH,
                            on_click=on_generate_config,
                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_800, padding=20),
                            width=300
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
                
                ft.Container(content=ft.Text("Vista Previa:", weight=ft.FontWeight.BOLD), margin=ft.margin.only(top=20)),
                
                ft.TextField(
                    ref=refs['output_textfield'],
                    multiline=True,
                    read_only=True,
                    text_style=ft.TextStyle(font_family="Consolas", size=14),
                    border_color=ft.Colors.BLUE_GREY_200,
                    expand=True
                )
            ], expand=True),
            padding=30
        )
    )