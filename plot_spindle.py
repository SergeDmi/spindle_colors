# Importing necessary modules
from pyx import *
from pyx.graph import graphxy, data, axis
from pyx.graph.axis import painter, tick
from pyx.deco import barrow
from numpy import *
from os import path
import sys
# sorry if the "import *" hurts your soul

"""
python plot_spindle.py file_name [other file_names] [-colorbar]:

plots the data in file_name into plot_name.pdf (+.eps)
into a beautiful schematic hightlighting the relevant information
i.e. the length, coded both in length and color

The data into file_name should be space-separated data.
Anterior pole-kinetochore distance | Posterior kinetochore-pole distance | 
    Anterior 95% confidence interval | Posterior 95% confidence interval

Options : 
-colorbar : also plots a reference colorbar

This code relies on python PyX : https://pyx-project.org/
This codes requires python modules pyx & numpy 
pyx requires a latex distribution

Copyright Serge Dmitrieff, www.biophysics.dev
Please acknowledge/cite the relevant article if you use this code.

"""

## UGLY : Hard coded parameters
# I know it's bad but do you really really want to parse a parameter file for that ?
# These are the general 'hard-coded' parameters
## 1- Boundaries of the graph (in µm)
LEFT=-8
RIGHT=8
## 2- Color sensitivity : we expect lengths between 6 and 8
MIN_DX=-2
MAX_DX=0.5
# the color for lengths <MINX and >MAXX will be set to MINX and MAXX respectively
## 3- We can invert the gradient if need be
INVERT_GRADIENT=1
## 4- Here is the gradient.btw
GRADIENT=color.gradient.Jet
#GRADIENT=color.rgbgradient.BlueRed
#GRADIENT=color.gradient.Jet
## 5- Size of the bars ... shame
SIZE_BARS=3.0


# This is the magic part !
def get_color(dl):
    # dl is the length change
    ix=(dl-MIN_DX)/(MAX_DX-MIN_DX)
    # ix should be between 0 and 1 to define the color
    if ix<=0:
        ix=0.0
    elif ix>=1:
        ix=1.0
    if INVERT_GRADIENT:
        ix=1.0-ix
    # we use a preset color gradient from pyton PyX
    return GRADIENT.getcolor(param=ix)

# generates a name for the PDF/EPS file
def get_out_name(fname):
    # getting filename without extension and path
    basename,ext=path.splitext(path.basename(fname))
    # we keep only the name after the first underscore (if any)
    # this is really silly to do without any option
    u_pos=basename.find('_')
    if u_pos>0:
        basename=basename[u_pos:]
    # getting path
    folder=path.dirname(fname)
    # putting together path and filename,
    return path.join(folder,'plot%s' % (basename))

# This is the part we do the plot
def do_nice_plot(fname):
    # first, we load the lengths from the file
    lengths = loadtxt(fname)
    nl, nc = lengths.shape
    # finding left and right lengths at t=0
    x_left=-lengths[0,0]
    x_right=lengths[0,1]

    # Variables we unfortunately need
    graph_height=3
    graph_distance=nl+1.0
    epsilon=0.007
    estimated_thickness=graph_height/graph_distance
    # We correct line thickness
    line_thickness=estimated_thickness+epsilon
    # Magic to get the size of the line at the end of the bar
    dh=estimated_thickness/1.5
    DH=array([-dh,dh])*SIZE_BARS
    DHUP=DH
    DHDN=DH
    #DHUP=array([0,dh])*3.6
    #DHDN=array([-dh,0])*3.6
    end_color=color.gray(0.1)
    # then we prepare the looks !
    # We make a decorator for the time axis
    pt = painter.regular(basepathattrs=[barrow.normal],
                    outerticklength=painter.ticklength.normal,
                    titledist=0.3) # discarded options : horizontal text titledirection=rotatetext.parallel , titlepos=0.95,
    # this are the ticks for the x axis
    ticks = [graph.axis.tick.tick(x,label="%s" %(x) ) for x in [LEFT,RIGHT]]
    ticks.append(graph.axis.tick.tick(0,label="0"  )  )


    # creating the canvas... gotta be done.
    c = canvas.canvas()
    # We create a graph
    f = c.insert(graph.graphxy(width=7,height=graph_height, xpos=0, ypos=0,key=None,y2=None,x2=None,xaxisat=nl+0.5,
                        x=graph.axis.linear(min=LEFT,max=RIGHT,title=None,parter=None,manualticks=ticks),    # defines its x axis
                        y=graph.axis.linear(min=-1, max=nl,title=r"time",reverse=1,parter=None,painter=pt))) # defines its y axis

    # We will iterate over each line of length, i.e. over each time step
    for i,res in enumerate(lengths):
        # Let's use the colors
        left_color=get_color(res[0]+x_left)
        right_color=get_color(res[1]-x_right)
        # And prepare the segments to plot
        left=[x_left,x_left+res[0]]
        right=[x_right,x_right-res[1]]
        # Segments plotted as thick lines
        f.plot([graph.data.points([(x,i) for j, x in enumerate(left) ], x=1, y=2,title=None)],
            [graph.style.line([style.linestyle.solid, style.linewidth(line_thickness),left_color])])
        f.plot([graph.data.points([(x,i) for j, x in enumerate(right) ], x=1, y=2,title=None)],
            [graph.style.line([style.linestyle.solid, style.linewidth(line_thickness),right_color])])

        # Small lines at the end of the segments
        f.plot([graph.data.points([(left[1] ,i+h) for h in DHUP ], x=1, y=2,title=None)],
            [graph.style.line([style.linestyle.solid, style.linewidth.thick,end_color])])
        f.plot([graph.data.points([(right[1],i+h) for h in DHDN ], x=1, y=2,title=None)],
            [graph.style.line([style.linestyle.solid, style.linewidth.thick,end_color])])

        # the small markers on the outside
        # for now, doesn't look good
        #f.plot([graph.data.points([(left[0],i)], x=1, y=2,title=None)],
        #    [graph.style.symbol(graph.style.symbol.circle, symbolattrs=[deco.filled([left_color]),deco.stroked([color.rgb.black])], size=0.04)])
        #f.plot([graph.data.points([(right[0],i)], x=1, y=2,title=None)],
        #    [graph.style.symbol(graph.style.symbol.circle, symbolattrs=[deco.filled([left_color]),deco.stroked([color.rgb.black])], size=0.04)])

        # Now plotting the black errorbars
        #left :
        f.plot([graph.data.points([(left[1],i+dh,lengths[i,3])], x=1, y=2, dx=3,title=None)],
            #[graph.style.symbol(graph.style.symbol.circle, symbolattrs=[color.rgb.black], size=0.01),graph.style.errorbar(errorbarattrs=[color.rgb.black,style.linewidth.thin])])
            [graph.style.errorbar(errorbarattrs=[color.rgb.black,style.linewidth.thin])])
        # right :
        f.plot([graph.data.points([(right[1],i-dh,lengths[i,2])], x=1, y=2, dx=3,title=None)],
            #[graph.style.symbol(graph.style.symbol.circle, symbolattrs=[color.rgb.black], size=0.01),graph.style.errorbar(errorbarattrs=[color.rgb.black,style.linewidth.thin])])
            [graph.style.errorbar(errorbarattrs=[color.rgb.black,style.linewidth.thin])])
    return c


def do_nice_colorbar():
    fname='colorbar'
    # Parameters for the color bar
    dy=0.1
    yy=array([0,dy]) #vertical segment
    bar_thickness=0.3
    num_colors=30
    c = canvas.canvas()
    # We create a graph
    f = c.insert(graph.graphxy(width=5,height=1, key=None,
                        x=graph.axis.linear(min=MIN_DX-bar_thickness/3.0,max=MAX_DX+bar_thickness/3.0,title=r"Distance"),    # defines its x axis
                        y=graph.axis.linear(min=-0.01, max=dy+0.01,title=None,parter=None)))
                        #y2=graph.axis.linear(min=0, max=(nc-0.5)*dy,title=None,parter=None,painter=None))) # defines its y axis
    #distances corresponding to colors
    distances=linspace(MIN_DX,MAX_DX,num_colors)
    for dist in distances:
        color=get_color(dist)
        f.plot([graph.data.points([(dist,y) for y in yy ], x=1, y=2,title=None)],
            [graph.style.line([style.linestyle.solid, style.linewidth(bar_thickness),color])])
    c.writePDFfile(fname)
    c.writeEPSfile(fname)   




# For a given file, we try to plot it and save the plot in the same folder
def plot_and_save(fname):
    # Let's try !
    try:
        # do the plot
        canevas=do_nice_plot(fname)
        # get the name
        out_name=get_out_name(fname)
        # save to pdf and EPS
        canevas.writePDFfile(out_name)
        canevas.writeEPSfile(out_name)
        return 1
    except:
        # Uncomment the next line to see where the error happened
        # canevas=do_nice_plot(fname)
        # Oh, no, we failed ! Are you sure the data was in the right format ?
        return 0


if __name__ == '__main__':
    # Checking if we were given the filenames in arguments
    if len(sys.argv)<2:
        raise ValueError('Not enough arguments (requires at least one filename or option)')
    # Yes !
    inputs=sys.argv[1:]
    arguments=[name for name in inputs if name.startswith('-')]
    names=[name for name in inputs if not name in arguments]

    # We try to plot for each file
    # results should be an array of 1 (success) or 0 (fail)
    results=[plot_and_save(fname) for fname in names]
    # Let's wrap it up now !
    print('\nManaged to create %s/%s plots ' %(sum(results),len(results)))
    if sum(results)<len(results):
        [print('-- Could not plot from %s' %names[i]) for i,res in enumerate(results) if res==0]

    if '-colorbar' in arguments:
        do_nice_colorbar()
