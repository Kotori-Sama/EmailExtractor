import os
import flet as ft
import pipline

class AppConfig:
    Version = "v0.1.0"
    Author = "Wang Yuchao"
    Title = "邮箱提取工具"

def main(page: ft.Page):

    def get_fonts():
        # 默认是黑体
        fonts = {'default': './assets/fonts/simhei.ttf'}

        # 获取字体文件，不区分大小写
        for file in os.listdir('./assets/fonts'):
            if file.endswith('.ttf',) or file.endswith('.ttc'):
                font_name = os.path.splitext(file)[0]
                fonts[font_name] = f'./assets/fonts/{file}'
            if file.endswith('.TTF',) or file.endswith('.TTC'):
                font_name = os.path.splitext(file)[0]
                fonts[font_name] = f'./assets/fonts/{file}'

        return fonts
    
    def toggle_theme(e):
        
        # 切换主题模式
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        page.update()
    ####################################################################################

    page.fonts = get_fonts()
    page.theme = ft.Theme(font_family="default")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = AppConfig.Title + " " + AppConfig.Version

    left_nav = ft.NavigationRail(
        # min_width=100,
        min_extended_width=180,
        label_type=ft.NavigationRailLabelType.ALL,
        selected_index=0,
        group_alignment=-0.9,
        destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME, 
                    selected_icon=ft.icons.HOME_FILLED, 
                    label="主页"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.STORAGE, 
                    selected_icon=ft.icons.STORAGE_ROUNDED, 
                    label="数据库"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SEARCH,
                    selected_icon=ft.icons.SEARCH,
                    label="查找",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="设置",
                ),
            ],
        # on_change=lambda e: print("Selected destination:", e.control.selected_index),
        extended = True,
        height = 600
    )
    

    theme_button = ft.Container(
        ft.IconButton(
            icon=ft.icons.NIGHTS_STAY_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.WB_SUNNY_OUTLINED,
            tooltip="切换夜间模式",
            on_click = toggle_theme
        ),
        alignment = ft.alignment.bottom_center,
        width=180    # 设置容器的宽度
    )


    page.add(
        ft.Row(
            [
                ft.Column(
                    controls=[
                        left_nav,
                        theme_button,
                    ],
                    # alignment = ft.alignment.center,
                    # expand=True,
                ),
                ft.VerticalDivider(width=1),
                ft.Column([ ft.Text("Body!")],expand=True),
            ],
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)