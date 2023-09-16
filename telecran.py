# coding: utf-8

from svgsketcher import SvgSketcher

class Telecran:
    def __init__(self):
        self.__sketcher = SvgSketcher.newCenteredCoordinates(xrange=100)
        
        self.Clear   = self.__sketcher.clear
        self.Save    = self.__sketcher.save
        self.Display = self.__sketcher.display

        self.MoveTo    = self.__sketcher.moveTo
        self.LineTo    = self.__sketcher.lineTo
        self.HLineTo   = self.__sketcher.hlineTo
        self.VLineTo   = self.__sketcher.vlineTo
        self.HLineLong = self.__sketcher.hlineLong
        self.VLineLong = self.__sketcher.vlineLong

        self.Point = self.__sketcher.point
        self.Text  = self.__sketcher.text
        self.Circle = self.__sketcher.circle
        self.Rectangle = self.__sketcher.rectangle
        self.Segment = self.__sketcher.segment
        self.Polygon = self.__sketcher.polygon

        self.Pencil = self.__sketcher.pencil