#!/usr/bin/env python

import logging
import os
import subprocess
import sys
import time
import pcbnew
import argparse
from kinparse import parse_netlist

from contextlib import contextmanager
from util import file_util
from export_util import (
    PopenContext,
    xdotool,
    wait_for_window,
    recorded_xvfb,
)

repo_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
sys.path.append(repo_root)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def pcbnew_cleanup(wait_init):
    """Send keystrokes for cleaning the pcb

    Keyword arguments:
    """
    # Give enough time to load the libraries
    # This should be a parameter
    time.sleep(float(wait_init))

    logger.info('Open Edit -> Cleanup tracks and vias')
    xdotool(['key', 'alt+e'])
    xdotool(['key', 'l'])
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


def delete_footprints(brd, variantRefs, variantName):
    """Delete the footprints that not belong to the specified variant refs
    """
    nlst = parse_netlist(brd + '.net')
    # Generate fields dict
    for i, part in enumerate(nlst.parts):
        nlst.parts[i].fieldsDic = {
                field.name: field.value for field in part.fields
                }
    # Save the refs
    fpts = []
    for part in nlst.parts:
        if 'variant' in part.fieldsDic:
            if part.fieldsDic['variant'] not in variantRefs:
                fpts.append(part.ref)
    # Remove footprints
    board = pcbnew.LoadBoard(brd + '.kicad_pcb')
    for module in board.GetModules():
        if module.GetReference() in fpts:
            print('Removing ' + module.GetReference())
            board.RemoveNative(module)

    board.Save(brd + '_' + variantName + '.kicad_pcb')


def cleanup(args):
    board_file_path = os.path.dirname(args.brd)
    board_file_name = os.path.basename(args.brd)
    board_file = os.path.join(
            project_root, args.brd +
            '_' + args.variantName+'.kicad_pcb')

    board = pcbnew.LoadBoard(board_file)

    output_dir = os.path.join(
            project_root,
            'CI-BUILD/'+board_file_name+'_'+args.variantName+'/DLF')
    file_util.mkdir_p(output_dir)

    # TODO: Remove when stable or add debug flag
    screencast_output_file = os.path.join(
            output_dir,
            'dlf'+args.variantName+'.ogv')

    with recorded_xvfb(
            screencast_output_file,
            width=800, height=600,
            colordepth=24):
        with PopenContext(
                ['pcbnew', board_file],
                close_fds=True) as pcbnew_proc:
            pcbnew_cleanup(args.wait_init)
            pcbnew_proc.terminate()


def main(argv):
    parser = argparse.ArgumentParser(
            description='Delete footprints and cleanup PCB'
            )
    parser.add_argument(
            '--dir',
            nargs='?', dest='dir', default='./')
    parser.add_argument(
            '--brd',
            nargs='?', dest='brd', required=True)
    parser.add_argument(
            '--variant-name',
            nargs='?', dest='variantName', default='')
    parser.add_argument(
            '--variant-refs',
            nargs='?', dest='variantRefs', default='')
    parser.add_argument(
            '--wait_init',
            nargs='?', dest='wait_init', default=10)

    args = parser.parse_args(argv)
    args.dir = os.path.abspath(os.path.join(os.getcwd(), args.dir))
    args.brd = os.path.join(os.getcwd(), args.brd)
    args.variantRefs = args.variantRefs.split(',')
    file_util.mkdir_p(args.dir)
    os.chdir(args.dir)

    delete_footprints(args.brd, args.variantRefs, args.variantName)
    cleanup(args)


if __name__ == '__main__':
    main(sys.argv[1:])
