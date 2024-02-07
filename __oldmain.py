"""
Gravy-Tools
Набор макросов с графическим интерфейсом для упрощения строительства
Предназначен для использования вне проекта BTE
"""

__author__ = 'Колесников Богдан aka podliva_2008'
__credits__ = ('Петров Артём aka Brigart (оригинал скрипта для ЧС), '
               'Занегин Владислав aka Criffane 14 (тестирование)')
__contact__ = 'Discord: podliva_2008'
__version__ = 'Протестировано на Minecraft 1.18.2 с FAWE 2.8.5'

from PIL import ImageTk, Image
import win32clipboard as wclip
import win32process as wproc
import win32api as wapi
import win32gui as wgui
import win32con as wcon
import pydirectinput
import requests

from tkinter import ttk, Tk, StringVar, IntVar, Canvas, Frame, messagebox
from io import BytesIO
import threading
import math
import json

class Script():
    def __init__(self):
        self.win_name = 'Minecraft* 1.18.2 - Сетевая игра (сторонний сервер)'
        pydirectinput.PAUSE = 0.01  # Понижаем дефолтную длинную паузу

        try:
            # Получаем настройки из файла конфига
            with open('config.json', 'r') as file:
                json_string = file.read()
                self.config = json.loads(json_string)
        except FileNotFoundError:
            # Если таковой файл осутствует, то создаём его
            # Дефолтный конфиг, использованный в ЧС Краснодара
            self.config = {
                'walls': [
                    {'block': 'granite',
                     'mix': 'granite,polished_granite'},
                    {'block': 'bricks',
                     'mix': 'granite,bricks,terracotta'},
                    {'block': 'andesite',
                     'mix': 'gravel,stone,andesite'},
                    {'block': 'birch_planks',
                     'mix': 'birch_planks,stripped_birch_wood'},
                    {'block': 'white_concrete_powder',
                     'mix': 'white_concrete_powder,white_wool'}
                ],
                'slope_roofs': ['spruce', 'acacia', 'dark_oak',
                                'smooth_stone', 'sandstone',
                                'cut_sandstone', 'stone_brick',
                                'quartz', 'jungle'],
                'flat_roofs': ['light_gray', 'blue']
            }

            with open('config.json', 'w') as file:
                json.dump(self.config, file, indent=4)

    def open_window(self):
        """Подготовка окна майнкрафта к работе скрипта"""

        try:
            # Получаем hwnd окна майнкрафта
            self.mc_hwnd = wgui.FindWindow(None, self.win_name)

            # https://clck.ru/37Dnza
            remote_thread, _ = wproc.GetWindowThreadProcessId(self.mc_hwnd)
            wproc.AttachThreadInput(wapi.GetCurrentThreadId(),
                                    remote_thread,
                                    True)

            # Разворачивание окна и установка на него фокуса
            wgui.ShowWindow(self.mc_hwnd, wcon.SW_MAXIMIZE)
            wgui.SetFocus(self.mc_hwnd)

            # Смена раскладки на английскую
            wapi.SendMessage(self.mc_hwnd, 0x0050, 0, 0x04090409)

            return True
        except Exception as e:
            print(e)
            messagebox.showerror('Gravy Tools',
                                 'Произошла ошибка. Открыт ли Minecraft? '
                                 'Подключены ли вы к серверу?')
            return False

    def echo(self, message):
        """Вставка текста в чат и его отправка"""

        # Во избежание проблем при простой поочерёдной печати каждого
        # символа, тупо кидаем сообщение в буфер обмена
        wclip.OpenClipboard(self.mc_hwnd)
        wclip.EmptyClipboard()
        wclip.SetClipboardText(message)
        wclip.CloseClipboard()

        pydirectinput.press('t')

        # ctrl + v
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('v')
        pydirectinput.keyUp('ctrl')

        pydirectinput.press('enter')

    def poly(self, polygons):
        """Скрипт для отрисовки контуров зданий"""

        pydirectinput.press('esc')  # Выходим из главного меню
        self.echo('//gmask')
        self.echo('//desel')
        self.echo('//sel cuboid')
        for _, pairs_list in enumerate(polygons):
            for i in range(len(pairs_list)):

                # Получение координат одной стороны полигона
                lat_1, lon_1 = pairs_list[i - 1]
                lat_2, lon_2 = pairs_list[i]

                # Построение линии
                self.echo(f'/tpll {lat_1}, {lon_1}')
                self.echo('//pos1')
                self.echo(f'/tpll {lat_2}, {lon_2}')
                self.echo('//pos2')
                self.echo('//shift 1 d')
                self.echo('//line bricks')

        messagebox.showinfo('Gravy Tools', 'Скрипт завершил свою работу')

    def houses(self, polygon):
        """
        Скрипт на ЧС by Brigart
        Изменения внесены by podliva_2008
        """

        tech = 'emerald_ore'  # id технического блока

        # Типы стен и крыш берутся из json-файла конфига
        walls = self.config['walls']
        slope_roofs = self.config['slope_roofs']
        flat_roofs = self.config['flat_roofs']

        roofs_list = ('_slab,'.join(slope_roofs) + '_slab,' +
                      '_carpet,'.join(flat_roofs) + '_carpet')
        full_roofs_list = ('_slab,'.join(slope_roofs) + '_slab,' +
                           '_wool,'.join(flat_roofs) + '_wool')

        # TODO: вернуть тип крыш ступеньками и команды для них

        pydirectinput.press('esc')  # Выходим из главного меню

        self.echo('//gmask')
        self.echo('//desel')
        self.echo('//sel poly')

        # Выделение области для работы скрипта
        for index, coord_pair in enumerate(polygon):
            lat, lon = coord_pair
            self.echo(f'/tpll {lat}, {lon}')
            if index == 0:
                self.echo('//pos1')
            else:
                self.echo('//pos2')
        self.echo('//shift 1 d')

        # Покраска пола в блок крыши
        # Установка блока крыши под центральным
        for i in range(len(slope_roofs)):
            color = f'{slope_roofs[i]}_slab[type=double]'
            c_id = f'{slope_roofs[i]}_slab'

            self.echo('//gmask '
                      f'#offset[0][1][0][{c_id}],'
                      f'#offset[0][2][0][{c_id}],'
                      f'#offset[0][3][0][{c_id}],'
                      f'#offset[0][4][0][{c_id}]')
            self.echo(f'//re grass_block,dirt {color}')
        
        for i in range(len(flat_roofs)):
            color = f'{flat_roofs[i]}_wool'
            c_id = f'{flat_roofs[i]}_carpet'

            self.echo('//gmask '
                      f'#offset[0][1][0][{c_id}],'
                      f'#offset[0][2][0][{c_id}],'
                      f'#offset[0][3][0][{c_id}],'
                      f'#offset[0][4][0][{c_id}]')
            self.echo(f'//re grass_block,dirt {color}')

        # Заливка пола блоком крыши
        for i in range(len(slope_roofs)):
            c_id = color = f'{slope_roofs[i]}_slab[type=double]'

            self.echo('//gmask '
                      f'#offset[1][0][0][{c_id}],'
                      f'#offset[-1][0][0][{c_id}],'
                      f'#offset[0][0][1][{c_id}],'
                      f'#offset[0][0][-1][{c_id}]')
            for _ in range(20):
                self.echo(f'//re grass_block,dirt {color}')

        for i in range(len(flat_roofs)):
            c_id = color = f'{flat_roofs[i]}_wool'

            self.echo('//gmask '
                      f'#offset[1][0][0][{c_id}],'
                      f'#offset[-1][0][0][{c_id}],'
                      f'#offset[0][0][1][{c_id}],'
                      f'#offset[0][0][-1][{c_id}]')
            for _ in range(20):
                self.echo(f'//re grass_block,dirt {color}')

        # Установка блока типа здания под центральным
        self.echo('//shift 1 u')
        self.echo('//gmask')

        self.echo(f'//re {roofs_list} gold_block')

        # Замена золотых блоков на технический блок
        self.echo('//gmask')
        self.echo('//shift 1 d')
        self.echo('//expand 3 u')
        self.echo(f'//re gold_block {tech}')
        self.echo('//contract 3 d')

        # Поднятие стен фундамента
        self.echo('//gmask 0')
        self.echo('//shift 1 u')
        self.echo('//expand 1 u')

        for i in range(len(walls)):
            color = walls[i]['block']

            self.echo(f'//re >{color} {color}')
            self.echo(f'//re >{color} bricks')

        self.echo('//contract 1 d')
        self.echo('//shift 1 d')

        # Определение высоты здания

        self.echo('//shift 11 u')
        for f in range(7, 0, -1):
            self.echo(f'//gmask #offset[0][-{f}][0][{tech}]')
            self.echo('//shift 1 d')

            self.echo(f'//re {roofs_list} {tech}')

            self.echo(f'//re air {tech}')

        self.echo('//shift 1 d')
        self.echo('//shift 5 u')
        for f in range(5, 0, -1):
            self.echo(f'//gmask #offset[0][-{f}][0][{tech}]')
            self.echo('//shift 1 d')

            self.echo(f'//re {roofs_list} {tech}')

            self.echo(f'//re air {tech}')

        self.echo('//shift 1 d')
        self.echo('//shift 3 u')
        for f in range(3, 0, -1):
            self.echo(f'//gmask #offset[0][-{f}][0][{tech}]')
            self.echo('//shift 1 d')

            self.echo(f'//re {roofs_list} {tech}')

            self.echo(f'//re air {tech}')

        self.echo('//shift 1 d')

        # Возведение первого уровня дома
        self.echo('//gmask')

        self.echo(f'//re >{full_roofs_list} {tech}')

        self.echo('//shift 1 u')

        # Возведение всех этажей

        for _ in range(9):
            self.echo('//gmask '
                      f'#offset[1][0][0][{tech}],'
                      f'#offset[-1][0][0][{tech}],'
                      f'#offset[0][0][1][{tech}],'
                      f'#offset[0][0][-1][{tech}]')

            for _ in range(20):
                self.echo(f'//re >{tech} {tech}')

            self.echo('//re >bricks bricks')
            
            self.echo('//gmask '
                      '#offset[1][0][0][bricks],'
                      '#offset[-1][0][0][bricks],'
                      '#offset[0][0][1][bricks],'
                      '#offset[0][0][-1][bricks]')
            self.echo('//re >bricks bricks')
            
            self.echo('//shift 1 u')

        self.echo('//shift 11 d')

        # Крыша

        self.echo('//expand 20 u')
        self.echo('//shift 3 u')

        # Четырёхскатная крыша из полублоков
        
        for i in range(len(slope_roofs)):
            for f in range(11, 4, -3):
                self.echo(f'//gmask air&#offset[0][-{f}][0]'
                          f'[{slope_roofs[i]}_slab]')
                self.echo(f'//re >{tech} {slope_roofs[i]}_slab[type=double]')

            self.echo('//gmask '
                      f'#offset[1][0][0][{slope_roofs[i]}_slab[type=double]],'
                      f'#offset[-1][0][0][{slope_roofs[i]}_slab[type=double]],'
                      f'#offset[0][0][1][{slope_roofs[i]}_slab[type=double]],'
                      f'#offset[0][0][-1][{slope_roofs[i]}_slab[type=double]]')
            self.echo(f'//re >bricks {slope_roofs[i]}_slab[type=bottom]')

            self.echo('//gmask '
                      f'#offset[2][0][0][{slope_roofs[i]}_slab[type=double]],'
                      f'#offset[-2][0][0][{slope_roofs[i]}_slab[type=double]],'
                      f'#offset[0][0][2][{slope_roofs[i]}_slab[type=double]],'
                      f'#offset[0][0][-2][{slope_roofs[i]}_slab[type=double]]')
            self.echo(f'//re >bricks {slope_roofs[i]}_slab[type=bottom]')

            self.echo('//gmask '
                      f'#offset[1][0][0][{slope_roofs[i]}_slab[type=bottom]],'
                      f'#offset[-1][0][0][{slope_roofs[i]}_slab[type=bottom]],'
                      f'#offset[0][0][1][{slope_roofs[i]}_slab[type=bottom]],'
                      f'#offset[0][0][-1][{slope_roofs[i]}_slab[type=bottom]]')
            self.echo(f'//re >bricks {slope_roofs[i]}_slab[type=bottom]')

            self.echo('//gmask '
                      f'#offset[1][1][0][{slope_roofs[i]}_slab[type=bottom]],'
                      f'#offset[-1][1][0][{slope_roofs[i]}_slab[type=bottom]],'
                      f'#offset[0][1][1][{slope_roofs[i]}_slab[type=bottom]],'
                      f'#offset[0][1][-1][{slope_roofs[i]}_slab[type=bottom]]')
            self.echo(f'//re air {slope_roofs[i]}_slab[type=top]')

            for _ in range(7):
                self.echo('//gmask !'
                          f'#offset[2][-1][0][air],'
                          f'#offset[-2][-1][0][air],'
                          f'#offset[0][-1][2][air],'
                          f'#offset[0][-1][-2][air]')
                self.echo(f'//re >{slope_roofs[i]}_slab[type=double] '
                          f'{slope_roofs[i]}_slab[type=bottom]')

                self.echo('//gmask !'
                          '#offset[1][0][0][air],'
                          '#offset[-1][0][0][air],'
                          '#offset[0][0][1][air],'
                          '#offset[0][0][-1][air]')
                self.echo(f'//re {slope_roofs[i]}_slab[type=bottom] '
                          f'{slope_roofs[i]}_slab[type=double]')
        
        # Плоская крыша из ковров
            
        for i in range(len(flat_roofs)):
            for f in range(11, 4, -3):
                self.echo(f'//gmask air&#offset[0][-{f}][0]'
                          f'[{flat_roofs[i]}_wool]')
                self.echo(f'//re >{tech} {flat_roofs[i]}_carpet')
            self.echo('//gmask '
                      f'#offset[1][0][0][{flat_roofs[i]}_carpet],'
                      f'#offset[-1][0][0][{flat_roofs[i]}_carpet],'
                      f'#offset[0][0][1][{flat_roofs[i]}_carpet],'
                      f'#offset[0][0][-1][{flat_roofs[i]}_carpet]')
            self.echo(f'//re >bricks {flat_roofs[i]}_carpet')
            self.echo(f'//re >bricks {flat_roofs[i]}_carpet')

        self.echo('//gmask')

        self.echo('//contract 20 d')
        self.echo('//gmask')
        self.echo('//shift 1 d')
        self.echo('//expand 1 u')

        # Окна

        for _ in range(3):
            self.echo('//re bricks end_rod')
            self.echo('//shift 3 u')

        self.echo('//shift 9 d')
        self.echo('//expand 6 u')

        self.echo('//gmask '
                  '#offset[1][0][0][air]&'
                  '#offset[-1][0][0][air]')
        self.echo('//re end_rod bricks')
        self.echo('//gmask '
                  '#offset[0][0][1][air]&'
                  '#offset[0][0][-1][air]')
        self.echo('//re end_rod bricks')

        self.echo('//gmask '
                  '#offset[1][0][0][end_rod]&'
                  '#offset[0][0][1][end_rod]')
        self.echo('//re end_rod bricks')
        self.echo('//gmask '
                  '#offset[-1][0][0][end_rod]&'
                  '#offset[0][0][-1][end_rod]')
        self.echo('//re end_rod bricks')
        self.echo('//gmask '
                  '#offset[1][0][0][end_rod]&'
                  '#offset[0][0][-1][end_rod]')
        self.echo('//re end_rod bricks')
        self.echo('//gmask '
                  '#offset[-1][0][0][end_rod]&'
                  '#offset[0][0][1][end_rod]')
        self.echo('//re end_rod bricks')

        self.echo('//gmask end_rod&'
                  '[#offset[1][0][0][emerald_ore],'
                  '#offset[-1][0][0][emerald_ore]]&'
                  '[#offset[1][0][0][air],'
                  '#offset[-1][0][0][air]]')
        self.echo('//re =abs(z)%3 bricks')
        self.echo('//gmask end_rod&'
                  '[#offset[0][0][1][emerald_ore],'
                  '#offset[0][0][-1][emerald_ore]]&'
                  '[#offset[0][0][1][air],'
                  '#offset[0][0][-1][air]]')
        self.echo('//re =abs(x)%3 bricks')

        self.echo('//gmask '
                  '#offset[1][0][0][end_rod],'
                  '#offset[-1][0][0][end_rod],'
                  '#offset[0][0][1][end_rod],'
                  '#offset[0][0][-1][end_rod]')
        self.echo(f'//re {tech} gray_stained_glass')

        # Текстуринг
        # Покраска стен всех этажей

        self.echo('//gmask')
        self.echo('//expand 2 u')

        for i in range(len(walls)):
            for f in range(1, 10):
                self.echo(f'//gmask #offset[0][-{f}][0][{walls[i]["block"]}]')
                self.echo(f'//re bricks {walls[i]["block"]}')

        self.echo('//gmask')
        
        # Миксы

        self.echo('//expand 1 d')

        for i in range(len(walls)):
            self.echo(f'//re {walls[i]["block"]} {walls[i]["mix"]}')
        
        # Покраска технических блоков в цвет бэкграунда окон

        self.echo(f'//re {tech} gray_concrete')
        
        self.echo('//desel')

        messagebox.showinfo('Gravy Tools', 'Скрипт завершил свою работу')

    def start(self, script, args):
        """Запуск скрипта в отдельном потоке дабы интерфейс не фризило"""

        if self.open_window():
            threading.Thread(target=script, args=args).start()


class Interface:
    def __init__(self):
        """Создание окна и виджетов, их настройка."""

        try:
            with open('cache.json', 'r') as file:
                json_string = file.read()
                cached_entry = json.loads(json_string)
        except FileNotFoundError:
               cached_entry = {
                   'coords': '45.02783176031718, 38.98838186625211',
                   'scale': 20
               }

        try:
            with open('maps.json', 'r') as file:
                json_string = file.read()
                self.maps_info = json.loads(json_string)
        except FileNotFoundError:
            self.maps_info = {
                'Яндекс схема': {
                    'tile_url': ('https://core-renderer-tiles.maps.yandex.'
                                 'net/tiles?l=map&x={}&y={}&z={}'),
                    'is_ellipsoid': True
                },
                'Яндекс спутник': {
                    'tile_url': ('https://core-sat.maps.yandex.net/'
                                 'tiles?l=sat&x={}&y={}&z={}'),
                    'is_ellipsoid': True
                }
            }

            with open('maps.json', 'w') as file:
                json.dump(self.maps_info, file, indent=4, ensure_ascii=False)

        # Окно и его настройки
        self.root = Tk()
        self.root.title('Gravy Tools')
        self.root.geometry('768x862')
        self.root.resizable(False, False)
        self.root.protocol('WM_DELETE_WINDOW', self.save_cache)

        self.scale = IntVar()
        self.coords = StringVar()
        self.maptype = StringVar()

        self.coords.set(cached_entry['coords'])
        self.maptype.set('Выберите карту')

        self.polygons = []
        self.polygon_points = []

        # Создаём рамки для размещения элементов управления
        upper_frame = Frame(self.root)
        lower_frame = Frame(self.root)

        # Создаём холст для размещения карты и полигонов
        self.map_canvas = Canvas(width=768, height=768, cursor='tcross')
        self.map_canvas.bind(sequence='<ButtonPress-1>', func=self.add_point)
        self.map_canvas.bind(sequence='<ButtonPress-2>', func=self.delete_poly)
        self.map_canvas.bind(sequence='<ButtonPress-3>', func=self.save_poly)

        upper_frame.pack()
        self.map_canvas.pack()
        lower_frame.pack()

        coords_entry = ttk.Entry(master=upper_frame,
                                 width=35,
                                 textvariable=self.coords)
        coords_button = ttk.Button(master=upper_frame,
                                        text='Обновить',
                                        command=self.update_map)

        self.scaling_label = ttk.Label(master=upper_frame, text=f'Масштаб: 20')
        self.scaling_scale = ttk.Scale(master=upper_frame,
                                       orient='horizontal',
                                       length=100,
                                       from_=0,
                                       to=20,
                                       variable=self.scale)
        self.scaling_scale.set(cached_entry['scale'])
        self.scaling_label['text'] = f'Масштаб: {self.scale.get()}'
        self.scaling_scale.bind(sequence='<Motion>',
                                func=lambda event: self.show_scale())
        self.scaling_scale.bind(sequence='<ButtonRelease-1>',
                                func=lambda event: self.update_map())

        maptypes = list(self.maps_info.keys())
        maptype_combobox = ttk.Combobox(master=upper_frame,
                                        width=15,
                                        textvariable=self.maptype,
                                        values=maptypes,
                                        state='readonly')
        maptype_combobox.bind(sequence='<<ComboboxSelected>>',
                              func=lambda event: self.update_map())
        
        scripts_label = ttk.Label(master=lower_frame, text='Скрипты:')

        poly_button = ttk.Button(master=lower_frame, text='Контуры')
        poly_button.bind(sequence='<ButtonRelease-1>',
                          func=lambda event: script.start(script.poly,
                                                          [self.polygons]))

        houses_button = ttk.Button(master=lower_frame, text='Дома')
        houses_button.bind(sequence='<ButtonRelease-1>',
                          func=lambda event: script.start(script.houses,
                                                          [self.polygons[-1]]))

        coords_entry.pack(side='left', padx=10, pady=10)
        coords_button.pack(side='left', padx=10, pady=10)
        self.scaling_scale.pack(side='left', padx=10, pady=10)
        self.scaling_label.pack(side='left', padx=10, pady=10)
        maptype_combobox.pack(side='left', padx=10, pady=10)

        scripts_label.pack(side='left', padx=10, pady=10)
        poly_button.pack(side='left', padx=10, pady=10)
        houses_button.pack(side='left', padx=10, pady=10)

        self.root.mainloop()

    def show_scale(self):
        """
        Отображение значения текущего масштаба.
        """

        self.scaling_label['text'] = f'Масштаб: {self.scale.get()}'

    def add_point(self, event):
        """Рисование полигона курсором."""

        tag = len(self.polygons)

        self.polygon_points.append(event.x)
        self.polygon_points.append(event.y)

        self.map_canvas.delete([f'poly_{tag}'])
        self.map_canvas.create_polygon(self.polygon_points,
                                       width=2,
                                       outline='red4',
                                       fill='red3',
                                       tags=[f'poly_{tag}'])

    def delete_poly(self, _):
        """Удаление последнего созданного или нарисованного полигона."""

        try:
            if len(self.polygon_points) > 0:
                tag = len(self.polygons)
                del self.polygon_points[-2:]
                self.map_canvas.delete([f'poly_{tag}'])
                self.map_canvas.create_polygon(self.polygon_points,
                                            width=2,
                                            outline='red4',
                                            fill='red3',
                                            tags=[f'poly_{tag}'])
            else:
                tag = -1 % len(self.polygons)
                del self.polygons[-1]
                self.map_canvas.delete([f'poly_{tag}'])
        except ZeroDivisionError:
            messagebox.showerror('Gravy Tools',
                                 'Нет полигонов или точек для удаления')


    def save_poly(self, _):
        """Сохранение/фиксация нарисованного полигона на одной позиции."""

        polygon_geopoints = []
        tag = len(self.polygons)
        try:
            self.map_canvas.delete([f'poly_{tag}'])
            self.map_canvas.create_polygon(self.polygon_points,
                                           width=2,
                                           outline='green4',
                                           fill='green3',
                                           tags=[f'poly_{tag}'])
            
            for index, value in enumerate(self.polygon_points):
                if index % 2 == 0:
                    x = value
                else:
                    y = value
                    lat, lon = self.mouse_to_geo(x, y)
                    polygon_geopoints.append((lat, lon))
        except IndexError:
            messagebox.showerror('Gravy Tools',
                                 'Нет полигонов для сохранения')

        self.polygons.append(polygon_geopoints)
        self.polygon_points = []

    def mouse_to_geo(self, x, y):
        """Перевод координат холста в географические координаты."""

        # Я хз как это объяснить, разбирайтесь сами
        x, y = x / 256 + self.tile_x - 1, y / 256 + self.tile_y - 1
        z = self.scale.get()

        # https://clck.ru/37BGai
        lon = x / (2 ** z) * 360 - 180
        lat = math.atan(math.sinh(math.pi - y / (2 ** z) *
                                  (math.pi * 2))) * 180 / math.pi
        return lat, lon

    def update_map(self):
        """Обновление тайлов карты по географическим координатам."""

        maptype = self.maptype.get()
        url = self.maps_info[maptype]['tile_url']
        is_ellipsoid = self.maps_info[maptype]['is_ellipsoid']

        lat, lon = self.coords.get().split(', ')
        lat, lon = float(lat), float(lon)
        z = self.scale.get()

        # Сначала высчитываем номер тайла для сферической проекции
        # https://clck.ru/37BGai
        beta = lat * math.pi / 180
        stile_x = int(((lon + 180) / 360) * (2 ** z))
        stile_y = int((1 - ((math.log(math.tan(beta) +
                                      (1 / math.cos(beta)))) / math.pi)) *
                                      (2 ** (z - 1)))

        # Однако если проекция эллиптическая, высчитываем смещение тайла
        # относительно сферической проекции, чтобы потом выровнять карты
        if is_ellipsoid:
            # https://clck.ru/37RLnz
            radius_a = 6378137
            radius_b = 6356752

            # Находим широту и долготу тайла сферической проекции
            lon = stile_x / (2 ** z) * 360 - 180
            lat = math.atan(math.sinh(math.pi - stile_y / (2 ** z) *
                                      (math.pi * 2))) * 180 / math.pi
            
            lat_radians = math.radians(lat)
            y_compr = (math.sqrt((radius_a ** 2) - (radius_b ** 2)) /
                             radius_a)

            m2 = (math.log((1 + math.sin(lat_radians)) /
                           (1 - math.sin(lat_radians))) / 2 - y_compr *
                           math.log((1 + y_compr * math.sin(lat_radians)) /
                                    (1 - y_compr * math.sin(lat_radians))) / 2)

            etile_x = int((lon + 180) / 360 * (2 ** z))
            etile_y = int((2 ** z) / 2 - m2 * (2 ** z) / 2 / math.pi)

            offset_x = int(((lon + 180) / 360 * (2 ** z) - etile_x) * 256)
            offset_y = int(((2 ** z) / 2 - m2 * (2 ** z) /
                            2 / math.pi - etile_y) * 256)

            x, y = etile_x, etile_y
        else:
            x, y = stile_x, stile_y
            offset_x = offset_y = 0

        self.tile_x, self.tile_y = stile_x, stile_y

        map = Image.new(mode='RGB', size=(1280, 1280))  # Сюда встанут тайлы
        for i in range(5):  # Высота участка карты будет 5 тайлов
            for q in range(5):  # Ширина участка карты будет 5 тайлов
                # Подробнее тут: https://clck.ru/37BGba
                response = requests.get(url.format(x-(2-q), y-(2-i), z))
                decoded = BytesIO(response.content)

                if response.status_code == 200:
                    tile = Image.open(decoded)
                    map.paste(im=tile, box=(256*q, 256*i))
        self.map_tk = ImageTk.PhotoImage(map)

        # Картинка и так смещена на -256 пикселей по x и y для отцентровки
        self.map_canvas.create_image((-256 - offset_x),
                                     (-256 - offset_y),
                                     anchor='nw',
                                     image=self.map_tk)

        # После обновления карты полигоны пропадают, поднимаем их
        for tag in range(len(self.polygons) + 1):
            self.map_canvas.tag_raise([f'poly_{tag}'])

    def save_cache(self):
        """Сохранение последних действий пользователя в кэше"""

        user_cache = {
            'coords': self.coords.get(),
            'scale': self.scale.get()
        }

        with open('cache.json', 'w') as file:
            json.dump(user_cache, file, indent=4)

        self.root.destroy()


if __name__ == '__main__':
    script = Script()
    interface = Interface()