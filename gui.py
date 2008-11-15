#!/usr/bin/env python

import gtk
import gobject
import threading

from newton import NewtonFractal as Newton
from piltopixbuf import image_to_pixbuf
from numpy import *
from os.path import expanduser, join, abspath, dirname

BASEPATH = abspath(dirname(__file__))

import colormaps

gobject.threads_init()


class FractalThread(threading.Thread):
    
    def __init__(self, parent):
        super(FractalThread, self).__init__()
        self.parent = parent

    def update_image(self):
        self.parent.img.queue_draw()

    def run(self):
        try:
            gobject.idle_add(self.parent.status_busy)
            self.parent.buffer = image_to_pixbuf(self.parent.get_newton().as_PIL_image(mode=self.parent.settings['mode']))
            self.parent.pixbuf_mask = self.parent.buffer.copy().render_pixmap_and_mask()
            self.parent.img.set_from_pixmap(*self.parent.pixbuf_mask)
        except:
            raise
        finally: 
            gobject.idle_add(self.update_image)
            gobject.idle_add(self.parent.status_ok)

class GUI:
    newton = None
    pixbuf = None
    buffer = None
    dragging = False
    clickx = 0
    clicky = 0
    defaults = {'xrange': [-1.5, 1.5], 'yrange': [-1.5, 1.5]}
    settings = {'colormap': colormaps.reds, 'mode': 'iterations'}

    def __init__(self):
        self._init_gui()
        self._init_savedialog()
        self.update()
        self.win.show_all()

    def _init_toolbar_items(self):
        icontheme = gtk.icon_theme_get_default()
        for item in self.toolbar_items:
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
        self.toolbar_items = [
            ['Save As...', 'Export High Quality', 'Private', 'document-save-as', self.action_export],
        #    ['Reset', 'Reset fractal', 'Private', 'gtk-clear', statusfunc],
            ['Zoom in', 'Zoom in', 'Private', 'zoom-in', self.zoom_in],
            ['Zoom out', 'Zoom out', 'Private', 'zoom-out', self.zoom_out],
            ['Reset zoom', 'Reset zoom', 'Private', 'zoom-original', self.zoom_reset],
            ['Set Iterations', 'Set the number of iterations', 'Private', 'gtk-preferences', self.set_iterations],
            ]
        self.toolbar = gtk.Toolbar()
        self._init_toolbar_items()

        self.colormapButton = gtk.MenuToolButton(gtk.STOCK_SELECT_COLOR)
        self.colormapButton.set_label("Colormap")
        colormapMenu = gtk.Menu()
        for name,map in colormaps.index:
            item = gtk.MenuItem(name)
            item.connect("activate", self.set_colormap, map)
            item.show()
            colormapMenu.append(item)
        self.colormapButton.set_menu(colormapMenu)
        self.toolbar.insert(self.colormapButton, -1)
        
        self.modeButton = gtk.MenuToolButton(gtk.STOCK_INDEX)
        self.modeButton.set_label("Mode")
        modeMenu = gtk.Menu()
        for mode in Newton.modes:
            item = gtk.MenuItem(mode)
            item.connect("activate", self.set_mode, mode)
            item.show()
            modeMenu.append(item)
        self.modeButton.set_menu(modeMenu)
        self.toolbar.insert(self.modeButton, -1)
        
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
        
        toolbarhbox = gtk.HBox(False)
        self.progressImage = gtk.Image()
        self.progressImage.set_from_file(join(BASEPATH, 'patience_static.png'))
        self.progress_pixbuf = self.progressImage.get_pixbuf()
        self.animation = gtk.gdk.PixbufAnimation(join(BASEPATH, 'patience.gif'))
        toolbarhbox.pack_start(self.progressImage, False, False)
        toolbarhbox.pack_start(self._init_toolbar())
        
        self.vbox.pack_start(toolbarhbox, False, False)
        self.vbox.pack_start(self.eventbox)
        self.vbox.pack_start(hbox, False, False, padding=10)
        self.vbox.pack_start(self.statusbar, False, False)

    def status_busy(self):
        self.progress_pixbuf = self.progressImage.get_pixbuf()
        self.progressImage.set_from_animation(self.animation)

    def status_ok(self):
        self.progressImage.set_from_pixbuf(self.progress_pixbuf)

    def update(self):
        try:
            self.func = eval("lambda z:" + self.function_box.get_text())
            self.deri = eval("lambda z:" + self.derivative_box.get_text())
        except:
            raise
        self._init_newton(force=True)
        self.update_image()

    def mouse_start_drag(self, widget, event):
        self.dragging = True
        self.clickx = event.x - (widget.allocation.width - self.img.get_pixmap()[0].get_size()[0])/2
        self.clicky = event.y - (widget.allocation.height - self.img.get_pixmap()[0].get_size()[1])/2

    def mouse_end_drag(self, widget, event):
        '''run and hide, tbh'''
        self.dragging = False
        self.pixbuf_mask = self.buffer.copy().render_pixmap_and_mask()
        self.img.set_from_pixmap(*self.pixbuf_mask)
        self.img.queue_draw()
        w = event.x - self.clickx - (widget.allocation.width - self.img.get_pixmap()[0].get_size()[0])/2
        h = event.y - self.clicky - (widget.allocation.height - self.img.get_pixmap()[0].get_size()[1])/2
        width, height = self.img.get_pixmap()[0].get_size()
        ywid = self.get_newton().yrange[1] - self.get_newton().yrange[0]
        xwid = self.get_newton().xrange[1] - self.get_newton().xrange[0]
        self.get_newton().yrange[1] -= (width - w - self.clickx)/width * ywid
        self.get_newton().yrange[0] += self.clickx / width * ywid
        self.get_newton().xrange[1] -= (height - h - self.clicky)/height * xwid
        self.get_newton().xrange[0] += self.clicky / height * xwid
        self.update_image()

    def _init_newton(self, force = False):
        if (not self.newton) or force:
                self.newton = Newton(self.func, self.deri, status=self.update_statusbar, 
                                            colormap = self.settings['colormap'] )

    def get_newton(self):
        if not self.newton:
            self._init_newton()
        return self.newton

    def mouse_move_event(self, widget, event):
        if self.dragging:
            gc = widget.window.new_gc()
            gc.set_line_attributes(3, gtk.gdk.LINE_ON_OFF_DASH,
                                   gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
            w = event.x - self.clickx - (widget.allocation.width - self.img.get_pixmap()[0].get_size()[0])/2
            h = event.y - self.clicky - (widget.allocation.height - self.img.get_pixmap()[0].get_size()[1])/2
            x,y = self.clickx, self.clicky
            if w < 0:
                x  += w;w *= -1
            if h < 0:
                y += h; h *= -1
            self.pixbuf_mask = self.buffer.copy().render_pixmap_and_mask()
            self.pixbuf_mask[0].draw_rectangle(gc, False, x, y, w, h)
            self.img.set_from_pixmap(*self.pixbuf_mask)
            self.img.queue_draw()

    def update_image(self):
        thr = FractalThread(self)
        thr.start()

    def zoom_out(self, event):
        self.get_newton().xrange *= 2
        self.get_newton().yrange *= 2
        self.update_image()

    def zoom_in(self, event):
        self.get_newton().xrange *= 0.5
        self.get_newton().yrange *= 0.5
        self.update_image()

    def zoom_reset(self, event):
        self.get_newton().set_xrange(*self.defaults['xrange'])
        self.get_newton().set_yrange(*self.defaults['yrange'])
        self.update_image()

    def update_statusbar(self, message):
        gobject.idle_add(self.update_status_message, message)

    def update_status_message(self, message):
        self.statusbar.remove(1, self.messid)
        self.messid = self.statusbar.push(1, message)

    def _init_savedialog(self):
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        filter = gtk.FileFilter()
        filter.set_name("PNG")
        filter.add_pattern("*.png")
        self.savedialog =  gtk.FileChooserDialog("Export..",
                                                 None,gtk.FILE_CHOOSER_ACTION_SAVE,
                                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE, gtk.RESPONSE_OK))	
        self.savedialog.set_default_response(gtk.RESPONSE_OK)
        self.savedialog.add_filter(filter)
        self.savedialog.set_do_overwrite_confirmation(True)

    def action_export(self, widget, data=None):
        self.savedialog.set_current_folder(expanduser("~"))
        response = self.savedialog.run()
        if response == gtk.RESPONSE_OK:
            filename = self.savedialog.get_filename()
            t = threading.Timer(0.01, self.do_export, (filename,))
            t.start()
        self.savedialog.hide()

    def do_export(self, filename):
        #print "exporting to %s" % filename
        gobject.idle_add(self.status_busy)
        img = self.get_newton().as_PIL_image(width=1000, height=1000, mode=self.settings['mode'])
        img.save(filename+".png")
        gobject.idle_add(self.status_ok)

    def set_colormap(self, widget, map):
        self.settings['colormap'] = map
        self.get_newton().colormap = map
        print "setting map to",  map
        self.update_image()

    def responseToDialog(entry, dialog, response):
	dialog.response(response)

    def set_iterations(self, widget):
        dialog = gtk.MessageDialog(
		None,
		gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		gtk.MESSAGE_QUESTION,
		gtk.BUTTONS_OK,
		None)
	dialog.set_markup('Number of iterations:')
	entry = gtk.Entry()
        entry.set_text("%s" % self.get_newton().maxit)
	entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
	hbox = gtk.HBox()
	hbox.pack_start(gtk.Label("Iterations:"), False, 5, 5)
	hbox.pack_end(entry)
	dialog.format_secondary_markup("The more iterations, the slower the fractal rendering will be. \
If using iterations mode, as opposed to roots mode, setting this too high will result in a loss of contrast or chaotic coloring.")
	dialog.vbox.pack_end(hbox, True, True, 0)
	dialog.show_all()
	dialog.run()
	text = entry.get_text()
	dialog.destroy()
	try:
            iterations = int(text)
            if iterations > 0:
                self.get_newton().maxit = iterations
                self.update_image()
        except:
            pass

    def set_mode(self, widget, mode):
        self.settings['mode'] = mode
        self.update_image()

if __name__ == '__main__':
    gui = GUI()
    gtk.main()
