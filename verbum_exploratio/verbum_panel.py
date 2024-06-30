#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 23:42:03 2024

@author: chris
"""
import wx
import wx.richtext as rt
from .etymology import Etymology
import re
import string

class VerbumPanel(wx.Panel):
    COLORS_TAB20 = [ # from matplotlib
        wx.Colour(31, 119, 180, 255),
        wx.Colour(174, 199, 232, 255),
        wx.Colour(255, 127, 14, 255),
        wx.Colour(255, 187, 120, 255),
        wx.Colour(44, 160, 44, 255),
        wx.Colour(152, 223, 138, 255),
        wx.Colour(214, 39, 40, 255),
        wx.Colour(255, 152, 150, 255),
        wx.Colour(148, 103, 189, 255),
        wx.Colour(197, 176, 213, 255),
        wx.Colour(140, 86, 75, 255),
        wx.Colour(196, 156, 148, 255),
        wx.Colour(227, 119, 194, 255),
        wx.Colour(247, 182, 210, 255),
        wx.Colour(127, 127, 127, 255),
        wx.Colour(199, 199, 199, 255),
        wx.Colour(188, 189, 34, 255),
        wx.Colour(219, 219, 141, 255),
        wx.Colour(23, 190, 207, 255),
        wx.Colour(158, 218, 229, 255),
    ]


    def __init__(self, parent):
        super().__init__(parent)
        self.current_highlight = None

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        t = rt.RichTextCtrl(self,
            style=wx.TE_MULTILINE | wx.TE_WORDWRAP, size=wx.Size(800, 600))
        font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Nimbus Roman')
        t.SetFont(font1)
        t.AppendText(self.get_test())
        t.Bind(wx.EVT_LEFT_UP, self.mouse_btn_left_cb)
        t.Bind(wx.EVT_KEY_UP, self.keypress_handler)
        t.SetInsertionPoint(0)
        self.text = t

        main_sizer.Add(self.text, 0, wx.ALL | wx.EXPAND, 5)
        self.etymology = Etymology('English')
        self.punctuation = string.punctuation + ' '
        self.top_related_langs = self.etymology.most_common_related_langs(reltypes=['derived_from'], count=20)
        self.update_highlighting()

        key = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=wx.Size(80, 600))
        for i,l in enumerate(self.top_related_langs):
            key.SetDefaultStyle(wx.TextAttr(self.COLORS_TAB20[i]))
            key.AppendText(l+"\n")

        key.SetEditable(False)
        main_sizer.Add(key, 0, wx.ALL | wx.TOP, 5)

        self.info = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=wx.Size(400, 600))
        self.info.SetEditable(False)
        main_sizer.Add(self.info, 0, wx.ALL | wx.TOP, 5)

        self.SetSizer(main_sizer)

    def set_text(self, text: str):
        self.text.SetValue(text)
        self.update_highlighting()

    def mouse_btn_left_cb(self, event: wx.Event):
        word, pos = self.get_word_at_caret()
        text = ""
        if self.etymology.has_word(word):
            rels = self.etymology.get_relationships(word, reltypes=['derived_from'], langs=self.top_related_langs)
            for r in rels:
                text += f"{r['type']} {r['lang']} {r['term']}\n"
        self.info.SetValue(text)

        self.change_highlight(pos)

    def keypress_handler(self, event: wx.KeyEvent):
        if event.GetKeyCode() == 13:
            self.update_highlighting()

    def change_highlight(self, pos: tuple[int]):
        if self.current_highlight:
            self.remove_highlight(self.current_highlight)
        self.current_highlight = pos
        self.add_highlight(pos)

    def remove_highlight(self, pos: tuple[int]):
        self.text.SetStyle(pos[0], pos[1], wx.TextAttr(wx.NullColour, wx.Colour(128,128,128, 0)))

    def add_highlight(self, pos: tuple[int]):
        self.text.SetStyle(pos[0], pos[1], wx.TextAttr(wx.NullColour, wx.Colour(128,128,128,255)))

    def get_word_at_caret(self) -> str:
        caret = self.text.GetCaretPosition()
        text = self.text.Value
        word = text[caret]
        c = caret - 1
        while text[c] not in self.punctuation:
            word = text[c]+word
            if c == 0: break
            c -= 1
        start = c
        if c > 0: start += 1

        c = caret + 1
        while text[c] not in self.punctuation:
            word = word+text[c]
            c += 1
        end = c
        #if c < len(text) - 1: end -= 1

        return word, (start, end)

    def update_text_file(self, file_path: str):
        with open(file_path, 'r') as fh:
            text = fh.read()
            self.set_text(text)

    def get_test(self) -> str:
        test_text = """Pinguicula vulgaris, the common butterwort, is a perennial carnivorous plant in the butterwort genus of the family Lentibulariaceae.
Description

It grows to a height of 3–16 centimetres (1.2–6.3 in), and is topped with a purple, and occasionally white, flower that is 15 millimetres (0.59 in) or longer, and shaped like a funnel. This butterwort grows in damp environments such as bogs and swamps, in low or subalpine elevations.[1] Being native to environments with cold winters, they produce a winter-resting bud (hibernaculum). There are three forms originating from Europe: P. vulgaris f. bicolor, which has petals that are white and purple; P. vulgaris f. albida, which has all white petals; and P. vulgaris f. alpicola, which has larger flowers.[2] The taxonomic status of these forms is not universally recognised – see e.g. The Plant List.[3]

Common butterwort is an insectivorous plant. Its leaves have glands that excrete a sticky fluid that traps insects; the glands also produce enzymes that digest the insects.[4] This serves as a way for the plant to access a source of nitrogen, as they generally grow in soil that is acidic and low in nutrients, such as bogs.[4][5] Insect capture is an adaptation to nutrient-poor conditions, and the plant is highly dependent on insects for nitrogen.
"""
        return test_text

    def update_highlighting(self):
        # first remove all highlighting
        text = self.text.Value
        end = len(text)
        self.text.SetStyle(0, end, wx.TextAttr(wx.WHITE))
        # now go through each word and see if it exists in the database and which root
        start = 0
        words = re.split(r"[\n \-\/]", text)
        clean = re.compile('[^A-Za-z]')
        for word in words:
            new_end = start + len(word)
            word = clean.sub('', word)
            end = start + len(word) # FIXME
            if self.etymology.has_word(word):
                rels = self.etymology.get_relationships(word,
                    langs=self.top_related_langs,
                    reltypes=['derived_from']
                )
                colour = wx.WHITE
                found = False
                for i,l in enumerate(self.top_related_langs):
                    if found: break
                    for r in rels:
                        if r['lang'] == l:
                            colour = self.COLORS_TAB20[i]
                            found = True
                            break
                self.text.SetStyle(start, end, wx.TextAttr(colour))
            start = new_end + 1
