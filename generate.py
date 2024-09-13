#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates the Comic Mono font files based on Comic Shanns font.

Based on:
- monospacifier: https://github.com/cpitclaudel/monospacifier/blob/master/monospacifier.py
- YosemiteAndElCapitanSystemFontPatcher: https://github.com/dtinth/YosemiteAndElCapitanSystemFontPatcher/blob/master/bin/patch
"""

import os
import re
import sys

import fontforge
import psMat
import unicodedata

def height(font):
    return float(font.capHeight)

def adjust_height(source, template, scale):
    source.selection.all()
    source.transform(scale * psMat.scale(height(template) / height(source)))
    for attr in ['ascent', 'descent',
                'hhea_ascent', 'hhea_ascent_add',
                'hhea_linegap',
                'hhea_descent', 'hhea_descent_add',
                'os2_winascent', 'os2_winascent_add',
                'os2_windescent', 'os2_windescent_add',
                'os2_typoascent', 'os2_typoascent_add',
                'os2_typodescent', 'os2_typodescent_add',
                ]:
        setattr(source, attr, getattr(template, attr))
    
font = fontforge.open('vendor/comic-shanns/v2-2/comic shanns.otf')
ref = fontforge.open('vendor/cousine/fonts/ttf/hinted/variable_ttf/Cousine-VF.ttf')
for g in font.glyphs():
    uni = g.unicode
    category = unicodedata.category(chr(uni)) if 0 <= uni <= sys.maxunicode else None
    if g.width > 0 and category not in ['Mn', 'Mc', 'Me']:
        target_width = 510
        if g.width != target_width:
            delta = target_width - g.width
            # Fix adapted from https://github.com/cpitclaudel/monospacifier/issues/32
            g.left_side_bearing = round(g.left_side_bearing + delta / 2)           
            g.right_side_bearing = round(g.right_side_bearing + delta - g.left_side_bearing)
            g.width = target_width

font.familyname = 'Comic Fork Mono'
font.version = '0.1'
font.comment = 'https://github.com/caioycosta/comic-fork-mono-font'
font.copyright = 'https://github.com/caioycosta/comic-fork-mono-font/blob/master/LICENSE'

adjust_height(font, ref, 1)
font.sfnt_names = [] # Get rid of 'Prefered Name' etc.
font.fontname = 'ComicForkMono'
font.fullname = 'Comic Fork Mono'
font.generate('ComicForkMono.ttf')

font.selection.all()
font.fontname = 'ComicForkMono-Bold'
font.fullname = 'Comic Fork Mono Bold'
font.weight = 'Bold'
font.changeWeight(32, "LCG", 0, 0, "squish")
font.generate('ComicForkMono-Bold.ttf')
