#!/usr/bin/env python

from numpy import *
import pylab
from PIL import Image 

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
	def map_colours(self, input, start, end, adjustment=lambda x:x):
		rs,gs,bs,als = start
		re,ge,be,ale = end
		ratio = input/self.maxit
		return  (ratio *(rs-re) + re) \
		    +  (ratio * (gs-ge) + ge) * 0x100 \
		    + (ratio*(bs-be) + be) * 0x10000 \
		    +  (ratio*(als-ale) + ale) * 0x1000000
		    
	def as_PIL_image(self, width=200, height=200, mode="iteration"):
		data = self.newtons_method(self.make_grid(width, height), mode)
		map = zeros(data.shape, uint32)
		map = self.map_colours(data, [0xaa,0x33,0xff,0x88], [0xff,0xff,0,0xff])
		img = Image.fromarray(map, 'RGBA')
		print data
		print map
		return img

if __name__ == '__main__':
	new = NewtonFractal(lambda z:z**4 - 1, lambda z:4*z**3)
#	new.show_fractal()
	im = new.as_PIL_image()
	im.save("/home/ben/testimage123.png")
#	print "%X" % new.map_colours(15, [0xff,0,0,0xff], [0x00,0,0,0xff])
#	print "%X" % new.map_colours(30, [0xff, 0,0,0xff], [0x00,0,0,0xff])
'''def newton( h,w, function, derivative, maxit=10 ):
        ''Returns an image of the Newton fractal of size (h,w).
        ''
        y,x = ogrid[ -3.0:3.0:h*1j, -3.0:3.0:w*1j ] # make a grid
#y,x = ogrid[ -1.4:1.4:h*1j, -2:0.8:w*1j ] # make a grid	
	z = x+y*1j # convert to array of complex
        divtime = maxit + zeros(z.shape, dtype=int) # colour!
        #print z
	#get the result
	#result = newtons_method(z, function, derivative, the_roots)
	#divtime = process_result(result, the_roots)
	#print divtime
        #return divtime
	return newtons_method(z, function, derivative, the_roots, count_iters = True)

def process_result(result, roots):
	return roots.searchsorted(result)

def newtons_method(guess, function, derivative, roots, maxit = 20, count_iters = False):
	z = guess
	if count_iters:
		iters = zeros(z.shape, dtype=int)
		last = z.copy()
	rootind = array(xrange(len(roots)))
	print roots
	for i in xrange(maxit):
		z = z - function(z)/derivative(z)
		if count_iters:
			iters[not_equal(z, last)] = i
			last = z.copy()
	if not count_iters:
		return z
	else:
		return iters

def convert_to_color(input):
	return input * 0x22002200 + 0xff

roots = array([0+1j, 0-1j, 1, -1], dtype=complex)
#func, deri = lambda x:x**4 - 1, lambda x: 4*x**3
#func, deri = sin, cos
#func, deri = lambda z: z**5 - 3j*z**3 - (5 + 2j) * z**2, lambda z: 5*z**4 - 9j*z**2 - (5+2j)*2*z
func, deri = lambda z:z**3 - 2*z + 2, lambda z:3*z**2 - 2
#pylab.imshow(newton(2500, 2500, func, deri, roots), cmap=pylab.get_cmap('hot'))
#pylab.savefig('/home/ben/Fig1.png', dpi=500)
#pylab.hot()
#pylab.show()
img = Image.fromarray(convert_to_color(newton(2500, 2500, func, deri, roots)), 'RGBA')
img.save("/home/ben/pilimage.png")
'''
