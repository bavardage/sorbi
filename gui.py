#!/usr/bin/env python

import gtk

from newton import NewtonFractal as Newton
from piltopixbuf import image_to_pixbuf
from numpy import *

def statusfunc(message):
    print "status: %s" % message

class GUI:
    newton = None
    pixbuf = None
    dragging = False
    defaults = {'xrange': [-3.0, 3.0], 'yrange': [-3.0, 3.0]}
    def __init__(self):
        self._init_gui()
        self.update()
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
        self.img.connect("mouse-down", lambda w: self.mouse_start_drag())
        self.img.connect("mouse-up", lambda w: self.mouse_end_drag())
        self.img.connect("mouse-move-event", self.mouse_move_event)
        self.function_label = gtk.Label("Function: ")
        self.function_box = gtk.Entry()
        self.function_box.set_text("z**4 - 1")
        self.derivative_label = gtk.Label("Derivative: ")
        self.derivative_box = gtk.Entry()
        self.derivative_box.set_text("4*z**3")
        hbox = gtk.HBox()
        hbox.pack_start(self.function_label)
        hbox.pack_start(self.function_box)
        hbox.pack_start(self.derivative_label)
        hbox.pack_start(self.derivative_box)
        
        self.update_button = gtk.Button("Update")
        self.update_button.connect("clicked", lambda w: self.update())
        
        self.vbox.pack_start(self._init_toolbar())
        self.vbox.pack_start(self.img)
        self.vbox.pack_start(hbox)
        self.vbox.pack_start(self.update_button)
        
        self.win.show_all()
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
    def mouse_start_drag(self):
        self.dragging = True
    def mouse_end_drag(self):
        self.dragging = True
    def mouse_move_event(self, widget):
        gc = widget.window.new_gc()
        gc.set_line_attributes(3, gtk.gdk.LINE_ON_OFF_DASH,
                                        gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
        self.img.set_from_pixbuf(self.pixbuf)
        self.img.window.draw_rectangle(gc, True, 10, 10, 100, 100)
    def update_image(self):
        if not self.newton:
            self.newton = Newton(self.func, self.deri, status=statusfunc)
        self.pixbuf = image_to_pixbuf(self.newton.as_PIL_image())
        self.img.set_from_pixbuf(self.pixbuf)
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

if __name__ == '__main__':
    gui = GUI()
    gtk.main()
