# -*- coding: utf-8 -*-
class Schema(Entity):

    def __init__(self):
        self.fulltext_engine = None
        self.version = None
        self.name = None
        self.descr = None
        self.domains = []
        self.tables = []