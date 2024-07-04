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
import spacy

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

    LEMMATIZERS = {
        "Catalan": "ca_core_news_sm",
        "Chinese": "zh_core_web_sm",
        "Croatian": "hr_core_news_sm",
        "Danish": "da_core_news_sm",
        "Dutch": "nl_core_news_sm",
        "English": "en_core_web_sm",
        "Finnish": "fi_core_news_sm",
        "French": "fr_core_news_sm",
        "German": "de_core_news_sm",
        "Greek": "el_core_news_sm",
        "Italian": "it_core_news_sm",
        "Japanese": "ja_core_news_sm",
        "Korean": "ko_core_news_sm",
        "Lithuanian": "lt_core_news_sm",
        "Macedonian": "mk_core_news_sm",
        "Multi-language": "xx_ent_wiki_sm",
        "Norwegian Bokmål": "nb_core_news_sm",
        "Polish": "pl_core_news_sm",
        "Portuguese": "pt_core_news_sm",
        "Romanian": "ro_core_news_sm",
        "Russian": "ru_core_news_sm",
        "Slovenian": "sl_core_news_sm",
        "Spanish": "es_core_news_sm",
        "Swedish": "sv_core_news_sm",
        "Ukrainian": "uk_core_news_sm",
    }

    def __init__(self, lang: str):
        self.load_lang(lang)
        self.language = lang
        # this is a shortcut for the primary language
        self.lang = self.DATA[lang]
        self.words = set(self.lang.keys())
        self.lemmatizer = None
        if lang in self.LEMMATIZERS:
            model = self.LEMMATIZERS[lang]
            try:
                self.lemmatizer = spacy.load(model)
            except:
                spacy.cli.download(model)
                self.lemmatizer = spacy.load(model)


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
        if self.lemmatizer:
            doc = self.lemmatizer(word)
            for token in doc:
                lemma = token.lemma_

                if lemma in self.words:
                    return lemma
                if lemma.lower() in self.words:
                    return lemma.lower()
        return None

    def get_relationships(self, word: str, reltypes: list[str]=None, langs: list[str]=None):
        word = self.get_base_word(word) or word
        rels = self.lang.get(word, self.lang.get(word.lower()))
        if rels is None: return []
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
        if not os.path.exists(data_file): return {}
        with gzip.open(data_file, 'r') as zfh:
            data = pickle.load(zfh)
            return data

if __name__ == "__main__":
    e = Etymology('English')
    for word in ["Thesaurus", "upsidedown", "occasionally", "plants", "virii", "viruses", "aardwolves", "abaci"]:
        print(word, e.get_base_word(word))
    # print(e.has_word("Thesaurus"))
    # print(e.has_word("upsidedown"))
    # print(e.has_word("occasionally"))
    # print(e.get_relationships("wall", reltypes=['derived_from']))
    # print(e.get_relationships("occasionally"))

    # print(e.most_common_related_langs(reltypes=['derived_from']))
