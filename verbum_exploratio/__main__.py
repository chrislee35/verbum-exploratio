import wx
from verbum_exploratio import VerbumExploratio

if __name__ == "__main__":
    app = wx.App(False)
    frame = VerbumExploratio()
    frame.SetSize(1300, 600)
    app.MainLoop()
