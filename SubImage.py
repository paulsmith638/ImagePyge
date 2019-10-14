import os
import wx
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
import mpl_toolkits.mplot3d.axes3d as plot3D
import scipy.ndimage
import numpy as np
from pylab import figure
class SubImage:
    def __init__(self,parent,image_array,rectangle,number):
        self.parent_panel = parent
        self.xcoord,self.ycoord = rectangle.get_xy()
        self.height,self.width = rectangle.get_height(),rectangle.get_width()
        self.subimage = image_array[int(self.ycoord):int(self.ycoord+self.height),
                                    int(self.xcoord):int(self.xcoord+self.width)]
        self.patch = rectangle
        self.number = number
        self.selected = False
        self.px_bck = 0
        self.psl_bck = 0

    def new_gui(self,guilist_panel):
        #creats a new subimage object with buttons bound to the main GUI
#        number = wx.StaticText(self.parent_panel,-1, str(self.number))
 
        # 3 buttons
        self.select = wx.ToggleButton(guilist_panel,self.number,"S",size=(22,22))
        self.display = wx.Button(guilist_panel,self.number,"D",size=(22,22))
        self.delete = wx.ToggleButton(guilist_panel,self.number+1000,"X",size=(22,22))
#        properties = wx.StaticText(self.parent_panel,-1, str(np.nansum(self.subimage)))

        si_hbox = wx.BoxSizer(wx.HORIZONTAL)
#        self.parent_panel.Bind(wx.EVT_TOGGLEBUTTON, self.on_select, self.select)
        flags = wx.ALIGN_CENTER_VERTICAL
#        si_hbox.Add(number,0,border=0,flag=flags)
        si_hbox.Add(self.select,0,border=0,flag=flags)
        si_hbox.Add(self.delete,0,border=0,flag=flags)
        si_hbox.Add(self.display,0,border=0,flag=flags)
#        si_hbox.Add(properties,0,border=0,flag=flags)
        return si_hbox

    def on_select(self,event):
        if self.select.GetValue() == True:
            self.selected = True
        else:
            self.selected = False

    def on_display(self,event):
        self.fig = matplotlib.pylab.figure()
#        self.canvas = FigCanvas(self,-1,self.fig)
        self.axes = plot3D.Axes3D(self.fig)
        shape = self.subimage.shape
        X = np.arange(0,shape[1],1)
        Y = np.arange(0,shape[0],1)
        X,Y = np.meshgrid(X,Y)
        Z = self.subimage

#        print "X",X.shape
#        print "Y",Y.shape
#        print "Z",Z.shape
        self.surface = self.axes.plot_surface(X,Y,Z,rstride=5,cstride=5,linewidth=0,cmap=matplotlib.cm.coolwarm)
        matplotlib.pyplot.show()

    def px_count(self):
        return np.nansum(self.subimage)

    def psl(self,info):
        if info["use_psl"]:
            res = float(info["pix_sx"])
            sens = float(info["sensitivity"])
            lat = float(info["lattitude"])
            scale = (2**float(info["pix_bitdepth"])) -1
        # taken from BAS2500 format desctiption - http:beamline.harima.riken.jp
        # array needs to be converted to float before normalizing
            scaled_array = np.divide(np.array(self.subimage,dtype='float32'),scale)
        #actual psl function 
            psl_array = (res/100)**2 * (4000/sens) * 10**(lat*(scaled_array-0.5))
#        print res,sens,lat,scale
#        print self.subimage,scaled_array,psl_array
            return np.nansum(psl_array)
        else:
            return self.px_count()


    def area(self):
        return np.prod(self.subimage.shape)

    def return_number(self):
        return self.number

    def set_number(self,number):
        self.number = number

    def on_move(self,keypress,shift=False):
        original_image = self.parent_panel.GetGrandParent().image
        #set up reasonable increments, no less than 1px, but larger for large
        #images
        xinc = int(original_image.shape[0]/100)
        yinc = int(original_image.shape[1]/100)
        #at some point, large increments need to be suported (not currently working)
        if shift:
            xinc = xinc * 10
            yinc = yinc * 10
        start = self.patch.get_xy()
        if keypress == 9314:
            shifted = (start[0]-xinc,start[1])
            self.patch.set_xy(shifted)
        if keypress == 9315:
            shifted = (start[0],start[1]-yinc)
            self.patch.set_xy(shifted)
        if keypress == 9316:
            shifted = (start[0]+xinc,start[1])
            self.patch.set_xy(shifted)
        if keypress == 9317:
            shifted = (start[0],start[1]+yinc)
            self.patch.set_xy(shifted)

        #reset the image
        self.xcoord,self.ycoord = self.patch.get_xy()
        self.height,self.width = self.patch.get_height(),self.patch.get_width()
        self.subimage = original_image[int(self.ycoord):int(self.ycoord+self.height),
                                       int(self.xcoord):int(self.xcoord+self.width)]

    def on_resize(self,keypress,shift=False,new_hw = None):
        original_image = self.parent_panel.GetGrandParent().image
        #set up reasonable increments, no less than 1px, but larger for large
        #images
        xinc = int(original_image.shape[0]/100)
        yinc = int(original_image.shape[1]/100)
        if shift:
            xinc = xinc * 10
            yinc = yinc * 10
        start = (self.patch.get_width(),self.patch.get_height())
        if keypress == 9314:
            wshift = start[0]-xinc
            self.patch.set_width(wshift)
        if keypress == 9315:
            hshift = start[1]-yinc
            self.patch.set_height(hshift)
        if keypress == 9316:
            wshift = start[0]+xinc
            self.patch.set_width(wshift)
        if keypress == 9317:
            hshift = start[1]+yinc
            self.patch.set_height(hshift)
        if new_hw:
            self.patch.set_height(new_hw[0])
            self.patch.set_width(new_hw[1])
        #reset the image
        self.xcoord,self.ycoord = self.patch.get_xy()
        self.height,self.width = self.patch.get_height(),self.patch.get_width()
        self.subimage = original_image[int(self.ycoord):int(self.ycoord+self.height),
                                       int(self.xcoord):int(self.xcoord+self.width)]
