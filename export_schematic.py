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

def eeschema_plot_schematic(output_name):
    """Send keystrokes for printing schematic

    Keyword arguments:
    output_name -- The output pdf file name
    """
    # Give enough time to load the libraries
    # This should be a parameter
    time.sleep(10)

    logger.info('Open File->Print')
    xdotool(['key', 'alt+f'])
    xdotool(['key', 'p'])

    wait_for_window('print', 'Print')

    logger.info('Set color output')
    xdotool(['key', 'alt+b'])

    logger.info('Open Print dialog')
    xdotool(['key', 'Tab'])
    xdotool(['key', 'Tab'])
    xdotool(['key', 'Tab'])
    xdotool(['key', 'Return'])

    logger.info('Enter build output directory')
    xdotool(['key', 'Tab'])
    xdotool(['key', 'alt+n'])
    xdotool(['type', output_name])

    wait_for_window('print', 'Print')
    logger.info('Print!')
    xdotool(['key', 'alt+p'])

    logger.info('Wait before shutdown')
    time.sleep(10)

def export_schematic(sch_name):
    """Print schematics to file in PDF format

    Keyword arguments:
    sch_name -- The schematic file name including relative path
    from project_root WITHOUT extension.
    """
    sch_file_path = os.path.dirname(sch_name)
    sch_file_name = os.path.basename(sch_name)
    schematic_file = os.path.join(project_root, sch_name+'.sch')

    output_dir = os.path.join(project_root, 'CI-BUILD/'+os.path.basename(sch_name)+'/SCH')
    file_util.mkdir_p(output_dir)

    #TODO: Remove when stable or add debug flag
    screencast_output_file = os.path.join(output_dir, 'export_schematic_screencast.ogv')
    schematic_output_pdf_file = os.path.join(output_dir, sch_file_name+'.pdf')

    with recorded_xvfb(screencast_output_file, width=800, height=600, colordepth=24):
        with PopenContext(['eeschema', schematic_file], close_fds=True) as eeschema_proc:
            eeschema_plot_schematic(schematic_output_pdf_file)
            eeschema_proc.terminate()

if __name__ == '__main__':
    if not sys.argv[1]:
        raise ValueError('Schematic file was not provided!')

    export_schematic(sys.argv[1])
