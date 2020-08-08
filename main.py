# -*- coding: utf-8 -*-
from extractor import IssueExtractor
from creator import ImageCreator

if __name__ == '__main__':
    ie = IssueExtractor()
    ie.export_issues()
    ic = ImageCreator()
    ic.parse_and_draw()

