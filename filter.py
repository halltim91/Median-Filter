'''
Timothy Hall
CS410 Computational Photography
Median Filtering in Constant Time

Based on paper at http://nomis80.org/ctmf.pdf


To Run:
	py filter.py
	* To filter an image, just set IMAGE_PATH and RADIUS and run as is.
		* Image should be in same folder as script
	* To run bench mark test, uncomment benchmark test and comment out image filtering code
	

'''
from PIL import Image
import random as rand
import time


BLANK = (0,0,0,0)


def naieve_median_filter(image, radius=5):
	'''
	Calculates median filter using naieve method. Very slow
		param: image (ImageFile): Input image
		param: radius (int): Kernal radius
		return: [(int, int, int, int),]: output image pixel array
	'''	
	l = (radius * 2)**2
	w, h = image.size
	pixels = image.load()
	H = []
	#Y = [[()] * w for _ in range(h)]
	Y = []
	for i in range(h):
		for j in range(w):
			for k in range(-radius, radius):
				if i + k < 0 or i + k > h - 1: # pad row if out of bounds
					for c in range(radius * 2):
						H.append(BLANK) 
				else:
					if j + k < 0 or j + k > w - 1: #pad if col out of bounds
						H.append(BLANK)
					else:
						for z in range(-radius, radius):
							if j + z > 0 and j + z < w -1:
								H.append(pixels[j + z, i + k])
							else:
								H.append(BLANK)
			H = sorted(H)
			Y.append(H[l // 2])
			H.clear()
	return Y

def huangs_median_filter(image, radius=3):
	'''
		Calculates median filter using Huang method (O(n))
			param: image (ImageFile): Input image
			param: radius (int): Kernal radius
			return: [(int, int, int, int),]: output image pixel array
	'''
	l = radius * 2 + 1
	w,h = image.size
	pixels = image.load()
	H = []
	# initialize Histogram
	for _ in range(l):
		H.append([BLANK for _ in range(l)])
	Y = []
	for i in range(h):
		for j in range(w):
			H.pop(0)
			H.append([])
			for k in range(-radius, radius):
				if  j + radius > w - 1:
					for i in range(l):
						H[-1].append(BLANK)
					break
				if i + k < 0 or i + k > h - 1:
					H[-1].append(BLANK)
				else:
					H[-1].append(pixels[j + radius, i + k])
			Y.append(median(H))
	return Y
			

def constant_median_filter(image, radius=3):
	'''
		Calculates median filter using constant time method
			param: image (ImageFile): Input image
			param: radius (int): Kernal radius
			return: [(int, int, int, int),]: output image pixel array
	'''
	dim = 2 * radius + 1
	width, height = image.size
	pixels = image.load()
	H = [] # Kernal
	h = [[] for _ in range(width)] # column histograms
	Y = [] # output pixel array
	# 'prime' the column histograms
	for c in h:
		for _ in range(radius):
			c.append(BLANK)
	for i in range(radius+1):
		for j in range(width):
			h[j].append(pixels[j, i])

	for i in range(height):
		for j in range(width):
			add = i + radius < height - 1
			# Update H
			if j == 0:
				# update col histograms for first radius + 1 cols					 
				for x in range(radius + 1):
					h[x].pop(0)
					if add:
						h[x].append(pixels[x, i + radius])
					else:
						h[x].append(BLANK)
					pushCol(H, h[x], dim)
			else:					
				if j + radius < width:	# not close to edge
					h[j + radius].pop(0)
					if add:
						h[j + radius].append(pixels[j + radius, i + radius])
					else:
						h[j + radius].append(BLANK)
					pushCol(H, h[j + radius], dim)
				else:
					H.pop(0)
			Y.append(median(H))
	return Y

def pushCol(H, h, l):
	''' 
		appends new col to H, removes left most column if necessary
			param: H ([[(int, int, int, int)],]): Kernel
			param: h ([(int, int, int, int),]):   column histogram being added to kernel
			param: l (int): the size of the kernal (2r + 1)
	'''
	H.append(h)
	if len(H) == l:
		H.pop(0)

def median(H):
	''' 
		Find the median of kernal
			param: H ([[(int, int, int, int),]]): kernal
			return: (int): median value
	'''
	if len(H) == 0:
		return None
	tmp = []
	for r in H:
		tmp.extend(r)
	tmp.sort()
	return tmp[len(tmp) // 2]

def benchmark(func,image, niter, radi):
	'''
		Runs an algorithm for specified iterations for each radi. Times each run and finds average run time
			param: func (function *): function being benchmarked
			param: image (ImageFile): image to be filtered
			param: niter (int): number of iterations to test
			param: radi (int[]): radi to be tested
			return: (float[]): average run time for each radius in radi
	'''
	results = []
	for r in radi:
		print(f'Testing {r}: ',end='', flush=True)
		dur = 0
		for i in range(niter):
			start = time.perf_counter()
			func(image,r)
			dur += time.perf_counter() - start
			print('.', end='', flush=True)
		results.append(dur/niter)
		print(f'avg: {results[-1]}', flush=True)	
	return results

def out_to_csv(r,h,c,n):
	'''
		Formats output to be imported as csv into excel
			param: r (int[]): radii used for testing
			param: h (float[]): average run times for Huangs method
			param: c (float[]): average run times from constant method
			param: n (float[]): average run times for naieve method
	'''
	print(f'Radius,Huang,Constant,naieve')
	for x in range(len(r)):
		print(f'{r[x]},{h[x]},{c[x]},{n[x]}')


def filter_image(img, radius, name):
	'''
		Filters an image using constant method. Saves output image
			param: img (string): filename of input image
			param: radius (int): filter radius
			param: name (string): name of output file, will be appended with radius size
	'''
	orig = Image.open(img)
	data = constant_median_filter(orig, radius)
	out = Image.new(orig.mode, orig.size)
	out.putdata(data)
	out.save(f'{name}_r{radius}.png')


if __name__ == '__main__':
	
	# FILTER SINGLE IMAGE
	IMAGE_PATH = 'test.png'
	RADIUS = 1
	filter_image(IMAGE_PATH, RADIUS, IMAGE_PATH[:-4])
	print('Done!')


	'''
	# BENCHMARK TEST
	radi = [1,2,3,4,5,6,7,8,9,10]
	niters = 55
	img = Image.open('test.png')
	huang = benchmark(huangs_median_filter, img, niters, radi)
	const = benchmark(constant_median_filter, img, niters, radi)
	naieve = benchmark(naieve_median_filter, img, niters, radi)
	out_to_csv(radi,huang,const,naieve)
	'''