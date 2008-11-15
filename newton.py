#!/usr/bin/env python

from numpy import *
import pylab
from PIL import Image 

import colormaps

class NewtonFractal:
	modes = ['iterations', 'roots']

	def __init__(self, function, derivative, maxit=30, status=None, colormap = None):
		self.function, self.derivative = function, derivative
		self.maxit = maxit
		self.xrange = array([-1.5, 1.5], dtype=float)
		self.yrange = array([-1.5, 1.5], dtype=float)
		self.status = (status if callable(status) else lambda x:x)
		self.colormap =(colormaps.reds if not colormap else colormap)

	def set_xrange(self, min, max):
		if min < max:
			self.xrange = array([min, max], dtype=float)

	def set_yrange(self, min, max):
		if min < max:
			self.yrange = array([min, max], dtype=float)

	def make_grid(self, w, h):
		y,x = ogrid[self.xrange[0]:self.xrange[1]:h*1j, \
				    self.yrange[0]:self.yrange[1]:w*1j]
		z = x+y*1j
		return z.astype(complex64)

	def newtons_method(self, guess, mode='iterations'):
		if mode not in self.modes:
			raise Exception("That is an invalid mode")
		self.status("Calculating...")
		z = guess
		if mode=='iterations':
			iters = zeros(z.shape, dtype=int)
		last = z.copy()
		mask = equal(z, last)
		for i in xrange(self.maxit):
			self.status("Iteration %i of %i" % (i, self.maxit))
			if mode == 'iterations':
				z[mask] = z[mask] - self.function(z[mask])/self.derivative(z[mask])
			else:
				z = z - self.function(z)/self.derivative(z)
			if mode=='iterations':
				iters[not_equal(z, last)] = i
			mask = not_equal(z, last)
			last = z.copy()
		self.status("... Done Calculating")
		if mode=='iterations':	
			return iters
		else:
			return z, unique(z[equal(z, last)])

	def show_fractal(self, width=200, height=200, mode="iterations"):
		data = self.newtons_method(self.make_grid(width, height), mode)
		pylab.imshow(data)
		pylab.hot()
		pylab.show()
		    
	def as_PIL_image(self, width=200, height=200, mode="iterations", dynamic_color = True):
		if mode == 'iterations':
			data = self.newtons_method(self.make_grid(width, height), mode)
		else:
			data, roots = self.newtons_method(self.make_grid(width, height), mode)
		map = zeros(data.shape, uint32)
		if mode == 'iterations':
			self.status("Mapping data to colors...")
			map = self.colormap.map_to_color(data)
			self.status("Done")
		elif mode == 'roots':
			data = roots.searchsorted(data)
			map = self.colormap.map_to_color(data)
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
