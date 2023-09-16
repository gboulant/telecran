# coding: utf-8

__author__ = "gboulant, nov. 2022"

import os
import inspect
import random

import unittest

import svgsketcher

class TestWrapper:
    """This class is for test purpose only. It can be use to wrap the
    execution of a sketching test, by starting the sketch, and ending by
    display and save a to SVG file"""
    outpattern="output.{fname}.svg"

    def __init__(self):
        self.sketcher = None
    
    def start(self, withaxis=True):
        cnvwidth = 600.
        cnvheight = 400.
        coordsys = svgsketcher.CoordinatesSystem.Centered(cnvwidth, cnvheight, xyunit=50.)
        sketcher = svgsketcher.SvgSketcher(cnvwidth,cnvheight).withCoordinatesSystem(coordsys)
        if withaxis: sketcher.unitaxis()
        self.sketcher = sketcher
        return sketcher

    def end(self, svgpath=None):
        if self.sketcher is None: return
        
        if svgpath is None:
            fname = inspect.stack()[1].function # 1 = fonction appelante
            svgpath = TestWrapper.outpattern.format(fname = fname)
    
        self.sketcher.display()
        self.sketcher.save(svgpath)
        print("SVG sketch saved in file: %s"%svgpath)

def outputpath(pattern="output.{fname}.svg"):
    fname = inspect.stack()[1].function # 1 = fonction appelante
    outpath = pattern.format(fname = fname)
    return outpath


class TestSvgSketcher(unittest.TestCase):
    def test_00_assertType(self):
        def testfct():
            pencil = 5
            svgsketcher.assertIsInstance(pencil, svgsketcher.SvgPencil)
        self.assertRaises(svgsketcher.SvgException, testfct)

    def test_01_coordinatesSystem(self):
        # The default coordinates system is the native pixel coordinates system
        # of the canvas. So we juste avec to check the identity.
        csys = svgsketcher.CoordinatesSystem()
        x, y = 0., 0.
        cx, cy = csys.cnvCoordinates(x,y)
        self.assertEqual(cx,x)
        self.assertEqual(cy,y)

        x, y = 30., 40.
        cx, cy = csys.cnvCoordinates(x,y)
        self.assertEqual(cx,x)
        self.assertEqual(cy,y)

        cnvwidth = 100
        cnvheight = 200
        xyunit = 5
        csys = svgsketcher.CoordinatesSystem.Centered(cnvwidth, cnvheight, xyunit)
        x, y = 0., 0.
        cx, cy = csys.cnvCoordinates(x,y)
        print("cx = %s cy = %s"%(cx, cy))
        self.assertEqual(cx, 0.5 * cnvwidth)
        self.assertEqual(cy, 0.5 * cnvheight)

        x, y = 7., -4.
        cx, cy = csys.cnvCoordinates(x,y)
        print("cx = %s cy = %s"%(cx, cy))
        self.assertEqual(cx, 0.5 * cnvwidth + x * xyunit)
        self.assertEqual(cy, 0.5 * cnvheight - y * xyunit)

        # retrieve the x, y coordinates form canvas native coordinates
        xres, yres = csys.xyCoordinates(cx,cy)
        self.assertEqual(xres, x)
        self.assertEqual(yres, y)

    def test_02_xyboundaries(self):
        cnvwidth = 100
        cnvheight = 200
        sketcher = svgsketcher.SvgSketcher(cnvwidth, cnvheight)

        # Define a coordinates system centered in the canvas
        Ohcoord = 0.5 * cnvwidth 
        Ovcoord = 0.5 * cnvheight
        xyunit = 5
        csys = svgsketcher.CoordinatesSystem(Ohcoord, Ovcoord, xyunit=xyunit, yinverse=True)

        sketcher.withCoordinatesSystem(csys)

        xmin, xmax, ymin, ymax = sketcher.xyboundaries()
        self.assertEqual(xmin, -10.)
        self.assertEqual(xmax, +10.)
        self.assertEqual(ymin, -20.)
        self.assertEqual(ymax, +20.)

    def test_02_draw_axis_and_boundaries(self):
        sketcher = svgsketcher.SvgSketcher.newCenteredCoordinates(xrange=4.)
        sketcher.circle(0., 0., 0.5)
        sketcher.circle(0., 0., 1.0)
        sketcher.unitaxis()
        sketcher.boundaries()
        sketcher.display()
        sketcher.save(outputpath(pattern="output.{fname}_no_offset.svg"))

        sketcher.clear()
        sketcher.circle(0., 0., 0.5)
        sketcher.circle(0., 0., 1.0)
        sketcher.unitaxis()
        sketcher.boundaries(xoffset="2%", yoffset="4%")
        sketcher.display()
        sketcher.save(outputpath(pattern="output.{fname}_with_offset.svg"))

    def test_03_save(self):
        sketcher = svgsketcher.SvgSketcher()
        sketcher.moveTo(100, 100)
        sketcher.lineTo(300, 200)
        svgpath = sketcher.save()
        print("SVG saved into file %s"%svgpath)
        self.assertTrue(os.path.exists(svgpath))

    def test_04_background(self):
        sketcher = svgsketcher.SvgSketcher()
        sketcher.moveTo(100, 100)
        sketcher.lineTo(300, 200)
        sketcher.backgroundColor = "yellow"

        sketcher.text(x=100, y=100, value="The background is yellow")

        sketcher.display()
        sketcher.save(outputpath())

    def test_05_boundingBox(self):
        x1, y1 = 0., 2.
        x2, y2 = 5., 0.
        x3, y3 = 6., 4.
        x4, y4 = 2., 5.
        xycoordinates = [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
        xmin, ymin, xmax, ymax = svgsketcher.boundingBox(xycoordinates)

        xmin_exp = x1
        xmax_exp = x3
        ymin_exp = y2
        ymax_exp = y4

        self.assertEqual(xmin, xmin_exp)
        self.assertEqual(xmax, xmax_exp)
        self.assertEqual(ymin, ymin_exp)
        self.assertEqual(ymax, ymax_exp)

    @staticmethod
    def _getElementsForBoundingTest():
        x1, y1 = 0., 2.
        x2, y2 = 5., 0.
        x3, y3 = 6., 4.
        x4, y4 = 2., 5.
        xycoordinates = [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]

        xtranslation = random.randint(-50, 50)
        ytranslation = random.randint(-50, 50)
        xycoordinates = [(p[0]+xtranslation, p[1]+ytranslation) for p in xycoordinates]

        def sketchfunc(sketcher):
            xypoint = xycoordinates[0]
            sketcher.point(xypoint[0], xypoint[1])
            sketcher.moveTo(xypoint[0], xypoint[1])
            for xypoint in xycoordinates[1:]:
                sketcher.point(xypoint[0], xypoint[1])
                sketcher.lineTo(xypoint[0], xypoint[1])

        return xycoordinates, sketchfunc

    def test_06_boundingByCoordinateSystem(self):
        xycoordinates, sketchfunc = TestSvgSketcher._getElementsForBoundingTest()

        # UC01: without offset
        cnvsize = 300
        csys = svgsketcher.CoordinatesSystem.BoundingBy(xypoints=xycoordinates, cnvsize=cnvsize)
        cnvwidth = csys.underlying_cnvwidth
        cnvheight = csys.underlying_cnvheight
        self.assertEqual(cnvwidth,cnvsize) # because we choose points more distributed along x axis
        self.assertLessEqual(cnvheight,cnvwidth)

        sketcher1 = svgsketcher.SvgSketcher(cnvwidth, cnvheight,coordinatesSystem=csys)
        sketchfunc(sketcher1)
        sketcher1.display()
        sketcher1.save(outputpath(pattern="output.{fname}_no_offset.svg"))

        # UC02: with an offset
        csys = svgsketcher.CoordinatesSystem.BoundingBy(xypoints=xycoordinates,xoffset=0.1, yoffset=0.2, cnvsize=300)
        cnvwidth = csys.underlying_cnvwidth
        cnvheight = csys.underlying_cnvheight
        self.assertEqual(cnvwidth,cnvsize) # because we choose points more distributed along x axis
        self.assertLessEqual(cnvheight,cnvwidth)

        sketcher2 = svgsketcher.SvgSketcher(cnvwidth, cnvheight,coordinatesSystem=csys)
        sketchfunc(sketcher2)
        sketcher2.display()
        sketcher2.save(outputpath(pattern="output.{fname}_with_offset.svg"))

        # UC03: with an offset given as a percentage
        csys = svgsketcher.CoordinatesSystem.BoundingBy(xypoints=xycoordinates,xoffset="2%", yoffset="2%", cnvsize=300)
        cnvwidth = csys.underlying_cnvwidth
        cnvheight = csys.underlying_cnvheight
        self.assertEqual(cnvwidth,cnvsize) # because we choose points more distributed along x axis
        self.assertLessEqual(cnvheight,cnvwidth)

        sketcher3 = svgsketcher.SvgSketcher(cnvwidth, cnvheight,coordinatesSystem=csys)
        sketchfunc(sketcher3)
        sketcher3.display()
        sketcher3.save(outputpath(pattern="output.{fname}_with_offset_as_percentage.svg"))


    def test_10_lines(self):
        sketcher = svgsketcher.SvgSketcher()
        
        # The default coordinate system is the pixel native coordinate
        # system of the SVG canvas. In this test example then, we use
        # directly the pixel coordinates for the placement of the
        # SVG elements.
        
        sketcher.moveTo(100, 100)
        sketcher.lineTo(300, 200)
        self.assertEqual(sketcher.x, 300)
        self.assertEqual(sketcher.y, 200)

        sketcher.hlineTo(x=400)
        self.assertEqual(sketcher.x, 400)
        self.assertEqual(sketcher.y, 200)
        
        sketcher.vlineTo(y=300)
        self.assertEqual(sketcher.x, 400)
        self.assertEqual(sketcher.y, 300)
        
        sketcher.hlineLong(dx=-50)
        self.assertEqual(sketcher.x, 350)
        self.assertEqual(sketcher.y, 300)

        sketcher.vlineLong(dy=-50)
        self.assertEqual(sketcher.x, 350)
        self.assertEqual(sketcher.y, 250)

        sketcher.display()
    
        svgpath = outputpath()
        sketcher.save(svgpath)

    def test_11_circle(self):
        tw = TestWrapper()
        sketcher = tw.start()

        _, _, ymin, ymax = sketcher.xyboundaries()
        R0 = 0.5 * (ymax - ymin) 
        dr = 0.4

        # Show how to draw circles of different colors.
        cx = 0.; cy = 0.; r = R0
        sketcher.circle(cx,cy,r)

        r-= dr
        sketcher.pencil.lineWidth +=2
        sketcher.circle(cx,cy,r)
        
        r-= dr
        sketcher.pencil.lineColor = "green"
        sketcher.circle(cx,cy,r)

        r-= dr
        sketcher.pencil.fillColor = "blue"
        sketcher.circle(cx,cy,r, fill=True, border=False)
        # Check that this circle is filled with blue, with no border

        r-= dr
        sketcher.pencil.fillColor = "yellow"
        sketcher.circle(cx,cy,r, fill=True, border=False)

        tw.end()

    def test_12_rectangle(self):
        tw = TestWrapper()
        sketcher = tw.start()

        sketcher.rectangle(-2, -1, 2, 1)
        sketcher.pencil.fillColor = "blue"
        x, y = 0.5, 0.5
        w, h = 2., 1.
        sketcher.rectangle(x, y, x+w, y+h, fill=True, border=False)

        tw.end()

    def test_13_point(self):
        tw = TestWrapper()
        sketcher = tw.start()

        sketcher.point(0.,0.,color="red")
        sketcher.point(1.,1.,label="A")
        sketcher.point(2.,2.,color = "blue", label="B")

        tw.end()

    def test_14_text(self):
        tw = TestWrapper()
        sketcher = tw.start()

        sketcher.text(-3., -1., "This text is black")
        sketcher.text(-3., +1., "This text is red", color="red")
        sketcher.text(-3., +2., "This text is red and bigger", size=30, color="red")
    
        tw.end()

    def test_15_segment(self):
        tw = TestWrapper()
        sketcher = tw.start()

        y0 = -3.
        dy = 0.3
        for i in range(10):
            ax = -3.
            ay = y0 + i * dy
            bx = +3.
            by = ay + 2*dy
            sketcher.segment(ax,ay,bx,by)

        x0 = -3.
        dx = 0.3
        for i in range(10):
            ax = x0 + i * dx
            ay = -3.
            bx = ax + 2*dx
            by = +3.
            sketcher.segment(ax,ay,bx,by)

        tw.end()

    def test_16_polygon(self):
        tw = TestWrapper()
        sketcher = tw.start()

        def points(x0,y0): 
            return [
                (x0, y0),
                (x0 + 2., y0),
                (x0 + 2., y0 + 0.5),
                (x0 + 1., y0 + 0.5),
                (x0 + 1., y0 + 1.),
                (x0, y0+1),
            ]

        x0, y0 = 1., 1.
        polygon = points(x0,y0)
        sketcher.polygon(polygon)

        x0, y0 = -2., -2.
        polygon = points(x0,y0)
        sketcher.polygon(polygon, closed=True)

        tw.end()

    def test_30_factory(self):
        xyrange = 100
        
        def sketchfunc(sketcher):
            offset = 1.
            sketcher.pencil.lineWidth = 4
            xmin, xmax, ymin, ymax = sketcher.xyboundaries()

            color = "red"
            sketcher.pencil.lineColor = color
            sketcher.point(xmin+offset, ymin+offset, color)
            sketcher.moveTo(xmin+offset, ymin+offset)
            sketcher.lineTo(xmin+offset, ymax-offset)

            color = "green"
            sketcher.pencil.lineColor = color
            sketcher.point(xmin+offset, ymax-offset, color)
            sketcher.lineTo(xmax-offset, ymax-offset)

            color = "blue"
            sketcher.pencil.lineColor = color
            sketcher.point(xmax-offset, ymax-offset, color)
            sketcher.lineTo(xmax-offset, ymin+offset)

            sketcher.display()
            sketcher.save(outputpath())

        # 2. The standard way (without the factory function "new")
        sketcher2  = svgsketcher.SvgSketcher()
        cnvwidth  = sketcher2.cnvwidth
        cnvheight = sketcher2.cnvheight
        cnvsize   = cnvwidth # arbitrary choice (default choice in the new factory function)
        xyunit = svgsketcher.CoordinatesSystem.xyrange2xyunit(xyrange, cnvsize)
        csys = svgsketcher.CoordinatesSystem.BottomLeft(cnvheight,xyunit=xyunit)        
        sketcher2.withCoordinatesSystem(csys)
        sketchfunc(sketcher2)

        # This standard way is more verbose, but in fact it is simply
        # the implementation of the factory function "new".
        # Note that with this method, you can set th multiple possible
        # parameters: sizes of the canvas in horizontal and vertical
        # direction, xyunit or xyrange dependening on the prefered way
        # to specify the length unit, and the most important the kind of
        # coordinates system.


        # 3. The new way. No more factory, just adapter functions to
        #    customize the coordinates system. More explicit (we now
        #    what we get, and with a single line)
        #
        # Note that we prefer the range to specify the length unit
        # (because more convenient in most usage), and the xrange (then
        # by respect to the width of the canvas)
        sketcher3  = svgsketcher.SvgSketcher().withBottomLeftCoordinates(xrange=xyrange)
        sketchfunc(sketcher3)

        # Or even better
        sketcher4  = svgsketcher.SvgSketcher.newBottomLeftCoordinates(xrange=xyrange)
        sketchfunc(sketcher4)

    def test_31_factory_boundedBy(self):
        xycoordinates, sketchfunc = TestSvgSketcher._getElementsForBoundingTest()
        sketcher = svgsketcher.SvgSketcher.newBoundedByCoordinates(xycoordinates)
        sketchfunc(sketcher)
        sketcher.display()
        sketcher.save(outputpath())
        

    def runTest(self):
        """This function executes the whole set of tests"""
        unittest.main(verbosity=2)

if __name__ == "__main__":
    t = TestSvgSketcher()
    #t.runTest()
    t.test_06_boundingByCoordinateSystem()
