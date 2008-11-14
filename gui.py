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
        
        self.img = gtk.DrawingArea()#gtk.Image()
        self.img.connect("expose-event", self.expose_event)
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
        hbox = gtk.HBox()
        hbox.pack_start(self.function_label)
        hbox.pack_start(self.function_box)
        hbox.pack_start(self.derivative_label)
        hbox.pack_start(self.derivative_box)
        
        self.update_button = gtk.Button("Update")
        self.update_button.connect("clicked", lambda w: self.update())
        
        self.vbox.pack_start(self._init_toolbar())
        self.vbox.pack_start(self.eventbox)
        self.vbox.pack_start(hbox)
        self.vbox.pack_start(self.update_button)
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
        self.clickx = event.x
        self.clicky = event.y
        print "start drag"
    def mouse_end_drag(self, wiget, event):
        self.dragging = False
        print "end drag"
    def mouse_move_event(self, widget, event):
        if self.dragging:
            x,y,width,height = 0,0, 100, 100
            gc = widget.window.new_gc()
            gc.set_line_attributes(3, gtk.gdk.LINE_ON_OFF_DASH,
                                   gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
            widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.pixbuf.render_pixmap_and_mask()[0], x, y, x, y, width, height)

            #self.img.set_from_pixbuf(self.pixbuf)
            w = event.x - self.clickx
            h = event.y - self.clicky
            self.img.window.draw_rectangle(gc, False, self.clickx, self.clicky, w, h)
    def expose_event(self, widget, event):
        print "Drawing"
        x , y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.pixbuf.render_pixmap_and_mask()[0], x, y, x, y, width, height)
        return False

    def update_image(self):
        if not self.newton:
            self.newton = Newton(self.func, self.deri, status=statusfunc)
        self.pixbuf = image_to_pixbuf(self.newton.as_PIL_image())
        #self.img.set_from_pixbuf(self.pixbuf)
        self.img.queue_draw()
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
