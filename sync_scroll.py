import sublime, sublime_plugin
from threading import Thread, Lock
from time import sleep

# some codes are from https://github.com/djjcast/sublime-ToggleMinimapOnScroll/blob/master/ToggleMinimapOnScroll.py

prev_view_id           = None
prev_viewport_position = None
prev_viewport_extent   = None

def viewport_scrolled():
    global prev_view_id, prev_viewport_position, prev_viewport_extent
    viewport_scrolled = False
    curr_view_id = sublime.active_window().active_view().id()
    curr_viewport_position = sublime.active_window().active_view().viewport_position()
    curr_viewport_extent = sublime.active_window().active_view().viewport_extent()
    if prev_view_id == curr_view_id and curr_viewport_position != prev_viewport_position and curr_viewport_extent == prev_viewport_extent:
        viewport_scrolled = True
    prev_view_id = curr_view_id
    prev_viewport_position = curr_viewport_position
    prev_viewport_extent = curr_viewport_extent
    return viewport_scrolled

def sample_viewport():
    if viewport_scrolled():
        sync_scroll()

def sync_scroll():
    window = sublime.active_window()
    curr_view = sublime.active_window().active_view()
    curr_viewport_position = sublime.active_window().active_view().viewport_position()

    for view in window.views():
        if view.id() != curr_view.id():
            view.set_viewport_position(curr_viewport_position)

class ViewportMonitor(Thread):
    sample_period = 0.1
    running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            sublime.set_timeout(sample_viewport, 0)
            sleep(self.sample_period)

viewport_monitor = None

def start():
    global viewport_monitor
    if viewport_monitor:
        viewport_monitor.stop()
    viewport_monitor = ViewportMonitor()
    viewport_monitor.start()
    sublime.status_message('SyncScroll *started*')

def stop():
    global viewport_monitor
    if viewport_monitor:
        viewport_monitor.stop()
    sublime.status_message('SyncScroll *stoped*')

def toggle():
    global viewport_monitor
    if viewport_monitor and viewport_monitor.running:
        stop()
    else:
        start()

class SyncScrollCommand(sublime_plugin.WindowCommand):
    def run(self, mode):
        if mode == 'toggle':
            toggle()
        elif mode == 'start':
            start()
        elif mode == 'stop':
            stop()
