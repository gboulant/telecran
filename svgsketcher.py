# coding: utf-8

__author__ = "gboulant, nov. 2022"

import os
import copy
import math
import tempfile

import environ

headPattern = "<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d'>"
linePattern = "<line x1='%.2f' y1='%.2f' x2='%.2f' y2='%.2f' style='%s'/>"
textPattern = "<text x='%.2f' y='%.2f' style='%s'>%s</text>"
rectPattern = "<rect x='%.2f' y='%.2f' width='%.2f' height='%.2f' style='%s'/>"
circPattern = "<circle cx='%.2f' cy='%.2f' r='%.2f' style='%s'/>"
footPattern = "</svg>"

class SvgException(Exception): pass
def assertIsInstance(value, expectedType):
    if not isinstance(value, expectedType):
        raise SvgException("An instance of %s is expected"%expectedType)

# =======================================================================
# The drawing pencil for graphical rendering (see docstring)

def cssvalue(data):
    if data is None: return "none"
    return data

class SvgPencil:
    """The pencil is the tool used by the sketcher for the graphical
    rendering of the sketching. The sketcher defines only the geometry
    of the drawing (see SvgSketcher) and uses the pencil for the
    rendering (color, width, font, etc).
    
    You can think of the SvgPencil really as a pencil, i.e. when
    composing a SVG sketch you can prepare a set of pencils and choose
    (associate to the skecther) the pencil of your choice depending on
    the expected rendering for the current drawing.
    """
    defaultLineWidth = 2
    defaultLineColor = "black"
    defaultFontFamily = "Cursive"
    defaultFontWeight = "normal"
    defaultFontSize = 20
    
    drawStylePattern = "stroke: %s; stroke-width: %d; fill: %s"
    textStylePattern = "font-family:%s; font-size:%s; font-weight:%s; fill: %s"

    def __init__(self):
        self.lineColor   = SvgPencil.defaultLineColor
        self.lineWidth   = SvgPencil.defaultLineWidth
        self.fillColor   = self.lineColor
        self.fontFamily  = SvgPencil.defaultFontFamily
        self.fontSize    = SvgPencil.defaultFontSize
        self.fontWeight  = SvgPencil.defaultFontWeight
        self.fontColor   = self.lineColor
        self._style =  None

    def forceStyle(self, style):
        self._style =  style

    def resetStyle(self):
        self._style = None

    def drawStyle(self):
        """Return the style value (css string) for drawing. The style string is
        created from the values of the pencil drawing parameters. If forceStyle
        is used, then the given value for style is considered instead (whatever
        the value of the pencil parameters are)"""
        if self._style is not None: return self._style
        return SvgPencil.drawStylePattern%(
            cssvalue(self.lineColor),
            cssvalue(self.lineWidth),
            cssvalue(self.fillColor))

    def textStyle(self):
        """Return the style value (css string) for writing texts. The style
        string is created from the values of the pencil font parameters. If
        forceStyle is used, then the given value for style is considered instead
        (whatever the value of the pencil parameters are)"""
        if self._style is not None: return self._style
        return SvgPencil.textStylePattern%(
            cssvalue(self.fontFamily),
            cssvalue(self.fontSize),
            cssvalue(self.fontWeight),
            cssvalue(self.fontColor))

    def clone(self):
        return copy.copy(self)

    def __repr__(self):
        s = "lineColor : %s\n"%cssvalue(self.lineColor)
        s+= "lineWidth : %s\n"%cssvalue(self.lineWidth)
        s+= "fillColor : %s"%cssvalue(self.fillColor)
        return s

# =======================================================================
# The user local coordinates system (see docstring)

class CoordinatesSystem:
    """
    CoordinatesSystem can be used to define a user coordinates system on
    the sketching canvas. A coordinates system allows the user to give
    position regarding to user coordinates x, y instead of the
    pixels native coordinates of the canvas, i.e. the number of pixels
    from top left corner along the horizontal axis (horizontal
    coordinates named hcoord) and the vertical axis (vertical
    coordinates named vcoord).
    
    The sketcher distinguishes two coordinates systems:
     
    1/ the SVG canvas native coordinates system, in which a position is
       defined by the number of pixels from top left corner along the
       horizontal and vertical axis respectively, with vertical axis oriented
       from top to bottom. In this coordinates system, the origin O is
       at the top left of the canvas, the X axis oriented on the right, and
       the Y axis toward the bottom.

    2/ the user coordinates system, where a position is defined by two
       coordinates (x, y) respect to an origin O and unit vector axis Ox and
       Oy. The position of O could be anywhere in the canvas, the length unit
       can be choosen by the user (not pixels), and the orientation of unit
       vector could be different, in particular a common convention is to
       consider an y axis oriented from bottom to top (inverse than the native
       orientation).

    The user gives coordinates considering a position in the user coordinates
    system, but the SVG elements placement requires coordinates given in the
    SVG canvas coordinates system (number of pixel from top left corner.
    
    Then the SvgSketcher uses the coordinates system to translate the
    user coordinates x, y in pixel native coordinates hcoord, vcoord for
    the placement of the element on the SVG canvas.
    """

    def __init__(self, Ohcoord=0, Ovcoord=0, xyunit=1, xinverse=False, yinverse=False):
        self.Ohcoord = Ohcoord    # horizontal distance from left (pixels)
        self.Ovcoord = Ovcoord    # vertical distance from top (pixels)
        self.xyunit = xyunit      # length unit (pixels by unit)
        self.xinverse = xinverse  # set to True for an x axis oriented to left 
        self.yinverse = yinverse  # set to True for an y axis oriented to top 

        self.underlying_cnvwidth = None   # canvas width with which the coordinates system has been determined 
        self.underlying_cnvheight = None  # canvas height with which the coordinates system has been determined
        # Note that this parameters concern only the creation process
        # (factory function) of the coordinates system. They are not
        # used for the coordinates transformation.

    def cnvCoordinates(self, x,y):
        """Return the position of the point in the canvas native coordinates
        system, i.e. number of pixels from top left corner along the horizontal
        and vertical axis (oriented to the bottom) respectivelly"""
        xsign = 2 * ( 0.5 - int(self.xinverse) )
        ysign = 2 * ( 0.5 - int(self.yinverse) )
        hcoord = self.Ohcoord + xsign * self.xyunit * x
        vcoord = self.Ovcoord + ysign * self.xyunit * y
        return hcoord, vcoord

    def xyCoordinates(self, hcoord, vcoord):
        xsign = 2 * ( 0.5 - int(self.xinverse) )
        ysign = 2 * ( 0.5 - int(self.yinverse) )
        x = (hcoord - self.Ohcoord)/(xsign * self.xyunit)
        y = (vcoord - self.Ovcoord)/(ysign * self.xyunit)
        return x, y
        
    def cnvScaling(self, length):
        return self.xyunit * length

    def xyScaling(self, pixels):
        return float(pixels) / self.xyunit

    # -----------------------------------------------------------------------------------
    # List of factory functions, i.e. functions that create predefined
    # coordinates systems for common configurations, and fitted for a
    # target canvas size. For most factory functions, you have to
    # specify the xyunit, i.e. the number of pixel of the length unit of
    # the coordinates system. But if more convenience for your use case,
    # tou may determine this xyunit from the xyrange, i.e. the whole
    # size of the canvas in the length unit (using first the
    # xyrange2xyunit function). 
    @staticmethod
    def xyrange2xyunit(xyrange, cnvsize):
        """Determine the xy unit from a xy range, considering a canvas
        of the size cnvsize. The xyunit is the number of pixel by unit,
        while the xyrange is the measure in units of the canvas size
        (given in pixel). For example, if we have a canvas of size 600
        pixels, and we want to define a length unit so that the width of
        the canvas is 10 units, then the xyunit is 600/10 = 60 pixels/unit."""
        return float(cnvsize)/xyrange

    @staticmethod
    def Centered(cnvwidth, cnvheight, xyunit=1, yinverse = True):
        Ohcoord = int(0.5 * cnvwidth)
        Ovcoord = int(0.5 * cnvheight)
        csys = CoordinatesSystem(Ohcoord, Ovcoord, xyunit=xyunit, yinverse=yinverse)
        # keep memory of the input canvas sizes
        csys.underlying_cnvwidth = cnvwidth
        csys.underlying_cnvheight = cnvheight
        return csys

    @staticmethod
    def _offsetValue(offset,range):
        """The offset can be specified as a percentage of the canva
        size using a string like '2%'. In such a case the value is
        2*range (a percentage of the given range). In all other cases,
        the value is considered as an absolute value"""
        if isinstance(offset,str) and offset.endswith('%'):
            value = float(offset[:-1]) * range / 100
        else:
            value = float(offset)
        return value

    @staticmethod
    def BoundingBy(xypoints, cnvsize, xoffset="1%", yoffset="1%", yinverse = True):
        xmin, ymin, xmax, ymax = boundingBox(xypoints)
        xoffset = CoordinatesSystem._offsetValue(xoffset,xmax-xmin)
        yoffset = CoordinatesSystem._offsetValue(yoffset,ymax-ymin)
        uw = xmax - xmin + 2*xoffset # width in the user length unit
        uh = ymax - ymin + 2*yoffset # height in the user length unit
        if uw > uh:
            cnvwidth = cnvsize
            cnvheight = cnvsize * float(uh)/uw
            xyunit = cnvsize/uw
        else:
            cnvwidth = cnvsize * float(uw)/uh
            cnvheight = cnvsize
            xyunit = cnvsize/uh

        # WRN: correct only in the case where yinverse is True
        yinverse = True # force to True in this version
        Ohcoord = -(xmin - xoffset) * xyunit
        Ovcoord = cnvheight + (ymin - yoffset)*xyunit

        csys = CoordinatesSystem(Ohcoord, Ovcoord, xyunit=xyunit, yinverse=yinverse)

        # keep memory of the computed canvas sizes
        csys.underlying_cnvwidth = cnvwidth
        csys.underlying_cnvheight = cnvheight
        return csys

    @staticmethod
    def BottomLeft(cnvheight, xyunit=1, yinverse = True):
        Ohcoord = 0
        Ovcoord = cnvheight
        csys = CoordinatesSystem(Ohcoord, Ovcoord, xyunit=xyunit, yinverse=yinverse)
        # keep memory of the computed canvas sizes
        csys.underlying_cnvheight = cnvheight
        return csys

    @staticmethod
    def TopLeft(xyunit=1):
        Ohcoord = 0
        Ovcoord = 0
        csys = CoordinatesSystem(Ohcoord, Ovcoord, xyunit=xyunit)
        return csys

# =======================================================================
# The sketcher

class SvgSketcher:
    defaultCanvasWidth  = 600. # pixels
    defaultCanvasHeight = 400. # pixels
    pointRadiusScale = 1.5  # scale factor on lineWidth
    defaultPencil = None
    defaultCoordinatesSystem = None

    def __init__(self,
                 cnvwidth = defaultCanvasWidth, cnvheight = defaultCanvasHeight,
                 pencil = defaultPencil, coordinatesSystem = defaultCoordinatesSystem):

        self.x = 0.
        self.y = 0.
        self.body = ""
        self.backgroundColor = None # transparent
        self.cnvwidth = cnvwidth
        self.cnvheight = cnvheight

        if pencil is None: self.pencil = SvgPencil()
        else: self.pencil = pencil

        if coordinatesSystem is None: self.coordinatesSystem = CoordinatesSystem.TopLeft()
        else: self.coordinatesSystem = coordinatesSystem

    def withPencil(self, pencil):
        assertIsInstance(pencil, SvgPencil)
        self.pencil = pencil
        return self

    def withCoordinatesSystem(self, coordinatesSystem):
        assertIsInstance(coordinatesSystem, CoordinatesSystem)
        self.coordinatesSystem = coordinatesSystem
        return self

    def toSVG(self):
        s = headPattern % (self.cnvwidth, self.cnvheight) + "\n"
        if self.backgroundColor is not None:
            # Add a full size rectangle as first element with fill color set to
            # the background color (classical method for SVG background color)
            s+="<rect width='100%%' height='100%%' fill='%s'/>\n"%self.backgroundColor
        s+= self.body
        s+= footPattern
        return s

    def __repr__(self):
        return self.toSVG()

    def clear(self):
        self.body = ""

    def save(self,filepath=None):
        if filepath==None: filepath = svgTempPath()
        with open(filepath,'w') as svgfile:
            svgfile.write(self.toSVG())        
        return filepath

    def display(self):
        SvgViewer.display(self.toSVG())

    # ---------------------------------------------------------
    def _cnvCoordinates(self,x,y):
        return self.coordinatesSystem.cnvCoordinates(x,y)

    def _cnvScaling(self, length):
        return self.coordinatesSystem.cnvScaling(length)

    def unitaxis(self, length=1.):
        "draw the unit vectors as defined by the coordinates system"
        self.moveTo(-0.1, 0.)
        self.hlineTo(length)
        self.moveTo(0., -0.1)
        self.vlineTo(length)

    def xyboundaries(self):
        """Returns the boundaries of the (cnvwidth x cnvheight) canvas in
        user coordinates system: xmin, xmax, ymin, ymax. These values
        depends on 1/ the size of the canvas and 2/ the user coordinates
        system (placement of the origin, and length unit).
        
        It is be computed by retrieving the position of the top left
        corner and the bottom rigth corner in the user coordinates
        system"""
        c1x, c1y = self.coordinatesSystem.xyCoordinates(0,0)
        c2x, c2y = self.coordinatesSystem.xyCoordinates(self.cnvwidth, self.cnvheight)

        if c1x < c2x:
            xmin = c1x
            xmax = c2x
        else:
            xmin = c2x
            xmax = c1x

        if c1y < c2y:
            ymin = c1y
            ymax = c2y
        else:
            ymin = c2y
            ymax = c1y

        return xmin, xmax, ymin, ymax

    def boundaries(self, xoffset="0%", yoffset="0%"):
        xmin, xmax, ymin, ymax = self.xyboundaries()
        xoffset = CoordinatesSystem._offsetValue(xoffset,xmax-xmin)
        yoffset = CoordinatesSystem._offsetValue(yoffset,ymax-ymin)
        self.rectangle(
            xmin+xoffset, ymin+yoffset,
            xmax-xoffset, ymax-yoffset)

    # ---------------------------------------------------------
    # Turtle-like drawing methods
    def moveTo(self,x,y):
        """Move to the coordinates x, y without drawing"""
        self.x = x
        self.y = y

    def lineTo(self,x,y):
        px1, py1 = self._cnvCoordinates(self.x,self.y)
        px2, py2 = self._cnvCoordinates(x,y)
        style = self.pencil.drawStyle()
        self.body += linePattern % (px1, py1, px2, py2, style) + "\n"
        self.x = x
        self.y = y

    def hlineTo(self,x):
        self.lineTo(x,self.y)

    def vlineTo(self,y):
        self.lineTo(self.x,y)

    def hlineLong(self,dx):
        self.lineTo(self.x+dx,self.y)

    def vlineLong(self,dy):
        self.lineTo(self.x,self.y+dy)

    # -------------------------------------------------------------
    # Sketching primitive functions
    def point(self, x, y, color=None, label=None):
        # Technically, we draw a filled circle with no border, with radius
        # proportional to the lineWidth with factor SvgSketcher.pointRadiusScale
        pcx, pcy = self._cnvCoordinates(x, y)
        pr = self.pencil.lineWidth * SvgSketcher.pointRadiusScale

        pencil = self.pencil.clone()
        pencil.lineColor = None
        if color is not None: pencil.fillColor = color
        
        style = pencil.drawStyle()
        self.body += circPattern % (pcx, pcy, pr, style) + "\n"

        if label is None: return
        # On décale le label d'une distance proportionnelle au rayon du
        # cercle symbolisant le point, à exprimer dans l'unité du
        # système de coordonnées:
        dx = dy = float(1.5*pr) / self.coordinatesSystem.xyunit
        self.text(x+dx, y+dy, value=label, color=color)

    def text(self, x, y, value, size=None, color=None):
        pencil = self.pencil.clone()
        if color is not None: pencil.fontColor = color
        if size is not None: pencil.fontSize = size
        px, py = self._cnvCoordinates(x, y)
        style = pencil.textStyle()
        self.body += textPattern % (px, py, style, value) + "\n"

    def circle(self, cx, cy, radius, fill=False, border=True):
        pcx, pcy = self._cnvCoordinates(cx, cy)
        pr = self._cnvScaling(radius)
        pencil = self.pencil.clone()
        if not fill: pencil.fillColor = None
        if not border: pencil.lineColor = None
        style = pencil.drawStyle()
        self.body += circPattern % (pcx, pcy, pr, style) + "\n"

    def rectangle(self, x1, y1, x2, y2, fill=False, border=True):
        """Add a rectangle in the canvas."""
        px1, py1 = self._cnvCoordinates(x1, y1)
        px2, py2 = self._cnvCoordinates(x2, y2)

        if px1 > px2: px1, px2 = px2, px1
        if py1 > py2: py1, py2 = py2, py1

        plx = px2-px1
        ply = py2-py1

        pencil = self.pencil.clone()
        if not fill: pencil.fillColor = None
        if not border: pencil.lineColor = None
        style = pencil.drawStyle()
        self.body += rectPattern % (px1, py1, plx, ply, style) + "\n"

    def segment(self, x1, y1, x2, y2):
        self.moveTo(x1,y1)
        self.lineTo(x2,y2)

    def polygon(self, points, closed=False):
        """
        The variable points is a list of point coordinates, each point
        coordinates is a tuple (x,y).
        """
        p = points[0]
        self.moveTo(p[0],p[1])
        for p in points[1:]: self.lineTo(p[0],p[1])
        if closed: self.lineTo(points[0][0],points[0][1])

    # ---------------------------------------------------------
    # Factory and/or adapter functions

    def withBottomLeftCoordinates(self,xrange=None):
        """
        Set a coordinates system whose origin is at the bottom left
        corner of the canvas and the y axis oriented upward.

        If xrange is not defined (None), we consider a value equal to
        the canvas width, i.e. xrange=cnvwidth, which means that we
        consider the native pixel unit (the coordinates values corespond
        to pixels)"""
        if xrange is None: xyunit = 1. 
        else: xyunit = CoordinatesSystem.xyrange2xyunit(xrange, self.cnvwidth)
        csys = CoordinatesSystem.BottomLeft(self.cnvheight, xyunit=xyunit)        
        return self.withCoordinatesSystem(csys)

    @staticmethod
    def newBottomLeftCoordinates(cnvwidth=defaultCanvasWidth,cnvheight=defaultCanvasHeight,xrange=None):
        return SvgSketcher(cnvwidth,cnvheight).withBottomLeftCoordinates(xrange)

    def withTopLeftCoordinates(self,xrange=None):
        """
        Set a coordinates system whose origin is at the top left
        corner of the canvas and the y axis oriented downward. 

        If xrange is not defined (None), we consider a value equal to
        the canvas width, i.e. xrange=cnvwidth, which means that we
        consider the native pixel unit (the coordinates values corespond
        to pixels)"""
        if xrange is None: xyunit = 1. 
        else: xyunit = CoordinatesSystem.xyrange2xyunit(xrange, self.cnvwidth)
        csys = CoordinatesSystem.TopLeft(xyunit=xyunit)        
        return self.withCoordinatesSystem(csys)

    @staticmethod
    def newTopLeftCoordinates(cnvwidth=defaultCanvasWidth,cnvheight=defaultCanvasHeight,xrange=None):
        return SvgSketcher(cnvwidth,cnvheight).withTopLeftCoordinates(xrange)

    def withCenteredCoordinates(self,xrange=None):
        """
        Set a coordinates system whose origin is at the bottom left
        corner of the canvas and the y axis oriented upward.

        If xrange is not defined (None), we consider a value equal to
        the canvas width, i.e. xrange=cnvwidth, which means that we
        consider the native pixel unit (the coordinates values corespond
        to pixels)"""
        if xrange is None: xyunit = 1. 
        else: xyunit = CoordinatesSystem.xyrange2xyunit(xrange, self.cnvwidth)
        csys = CoordinatesSystem.Centered(self.cnvwidth, self.cnvheight, xyunit=xyunit)        
        return self.withCoordinatesSystem(csys)

    @staticmethod
    def newCenteredCoordinates(cnvwidth=defaultCanvasWidth,cnvheight=defaultCanvasHeight,xrange=None):
        return SvgSketcher(cnvwidth,cnvheight).withCenteredCoordinates(xrange)

    @staticmethod
    def newBoundedByCoordinates(xycoordinates, xoffset="1%", yoffset="1%", cnvsize=defaultCanvasWidth):
        csys = CoordinatesSystem.BoundingBy(xycoordinates, cnvsize, xoffset, yoffset)
        cnvwidth = csys.underlying_cnvwidth
        cnvheight = csys.underlying_cnvheight
        return SvgSketcher(cnvwidth, cnvheight,coordinatesSystem=csys)

    def withNativeCoordinates(self):
        """Set a coordinates system that corresponds to the canvas
        native coordinates, i.e. an origin at the top left corner, y
        axis oriented downward, and coordinates in pixels"""
        return self.withTopLeftCoordinates()

    @staticmethod
    def newNativeCoordinates(cnvwidth=defaultCanvasWidth,cnvheight=defaultCanvasHeight):
        return SvgSketcher(cnvwidth,cnvheight).withNativeCoordinates()


def cnvWidthHeight(xywidth, xyheight, cnvsize):
    """Returns the canvas width and height (cnvwidth and cnvheight in
    pixels) in the same aspect ratio than the input xywidth and xyheight
    (values given in a user length unit), and with a maximal size of
    cnvsize (weither cnvwidth or cnvheight depending on the highest
    dimension"""
    if xywidth > xyheight:
        cnvwidth = int(cnvsize)
        cnvheight = int(cnvsize * float(xyheight)/xywidth)
    else:
        cnvwidth = int(cnvsize * float(xywidth)/xyheight)
        cnvheight = int(cnvsize)
    return cnvwidth, cnvheight

# =======================================================================

class SvgSketcherWrapper:
    def __init__(self, sketcher):
        assertIsInstance(sketcher, SvgSketcher)
        self.sketcher = sketcher

    def clear(self):
        self.sketcher.clear()

    def display(self):
        self.sketcher.display()

    def save(self,filepath=None):
        self.sketcher.save(filepath)

    def __repr__(self):
        return str(self.sketcher)

# =======================================================================
# Additional tools for SVG data management

class SvgViewer:
    """The viewer can be used to display a graphical representation of
    a SVG text (whatever the sourcce of the text, created from the
    SvgSketcher or load from a svg file. It can display the text using
    different way depending on the context:
    
    - Default: executes an external program (system call execution)
    - Notebook: display in the notebook directly (IPython.display)
    """
    viewerpath = "eog"
    cmdpattern = "{viewerpath} {svgpath}"
    synchrocmd = True
    displayOn = environ.DISPLAY_ON

    @staticmethod
    def display(svgtext):
        if environ.inNotebook():
            SvgViewer._displayWithJupyterNotebook(svgtext)
        else:
            SvgViewer._displayWithExternalViewer(svgtext)
 
    @staticmethod
    def _displayWithExternalViewer(svgtext):
        if not SvgViewer.displayOn: return
 
        svgpath = svgTempPath()
        with open(svgpath, 'w') as svgfile: svgfile.write(svgtext)
        cmd = SvgViewer.cmdpattern.format(
            viewerpath = SvgViewer.viewerpath,
            svgpath    = svgpath)
        os.system(cmd)
        if SvgViewer.synchrocmd: os.unlink(svgpath)

    @staticmethod
    def _displayWithJupyterNotebook(svgtext):
        try:
            from IPython.display import display
            from IPython.core.display import HTML
            display(HTML(svgtext))
        except ImportError:
            print("ERR: it seems you are not in a jupyter notebook")            

def svg2png(svgpath, pngpath=None):
    # WRN: note that this function requires ImageMagick and its python binding
    # named Wand (on debian, install the packages imagemagick and python3-wand)
    try:
        from wand.image import Image
    except ImportError:
        print("ERR: svg2png requires imagemagick and python3-wand -> Cancel")
        return

    if pngpath is None:
        pngpath = "%s.png"%os.path.splitext(svgpath)[0]

    srcimg = Image(filename=svgpath)
    outimg = srcimg.convert('png')
    outimg.save(filename=pngpath)
    return pngpath

def svgTempPath():
    """Return a filepath generated using tempfile"""
    with tempfile.NamedTemporaryFile(suffix='.svg') as svgfile:
        filepath = svgfile.name
    return filepath

def boundingBox(xycoordinates):
    """Return the bounding coordinates for the specified list of (x,y)
    coordinates, i.e. the coordinates (xmi, ymin) and (xmax, ymax)
    respectively of the left bottom point and the top right point of the
    rectangle bounding the whole set of input points coordinates
    
    :param xycoordinates: list of (x,y) coordinates
    :return: xmin, ymin, xmax, ymax
    """
    assertIsInstance(xycoordinates, list)
    xmin, ymin = math.inf, math.inf
    xmax, ymax = -math.inf, -math.inf
    for xytuple in xycoordinates:
        x = xytuple[0]
        y = xytuple[1]
        if x > xmax: xmax = x
        if x < xmin: xmin = x
        if y > ymax: ymax = y
        if y < ymin: ymin = y
            
    return xmin, ymin, xmax, ymax
