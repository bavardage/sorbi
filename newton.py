#!/usr/bin/env python

from numpy import *
import pylab
from PIL import Image 

class Colormap:
	def __init__(self, start, end, adjustment=None, max=None):
		self.start = start
		self.end = end
		self.adjustment = (adjustment if callable(adjustment) else lambda x:x)
		self.max = max
	def map_to_color(self, input):
		rs,gs,bs,als = self.start
		re,ge,be,ale = self.end
		max = (self.max if self.max else input.max())
		ratio = true_divide(input, max)
		ratio = self.adjustment(ratio)
		return  (((rs-re)*ratio + re).astype(uint32) \
		    +  ((gs-ge)*ratio + ge).astype(uint32) * 0x100 \
		    + ((bs-be)*ratio + be).astype(uint32) * 0x10000 \
		    +  ((als-ale)*ratio + ale).astype(uint32) * 0x1000000)

class NewtonFractal:
	def __init__(self, function, derivative, maxit=30):
		self.function, self.derivative = function, derivative
		self.maxit = maxit
		self.xrange = [-3, 3]
		self.yrange = [-3, 3]
	def x_range(self, min, max):
		if min < max:
			self.xrange = [min, max]
	def y_range(self, min, max):
		if min < max:
			self.yrange = [min, max]
	def make_grid(self, w, h):
		y,x = ogrid[self.xrange[0]:self.xrange[1]:h*1j, \
				    self.yrange[0]:self.yrange[1]:w*1j]
		z = x+y*1j
		return z
	def newtons_method(self, guess, mode='iteration'):
		if mode=='iteration':
			z = guess
			iters = zeros(z.shape, dtype=int)
			last = z.copy()
			for i in xrange(self.maxit):
				z = z - self.function(z)/self.derivative(z)
				iters[not_equal(z, last)] = i
				last = z.copy()
			return iters
		else:
			print "mode not supported"
	
	def show_fractal(self, width=200, height=200, mode="iteration"):
		data = self.newtons_method(self.make_grid(width, height), mode)
		pylab.imshow(data)
		pylab.hot()
		pylab.show()
		    
	def as_PIL_image(self, width=200, height=200, mode="iteration", adjustment = None, dynamic_color = True):
		data = self.newtons_method(self.make_grid(width, height), mode)
		map = zeros(data.shape, uint32)
		col = Colormap([0xaa, 0x33, 0xff, 0x88],
			       [0xff, 0xff, 0x0, 0xff],
			       adjustment = adjustment,
			       max = (self.maxit if not dynamic_color else None))
		#map = self.map_colours(data, col.start, col.end)
		map = col.map_to_color(data)
		img = Image.fromarray(map, 'RGBA')
		return img

if __name__ == '__main__':
	new = NewtonFractal(lambda z:z**4 - 1, lambda z:4*z**3)
	im = new.as_PIL_image()
	im.save("/home/ben/testimage123.png")
	new.x_range(-1,1)
	new.y_range(-1,1)
	im = new.as_PIL_image(width=1000, height=1000)
	im.save("/home/ben/testzoom.png")
