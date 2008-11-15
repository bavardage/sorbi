from numpy import *

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

class IndexedColormap:
	def __init__(self, colors):
		self.colors = array(colors, dtype=uint32)
	def map_to_color(self, input):
		return self.colors[input % len(self.colors)]

rasta=IndexedColormap([
        0xff0000ff, 0xff000088, 0xff000000, 0x008800, 
        0xff00ff00, 0xff00ff88, 0xff00ffff, 0xff0088ff,
        0xff0000ff, 0xff000088, 0xff000000,
        ])

ocean = IndexedColormap([
        0xffff0000, 0xffcc0000, 0xffaa0000,
        0xff990000, 0xff770000, 0xff550000,
        0xff330000, 0xff110000, 0xff330000,
        0xff550000, 0xff770000, 0xff990000,
        0xffaa0000, 0xffcc0000])

reds = Colormap(
    [0xff, 0xff, 0x00, 0xff],
    [0xff, 0x00, 0x0, 0xff])

blues = Colormap(
    [0xff, 0x00, 0xff, 0xff],
    [0x00, 0x00, 0xff, 0xff])

primary = IndexedColormap([
        0xffff0000, 0xff00ff00, 0xff0000ff,
        ])


index = [("Rastafarian", rasta), ("Ocean", ocean), 
         ("Reds", reds), ("Blues", blues),
         ("Primary", primary),
]
