#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 23:34:29 2024

@author: chris
"""
import wx
from .verbum_panel import VerbumPanel
from .wikipedia import get_wikipedia_article
from .etymology import Etymology

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
        quit_menu_item = file_menu.Append(
            wx.ID_ANY, 'E&xit\tCtrl+X', 'Exit the program',
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
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.onExit,
            source=quit_menu_item,
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
        ignore_language_menu_item = settings_menu.Append(
            wx.ID_ANY, 'Ignore Language',
            'Select a language to ignore relationships with'
        )
        increase_font_size_menu_item = settings_menu.Append(
            wx.ID_ANY, 'Increase Font Size\tCtrl++', 'Increases the font size'
        )
        decrease_font_size_menu_item = settings_menu.Append(
            wx.ID_ANY, 'Decrease Font Size\tCtrl+-', 'Decreases the font size'
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
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.ignore_language,
            source=ignore_language_menu_item
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.increase_font_size,
            source=increase_font_size_menu_item
        )
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.decrease_font_size,
            source=decrease_font_size_menu_item
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
        dlg = MultipleChoiceDialog(self,
            message='Which term relationships do you want to use?',
            caption="Word Relationship Preferences",
            choices=Etymology.RELTYPES,
            selected=self.panel.reltypes
        )
        if dlg.ShowModal() == wx.ID_OK:
            reltypes = dlg.GetSelections()
            if len(reltypes) > 0:
                self.panel.set_reltypes(reltypes)
        dlg.Destroy()

    def configure_language(self, event):
        dlg = wx.SingleChoiceDialog(self,
            message='Which language is the document to be analyzed.',
            caption='Language Picker',
            choices=Etymology.LANGUAGES
        )
        idx = Etymology.LANGUAGES.index(self.panel.language)
        dlg.SetSelection(idx)
        if dlg.ShowModal() == wx.ID_OK:
            language = dlg.GetStringSelection()
            self.panel.set_language(language)
        dlg.Destroy()

    def ignore_language(self, event):
        dlg = wx.SingleChoiceDialog(self,
            message='Which language should be ignored for highlighting relationships.',
            caption='Ignored Language Picker',
            choices=self.panel.top_related_langs
        )
        dlg.SetSelection(0)
        if dlg.ShowModal() == wx.ID_OK:
            language = dlg.GetStringSelection()
            self.panel.ignore_language(language)
        dlg.Destroy()

    def increase_font_size(self, event):
        self.panel.set_fontsize(self.panel.font_size + 2)

    def decrease_font_size(self, event):
        if self.panel.font_size > 4:
            self.panel.set_fontsize(self.panel.font_size - 2)

    def onExit(self, event):
        self.Close()

class MultipleChoiceDialog(wx.Dialog):
    def __init__(self, parent, message:str, caption:str, choices: list[str]=[],selected: list[str]=[]):
        wx.Dialog.__init__(self, parent, -1)
        self.SetTitle(caption)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.StaticText(self, -1, message)
        self.clb = wx.CheckListBox(self, -1, choices = choices)
        self.chbox = wx.CheckBox(self, -1, 'Select all')
        self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_CHECKBOX, self.EvtChBox, self.chbox)

        sizer.Add(self.message, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.clb, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.chbox, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.clb.SetCheckedStrings(selected)

    def GetSelections(self):
        return self.clb.GetCheckedStrings()

    def EvtChBox(self, event):
        state = self.chbox.IsChecked()
        for i in range(self.clb.GetCount()):
            self.clb.Check(i, state)
