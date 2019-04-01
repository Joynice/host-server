# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from html_similarity import similarity

class Site_Similarity(object):
    def __init__(self, doc1, doc2):
        self.doc1 = doc1
        self.doc2 = doc2

    def judge(self):
        return similarity(self.doc1, self.doc2)
