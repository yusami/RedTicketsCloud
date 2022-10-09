# -*- coding: utf-8 -*-
from src.extractor import IssueExtractor
from src.creator import ImageCreator

if __name__ == '__main__':
    ie = IssueExtractor()
    ie.export_issues()
    ic = ImageCreator()
    ic.parse_and_draw()

