#!/usr/bin/env python

#   Copyright 2015-2016 Scott Bezek and the splitflap contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import os
import subprocess
import sys
import time

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

def pcbnew_export_grb(output_directory):
    wait_for_window('pcbnew', '\[')

    logger.info('Focus main pcbnew window')
    xdotool(['search', '--name', '\[', 'windowfocus'])

    logger.info('Open File->Plot')
    xdotool(['key', 'alt+f'])
    xdotool(['key', 'l'])

    logger.info('Set output directory')
    wait_for_window('plot', 'Plot')
    xdotool(['key', 'Tab'])
    xdotool(['type', output_directory])

    logger.info('Plot!')
    xdotool(['search', '--name', 'Plot', 'windowfocus'])
    xdotool(['key', 'shift+Tab'])
    xdotool(['key', 'shift+Tab'])
    xdotool(['key', 'shift+Tab'])
    xdotool(['key', 'shift+Tab'])
    xdotool(['key', 'shift+Tab'])
    xdotool(['key', 'Return'])

    logger.info('Wait before shutdown')
    time.sleep(2)

def export_grb(brd_name):
    """Plot the selected PCB layers in Gerber format

    Keyword arguments:
    board_name -- The board file name including relative path
    from project_root WITHOUT extension.
    """
    brd_file_path = os.path.dirname(brd_name)
    brd_file_name = os.path.basename(brd_name)
    brd_file = os.path.join(project_root, brd_name+'.kicad_pcb')

    output_dir = os.path.join(project_root, 'CI-BUILD/GRB')
    file_util.mkdir_p(output_dir)

    screencast_output_file = os.path.join(output_dir, 'export_grb_screencast.ogv')

    with recorded_xvfb(screencast_output_file, width=800, height=600, colordepth=24):
        with PopenContext(['pcbnew', brd_file], close_fds=True) as pcbnew_proc:
            pcbnew_export_bom(output_dir)
            pcbnew_proc.terminate()

    # Copy BOM to CI Folder
    subprocess.check_call([
        'mv',
        sch_name+'.xml',
        output_dir,
    ])

if __name__ == '__main__':
    if not sys.argv[1]:
        raise ValueError('Board file was not provided!')

    export_grb(sys.argv[1])

