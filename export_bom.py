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

def eeschema_export_bom(output_directory, wait_init):
    # Give enough time to load the libraries
    time.sleep(float(wait_init))

    logger.info('Open Tools->Generate Bill Of Materials')
    xdotool(['key', 'alt+t'])
    xdotool(['key', 'm'])

    logger.info('Run generate')
    wait_for_window('plot', 'Bill of Material')
    xdotool(['search', '--name', 'Bill of Material', 'windowfocus'])
    xdotool(['key', 'Return'])

    logger.info('Wait before shutdown')
    time.sleep(5)

def export_bom(prjfile, wait_init):
    """Creates the BOM in xml

    Keyword arguments:
    prjfile -- The project file name including relative path
    from project_root WITHOUT extension.
    """
    sch_file_path = os.path.dirname(prjfile)
    sch_file_name = os.path.basename(prjfile)
    schematic_file = os.path.join(project_root, prjfile+'.sch')

    output_dir = os.path.join(project_root,'CI-BUILD/'+sch_file_name+'/BOM')
    file_util.mkdir_p(output_dir)

    screencast_output_file = os.path.join(output_dir, 'export_bom_screencast.ogv')

    with recorded_xvfb(screencast_output_file, width=800, height=600, colordepth=24):
        with PopenContext(['eeschema', schematic_file], close_fds=True) as eeschema_proc:
            eeschema_export_bom(output_dir, wait_init)
            eeschema_proc.terminate()

    # Copy xml BOM to CI Folder
    subprocess.check_call([
        'mv',
        prjfile+'.xml',
        output_dir,
    ])

    # Copy csv BOM to CI Folder
    subprocess.check_call([
        'mv',
        prjfile,
        output_dir+'/'+sch_file_name+'.csv',
    ])

if __name__ == '__main__':
    wait = 10
    if len(sys.argv) < 2:
        raise ValueError('Project file was not provided!')
    elif len(sys.argv) > 2:
        wait = sys.argv[2]

    export_bom(sys.argv[1], wait)

