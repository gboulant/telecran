# coding: utf-8

class Telecran:
    def __init__(self):
        from svgsketcher import SvgSketcher
        self.__sketcher = SvgSketcher.newCenteredCoordinates(xrange=200)
        
        self.clear   = self.__sketcher.clear
        self.save    = self.__sketcher.save
        self.display = self.__sketcher.display

        self.moveTo    = self.__sketcher.moveTo
        self.lineTo    = self.__sketcher.lineTo
        self.hlineTo   = self.__sketcher.hlineTo
        self.vlineTo   = self.__sketcher.vlineTo
        self.hlineLong = self.__sketcher.hlineLong
        self.vlineLong = self.__sketcher.vlineLong

        self.point = self.__sketcher.point
        self.text  = self.__sketcher.text
        self.circle = self.__sketcher.circle
        self.rectangle = self.__sketcher.rectangle
        self.segment = self.__sketcher.segment
        self.polygon = self.__sketcher.polygon

        self.pencil = self.__sketcher.pencil