import sys
import os
import errno
import pcbnew
import argparse
import re
import datetime
from util import file_util

def tag(args):
    board = pcbnew.LoadBoard(args.brd + '.kicad_pcb')

    for draw in board.GetModules():
        for d in draw.GraphicalItems():
            if d.GetClass() == 'MTEXT':
                txt = d.GetText()
                if txt == "$date$" and (args.tag_date or args.all):
                    d.SetText("%s"%datetime.date.today())
                if txt == "$commit$" and (args.tag_commit or args.all):
                    d.SetText("%s"%args.commit)
                if txt == "$tag$" and (args.tag_tag or args.all):
                    d.SetText("%s"%args.tag)
                if txt == "$variant$" and (args.tag_var or args.all):
                    d.SetText("%s"%args.variant)

    pcbnew.SaveBoard(args.brd + '.kicad_pcb', board)

def main(argv):
   parser = argparse.ArgumentParser(description='Tag board with different information')
   parser.add_argument('--brd', nargs='?', dest='brd', required=True)
   parser.add_argument('--tag-date', action='store_true', dest='tag_date', default=False)
   parser.add_argument('--tag-commit', action='store_true', dest='tag_commit', default=False)
   parser.add_argument('--tag-tag', action='store_true', dest='tag_tag', default=False)
   parser.add_argument('--tag-variant', action='store_true', dest='tag_var', default=False)
   parser.add_argument('--variant', nargs='?', dest='variant', required=True)
   parser.add_argument('--commit', nargs='?', dest='commit', required=True)
   parser.add_argument('--tag', nargs='?', dest='tag', required=True)
   parser.add_argument('--all', action='store_true', dest='all', default=False)

   args = parser.parse_args(argv)

   args.brd = os.path.join(os.getcwd(), args.brd)

   tag(args)

if __name__ == '__main__':
    main(sys.argv[1:])
