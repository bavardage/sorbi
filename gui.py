#!/usr/bin/env python

import gtk
import gobject
import threading

from newton import NewtonFractal as Newton
from piltopixbuf import image_to_pixbuf
from numpy import *

gobject.threads_init()


def statusfunc(message):
    print "status: %s" % message

class FractalThread(threading.Thread):
    def __init__(self, parent):
        super(FractalThread, self).__init__()
        self.parent = parent
    def update_image(self):
        self.parent.img.queue_draw()
    def run(self):
        if not self.parent.newton:
            self.parent.newton = Newton(self.parent.func, self.parent.deri, status=self.parent.update_statusbar)
            self.parent.newton.colormap.adjustment = lambda x:x**0.5
        self.parent.buffer = image_to_pixbuf(self.parent.newton.as_PIL_image())
        self.parent.pixbuf_mask = self.parent.buffer.copy().render_pixmap_and_mask()
        self.parent.img.set_from_pixmap(*self.parent.pixbuf_mask)
        gobject.idle_add(self.update_image)
class GUI:
    newton = None
    pixbuf = None
    buffer = None
    dragging = False
    clickx = 0
    clicky = 0
    defaults = {'xrange': [-3.0, 3.0], 'yrange': [-3.0, 3.0]}
    def __init__(self):
        self._init_gui()
        self.update()
        self.win.show_all()
    def _init_toolbar_items(self):
        print "in init toolbar items"
        icontheme = gtk.icon_theme_get_default()
        for item in self.toolbar_items:
            print "infor"
            print item
            if(isinstance(item, str)):
                if item == 'sep':
                    self.toolbar.insert(gtk.SeparatorToolItem(), -1)
            else:	
                image = gtk.Image()
                image.set_from_pixbuf(icontheme.load_icon(item[3], 24, 0))
                toolbutton = gtk.ToolButton(icon_widget=image, label=item[0])
                toolbutton.set_tooltip_text(item[1])
                toolbutton.set_homogeneous(False); toolbutton.set_expand(False)
                toolbutton.connect("clicked", item[4])
                self.toolbar.insert(toolbutton, -1)
    def _init_toolbar(self):
        print "in init toolbar"
        self.toolbar_items = [
            ['Save As...', 'Export High Quality', 'Private', 'document-save-as', statusfunc],
            ['Reset', 'Reset fractal', 'Private', 'gtk-clear', statusfunc],
            ['Zoom in', 'Zoom in', 'Private', 'zoom-in', self.zoom_in],
            ['Zoom out', 'Zoom out', 'Private', 'zoom-out', self.zoom_out],
            ['Reset zoom', 'Reset zoom', 'Private', 'zoom-original', self.zoom_reset],
            ]
        self.toolbar = gtk.Toolbar()
        self._init_toolbar_items()
        self.toolbar.show_all()
        return self.toolbar
    def _init_gui(self):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_decorated(False)
        self.vbox = gtk.VBox()
        self.win.add(self.vbox)
        self.win.set_default_size(500, 500)
        self.win.set_title("Sorbi")
        self.win.connect("delete_event", gtk.main_quit)
        
        self.img = gtk.Image()
        self.eventbox = gtk.EventBox()
        self.eventbox.add(self.img)
        self.eventbox.connect("button-press-event", self.mouse_start_drag)
        self.eventbox.connect("button-release-event", self.mouse_end_drag)
        self.eventbox.connect("motion-notify-event", self.mouse_move_event)
        self.function_label = gtk.Label("Function: ")
        self.function_box = gtk.Entry()
        self.function_box.set_text("z**4 - 1")
        self.derivative_label = gtk.Label("Derivative: ")
        self.derivative_box = gtk.Entry()
        self.derivative_box.set_text("4*z**3")
        self.update_button = gtk.Button("Update")
        self.update_button.connect("clicked", lambda w: self.update())
        hbox = gtk.HBox()
        hbox.pack_start(self.function_label)
        hbox.pack_start(self.function_box)
        hbox.pack_start(self.derivative_label)
        hbox.pack_start(self.derivative_box)
        hbox.pack_start(self.update_button, False, False, padding=5)
        
        self.statusbar = gtk.Statusbar()
        self.messid = self.statusbar.push(1, "Ready")
        
        self.vbox.pack_start(self._init_toolbar(), False, False)
        self.vbox.pack_start(self.eventbox)
        self.vbox.pack_start(hbox, False, False, padding=10)
        #self.vbox.pack_start(self.update_button, False, False)
        self.vbox.pack_start(self.statusbar, False, False)
    def export(self):
        print "exporting"
    def update(self):
        try:
            self.func = eval("lambda z:" + self.function_box.get_text())
            self.deri = eval("lambda z:" + self.derivative_box.get_text())
        except:
            print "exception!"
            raise
        self.newton = None
        self.update_image()
    def mouse_start_drag(self, widget, event):
        self.dragging = True
        print event.x, widget.allocation.width, self.img.allocation.width
        self.clickx = event.x - (widget.allocation.width - self.img.get_pixmap()[0].get_size()[0])/2
        self.clicky = event.y - (widget.allocation.height - self.img.get_pixmap()[0].get_size()[1])/2
        print "start drag"
    def mouse_end_drag(self, widget, event):
        self.dragging = False
        self.pixbuf_mask = self.buffer.copy().render_pixmap_and_mask()
        self.img.set_from_pixmap(*self.pixbuf_mask)
        self.img.queue_draw()
        w = event.x - self.clickx - (widget.allocation.width - self.img.get_pixmap()[0].get_size()[0])/2
        h = event.y - self.clicky - (widget.allocation.height - self.img.get_pixmap()[0].get_size()[1])/2
        width, height = self.img.get_pixmap()[0].get_size()
        ywid = self.newton.yrange[1] - self.newton.yrange[0]
        xwid = self.newton.xrange[1] - self.newton.xrange[0]
        self.newton.yrange[1] -= (width - w - self.clickx)/width * ywid
        self.newton.yrange[0] += self.clickx / width * ywid
        self.newton.xrange[1] -= (height - h - self.clicky)/height * xwid
        self.newton.xrange[0] += self.clicky / height * xwid
        self.update_image()
    def mouse_move_event(self, widget, event):
        if self.dragging:
            gc = widget.window.new_gc()
            gc.set_line_attributes(3, gtk.gdk.LINE_ON_OFF_DASH,
                                   gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
            w = event.x - self.clickx - (widget.allocation.width - self.img.get_pixmap()[0].get_size()[0])/2
            h = event.y - self.clicky - (widget.allocation.height - self.img.get_pixmap()[0].get_size()[1])/2
            x,y = self.clickx, self.clicky
            if w < 0:
                x  += w
                w *= -1
            if h < 0:
                y += h
                h *= -1
            self.pixbuf_mask = self.buffer.copy().render_pixmap_and_mask()
            self.pixbuf_mask[0].draw_rectangle(gc, False, x, y, w, h)
            self.img.set_from_pixmap(*self.pixbuf_mask)
            self.img.queue_draw()
    def update_image(self):
        thr = FractalThread(self)
        thr.start()
        '''        if not self.newton:
        self.newton = Newton(self.func, self.deri, status=self.update_statusbar)
        self.newton.colormap.adjustment = lambda x:x**0.5
        self.buffer = image_to_pixbuf(self.newton.as_PIL_image())
        self.pixbuf_mask = self.buffer.copy().render_pixmap_and_mask()
        self.img.set_from_pixmap(*self.pixbuf_mask)
        #self.img.queue_draw()'''
    def zoom_out(self, event):
        if not self.newton:
            return
        self.newton.xrange *= 2
        self.newton.yrange *= 2
        self.update_image()
    def zoom_in(self, event):
        if not self.newton:
            return
        self.newton.xrange *= 0.5
        self.newton.yrange *= 0.5
        self.update_image()
    def zoom_reset(self, event):
        if not self.newton:
            return
        self.newton.set_xrange(*self.defaults['xrange'])
        self.newton.set_yrange(*self.defaults['yrange'])
        self.update_image()
    def update_statusbar(self, message):
        print "message: %s" % message
        gobject.idle_add(self.update_status_message, message)
    def update_status_message(self, message):
        self.statusbar.remove(1, self.messid)
        self.messid = self.statusbar.push(1, message)
        

if __name__ == '__main__':
    gui = GUI()
    gtk.main()
