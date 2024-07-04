#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 17:44:19 2024

@author: chris
"""
import wx
import re
from verbum_exploratio.etymology import Etymology

class VerbumTreeFrame(wx.Frame):
    def __init__(self, doc: str, doclang: str = 'English', reltypes: list[str] = None):
        wx.Frame.__init__(self, None, -1)
        self.SetSize(wx.Size(500, 768))
        self.panel = wx.Panel(self)
        self.tree = wx.TreeCtrl(self.panel, 1,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)

        self.reltypes = reltypes
        self.langs_words_tree(self.tree, doc, doclang)

        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.tree, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.panel.SetSizer(self.vbox)

    def OnSelChanged(self, event):
        item = event.GetItem()
        data = self.tree.GetItemData(item)
        if data is None: return
        print(data)
        lang = data['lang']
        term = data['term']
        e = Etymology(lang)
        rels = e.get_relationships(term, reltypes=self.reltypes)
        if rels == None: rels = []
        for r in rels:
            self.tree.AppendItem(item, f"{lang}:{term} {r['type']} {r['lang']}:{r['term']}", data=r)

    def langs_words_tree(self, tree: wx.TreeCtrl, doc: str, doclang: str) -> [list[str], list[str], list[list[str]]]:
        e = Etymology(doclang)
        clean1 = re.compile(r"[^\w]", re.U) # this should match all latin unicode as well as A-Z
        clean2 = re.compile(r"\d", re.U) # this should match all latin unicode as well as A-Z

        root = tree.AddRoot(doclang)
        langs = {}
        seen = set()

        for word in re.split(r"[\n \-\/]", doc):
            clean = clean2.sub('', clean1.sub('', word)).strip()
            if clean is None or len(clean) == 0: continue

            word = e.get_base_word(clean)
            if word is None or len(word) == 0: continue
            if word in seen: continue
            seen.add(word)

            rels = e.get_relationships(word, reltypes=self.reltypes)
            if rels is None or len(rels) == 0: continue
            for r in rels:
                if r['lang'] not in langs:
                    langs[r['lang']] = { 'node': tree.AppendItem(root, r['lang']), 'rels': {} }
                if r['type'] not in langs[r['lang']]['rels']:
                    langs[r['lang']]['rels'][r['type']] = tree.AppendItem(langs[r['lang']]['node'], r['type'])
                tree.AppendItem(langs[r['lang']]['rels'][r['type']], word+" => "+r['term'], data=r)
        return tree



if __name__ == "__main__":
    app = wx.App()
    testdoc = """It grows to a height of 3–16 centimetres (1.2–6.3 in), and is topped with a purple, and occasionally white, flower that is 15 millimetres (0.59 in) or longer, and shaped like a funnel. This butterwort grows in damp environments such as bogs and swamps, in low or subalpine elevations.[1] Being native to environments with cold winters, they produce a winter-resting bud (hibernaculum). There are three forms originating from Europe: P. vulgaris f. bicolor, which has petals that are white and purple; P. vulgaris f. albida, which has all white petals; and P. vulgaris f. alpicola, which has larger flowers.[2] The taxonomic status of these forms is not universally recognised – see e.g. The Plant List.[3]"""
    #app.frame = VerbumTreeFrame(testdoc, reltypes=['derived_from'])
    app.frame = VerbumTreeFrame(testdoc, reltypes=None)
    app.frame.Show()
    app.MainLoop()
