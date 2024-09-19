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
from enum import IntFlag

class FontWrapper:
    class Styles(IntFlag):
        REGULAR = 0
        BOLD = 1
        ITALIC = 2
        
    def getOs2Style(self):
        os2styles = { self.Styles.REGULAR : 64,
               self.Styles.BOLD : 32,
               self.Styles.ITALIC : 1, 
               self.Styles.BOLD | self.Styles.ITALIC : 33 }
        return os2styles[self.style]
    
    def __init__(self, font):
        self._font = font
        self.style = self.Styles.REGULAR
        
    def __getattr__(self, name):
        return getattr(self._font, name)
    
    def __setattr__(self, name, value):
        if name not in ['style', '_font']: #future proofing!
            print("Setting property", name, "to", value)
            object.__setattr__(self._font, name, value)
        else:            
            object.__setattr__(self, name, value)

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

def create_base_font():
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
    adjust_height(font, ref, 1)
    ref.close()
    return FontWrapper(font)

def family_props(font):
    font.familyname = 'Comic Fork Mono'
    font.version = '0.2'
    font.comment = 'https://github.com/caioycosta/comic-fork-mono-font'
    font.copyright = 'https://github.com/caioycosta/comic-fork-mono-font/blob/master/LICENSE'
    # TODO bring preferred names back
    font.sfnt_names = [] # Get rid of 'Prefered Name' etc.
    font.fontname = ('Comic Fork Mono-' + style_string(font)).replace(' ', '')
    font.fullname = ('Comic Fork Mono ' + style_string(font))
    # Manually set subfamily so that it is "Bold Italic" not "BoldItalic"s
    font.appendSFNTName('English (US)', 'SubFamily', style_string(font))
    font.macstyle = font.style
    font.os2_stylemap = font.getOs2Style()

def regular_props(font):
    font.os2_weight = 400        
    font.weight = 'Regular'

def save(font):
    filename = 'Comic Fork Mono ' + style_string(font) + '.ttf'
    print("Saving font file", filename)
    font.generate(filename)

def bold_transformation(font): 
    font.selection.all()
    font.changeWeight(64, "LCG", 0, 0, "squish")
    font.style = font.style | FontWrapper.Styles.BOLD

def style_string(font):
    resulting_styles = []
    if font.style == FontWrapper.Styles.REGULAR:
        return 'Regular'
    else: 
        if font.style & FontWrapper.Styles.BOLD:
            resulting_styles.append('Bold')
        if font.style & FontWrapper.Styles.ITALIC:
            resulting_styles.append('Italic')
        return ' '.join(resulting_styles)
        
def bold_props(font):
    font.os2_weight = 700
    font.weight = 'Bold'
        
def italic_props(font):
    # wip. no specific italic properties yet..
    pass

def italic_transformation(font):
    # wip
    font.selection.all()
    # 15 degrees (roughly)
    font.transform(psMat.skew(3.14 * 15 / 180.0), ('noWidth',))
    font.style = font.style | FontWrapper.Styles.ITALIC

# Create Regular Font
f = create_base_font()
family_props(f)
regular_props(f)
save(f)
f.close()

# Create Bold Font
f = create_base_font()
bold_transformation(f)
bold_props(f)
family_props(f)
save(f)
f.close()

# Create Italic Font
f = create_base_font()
italic_transformation(f)
italic_props(f)
family_props(f)
save(f)
f.close()

# Create Bold Italic Font
f = create_base_font()
italic_transformation(f)
bold_transformation(f)
italic_props(f)
bold_props(f)
family_props(f)
save(f)
f.close()