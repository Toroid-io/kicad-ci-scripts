import sys
import os
import errno
import pcbnew
import argparse

def plot(args):
    board = pcbnew.LoadBoard(args.brd + '.kicad_pcb')

    # Load board and initialize plot controller
    pc = pcbnew.PLOT_CONTROLLER(board)
    po = pc.GetPlotOptions()
    po.SetPlotFrameRef(False)
    po.SetExcludeEdgeLayer(True)
    po.SetOutputDirectory(args.dir)
    po.SetUseGerberProtelExtensions(args.protel)

    # Load board and initialize excellon writter
    er = pcbnew.EXCELLON_WRITER(board)
    mirror = False
    minimalHeader = False
    offset = pcbnew.wxPoint(0, 0)
    merge_npth = not args.splitth
    er.SetOptions(mirror, minimalHeader, offset, merge_npth)
    metric_format = True
    er.SetFormat(metric_format)
    generate_drill = True
    generate_map = False

    if(args.drl or args.all):
        if(args.splitth):
            print('Plotting to ' + os.path.join(args.dir, os.path.basename(args.brd)) + '-PTH.drl')
            print('Plotting to ' + os.path.join(args.dir, os.path.basename(args.brd)) + '-NPTH.drl')
        else:
            print('Plotting to ' + os.path.join(args.dir, os.path.basename(args.brd)) + '.drl')
        er.CreateDrillandMapFilesSet(args.dir, generate_drill, generate_map)

    if(args.fcu or args.all):
        suffix = 'F.Cu'
        if(args.protel):
            suffix = ''
        # Set current layer
        pc.SetLayer(pcbnew.F_Cu)
        # Plot single layer to file
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GTL')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    if(args.bcu or args.all):
        suffix = 'B.Cu'
        if(args.protel):
            suffix = ''
        pc.SetLayer(pcbnew.B_Cu)
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GBL')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    if(args.fmask or args.all):
        suffix = 'F.Mask'
        if(args.protel):
            suffix = ''
        pc.SetLayer(pcbnew.F_Mask)
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GTS')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    if(args.bmask or args.all):
        suffix = 'B.Mask'
        if(args.protel):
            suffix = ''
        pc.SetLayer(pcbnew.B_Mask)
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GBS')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    if(args.fsilks or args.all):
        suffix = 'F.SilkS'
        if(args.protel):
            suffix = ''
        pc.SetLayer(pcbnew.F_SilkS)
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GTO')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    if(args.bsilks or args.all):
        suffix = 'B.SilkS'
        if(args.protel):
            suffix = ''
        pc.SetLayer(pcbnew.B_SilkS)
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GBO')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    if(args.edgecuts or args.all):
        suffix = 'Edge.Cuts'
        if(args.protel):
            suffix = ''
        pc.SetLayer(pcbnew.Edge_Cuts)
        pc.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, 'GML')
        print('Plotting to ' + pc.GetPlotFileName())
        pc.PlotLayer()

    pc.ClosePlot()


def mkdir_p(path):
    try:
        os.makedirs(os.path.abspath(path))
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main(argv):
   parser = argparse.ArgumentParser(description='Plot Gerber Files')
   parser.add_argument('--brd', nargs='?', dest='brd', required=True)
   parser.add_argument('--dir', nargs='?', dest='dir', default='./')
   parser.add_argument('--all', action='store_true', dest='all', default=False)
   parser.add_argument('--protel', action='store_true', dest='protel', default=False)

   parser.add_argument('--fcu', action='store_true', dest='fcu', default=False)
   parser.add_argument('--bcu', action='store_true', dest='bcu', default=False)
   parser.add_argument('--fmask', action='store_true', dest='fmask', default=False)
   parser.add_argument('--bmask', action='store_true', dest='bmask', default=False)
   parser.add_argument('--fsilks', action='store_true', dest='fsilks', default=False)
   parser.add_argument('--bsilks', action='store_true', dest='bsilks', default=False)
   parser.add_argument('--edgecuts', action='store_true', dest='edgecuts', default=False)
   parser.add_argument('--drl', action='store_true', dest='drl', default=False)
   parser.add_argument('--splitth', action='store_true', dest='splitth', default=False)

   args = parser.parse_args(argv)
   args.dir = os.path.abspath(os.path.join(os.getcwd(), args.dir))

   args.brd = os.path.join(os.getcwd(), args.brd)

   mkdir_p(args.dir)
   os.chdir(args.dir)

   plot(args)

if __name__ == '__main__':
    main(sys.argv[1:])
