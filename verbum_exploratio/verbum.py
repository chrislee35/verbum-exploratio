#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 23:34:29 2024

@author: chris
"""
import wx
from .verbum_panel import VerbumPanel
from .wikipedia import get_wikipedia_article

class VerbumExploratio(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='Verbum Exploratio')
        self.panel = VerbumPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_file_menu_item = file_menu.Append(
            wx.ID_ANY, 'Open File',
            'Open a text file'
        )
        fetch_wikipedia_menu_item = file_menu.Append(
            wx.ID_ANY, 'Import from Wikipedia',
            'Import an article from Wikipedia'
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_open_file,
            source=open_file_menu_item,
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.import_wikipedia,
            source=fetch_wikipedia_menu_item
        )

        settings_menu = wx.Menu()
        relationship_type_menu_item = settings_menu.Append(
            wx.ID_ANY, 'Relationship Settings',
            'Configure which relationships to explore'
        )
        language_menu_item = settings_menu.Append(
            wx.ID_ANY, 'Language',
            'Select the language of the shown document'
        )
        menu_bar.Append(settings_menu, '&Preferences')
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.configure_relationships,
            source=relationship_type_menu_item
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.configure_language,
            source=language_menu_item
        )

        self.SetMenuBar(menu_bar)

    def on_open_file(self, event):
        title = "Choose a text file:"
        dlg = wx.FileDialog(self, title, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.panel.update_text_file(dlg.GetPath())
        dlg.Destroy()

    def import_wikipedia(self, event):
        title = "Import an article from Wikipedia:"
        dlg = wx.TextEntryDialog(self,
             'Which article title? e.g., en:Yulia_Lipnitskaya',
             caption=title,
             value="",
             style=wx.OK | wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            article = dlg.GetValue()
            lang = 'en'
            if ':' in article:
                lang, article = article.split(':', 1)
            page = get_wikipedia_article(article)
            self.panel.set_text(page)
        dlg.Destroy()

    def configure_relationships(self, event):
        pass

    def configure_language(self, event):
        pass
