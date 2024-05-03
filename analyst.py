import time
import websockets
from matplotlib import pyplot as plt
from matplotlib import widgets as pltw
import numpy as np
import asyncio
from threading import Thread
import json
import sys
import getopt

plt.rcParams['font.family'] = 'SimHei'

_type_idle = -1
_type_contour = 1

draw_env = {
    "type": _type_idle
}

def debug(msg):
    print(f"[DEBUG] {msg}")
def error(msg):
    print(f"[ERROR] {msg}")
def warn(msg):
    print(f"[WARN] {msg}")
    
def take_of_default(k, d):
    if k in draw_env["ctx"]:
        return draw_env["ctx"][k]
    else:
        return d
    
def take_of(k, error="null pointer exception"):
    if k in draw_env["ctx"]:
        return draw_env["ctx"][k]
    else:
        raise Exception(error)
        
def is_support_type(t):
    if t == _type_contour:
        return True
    else:
        return False
        
def update_draw_env(new_env):
    draw_env["ctx"] = new_env["ctx"]
    draw_env["type"] = new_env["type"]

async def handle_event(websocket, path):
    ip, _ = websocket.remote_address
    debug(f"client connected: {ip}")
    async for message in websocket:
        try:
            new_env = json.loads(message)
            new_draw_type = new_env["type"] if "type" in new_env else -1
            if is_support_type(new_draw_type):
                update_draw_env(new_env)
            else:
                warn(f"not support draw type {new_draw_type}.")
        except:
            error(f"unable handle this request.")

def setup_ws_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    start_server = websockets.serve(handle_event, "127.0.0.1", ws_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

class Draw(object):
    def flush(self):
        fig.canvas.draw()
        fig.canvas.flush_events()

class Contour(Draw):
    
    __style_0 = 0
    __style_1 = 1
    __style_2 = 2
    
    __colorbar_added = False
    __options_added = False
    __colorbar = None

    __style = __style_0
    __linewidths = 1.5
    __linestyles = "-"
    __title_font_size = 18
    __axis_font_size = 13
    __levels = 14
    
    def __init__(self):
        plt.subplots_adjust(left=0.3)
        margin_top = 0.7
        style_radio_ax = plt.axes([0.03, margin_top, 0.15, 0.15])
        self.__style_labels = ["风格一", "风格二", "风格三"]
        self.__style_radio_button = pltw.RadioButtons(style_radio_ax, self.__style_labels)
        self.__style_radio_button.on_clicked(self.__on_radio_action)

        margin_top = margin_top - 0.05
        linewidths_slider_ax = plt.axes([0.07, margin_top, 0.12, 0.02])
        self.__linewidths_slider = pltw.Slider(linewidths_slider_ax, "线条宽度", 0.0, 5.0, valinit=self.__linewidths)
        self.__linewidths_slider.on_changed(self.__on_update_linewidths)

        margin_top = margin_top - 0.05
        title_font_size_slider_ax = plt.axes([0.07, margin_top, 0.12, 0.02])
        self.__title_font_size_slider = pltw.Slider(title_font_size_slider_ax, "标题尺寸", 13, 50, valinit=self.__title_font_size)
        self.__title_font_size_slider.on_changed(self.__on_update_title_font_size)

        margin_top = margin_top - 0.05
        axis_font_size_slider_ax = plt.axes([0.07, margin_top, 0.12, 0.02])
        self.__axis_font_size_slider = pltw.Slider(axis_font_size_slider_ax, "刻度尺寸", 10, 30, valinit=self.__axis_font_size)
        self.__axis_font_size_slider.on_changed(self.__on_update_axis_font_size)

        margin_top = margin_top - 0.05
        levels_slider_ax = plt.axes([0.07, margin_top, 0.12, 0.02])
        self.__levels_slider = pltw.Slider(levels_slider_ax, "划分粒度", 10, 30, valinit=self.__levels)
        self.__levels_slider.on_changed(self.__on_update_levels)

    def __on_update_linewidths(self, value):
        self.__linewidths = float(value)

    def __on_update_title_font_size(self, value):
        self.__title_font_size = value

    def __on_update_axis_font_size(self, value):
        self.__axis_font_size = value

    def __on_update_levels(self, value):
        self.__levels = int(value)

    def __on_radio_action(self, label):
        if(label in self.__style_labels):
            self.__on_update_style(label)

    def __on_update_style(self, label):
        global _request_reset
        new_style = self.__style_labels.index(label)
        if new_style == self.__style_0:
            self.__linewidths = 1.5
            self.__linestyles = "-"
        elif new_style == self.__style_1:
            pass
        else:
            self.__linewidths = 0.8
            self.__linestyles = "-."
        self.__style = new_style

    def __load_ctx(self):
        ctx = {
            "data": take_of("data"),
            "row": take_of("row"),
            "col": take_of("col"),
            "title": take_of_default("title", "无标题"),
            "cmap": take_of_default("cmap", "viridis"),
            "transpose": take_of_default("transpose", False)
        }
        return ctx

    def __clean_ax(self):
        ax.cla()
            
    def __plot_colorbar(self, cntr):
        if self.__colorbar == None:
            self.__colorbar = fig.colorbar(cntr, ax=ax)
        else:
            self.__colorbar.update_normal(cntr)
        
    def plot(self):
        ctx = self.__load_ctx()
        data_sheet = []
        row = ctx["row"]
        col = ctx["col"]
        data = ctx["data"]
        for i in range(col):
            g = []
            for j in range(i * row, i * row + row):
                g.append(data[j])
            data_sheet.append(g)
        self.__clean_ax()
        ax.grid(linestyle="-.")
        flush_status = True
        if ctx["transpose"] == True:
            data_sheet = np.transpose(np.mat(data_sheet))
        if self.__style == self.__style_0:
            cntr = ax.contour(data_sheet, self.__levels, cmap=ctx["cmap"], linewidths=self.__linewidths, linestyles=self.__linestyles)
            ax.clabel(cntr, inline=True, fontsize=8)
        elif self.__style == self.__style_1:
            cntr = ax.contourf(data_sheet, self.__levels, cmap=ctx["cmap"])
        elif self.__style == self.__style_2:
            ax.contour(data_sheet, self.__levels, colors="k", linewidths=self.__linewidths, linestyles=self.__linestyles)
            cntr = ax.contourf(data_sheet, self.__levels, cmap=ctx["cmap"])
        else:
            warn(f"unknown this style {__style}")
            flush_status = False
        if flush_status:
            ax.set_title(ctx["title"], fontsize=self.__title_font_size)
            ax.tick_params(axis="x", labelsize=self.__axis_font_size)
            ax.tick_params(axis="y", labelsize=self.__axis_font_size)
            self.__plot_colorbar(cntr)
            self.flush()

def run_main_loop():
    contour = Contour()
    global _request_reset
    while True:
        draw_type = draw_env["type"]
        if draw_type == _type_contour:
            contour.plot()
        else:
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.1)

if __name__ == '__main__':
    
    global figure_width
    figure_width = 12.8
    global figure_height
    figure_height = 5.2
    global title_size
    title_size = 18
    global ws_port
    ws_port = 55559
    optlist, args = getopt.getopt(sys.argv[1:], "s:", ["size="])
    for opt, value in optlist:
        if opt in ("-s", "--size"):
            figure_width, figure_height = map(lambda x: float(x) / 100.0, value.split("x"))
            
    plt.ion()
    global fig
    global ax
    fig, ax = plt.subplots()
    fig.set_figwidth(figure_width)
    fig.set_figheight(figure_height)
    ws_thread = Thread(target=setup_ws_server)
    ws_thread.daemon = True
    ws_thread.start()
    debug(f"waiting for client to connect, ws_port={ws_port}.")
    run_main_loop()