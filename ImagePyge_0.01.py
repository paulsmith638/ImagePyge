#adapted from http://eli.thegreenplace.net/files/prog_code/wx_mpl_bars.py.txt
import os
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import ReadImage
import SubImage
import Panels
import numpy as np
#old imports from previous versions
#from pylab import *
#from scipy import ndimage
#from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
#import Grid


class MasterGUI(wx.Frame):
    """ The main frame of the application
    overrides wx.Frame - fixed size""" 
    title = 'Image Viewer/Quantification (ImagePyge) Beta'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title,size=(1200,750))
#        self.SetMaxSize((1200,1200))
        #accelerator table for keyboard shortcuts
        #lurd -> 314,315,316, 317 etc.
        self.Bind(wx.EVT_MENU,self.on_keypress,id=9314)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=9315)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=9316)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=9317)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=8314)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=8315)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=8316)
        self.Bind(wx.EVT_MENU,self.on_keypress,id=8317)
        self.accel_table = wx.AcceleratorTable([(wx.ACCEL_NORMAL,314,9314),
                                                (wx.ACCEL_NORMAL,315,9315),
                                                (wx.ACCEL_NORMAL,316,9316),
                                                (wx.ACCEL_NORMAL,317,9317),
                                                (wx.ACCEL_NORMAL,328,8314),
                                                (wx.ACCEL_NORMAL,332,8315),
                                                (wx.ACCEL_NORMAL,330,8316),
                                                (wx.ACCEL_NORMAL,326,8317),
                                                ])
        self.SetAcceleratorTable(self.accel_table)

        self.splash = np.ones([100,100],dtype=np.uint16)
        self.image = self.splash
        self.info = {"use_psl":False}
        self.get_image_stats()
        #setup master panel here, all objects are children
        self.master_panel = wx.Panel(self)
        self.create_master_layout()
        #initialize image parameters
        self.display_params = dict([
                ('color_map','Greys'),
                ('lum_min',None),
                ('lum_max',None),
                ('alpha',100)])
        # a list to be populated later
        self.si_data = []
        self.draw_figure()

    def create_menu(self):
        #std application menus (file,edit,help)
        self.menubar = wx.MenuBar()
        file_submenu = wx.Menu()
        open_fuji = file_submenu.Append(2001, "Open FUJI via .inf", "Open a FUJI ISAC .inf file")
        open_img = file_submenu.Append(2002, "Open a PNG/BMP/TIFF Image", "Open a PNG/BMP/TIFF image")

        menu_file = wx.Menu()
        menu_file.AppendMenu(-1,'Open Image File',file_submenu)
    
        self.Bind(wx.EVT_MENU, self.on_open, open_fuji)
        self.Bind(wx.EVT_MENU, self.on_open, open_img)
        menu_file.AppendSeparator()

        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()

        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        
        menu_edit=wx.Menu()
        m_copy = menu_edit.Append(-1, "&Copy Data\tCtrl-C", "Copy All Data")
        self.Bind(wx.EVT_MENU, self.on_copy,m_copy)

        menu_help = wx.Menu()
        m_help = menu_help.Append(-1, "&Help\tF1", "Program Help/Doc")
        self.Bind(wx.EVT_MENU, self.on_help, m_help)
        
        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_edit, "&Edit")
        self.menubar.Append(menu_help, "&Help")
        self.SetMenuBar(self.menubar)

    def create_panel_1(self):
        #main image panel, wx.Panel to which Figure/Canvass are added
        self.patches = []
        self.image_panel = Panels.ImagePanel(self.master_panel)
        #provide a local pointer to the axis for matplotlib edits
        self.axes = self.image_panel.axes
        self.canvas = self.image_panel.canvas
        

    def create_panel_2(self):
        #the subimage list/action panel - grid and lots of buttons
        self.si_panel = Panels.SIlistPanel(self.master_panel)
        self.grid = self.si_panel.grid
        self.si_button_list = self.si_panel.si_button_list
        self.Bind(wx.EVT_BUTTON, self.on_copy, self.si_panel.copy_but)

    def create_panel_3(self):
        #Creates the image manipulation tools (rotate, crop, etc.)
        self.button_panel = Panels.ButtonPanel(self.master_panel)
        #buttons for image manipulation
        self.Bind(wx.EVT_BUTTON, self.on_rot90, self.button_panel.rot90)
        self.Bind(wx.EVT_BUTTON, self.on_rot90neg, self.button_panel.rot90neg)
        self.Bind(wx.EVT_BUTTON, self.on_flipHoriz, self.button_panel.flipHoriz)
        self.Bind(wx.EVT_BUTTON, self.on_flipVert, self.button_panel.flipVert)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_crop, self.button_panel.cropbut)

        #buttons for subimage/peak manipulation
        self.Bind(wx.EVT_BUTTON, self.on_duplicate, self.button_panel.duplicate)
        self.Bind(wx.EVT_BUTTON, self.on_delete, self.button_panel.delete)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_crop, self.button_panel.cropbut)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_move, self.button_panel.move)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_resize, self.button_panel.resize)

        self.Bind(wx.EVT_BUTTON, self.on_select_all, self.button_panel.select_all)
        self.Bind(wx.EVT_BUTTON, self.on_select_none, self.button_panel.select_none)
        self.Bind(wx.EVT_BUTTON, self.on_bck_corr, self.button_panel.background)
        self.Bind(wx.EVT_BUTTON, self.on_uniform, self.button_panel.uniform)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.button_panel.refresh)
        self.Bind(wx.EVT_BUTTON, self.on_byteswap, self.button_panel.byteswap)


    def create_panel_4(self):
        #Creates the image control panel, sliders, color pickers etc.
        self.control_panel = Panels.ControlPanel(self.master_panel)
        self.Bind(wx.EVT_COMBOBOX,self.on_select_scheme,self.control_panel.color_scheme)
        self.Bind(wx.EVT_SLIDER, self.image_update)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_line_color,self.control_panel.color_pick)
        self.control_panel.color_pick.SetColour('#FF0000')

    def create_master_layout(self):
        self.create_menu()
        self.create_status_bar()
        self.create_panel_1()
        self.create_panel_2()
        self.create_panel_3()
        self.create_panel_4()

        
        #
        # Layout (each panel is currently fixed size and position
        # --perhaps switch to sizers later
        ##########################################
        # (1)         -(2)    -
        #             -       -
        #             -       -
        #             -       -
        #             -       -
        #             -       -
        #             -       -
        #----------------------
        #(3)          -(4)    -
        #----------------------
#didn't work so well, allowed panels to have irregular sizes
#TODO - redesign with proper boxsizers
#        self.master_sizer.Add(self.image_panel,pos=(0,0),span=(15,15))
#        self.master_sizer.Add(self.si_panel, pos=(0,15),span=(12,5))
#        self.master_sizer.Add(self.button_panel, pos=(15,0),span=(5,15))
#        self.master_sizer.Add(self.control_panel, pos=(12,15),span=(5,8))
#        self.master_sizer.Layout()
#        self.master_sizer.Fit(self)



    def create_status_bar(self):
        #canned method for status bar at the bottom, not much implemented
        self.statusbar = self.CreateStatusBar()


# IMAGE related functions:
    def get_image_stats(self):
        #gets array info once image has been read in
        self.image_stats = dict([
                ('mean',self.image.mean()),
                ('max',self.image.max()),
                ('min',self.image.min())])


    def reset_sliders(self):
        # if image changes (eg cropped) reset the sliders to the new dynamic ranges
        self.control_panel.vmax_slider.SetRange(0,self.image_stats['max'])
        self.control_panel.vmin_slider.SetRange(0,self.image_stats['max'])
        self.control_panel.vmax_slider.SetValue(self.image_stats['max'])
        self.control_panel.vmin_slider.SetValue(0)
#        self.control_panel.alpha_slider.SetRange(0,100)

    def image_update(self,event):
        #called for image adjust events (sliders, colors, etc)
        self.get_image_stats()
        self.display_params['lum_max'] = self.control_panel.vmax_slider.GetValue()
        self.display_params['lum_min'] = self.control_panel.vmin_slider.GetValue()
#        self.display_params['alpha'] =   self.control_panel.alpha_slider.GetValue()
        self.draw_figure()

    def draw_figure(self):
        #redraws the figure after an operation (called alot)
        self.axes.clear()
        #the actual image display
        self.axes.imshow(self.image,interpolation='bilinear',
                         cmap=self.display_params['color_map'], 
                         vmin=self.display_params['lum_min'],
                         vmax=self.display_params['lum_max'],
#                         alpha=int(self.display_params['alpha']/20),
                         norm=None)
        self.toggle_selector = RectangleSelector(self.axes, self.on_rect_select, drawtype='box')
        #draw patches
        if len(self.si_data) > 0:
            #returns an rgba tuple, converted to 0-1 range for matplotlib
            patch_color = self.control_panel.color_pick.GetColour()
            #default color is red, but doesn't always regester as type color, so catch wrong types
            if not isinstance(patch_color,wx.Colour):
                patch_color = wx.Colour(255,0,0)
            color_tuple = (float(patch_color.Red())/256,float(patch_color.Green())/256,float(patch_color.Blue())/256)
            linewidth = self.control_panel.si_size_slider.GetValue()
            for subim in self.si_data:
                patch  = subim.patch
                number = subim.number
                selected = subim.selected
                patch.set_linewidth(linewidth)
                if selected:
                    patch.set_linestyle('dotted')
                else:
                    patch.set_linestyle(None)
                patch.set_color(color_tuple)
                patch.set_antialiased(True)
                instance = self.axes.add_patch(patch)
                #create the matplotlib text artist here
                label = matplotlib.text.Text(x=subim.xcoord,y=subim.ycoord-2,text=number)
                label.set_color(color_tuple)
                label.set_weight('bold')
                
                self.axes.add_artist(label)
                
        self.canvas.draw()    

    def on_rect_select(self,eclick,erelease):
          x,y = eclick.xdata,eclick.ydata
          width,height = abs(erelease.xdata - eclick.xdata), abs(erelease.ydata - eclick.ydata)
          rectangle = matplotlib.patches.Rectangle((x,y),width,height,fill=False,label="box",antialiased=True)
          # are we cropping?
          if self.button_panel.cropbut.GetValue() == True:
              self.axes.add_patch(rectangle)
              self.canvas.draw()
              confirm = wx.MessageDialog(self,
                                         "Crop to current selection?",
                                         "Crop?", wx.YES_NO)
              result = confirm.ShowModal()
              confirm.Destroy()
              self.button_panel.cropbut.SetValue(False)
              self.button_panel.txt_ins.SetLabel("\tUse the Mouse to select peaks/areas for quantitation")
              if result == wx.ID_YES:
                  self.image = self.image[int(y):int(y+height),int(x):int(x+width)]   
                  self.image_update(None)
                  self.si_list = []
                  self.patches = []
                  self.update_si_list()
                  self.draw_figure()
          # if not a crop, new selection
          else:
              si_number = len(self.si_data) + 1
              self.patches.append((si_number,rectangle))
              subim = SubImage.SubImage(self.si_panel,self.image,rectangle,si_number) 
              subim.selected = False
              self.si_data.append((subim))
              self.update_si_list()

    def update_si_list(self):
        #clear old stuff
        self.si_button_list.DeleteWindows()
        if len(self.si_data) > 0:
            new_sizer = None
            new_sizer = wx.BoxSizer(wx.VERTICAL)
            for subim in self.si_data:
                #gui_entry is a BoxSizer full of buttons
                #they must have the scrollwindow as their parent
                gui_entry = subim.new_gui(self.si_panel.scroll)
                new_sizer.Add(gui_entry,-1,border=0,flag=wx.ALIGN_LEFT|wx.FIXED_MINSIZE)
                self.master_panel.Bind(wx.EVT_TOGGLEBUTTON, self.on_select, subim.select,id=subim.number)
                self.master_panel.Bind(wx.EVT_BUTTON, subim.on_display, subim.display,id=subim.number)
                self.master_panel.Bind(wx.EVT_TOGGLEBUTTON, self.on_select_and_kill, subim.delete,id=subim.number+1000)
                if subim.selected:
                    subim.select.SetValue(True)
                #grid editing
                self.make_grid(self.grid.myGrid)
            self.si_button_list.Add(new_sizer,-1)
            self.canvas.draw()
#            self.si_panel.Layout()
            self.si_panel.scroll_update()
        else:
            self.make_grid(self.grid.myGrid)
            
        self.draw_figure()


    def make_grid(self,grid):
        if grid.GetNumberRows() > 0:
            grid.DeleteRows(0,grid.GetNumberRows())
        for subim in self.si_data:
            grid.AppendRows(numRows=1)
            grid.SetCellValue(subim.number-1,0,str(subim.number))
            grid.SetCellValue(subim.number-1,1,str(subim.area()))
            grid.SetCellValue(subim.number-1,2,str(int(subim.px_count()/1000)))
            grid.SetCellValue(subim.number-1,3,str(int((subim.px_count() - subim.px_bck*subim.area())/1000)))
            grid.SetCellValue(subim.number-1,4,str(int(subim.psl(self.info))))
            grid.SetCellValue(subim.number-1,5,str(int(subim.psl(self.info) - subim.psl_bck*subim.area())))

    def on_select_scheme(self, event):
        self.display_params['color_map'] = matplotlib.cm.get_cmap(event.GetString())
        self.draw_figure()

    def on_line_color(self,event):
        self.draw_figure()

    def on_rot90(self, event):
        self.image = np.rot90(self.image,3)
        self.si_list = []
        self.patches = []
        self.update_si_list()
        self.draw_figure()

    def on_rot90neg(self, event):
        self.image = np.rot90(self.image,1)
        self.si_list = []
        self.patches = []
        self.update_si_list()
        self.draw_figure()

    def on_flipHoriz(self, event):
        self.image = np.fliplr(self.image)
        self.si_list = []
        self.patches = []
        self.update_si_list()
        self.draw_figure()

    def on_flipVert(self, event):
        self.image = np.flipud(self.image)
        self.si_list = []
        self.patches = []
        self.update_si_list()
        self.draw_figure()

    def on_crop(self, event):
        #just the button/message event - cropping is handled by the rectangle select function 
        if self.button_panel.cropbut.GetValue():
            self.crop_image = True
            self.button_panel.txt_ins.SetLabel("\tUse the mouse to select an area to crop to (with confirmation)")
        else:
            self.crop_image = False
            self.button_panel.txt_ins.SetLabel("\tUse the Mouse to select peaks/areas for quantitation")
        self.button_panel.Layout()
    
    def on_copy(self,event):
        self.grid.copy()

    def on_bck_corr(self,event):
        choices = []
        for si in self.si_data:
            if si.area() > 0:
                choices.append(str("Box: "+str(si.number)+" Background: "+str(int(si.px_count()/si.area()))))
        choices.append(str("NONE:_USE_NO_CORRECTION "+ str(0)))
        dlg = wx.SingleChoiceDialog(self, "Pick a selection for background correction:\n"
                                          "The mean signal per pixel in this selection\n"
                                          "will be used to correct all selections.",
                                    'Background Selection', choices, wx.CHOICEDLG_STYLE)
        dlg.ShowModal()
        response =  dlg.GetStringSelection()
        sel = response.split(' ')[1]
        dlg.Destroy()
        pick = next((si for si in self.si_data if si.number == int(sel)), None)
        if pick: 
            if pick.area() != 0:
                px_background = pick.px_count()/pick.area()
                psl_background = pick.psl(self.info)/pick.area()
        else:
            px_background = 0
            psl_background = 0
        for si in self.si_data:
            si.px_bck = px_background
            si.psl_bck = psl_background
        self.make_grid(self.grid.myGrid)
        self.update_si_list()
        self.draw_figure()


    def on_uniform(self,event):
        choices = []
        for si in self.si_data:
            choices.append(str(si.number))
        selected = self.get_selected()
        if len(selected) == 0:
            dlg=wx.MessageDialog(self,'No selections! Please select boxes for formatting!','ERROR: None Selected!',wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.SingleChoiceDialog(self, 'Pick a selection for sizing all boxes:', 
                                    'Make Selections Uniform?', choices, wx.CHOICEDLG_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                sel =  dlg.GetStringSelection()
                dlg.Destroy()
                pick = next((si for si in selected if si.number == int(sel)), None)
                height,width = pick.height,pick.width
                for si in selected:
                    si.on_resize(None,new_hw = (height,width))
                self.draw_figure()



    def on_select(self,event):
        button_id = event.GetId()
        choice = event.GetEventObject().GetValue()                
        for subimage in self.si_data:
            if subimage.number == button_id:
                subimage.selected = choice
        self.draw_figure()


    def on_select_all(self,event):
        for subimage in self.si_data:
            subimage.selected = True
            subimage.select.SetValue(True)
        self.draw_figure()

    def on_select_none(self,event):
        for subimage in self.si_data:
            subimage.selected = False
            subimage.select.SetValue(False)
        self.draw_figure()

    def on_delete(self,event):
        #I have no idea why this loop is needed
        #perhaps some delay, call 10 times to be sure all elements are killed!
        for i in np.arange(0,10,1):
            for i,subim in enumerate(self.si_data):
                if subim.selected == True | subim.select.GetValue() == True:
                    del self.si_data[i]
        self.renumber_si()
        self.update_si_list()

    def on_select_and_kill(self,event):
        #kill/delete button id's are augmented by 1000
        si_number = event.GetId()-1000
        for subimage in self.si_data:
            if subimage.number == si_number:
                self.si_data.remove(subimage)
        self.renumber_si()
        self.update_si_list()

    def renumber_si(self):
        sorted_list = sorted(self.si_data,key=SubImage.SubImage.return_number)
        for n,subimage in enumerate(sorted_list):
            subimage.set_number(n+1)


    def on_move(self,event):
        #just update txt, actual work is done by keypress handler
        if self.button_panel.move.GetValue():
            self.button_panel.resize.SetValue(False)
            self.button_panel.txt_ins.SetLabel("\tMove Selected Boxes with the keypad (WARNING -> SLOW!)")
        else:
            self.button_panel.txt_ins.SetLabel("\tUse the Mouse to select peaks/areas for quantitaion")

    def on_resize(self,event):
        #just update txt, actual work is done by keypress handler
        if self.button_panel.resize.GetValue():
            self.button_panel.move.SetValue(False)
            self.button_panel.txt_ins.SetLabel("\tResize Selected Boxes with the keypad (WARNING -> SLOW!)")
        else:
            self.button_panel.txt_ins.SetLabel("\tUse the Mouse to select peaks/areas for quantitaion")


    def on_refresh(self,event):
        #just in case something isn't updated?
        self.renumber_si()
        self.update_si_list()
        self.image_update(event)
        self.reset_sliders()
        self.make_grid(self.grid.myGrid)
        self.draw_figure()

    def on_keypress(self,event):
        # handle all keypress events
        key = event.GetId()
        #pass events to move if 'move' is pressed
        if self.button_panel.move.GetValue():
            si_list = self.get_selected()
            if len(si_list) > 0:
                for si in si_list:
                    SubImage.SubImage.on_move(si,key,shift=False)
                    self.draw_figure()
        #pass events to move if 'resize' is pressed
        if self.button_panel.resize.GetValue():
            si_list = self.get_selected()
            if len(si_list) > 0:
                for si in si_list:
                    SubImage.SubImage.on_resize(si,key,shift=False)
                    self.draw_figure()
                
    def get_selected(self):
        #return a sublist of selected subimage instances for moving/resizing/deleting/etc
        si_list = []
        for subimage in self.si_data:
            if subimage.selected == True:
                si_list.append(subimage)
        return si_list


    def on_duplicate(self,event):
        si_list = self.get_selected()
        if len(si_list) > 0:
            for si in si_list:
                si_number = len(self.si_data) + 1
                orig_pos = (si.xcoord,si.ycoord)
                height,width = si.height,si.width
                new_pos = (orig_pos[0]+20,orig_pos[1]+20)
                rectangle = matplotlib.patches.Rectangle(new_pos,width,height,fill=False,label="box",antialiased=True)                
                new_subim = SubImage.SubImage(self.si_panel,self.image,rectangle,si_number) 
                si.selected=False
                new_subim.selected=True
                self.si_data.append((new_subim))
                self.update_si_list()

    def on_save_plot(self, event):
        #std matplotlib output with patches
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=300)

        
    def on_byteswap(self,event):
        #raw image endianness issues, allow byte swapping for 16bit unsigned raw ISAC
        try:
            self.image.byteswap(True)
            self.draw_figure()
        except:
            pass

    def on_exit(self, event):
        self.Destroy()

    def on_open(self, event):
        id = event.GetId()
        if id == 2001:
            dialog = wx.FileDialog(self,message="Open FUJI ISAC Image", defaultDir=os.getcwd(),
                               defaultFile="test.inf", wildcard="INF (*.inf)|*.inf",
                               style=wx.OPEN)
            if dialog.ShowModal() == wx.ID_OK:
                filename = dialog.GetPaths()[0]
                self.image_obj = ReadImage.read_fuji(filename) 
        if id == 2002:
            dialog = wx.FileDialog(self,message="Open Other Image", defaultDir=os.getcwd(),
                               defaultFile="",
                               style=wx.OPEN)
            if dialog.ShowModal() == wx.ID_OK:
                filename = dialog.GetPaths()[0]
                self.image_obj = ReadImage.read_image(filename) 
        self.image = self.image_obj["image"]
        self.info = self.image_obj["info"]
        self.get_image_stats()
        self.reset_sliders()
        self.si_data = []
        self.draw_figure()


    def on_help(self, event):
        dialog = wx.Dialog(self,-1,size=(600,600),style=wx.DEFAULT_DIALOG_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        textwin = wx.TextCtrl(dialog,-1,size=(600,600),style=wx.TE_MULTILINE|
                              wx.TE_PROCESS_ENTER|
                              wx.RAISED_BORDER|wx.VSCROLL)
        if textwin.LoadFile('./README.txt',0):
            pass
        else:
            textwin.WriteText("OOPS, can't find README.txt, see source files")
        sizer.Add(textwin,-1,flag=wx.EXPAND)
        dialog.SetSizer(sizer)
        dialog.ShowModal()


if __name__ == '__main__':
    app = wx.App()
    app.frame = MasterGUI()
    app.frame.Show()
# uncomment for gui inspection window
#    import wx.lib.inspection
#    wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()

