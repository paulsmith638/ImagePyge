import wx
import wx.grid as gridlib

class MyGridPanel(wx.Panel):

    def __init__(self,parent_panel):
        """Constructor"""
        wx.Panel.__init__(self,parent=parent_panel)
        self.myGrid = gridlib.Grid(self)
        self.myGrid.CreateGrid(0, 6)
        self.myGrid.DisableDragRowSize()
        self.myGrid.SetDefaultRowSize(22,resizeExistingRows = True)
        self.myGrid.SetRowLabelSize(0)
        self.myGrid.SetColLabelSize(0)
        self.myGrid.SetColSize(0,25)
        self.myGrid.SetColSize(1,50)
        self.myGrid.SetColSize(2,60)
        self.myGrid.SetColSize(3,60)
        self.myGrid.SetColSize(4,60)
        self.myGrid.SetColSize(5,60)

#        print self.myGrid.GetRowSize(1)
 
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.myGrid, -1)
        self.SetSizer(self.sizer)
        self.sizer.FitInside(parent_panel)

#    def ClearGrid(self):
#        self.myGrid.ClearGrid()

    def copy(self):
        #self is actualy a panel with a grid
        grid = self.myGrid
        #for selecting a bit of the grid (not implemented at the moment)
#        RowTopLeft, ColTopLeft = grid.GetSelectionBlockTopLeft()[-1]
#        RowBottomRight, ColBottomRight = grid.GetSelectionBlockBottomRight()[-1]
        RowTopLeft, ColTopLeft = (0,0)
        RowBottomRight, ColBottomRight = (grid.GetNumberRows(),grid.GetNumberCols())
        rows = range(RowTopLeft, RowBottomRight)
        cols = range(ColTopLeft, ColBottomRight)
        data = '\n'.join('\t'.join(grid.GetCellValue(r, c) for c in cols) for r in rows)
        clipboard = wx.TextDataObject()
        clipboard.SetText(data)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
