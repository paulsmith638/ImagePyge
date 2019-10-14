import os
import wx
import matplotlib
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
from scipy import ndimage
import Grid

class ImagePanel(wx.Panel):
    def __init__(self,parent_panel):
        """ Creates the main panel with all the controls on it:
            canvas for image display 
            navigation toolbar via matplotlib
            setup with boxsizer
        """
        wx.Panel.__init__(self,parent_panel,size=(800,600),pos=(0,0))
        self.panel1_box = wx.BoxSizer(wx.VERTICAL)
        
        # Create the mpl Figure and FigCanvas objects. 
        self.dpi = 100
        self.fig = Figure((8.0, 5.5), dpi=self.dpi)
        self.canvas = FigCanvas(self, -1, self.fig)
        self.toolbar = NavigationToolbar(self.canvas)
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.08, bottom=0.1, right=0.98, top=0.98,wspace=0,hspace=0)
        #list of patch objects to draw on the plot
        self.patches = []
        self.panel1_box.Add(self.toolbar,1,border=0,flag=wx.ALIGN_LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.panel1_box.Add(self.canvas,15,border=0,flag=wx.ALIGN_LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.panel1_box)
#        self.toolbar.Realize()
#        self.toolbar.update()
        self.FitInside()
        self.Layout()

class SIlistPanel(wx.Panel):
    def __init__(self,parent_panel):
        wx.Panel.__init__(self,parent_panel,size=(400,450),pos=(800,0))
        """Creats the subimage peaks list and controls panel

        ##################################
        ----text stuff------------------
        si-buttons| si_grid_list
         vbox     |  grid
         panel2   |
                  |

        everything is set to 22px to keep buttons aligned with the grid width
        """ 
        self.scroll = wx.ScrolledWindow(self,-1,size=(400,400),pos=(0,25))
        # big list of txt objects
        txt1 = wx.StaticText(self,-1,"ACTIONS",size=(65,20),pos=(0,0))
        txt2 = wx.StaticText(self,-1,"Bx",     size=(25,20),pos=(65,0))
        txt3 = wx.StaticText(self,-1,"AREA",   size=(60,20),pos=(94,0))
        txt4 = wx.StaticText(self,-1,"ABS(k)", size=(60,20),pos=(140,0))
        txt5 = wx.StaticText(self,-1,"ABS-bk", size=(60,20),pos=(200,0))
        txt6 = wx.StaticText(self,-1,"PSL",    size=(60,20),pos=(260,0))
        txt7 = wx.StaticText(self,-1,"PSL-bk", size=(60,20),pos=(320,0))



#        text = wx.StaticText(self,-1, "ACTIONS  Bx AREA      Abs(k)  AbsCor(k) PSL PSL-Corr",
#                             size=(400,22),pos=(0,0))

        self.si_button_list = wx.BoxSizer(wx.VERTICAL)

        self.grid = Grid.MyGridPanel(self.scroll)
        self.copy_but = wx.Button(self, -1, "Copy data to Clipboard",size=(400,25),pos=(0,425))

        self.split_panel = wx.BoxSizer(wx.HORIZONTAL)
        self.split_panel.Add(self.si_button_list,border=0)
        self.split_panel.Add(self.grid,1,border=0)
        self.scroll.SetSizer(self.split_panel)
        w,h = self.GetSize() 
        self.scroll.SetScrollbars(1,1,w,h)
        self.Fit()
        self.Layout()
        
    def scroll_update(self):
        #not sure if ever called?
        self.Layout()
        w,h = self.GetSize()        
        self.scroll.SetScrollbars(1,1,w,h)




class ButtonPanel(wx.Panel):
    def __init__(self,parent_panel):       
        """Creats the subimage peaks list and controls panel

        ##################################
        Grid Sizer with lots of buttons
        """ 

        wx.Panel.__init__(self,parent_panel,size=(800,150),pos=(0,600))


      #buttons for image manipulation
        self.line1     = wx.StaticText(self,-1, "  Arrange  \n  Image  ",style=wx.ALIGN_CENTER)
        self.rot90     = wx.Button(self, -1, "rot 90")
        self.rot90neg  = wx.Button(self, -1, "rot -90")
        self.flipHoriz = wx.Button(self, -1, "flip H")
        self.flipVert  = wx.Button(self, -1, "flip V")
        self.cropbut   = wx.ToggleButton(self,1,'Crop')
        self.cropbut.SetValue(False)

        self.line2     = wx.StaticText(self,-1, "  Manage  \n  Boxes  ",style=wx.ALIGN_CENTER)
        self.move      = wx.ToggleButton(self, -1, "Move")
        self.resize    = wx.ToggleButton(self, -1, "Resize")
        self.duplicate = wx.Button(self, -1, "Duplicate")
        self.delete    = wx.Button(self, -1, "Delete")
        self.background    = wx.Button(self, -1, "Bck Corr")
        self.uniform       = wx.Button(self, -1, "Uniform")
        self.refresh       = wx.Button(self, -1, "Refresh")
        self.byteswap      = wx.Button(self, -1, "Swap Bytes")

        #creates select all/none subbuttons
        self.seltxt     = wx.StaticText(self,-1, "Select:",style=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        self.select_all = wx.Button(self, -1, "All")
        self.select_none = wx.Button(self, -1, "None")

        self.cont_buttons = wx.GridBagSizer(0,0)
        self.cont_buttons.SetRows(3)
        self.cont_buttons.SetCols(10)

        #a txt widget to display messages with instruction
        self.line3   = wx.StaticText(self,-1, "INSTRUCTIONS:",style=wx.ALIGN_CENTER)
        self.txt_ins = wx.StaticText(self,-1, "\tUse the Mouse to select peaks/areas for quantitaion",
                                     style=wx.ALIGN_CENTER)

        flags = wx.EXPAND
        self.cont_buttons.Add(self.line1, (0,0),(1,2),flag=flags)
        self.cont_buttons.Add(self.rot90, (0,2),(1,1),flag=flags)
        self.cont_buttons.Add(self.rot90neg, (0,3),(1,1),flag=flags) 
        self.cont_buttons.Add(self.flipHoriz, (0,4),(1,1),flag=flags)
        self.cont_buttons.Add(self.flipVert, (0,5),(1,1),flag=flags) 
        self.cont_buttons.Add(self.cropbut, (0,6),(1,1),flag=flags) 
        self.cont_buttons.Add(self.seltxt, (0,7),(1,1),flag=flags) 
        self.cont_buttons.Add(self.select_all, (0,8),(1,1),flag=flags) 
        self.cont_buttons.Add(self.select_none, (0,9),(1,1),flag=flags) 
        


        self.cont_buttons.Add(self.line2, (1,0),(1,2),flag=flags)
        self.cont_buttons.Add(self.move, (1,2),(1,1),flag=flags) 
        self.cont_buttons.Add(self.resize, (1,3),(1,1),flag=flags)
        self.cont_buttons.Add(self.duplicate, (1,4),(1,1),flag=flags) 
        self.cont_buttons.Add(self.delete, (1,5),(1,1),flag=flags) 
        self.cont_buttons.Add(self.background, (1,6),(1,1),flag=flags) 
        self.cont_buttons.Add(self.uniform, (1,7),(1,1),flag=flags) 
        self.cont_buttons.Add(self.refresh, (1,8),(1,1),flag=flags) 
        self.cont_buttons.Add(self.byteswap, (1,9),(1,1),flag=flags) 
        self.cont_buttons.Add(self.line3,(2,0),(1,2),flag=flags)
        self.cont_buttons.Add(self.txt_ins,(2,3),(1,7),flag=flags)
        self.SetSizer(self.cont_buttons)
        self.cont_buttons.SetDimension(0,600,800,150)
        self.cont_buttons.Fit(self)
        self.cont_buttons.Layout()

        self.Fit()
        self.Layout()

class ControlPanel(wx.Panel):
    def __init__(self,parent_panel):
        """Creats the subimage peaks list and controls panel

        ##################################
        mini gui with sliders/combos/etc
        """ 
        wx.Panel.__init__(self,parent_panel,size=(400,450),pos=(800,450))

        #sliders
        self.vmax_slider = wx.Slider(self,-1,
                                     value=20,
                                     minValue=0,
                                     maxValue=20,
                                     size=(150,-1),
                                     style= wx.SL_HORIZONTAL | wx.SL_LABELS,
                                     name = 'High-Cut')
        self.vmin_slider = wx.Slider(self,-1,
                                     value=0,
                                     minValue=0,
                                     maxValue=20,
                                     size=(150,-1),
                                     style=wx.SL_HORIZONTAL | wx.SL_LABELS,
                                     name = 'Low-Cut')
#alpha slider, not implemented, bind in main bui if needed, also reset_sliders() method
#        self.alpha_slider = wx.Slider(self,-1,
#                                      value=20,
#                                      minValue=0,
#                                      maxValue=20,
#                                      size=(150,-1),
#                                      style=wx.SL_HORIZONTAL | wx.SL_LABELS ,
#                                      name = 'Alpha')

        #box linewidth slider range 1-5
        self.si_size_slider = wx.Slider(self,-1,
                                        value=2,
                                        minValue=1,
                                        maxValue=5,
                                        size=(150,-1),
                                        style=wx.SL_HORIZONTAL | wx.SL_LABELS,
                                        name ='line width')


        #color schemes
        #known in the matplotlib color namespace
        color_maps = ('Greys','Blues','Greens','Reds','cool','jet','bone','spring','summer','winter')
        self.color_scheme = wx.ComboBox(self,-1,
                                        choices=color_maps,
                                        style=wx.CB_READONLY)

        #color picker, set initially to red (bombs on osx?)
        self.color_pick = wx.ColourPickerCtrl(self,-1,col='#FF0000')

        label1 = wx.StaticText(self,-1, "  Color Scheme")
        label2 = wx.StaticText(self,-1, "  Line Color")
        label3 = wx.StaticText(self,-1, "  Line Width")
        label4 = wx.StaticText(self,-1, "  Max Cutoff")
        label5 = wx.StaticText(self,-1, "  Min Cutoff")
#        label6 = wx.StaticText(self,-1, "  Alpha")


        flags = wx.ALIGN_CENTER_HORIZONTAL | wx.FIXED_MINSIZE | wx.EXPAND

        self.main_sizer = wx.GridBagSizer(6,2)

        self.main_sizer.Add(label1,(0,0),(1,1),flag=flags)
        self.main_sizer.Add(self.color_scheme,(0,1),(1,1),flag=flags)

        self.main_sizer.Add(label2,(1,0),(1,1),flag=flags)
        self.main_sizer.Add(self.color_pick,(1,1),(1,1))

        self.main_sizer.Add(label3,(2,0),(1,1),flag=flags)
        self.main_sizer.Add(self.si_size_slider,(2,1),(1,1),flag=flags)

        self.main_sizer.Add(label4,(3,0),(1,1),flag=flags)
        self.main_sizer.Add(self.vmax_slider,(3,1),(1,1),flag=flags)

        self.main_sizer.Add(label5,(4,0),(1,1),flag=flags)
        self.main_sizer.Add(self.vmin_slider,(4,1),(1,1),flag=flags)

#        self.main_sizer.Add(label6,(5,0),(1,1),flag=flags)
#        self.main_sizer.Add(self.toolbar,(5,1),(1,1))#,flag=flags)

        self.SetSizer(self.main_sizer)
        self.Fit()
        self.Layout()



