#!/usr/bin/env python

import logging
import os
import subprocess
import sys
import time
import pcbnew
import argparse

from contextlib import contextmanager

repo_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
sys.path.append(repo_root)

from util import file_util
from export_util import (
    PopenContext,
    xdotool,
    wait_for_window,
    recorded_xvfb,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def pcbnew_cleanup(footprints, wait_init):
    """Send keystrokes for cleaning the pcb

    Keyword arguments:
    footprints -- the list of footprints
    """
    # Give enough time to load the libraries
    # This should be a parameter
    time.sleep(float(wait_init))

    logger.info('Open Edit -> Cleanup tracks and vias')
    xdotool(['key', 'alt+e'])
    xdotool(['key', 'c'])
    xdotool(['key', 'c'])
    xdotool(['key', 'c'])
    xdotool(['key', 'Return'])

    wait_for_window('cleanup', 'Cleaning Options')

    logger.info('Go!')
    xdotool(['key', 'Return'])

    logger.info('Wait to fill')
    time.sleep(5)

    xdotool(['key', 'b'])

    logger.info('Wait to save')
    time.sleep(4)

    logger.info('Save board')
    xdotool(['key', 'alt+f'])
    xdotool(['key', 's'])

    logger.info('Wait before shutdown')
    time.sleep(5)

def delete_footprints(args):
    """Delete the selected footprints from board
    """
    board = pcbnew.LoadBoard(args.brd + '.kicad_pcb')
    for module in board.GetModules():
        if module.GetReference() in args.footprints:
            print "Removing "+module.GetReference()
            board.RemoveNative(module)

    board.Save(args.brd + '_' + args.variant + '.kicad_pcb')

def cleanup(args):
    board_file_path = os.path.dirname(args.brd);
    board_file_name = os.path.basename(args.brd);
    board_file = os.path.join(project_root, args.brd+'_'+args.variant+'.kicad_pcb')

    board = pcbnew.LoadBoard(board_file)

    output_dir = os.path.join(project_root,
            'CI-BUILD/'+board_file_name+'_'+args.variant+'/DLF')
    file_util.mkdir_p(output_dir)

    #TODO: Remove when stable or add debug flag
    screencast_output_file = os.path.join(output_dir, 'dlf'+args.variant+'.ogv')

    with recorded_xvfb(screencast_output_file, width=800, height=600, colordepth=24):
        with PopenContext(['pcbnew', board_file], close_fds=True) as pcbnew_proc:
            pcbnew_cleanup(args.footprints, args.wait_init)
            pcbnew_proc.terminate()

def main(argv):
    parser = argparse.ArgumentParser(description='Delete footprints and cleanup PCB')
    parser.add_argument('--dir', nargs='?', dest='dir', default='./')
    parser.add_argument('--brd', nargs='?', dest='brd', required=True)
    parser.add_argument('--variant', nargs='?', dest='variant', default='')
    parser.add_argument('--footprints', nargs='?', dest='footprints', required=True)
    parser.add_argument('--wait_init', nargs='?', dest='wait_init', default=10)
    args = parser.parse_args(argv)
    args.dir = os.path.abspath(os.path.join(os.getcwd(), args.dir))
    args.brd = os.path.join(os.getcwd(), args.brd)
    args.footprints = args.footprints.split(',')
    file_util.mkdir_p(args.dir)
    os.chdir(args.dir)

    delete_footprints(args)
    cleanup(args)

if __name__ == '__main__':
    main(sys.argv[1:])

