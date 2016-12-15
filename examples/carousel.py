#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# Loosely based on poster_demo by @bjerrep
# https://github.com/bjerrep/ssd1306/blob/master/examples/poster_demo.py

import psutil

from demo_opts import device
from oled.virtual import viewport, snapshot
import hotspot.memory as memory
import hotspot.uptime as uptime
import hotspot.cpu_load as cpu_load
import hotspot.clock as clock
import hotspot.network as network
import hotspot.disk as disk


def position(max):
    forwards = range(0, max)
    backwards = range(max, 0, -1)
    while True:
        for x in forwards:
            yield x
        for x in backwards:
            yield x


def pause_every(interval, generator):
    try:
        while True:
            x = generator.next()
            if x % interval == 0:
                for _ in range(20):
                    yield x
            else:
                yield x
    except StopIteration:
        pass


def intersect(a, b):
    return list(set(a) & set(b))

def main():
    widget_width = device.width / 2
    widget_height = device.height

    # Either function or subclass
    #  cpuload = hotspot(widget_width, widget_height, cpu_load.render)
    #  cpuload = cpu_load.CPU_Load(widget_width, widget_height, interval=1.0)
    utime = snapshot(widget_width, widget_height, uptime.render, interval=1.0)
    mem = snapshot(widget_width, widget_height, memory.render, interval=2.0)
    dsk = snapshot(widget_width, widget_height, disk.render, interval=2.0)
    cpuload = snapshot(widget_width, widget_height, cpu_load.render, interval=0.5)
    clk = snapshot(widget_width, widget_height, clock.render, interval=1.0)

    network_ifs = psutil.net_if_stats().keys()
    wlan = intersect(network_ifs, ["wlan0", "wl0"])[0]
    eth = intersect(network_ifs, ["eth0", "en0"])[0]
    lo = intersect(network_ifs, ["lo", "lo0"])[0]

    net_wlan = snapshot(widget_width, widget_height, network.stats(wlan), interval=2.0)
    net_eth = snapshot(widget_width, widget_height, network.stats(eth), interval=2.0)
    net_lo = snapshot(widget_width, widget_height, network.stats(lo), interval=2.0)

    widgets = [cpuload, utime, clk, net_wlan, net_eth, net_lo, mem, dsk]

    virtual = viewport(device, width=widget_width * len(widgets), height=widget_height)
    for i, widget in enumerate(widgets):
        virtual.add_hotspot(widget, (i * widget_width, 0))

    for x in pause_every(widget_width, position(widget_width * (len(widgets) - 2))):
        virtual.set_position((x, 0))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
