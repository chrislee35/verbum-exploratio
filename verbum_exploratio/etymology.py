#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 22:26:12 2024

@author: chris
"""
import pickle
import gzip
import os
import glob

def enumerate_lanaguages():
    dn = os.path.dirname(__file__)
    data_files = os.path.join(dn,"data","etymology-*.pckl.gz")
    languages = []
    for data_file in glob.glob(data_files):
        lang = data_file.replace('.pckl.gz', '').split("-")[-1]
        languages.append(lang)
    return sorted(languages)

class Etymology:
    DATA = {}

    RELTYPES = [
        "abbreviation_of",
        "back-formation_from",
        "blend_of",
        "borrowed_from",
        "calque_of",
        "clipping_of",
        "cognate_of",
        "compound_of",
        "derived_from",
        "doublet_with",
        "etymologically_related_to",
        "group_affix_root",
        "group_derived_root",
        "group_related_root",
        "has_affix",
        "has_confix",
        "has_prefix",
        "has_prefix_with_root",
        "has_root",
        "has_suffix",
        "inherited_from",
        "initialism_of",
        "is_onomatopoeic",
        "learned_borrowing_from",
        "named_after",
        "orthographic_borrowing_from",
        "phono-semantic_matching_of",
        "semantic_loan_of",
        "semi_learned_borrowing_from",
        "unadapted_borrowing_from",
    ]

    LANGUAGES = enumerate_lanaguages()

    def __init__(self, lang: str):
        self.load_lang(lang)
        self.language = lang
        # this is a shortcut for the primary language
        self.lang = self.DATA[lang]
        self.words = set(self.lang.keys())

    def load_lang(self, lang: str):
        if Etymology.DATA.get(lang) is None:
            Etymology.DATA[lang] = Etymology.load_data(lang)

    def has_word(self, word: str):
        return self.get_base_word(word) is not None

    def get_base_word(self, word: str):
        if word in self.words:
            return word
        if word.lower() in self.words:
            return word.lower()
        # maybe it's plural
        if len(word) > 3 and word.endswith('s') and word[0:-1] in self.words:
            return word[0:-1]
        if len(word) > 3 and word.endswith('s') and word[0:-1].lower() in self.words:
            return word[0:-1].lower()
        # maybe it's really plural
        if len(word) > 4 and word.endswith('es') and word[0:-2] in self.words:
            return word[0:-2]
        if len(word) > 4 and word.endswith('es') and word[0:-2].lower() in self.words:
            return word[0:-2].lower()
        return None

    def get_relationships(self, word: str, reltypes: list[str]=None, langs: list[str]=None):
        word = self.get_base_word(word)
        rels = self.lang.get(word, self.lang.get(word.lower()))
        if reltypes:
            rels = [x for x in rels if x['type'] in reltypes]
        if langs:
            rels = [x for x in rels if x['lang'] in langs]
        return rels

    def most_common_related_langs(self, reltypes: list[str]=None, count=10):
        langs = self.lang["DERIVED_FROM"]
        return [x[0] for x in langs.most_common(count)]

    @staticmethod
    def load_data(lang: str):
        dn = os.path.dirname(__file__)
        data_file = os.path.join(dn,"data",f"etymology-{lang}.pckl.gz")
        with gzip.open(data_file, 'r') as zfh:
            data = pickle.load(zfh)
            return data



if __name__ == "__main__":
    e = Etymology('English')
    print(e.has_word("Thesaurus"))
    print(e.has_word("upsidedown"))
    print(e.get_relationships("wall", reltypes=['derived_from']))

    print(e.most_common_related_langs(reltypes=['derived_from']))
