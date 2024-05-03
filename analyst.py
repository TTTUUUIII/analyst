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
plt.rcParams['axes.unicode_minus'] = False

_type_idle = -1
_type_contour = 1

_interrupt = False
_debug = False

draw_env = {
    "type": _type_idle,
    "figure_width": 12.8,
    "figure_height": 5.2,
    "title_size": 18,
    "ws_port": 55559,
    "interval": 0.1,
    "ims": {}
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
    start_server = websockets.serve(handle_event, "127.0.0.1", draw_env["ws_port"])
    asyncio.get_event_loop().run_until_complete(start_server)
    debug(f"waiting for client to connect, ws_port={draw_env["ws_port"]}.")
    asyncio.get_event_loop().run_forever()

class Draw(object):
    def flush(self):
        fig.canvas.draw()
        fig.canvas.flush_events()

class Contour(Draw):
    
    __style_0 = 0
    __style_1 = 1
    __style_2 = 2
    __all_cmaps = ["viridis" ,"cividis" , "plasma" , "inferno" , "magma", "hot" , "jet"]
    
    __colorbar_added = False
    __options_added = False
    __colorbar = None

    __style = __style_0
    __linewidths = 1.5
    __linestyles = "-"
    __title_font_size = 18
    __axis_font_size = 13
    __levels = 14
    __cmap = __all_cmaps[0]
    
    def __init__(self):
        margin_top = 0.75
        margin_left = 0.05
        slider_width = 0.08
        self.__style_labels = ["风格一", "风格二", "风格三"]
        item_count = len(self.__style_labels)
        style_radio_ax = plt.axes([margin_left - 0.04, margin_top, 0.13, 0.05 * item_count])
        self.__style_radio_button = pltw.RadioButtons(style_radio_ax, self.__style_labels)
        self.__style_radio_button.on_clicked(self.__on_radio_action)

        self.__cmap_labels = [f"色调{i}" for i in range(1, len(self.__all_cmaps) + 1)]
        item_count = len(self.__cmap_labels)
        margin_top = margin_top - 0.05 * item_count - 0.03
        cmap_radio_ax = plt.axes([margin_left - 0.04, margin_top, 0.13, 0.05 * item_count])
        self.__cmap_radio_button = pltw.RadioButtons(cmap_radio_ax, self.__cmap_labels)
        self.__cmap_radio_button.on_clicked(self.__on_radio_action)

        margin_top = margin_top - 0.05
        linewidths_slider_ax = plt.axes([margin_left, margin_top, slider_width, 0.02])
        self.__linewidths_slider = pltw.Slider(linewidths_slider_ax, "线条宽度", 0.0, 3.0, valinit=self.__linewidths)
        self.__linewidths_slider.on_changed(self.__on_update_linewidths)

        margin_top = margin_top - 0.05
        title_font_size_slider_ax = plt.axes([margin_left, margin_top, slider_width, 0.02])
        self.__title_font_size_slider = pltw.Slider(title_font_size_slider_ax, "标题尺寸", 13, 50, valinit=self.__title_font_size)
        self.__title_font_size_slider.on_changed(self.__on_update_title_font_size)

        margin_top = margin_top - 0.05
        axis_font_size_slider_ax = plt.axes([margin_left, margin_top, slider_width, 0.02])
        self.__axis_font_size_slider = pltw.Slider(axis_font_size_slider_ax, "刻度尺寸", 10, 30, valinit=self.__axis_font_size)
        self.__axis_font_size_slider.on_changed(self.__on_update_axis_font_size)

        margin_top = margin_top - 0.05
        levels_slider_ax = plt.axes([margin_left, margin_top, slider_width, 0.02])
        self.__levels_slider = pltw.Slider(levels_slider_ax, "划分粒度", 10, 35, valinit=self.__levels)
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
        if label in self.__style_labels:
            self.__on_update_style(label)
        elif label in self.__cmap_labels:
            self.__on_update_cmap(label)
    
    def __on_update_cmap(self, label):
        new_cmap_index = self.__cmap_labels.index(label)
        self.__cmap = self.__all_cmaps[new_cmap_index]

    def __on_update_style(self, label):
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
            "row": take_of_default("row", 0),
            "col": take_of_default("col", 0),
            "title": take_of_default("title", "无标题"),
            "remap": take_of_default("remap", False),
            "transpose": take_of_default("transpose", False)
        }
        return ctx

    def __clean_ax(self):
        ax.cla()
            
    def __plot_colorbar(self, cntr):
        if self.__colorbar == None:
            self.__colorbar = fig.colorbar(cntr, ax=ax, use_gridspec=True)
        else:
            self.__colorbar.update_normal(cntr)
    
    def __remap_data(self, data, row, col):
        new_data = []
        for i in range(col):
            g = []
            for j in range(i * row, i * row + row):
                g.append(data[j])
            new_data.append(g)
        return new_data

        
    def plot(self):
        ctx = self.__load_ctx()
        z = self.__remap_data(ctx["data"], ctx["row"], ctx["col"]) if ctx["remap"] else ctx["data"]
        if transpose:
            z = np.transpose(np.mat(z))
        self.__clean_ax()
        ax.grid(linestyle="-.")
        flush_status = True
        if self.__style == self.__style_0:
            cntr = ax.contour(z, self.__levels, cmap=self.__cmap, linewidths=self.__linewidths, linestyles=self.__linestyles)
            ax.clabel(cntr, inline=True, fontsize=8)
        elif self.__style == self.__style_1:
            cntr = ax.contourf(z, self.__levels, cmap=self.__cmap)
        elif self.__style == self.__style_2:
            cntr = ax.contourf(z, self.__levels, cmap=self.__cmap)
            ax.contour(cntr, self.__levels, colors="k", linewidths=self.__linewidths, linestyles=self.__linestyles)
        else:
            warn(f"unknown this style {__style}")
            flush_status = False
        if flush_status:
            ax.set_title(ctx["title"], fontsize=self.__title_font_size)
            ax.tick_params(axis="x", labelsize=self.__axis_font_size)
            ax.tick_params(axis="y", labelsize=self.__axis_font_size)
            self.__plot_colorbar(cntr)
            self.flush()

def on_window_close(event):
    global _interrupt
    _interrupt = True

def test_data():
    x, y = np.meshgrid(np.arange(7), np.arange(10))
    return np.sin(0.5 * x) * np.cos(0.52 * y)

def env_create():
    plt.ion()
    global fig
    global ax
    fig, ax = plt.subplots()
    fig.set_figwidth(draw_env["figure_width"])
    fig.set_figheight(draw_env["figure_height"])
    plt.connect("close_event", on_window_close)
    plt.subplots_adjust(left=0.2)
    ax.grid(linestyle="-.")
    if _debug:
        draw_env["type"] = _type_contour
        draw_env["ctx"] = {
            "data": test_data(),
            "remap": False
        }

def env_destory():
    plt.ioff()
    plt.close()

def get_impl(id):
    if id in draw_env["ims"]:
        return draw_env["ims"][id]
    if id == "contour":
        draw_env["ims"][id] = Contour()
    else:
        warn(f"{id} not impl!")
        return None
    return draw_env["ims"][id]

def run_main_loop():
    global _interrupt
    env_create()
    while not _interrupt:
        draw_type = draw_env["type"]
        if draw_type == _type_contour:
            im = get_impl("contour")
            if im != None:
                im.plot()
        else:
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(draw_env["interval"])
    env_destory()
    debug("main loop has interrupted.")

def show_help():
    usage = """
        usage: 
            python analyst.py [options]
        options:
            -s, --size          初始化窗口尺寸。
            -f, --fps           绘制速度，值越大绘制速度越快，1-30。
            -d, --debug         用于调试模式，调试模式下程序只绘制内部生成的样板数据，且任何其他功能（例如：websocket）都处于禁用状态。
            -h, --help          显示帮助信息。
    """
    print(usage)

def parse_args():
    status = True
    optlist, args = getopt.getopt(sys.argv[1:], "s:f:d:h", ["size=", "fps=", "debug=", "help"])
    for opt, value in optlist:
        if opt in ("-s", "--size"):
            draw_env["figure_width"], draw_env["figure_height"] = map(lambda x: float(x) / 100.0, value.split("x"))
        elif opt in ("-f", "--fps"):
            draw_env["interval"] = 1.0 / float(value)
        elif opt in ("-d", "--debug"):
            global _debug
            _debug = value in ("true", "True")
        elif opt in ["-h", "--help"]:
            show_help()
            status = False
            break
        else:
            raise Exception(f"unknown option {opt}")
    return status

if __name__ == '__main__':
    if parse_args():
        if not _debug:
            ws_thread = Thread(target=setup_ws_server)
            ws_thread.daemon = True
            ws_thread.start()
        run_main_loop()