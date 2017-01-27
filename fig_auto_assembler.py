import svgutils.transform as sg
from svgutils.transform import fromfile, from_mpl
from svgutils.compose import *
from svgutils.templates import *
import string
import sys, os

# Some util functions 
# A tiny function to show a inline SVG image
from IPython.display import SVG, display
def show_svg(path):
    display(SVG(path))
a4_width_cm = 21 
a4_height_cm = 29.7
def cm2inch(*tupl):
    inch = 2.54 # cm/inch
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)
def cm2px(*tupl):
    px = 0.0353  # px/cm
    if isinstance(tupl[0], tuple):
        return tuple(i/px for i in tupl[0])
    else:
        return tuple(i/px for i in tupl)
    
def add_label(figfile, fig_width, fig_height, label, loc=(15, 20), labelsize=12, outname="fig"):
    savedir = os.path.dirname(figfile)
    fig = sg.SVGFigure(str(fig_width)+"cm", str(fig_height)+"cm")
    figA = sg.fromfile(figfile)
    # get the plot objects
    plot1 = figA.getroot()
    # add text labels
    txt1 = sg.TextElement(loc[0], loc[1], label, size=labelsize, weight="bold")
    fig.append([plot1])
    fig.append([txt1])
    # save generated SVG files
    fig.save(outname)
    
def combine_horizontally(figfile1, figfile2, figwidth1, figheight1, figwidth2, figheight2, outfile="out.svg"):
    #create new SVG figure
    fig = sg.SVGFigure(str(figwidth1+figwidth2)+"cm", str(max(figheight1, figheight2))+"cm")
    figdir = os.path.dirname(figfile1)
    # load matpotlib-generated figures
    fig1 = sg.fromfile(figfile1)
    fig2 = sg.fromfile(figfile2)
    # get the plot objects
    plot1 = fig1.getroot()
    plot2 = fig2.getroot()
    plot1.moveto(0, 0, scale=1)
    plot2.moveto(cm2px(figwidth1), 0, scale=1)

    # append plots and labels to figure
    fig.append([plot1, plot2])
    # save generated SVG files
    fig.save(os.path.join(figdir, outfile))

def combine_vertically(figfile1, figfile2, figwidth1, figheight1, figwidth2, figheight2, outfile="out.svg"):
    #create new SVG figure
    fig = sg.SVGFigure(str(max(figwidth1, figwidth2))+"cm", str(figheight1+figheight2)+"cm")
    figdir = os.path.dirname(figfile1)
    # load matpotlib-generated figures
    fig1 = sg.fromfile(figfile1)
    fig2 = sg.fromfile(figfile2)
    # get the plot objects
    plot1 = fig1.getroot()
    plot2 = fig2.getroot()
    plot1.moveto(0, 0, scale=1)
    plot2.moveto(0, cm2px(figheight1), scale=1)

    # append plots and labels to figure
    fig.append([plot1, plot2])
    # save generated SVG files
    fig.save(os.path.join(figdir, outfile))
    
def generate_skeltonSVG(fname, w, h, label="X", loc=(15, 20), labelsize=12):
    Figure(str(w)+"cm", str(h)+"cm",
           Panel(Text(label, x=loc[0], y=loc[1], weight="bold", size=labelsize))
          ).save(fname)
#     fig = sg.SVGFigure(str(w)+"cm", str(h)+"cm")
#     # get the plot objects
#     plot1 = fig.getroot()
#     # save generated SVG files
#     fig.save(fname)
#     add_label(fname, w, h, label, loc=loc, labelsize=labelsize)
def combine_SVG(svgfig1, svgfig2, command, outfile):
    if command == "h":
        combine_horizontally(svgfig1.fname, svgfig2.fname, svgfig1.w, svgfig1.h, svgfig2.w, svgfig2.h, outfile)
        return(Svgfig(outfile, svgfig1.w+svgfig2.w, svgfig1.h))
    elif command == "v":
        combine_vertically(svgfig1.fname, svgfig2.fname, svgfig1.w, svgfig1.h, svgfig2.w, svgfig2.h, outfile)
        return(Svgfig(outfile, svgfig1.w, svgfig1.h+svgfig2.h))
    else:
        assert("Something Wrong!")
def return_sizes():
    return(21, 29.7)
class Svgfig(object):
    def __init__(self, fname, w, h):
        self.fname = fname
        self.w = w
        self.h = h
        self.a4_width_cm = 21 
        self.a4_height_cm = 29.7
class SVGFIG(Svgfig):
    def __init__(self, fname, fw, fh, fw_dict, fh_dict, command):
        super().__init__(fname, None, None)
        self.fig_dict = dict(); self.fname_dict = dict()
        self.command = command
        self.fw_dict = fw_dict; self.fh_dict = fh_dict
        self.figdir = os.path.dirname(fname)
        for key in self.fw_dict.keys():
            fname_ = os.path.join(self.figdir, os.path.splitext(os.path.basename(self.fname))[0]+key+".svg")
            self.fig_dict[key] = Svgfig(fname_, fw_dict[key], fh_dict[key])
            self.fname_dict[key] = fname_
    def generate_skeltonSVGs(self):
        for key in self.fw_dict.keys():
            generate_skeltonSVG(self.fname_dict[key], fw_dict[key], fh_dict[key], label = key)
    def assemble(self):
        command_list = list(purse_inverse_polish_command(self.command))
        print("command_list: ", command_list)
        tmpfile = os.path.join(os.path.dirname(self.fname), "tmp.svg")        
        op_symbols = "vh"
        stack = list()
        while command_list:
            symbol = command_list.pop(0)
            print("stack: ", stack)
            if symbol not in op_symbols:
                stack.append(symbol)
            else:
                command = symbol
                key2 = stack.pop()
                key1 = stack.pop()
                tmpsvg = combine_SVG(self.fig_dict[key1], self.fig_dict[key2], command, tmpfile)
                self.fig_dict["tmp"] = tmpsvg
                self.fname_dict["tmp"] = tmpfile
                stack.append("tmp")
        self.w = tmpsvg.w
        self.h = tmpsvg.h
        os.rename(tmpfile, self.fname) 
    def get_figinfo(self, label):
        w, h = self.fw_dict[label], self.fh_dict[label]
        fname = self.fig_dict[label].fname
        return(fname, w, h)
        
def process_inverse_polish_command(command):
    op_symbols = "vh"
    command_list = list(command); stack = list()
    while command_list:
        symbol = command_list.pop(0)
        if symbol not in op_symbols:
            stack.append(symbol)
        else:
            b = stack.pop()
            a = stack.pop()
            if symbol is "v":
                stack.append(symbol)
            elif symbol is "h":
                stack.append(symbol)
    return(stack)

def purse_inverse_polish_command(command):
    op_symbols ="vh()"
    op_priority_dict = {"v" : 0, "h" : 0, "(" : -1, ")" : -1}
    symbols = string.ascii_uppercase
    command_list = list(command); ipolish_stack= list(); op_stack = list()
    while command_list:
        symbol =  command_list.pop(0)
        if symbol not in op_symbols:
            ipolish_stack.append(symbol)
        elif symbol in op_symbols:
            if not op_stack:
                op_stack.append(symbol)
            elif symbol is "(":
                op_stack.append(symbol)
            elif symbol is ")":
                while True:
                    tmp_symbol = op_stack.pop()
                    if tmp_symbol is "(":
                        break
                    else:
                        ipolish_stack.append(tmp_symbol)
            else:
                if op_priority_dict[symbol] > op_priority_dict[op_stack[-1]]:
                    op_stack.append(symbol)
                else:
                    ipolish_stack.append(op_stack.pop()); op_stack.append(symbol)
    while op_stack:
        ipolish_stack.append(op_stack.pop())
    return(ipolish_stack)
