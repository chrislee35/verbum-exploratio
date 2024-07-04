#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 23:26:20 2024

@author: chris
"""
import wx
import re
import matplotlib.pyplot as plt
import networkx as nx
from verbum_exploratio.etymology import Etymology
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas

class VerbumNetworkFrame(wx.Frame):

    def __init__(self, doc: str, doclang: str='English', reltypes: list[str]=None):
        wx.Frame.__init__(self, None, -1)
        self.SetSize(wx.Size(1280, 768))

        self.panel = wx.Panel(self)
        self.fig = plt.figure(facecolor='k')
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        words, langs, relationships = self.langs_words_relationship(doc, doclang, reltypes)
        langs = [doclang]+langs
        nodes = list(range(len(langs) + len(words)))
        edges = []

        for rel in relationships:
            word, rt, rl, rt = rel
            lang_idx = langs.index(rl)
            word_idx = len(langs) + words.index(word)
            edges.append( (lang_idx, word_idx))
            edges.append( (0, word_idx))

        lengths = dict( [(e, {'len': 1}) for e in edges] )

        #node_sizes = [ len(node)*150 for node in langs+words ]
        #node_color = ["#999999"] * len(langs) + [ "#999999" ] * len(words)
        node_label = dict(list(enumerate(langs+words)))

        G = nx.Graph()

        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        nx.set_edge_attributes(G, lengths)
        #pos = nx.spring_layout(G)
        #pos = nx.bfs_layout(G, start=0, scale=2)
        shells = [
            [0],
            [x+1+len(langs) for x in list(range(len(words)))],
            [x+1 for x in list(range(len(langs)))],
        ]
        pos = nx.shell_layout(G, nlist=shells)

        nx.draw_networkx(G,
             pos = pos,
             node_size = 10,
             node_color = "#333333",
             edge_color = 'b',
             font_color = 'w',
             labels = node_label,
             node_shape = 'o',
             font_size = 10,
             with_labels = True
        )

        plt.axis('off')

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.panel.SetSizer(self.vbox)

    def langs_words_relationship(self, doc: str, doclang: str, reltypes: list[str]) -> [list[str], list[str], list[list[str]]]:
        e = Etymology(doclang)
        clean1 = re.compile(r"[^\w]", re.U) # this should match all latin unicode as well as A-Z
        clean2 = re.compile(r"\d", re.U) # this should match all latin unicode as well as A-Z
        seen = set()
        words = set()
        langs = set()
        relations = []

        for word in re.split(r"[\n \-\/]", doc):
            clean = clean2.sub('', clean1.sub('', word))
            if clean is None or len(clean) == 0: continue

            word = e.get_base_word(clean)
            if word is None or len(word) == 0: continue
            if word in seen: continue
            seen.add(word)

            rels = e.get_relationships(word, reltypes=reltypes)
            if rels is None or len(rels) == 0: continue
            words.add(word)
            for r in rels:
                langs.add(r['lang'])
                relations.append([
                    word,
                    r['type'],
                    r['lang'],
                    r['term']
                ])
        return(sorted(list(words)), sorted(list(langs)), relations)

if __name__ == '__main__':
  app = wx.App()
  testdoc = """It grows to a height of 3–16 centimetres (1.2–6.3 in), and is topped with a purple, and occasionally white, flower that is 15 millimetres (0.59 in) or longer, and shaped like a funnel. This butterwort grows in damp environments such as bogs and swamps, in low or subalpine elevations.[1] Being native to environments with cold winters, they produce a winter-resting bud (hibernaculum). There are three forms originating from Europe: P. vulgaris f. bicolor, which has petals that are white and purple; P. vulgaris f. albida, which has all white petals; and P. vulgaris f. alpicola, which has larger flowers.[2] The taxonomic status of these forms is not universally recognised – see e.g. The Plant List.[3]"""
  app.frame = VerbumNetworkFrame(testdoc, reltypes=['derived_from'])
  app.frame.Show()
  app.MainLoop()
