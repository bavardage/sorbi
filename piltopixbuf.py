import StringIO
import PIL.Image
import gtk

def image_to_pixbuf(image):
    fd = StringIO.StringIO()
    image.save(fd, "ppm")
    contents = fd.getvalue()
    fd.close()
    loader = gtk.gdk.PixbufLoader("pnm")
    loader.write(contents, len(contents))
    pixbuf = loader.get_pixbuf()
    loader.close()
    return pixbuf

'''
Sample Usage:
image = PIL.Image.open("example.png")
pixbuf = image_to_pixbuf(image)
image = gtk.Image()
image.set_from_pixbuf(pixbuf)'''
