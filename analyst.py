import time
import websockets
from matplotlib import pyplot as plt
import numpy as np
import asyncio
from threading import Thread
import json
import sys
import getopt

plt.rcParams['font.family'] = 'SimHei'

_type_idle = -1
_type_contour = 1

_style_0 = 0
_style_1 = 1
_style_2 = 2

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
    
def flush():
    fig.canvas.draw()
    fig.canvas.flush_events()

def contour_ctx():
    ctx = {
        "data": take_of("data"),
        "row": take_of("row"),
        "col": take_of("col"),
        "title": take_of_default("title", ""),
        "levels": take_of_default("levels", 14),
        "cmap": take_of_default("cmap", "viridis"),
        "transpose": take_of_default("transpose", False),
        "style": take_of_default("style", _style_0),
        "linewidths": take_of_default("linewidths", 0.5),
        "linestyles": take_of_default("linestyles", "-")
    }
    return ctx
    
colorbar_added = False

def plot_contour():
    ctx = contour_ctx()
    data_sheet = []
    row = ctx["row"]
    col = ctx["col"]
    data = ctx["data"]
    for i in range(col):
        g = []
        for j in range(i * row, i * row + row):
            g.append(data[j])
        data_sheet.append(g)
    ax.cla()
    if ctx["transpose"] == True:
        data_sheet = np.transpose(np.mat(data_sheet))
    if ctx["style"] == _style_0:
        cntr = ax.contour(data_sheet, ctx["levels"], cmap=ctx["cmap"], linestyles=ctx["linestyles"], linewidths=ctx["linewidths"])
        ax.clabel(cntr, inline=True, fontsize=8)
    elif ctx["style"] == _style_1:
        cntr = ax.contourf(data_sheet, ctx["levels"], cmap=ctx["cmap"])
    else:
        ax.contour(data_sheet, ctx["levels"], linestyles=ctx["linestyles"], colors="k", linewidths=ctx["linewidths"])
        cntr = ax.contourf(data_sheet, ctx["levels"], cmap=ctx["cmap"])
    ax.set_title(ctx["title"], fontsize=title_size)
    global colorbar_added
    if not colorbar_added:
        ax.get_figure().colorbar(cntr, ax=ax)
        colorbar_added = True
    
def run_main_loop():
    while True:
        draw_type = draw_env["type"]
        if draw_type == _type_contour:
            plot_contour()
        else:
            pass
        flush()
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
    
    optlist, args = getopt.getopt(sys.argv[1:], "", ["size=", "titlesize="])
    for opt, value in optlist:
        if opt in ("--size"):
            figure_width, figure_height = map(lambda x: float(x) / 100.0, value.split("x"))
        if opt in ("--titlesize"):
            title_size = int(value)
            
    plt.ion()
    global fig
    global ax
    fig, ax = plt.subplots()
    fig.set_figwidth(figure_width)
    fig.set_figheight(figure_height)
    ax.grid(linestyle="-.")
    
    ws_thread = Thread(target=setup_ws_server)
    ws_thread.daemon = True
    ws_thread.start()
    debug(f"waiting for client to connect, ws_port={ws_port}.")
    run_main_loop()