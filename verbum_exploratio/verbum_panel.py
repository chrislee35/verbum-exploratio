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
        self.font_size = 14
        self.current_highlight = None

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        t = rt.RichTextCtrl(self,
            style=wx.TE_MULTILINE | wx.TE_WORDWRAP, size=wx.Size(800, 600))
        font1 = wx.Font(wx.FontInfo(self.font_size).Family(wx.FONTFAMILY_MODERN))
        font2 = wx.Font(wx.FontInfo(self.font_size - 2).Family(wx.FONTFAMILY_MODERN))
        t.SetFont(font1)
        t.SetBackgroundColour(wx.BLACK)
        t.Bind(wx.EVT_LEFT_UP, self.main_click_handler)
        t.Bind(wx.EVT_KEY_UP, self.keypress_handler)
        t.SetInsertionPoint(0)

        self.default_font = font1
        self.text = t
        self.legend = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=wx.Size(80, 600))
        self.legend.SetBackgroundColour(wx.BLACK)
        self.info = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=wx.Size(400, 600))
        self.info.SetFont(font2)
        self.info.SetEditable(False)
        self.info.SetBackgroundColour(wx.BLACK)
        self.info.Bind(wx.EVT_LEFT_UP, self.info_click_handler)

        main_sizer.Add(self.text, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(self.legend, 0, wx.ALL | wx.TOP, 5)
        main_sizer.Add(self.info, 0, wx.ALL | wx.TOP, 5)

        self.SetSizer(main_sizer)

        self.reltypes = Etymology.RELTYPES
        self.set_language('English')

        self.set_text(self.get_test())

        self.timer = wx.Timer(self)
        self.info_default_background_colour = self.info.GetBackgroundColour()
        self.Bind(wx.EVT_TIMER, lambda x: self.info.SetBackgroundColour(self.info_default_background_colour))

    def set_fontsize(self, points: int):
        self.font_size = points
        self.default_font = wx.Font(wx.FontInfo(self.font_size).Family(wx.FONTFAMILY_MODERN))
        font2 = wx.Font(wx.FontInfo(self.font_size - 2).Family(wx.FONTFAMILY_MODERN))
        self.info.SetFont(font2)
        self.update_highlighting()

    def set_language(self, lang: str):
        self.language = lang
        self.etymology = Etymology(lang)
        self.punctuation = string.punctuation + ' ' + '\n'
        self.top_related_langs = self.etymology.most_common_related_langs(reltypes=self.reltypes, count=20)
        self.update_legend()
        self.update_highlighting()

    def ignore_language(self, lang: str):
        if lang in self.top_related_langs:
            idx = self.top_related_langs.index(lang)
            self.top_related_langs.remove(lang)
            clr = self.COLORS_TAB20.pop(idx)
            self.COLORS_TAB20.append(clr)
            self.update_legend()
            self.update_highlighting()

    def set_reltypes(self, reltypes: list[str]):
        self.reltypes = reltypes
        self.top_related_langs = self.etymology.most_common_related_langs(reltypes=self.reltypes, count=20)
        self.update_legend()
        self.update_highlighting()

    def update_legend(self):
        self.legend.SetEditable(True)
        self.legend.SetValue("")
        for i,l in enumerate(self.top_related_langs):
            self.legend.SetDefaultStyle(wx.TextAttr(self.COLORS_TAB20[i]))
            self.legend.AppendText(l+"\n")
        self.legend.SetEditable(False)

    def set_text(self, text: str):
        self.text.SetValue(text)
        self.update_highlighting()

    def main_click_handler(self, event: wx.Event):
        word, pos = self.get_word_at_caret()
        if self.append_info_for_word(self.etymology, word):
            self.change_highlight(pos)

    def append_info_for_word(self, e: Etymology, word: str) -> bool:
        if e.has_word(word):
            base_word = e.get_base_word(word)
            if word == base_word:
                text = f"{word}:\n"
            else:
                text = f"{word} => {base_word}:\n"

            top_related_langs = e.most_common_related_langs(reltypes=self.reltypes, count=20)
            rels = e.get_relationships(word, reltypes=self.reltypes, langs=top_related_langs+[e.language])
            for r in rels:
                text += f"  {r['type']}  {r['lang']}  {r['term']}\n"
            text += "\n"
            self.info.AppendText(text)
            return True
        return False

    def info_click_handler(self, event: wx.Event):
        i = self.info
        pos = i.GetInsertionPoint()
        xy = i.PositionToXY(pos)
        line = i.GetLineText(xy[2])
        if line.startswith('  '):
            t, l, term = line.strip().split('  ', 2)
            e = Etymology(l) # this will be fast once the language is cached
            if not self.append_info_for_word(e, term):
                i.SetBackgroundColour(wx.Colour(40,30,40))
                self.timer.Start(300)


    def keypress_handler(self, event: wx.KeyEvent):
        char = chr(event.GetKeyCode())
        if event.GetKeyCode() == 13 or char in self.punctuation + "\n":
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
        while c < len(text) and text[c] not in self.punctuation:
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
        off_white = wx.Colour(220, 220, 220)
        self.text.SetStyle(0, end, wx.TextAttr(off_white))
        # now go through each word and see if it exists in the database and which root
        start = 0
        words = re.split(r"[\n \-\/]", text)
        clean = re.compile(r"[^\w]", re.U) # this should match all latin unicode as well as A-Z
        clean2 = re.compile(r"\d", re.U) # this should match all latin unicode as well as A-Z
        # Diacritical marks are so cliché.
        unrecognized_font = wx.Font(wx.FontInfo(self.font_size).Family(wx.FONTFAMILY_TELETYPE))
        for word in words:
            new_end = start + len(word)
            clean_word = clean.sub('', word)
            clean_word = clean2.sub('', clean_word)
            try:
                offset = word.index(clean_word)
                word = clean_word
            except ValueError:
                offset = 0
            end = start + len(word) # FIXME
            if self.etymology.has_word(word):
                rels = self.etymology.get_relationships(word,
                    langs=self.top_related_langs,
                    reltypes=self.reltypes
                )
                colour = off_white
                found = False
                for i,l in enumerate(self.top_related_langs):
                    if found: break
                    for r in rels:
                        if r['lang'] == l:
                            colour = self.COLORS_TAB20[i]
                            found = True
                            break
                self.text.SetStyle(start+offset, end+offset, wx.TextAttr(colour, font=self.default_font))
            else:
                ta = wx.TextAttr(wx.Colour(64,64,64), font=unrecognized_font)
                self.text.SetStyle(start+offset, end+offset, ta)
            start = new_end + 1
