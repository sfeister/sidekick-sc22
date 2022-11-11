from __future__ import print_function
import binascii
import struct
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import sys
import getopt


class ColorDetector:
    def find_dominant_color(self):
        y0 = 540 - self.roi_span
        x0 = 960 - self.roi_span
        y1 = 540 + self.roi_span
        x1 = 960 + self.roi_span

        img = Image.open(self.file_name,mode='r').convert('RGB')

        NUM_CLUSTERS = self.num_of_colors

        img_crop = img.crop((x0,y0,x1,y1))
        #img_crop.save('test4.bmp')
        # Extracting the image data &
        # creating an numpy array out of it
        img_arr = np.array(img_crop)

        # Creating an image out of the previously modified array
        img = Image.fromarray(img_arr)

        ar = np.asarray(img_arr)
        shape = ar.shape
        ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

        print('finding clusters')
        codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
        print('cluster centres:\n', codes)

        vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
        counts, bins = np.histogram(vecs, len(codes))    # count occurrences

        index_max = np.argmax(counts)                    # find most frequent
        peak = codes[index_max]
        colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        print('most frequent is %s (#%s)' % (peak, colour))
        idx = 2
        val = 0
        for c in peak:
            val = val + int(c)*pow(256,idx)
            idx = idx - 1
        print(val)
        print(bytearray(int(c) for c in peak))
        return val
        # Displaying the image
        # img.show()
        del img

    def process_args(self):
        argv = sys.argv[1:]
        try:
            opts, args = getopt.getopt(argv, "r:c:f:")
        except:
            print("Error")

        for opt, arg in opts:
            if opt in ['-r']:
                self.roi_span = int(arg)
            elif opt in ['-c']:
                self.num_of_colors = int(arg)
            elif opt in ['-f']:
                self.file_name = str(arg)

    def crop_and_detect(self):
        return self.find_dominant_color()
    
    def __init__(self, update=False):
        self.roi_span = 50 
        self.num_of_colors = 3
        self.file_name = "test.bmp"
        if update == True:
           self.process_args()

def run_color_detection():
     d = ColorDetector()
     val = d.crop_and_detect()
     del d
     return val

if __name__=="__main__":
    run_color_detection()
