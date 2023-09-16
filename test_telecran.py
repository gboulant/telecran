import unittest
import telecran

class TestTelecran(unittest.TestCase):
    def test_01_telecran(self):
        t = telecran.Telecran()
        
        t.moveTo(-80,-50)
        t.point()
        t.lineTo(0,-20)
        t.vlineTo(25)

        t.pencil.lineColor = "green"
        t.pencil.lineWidth = 4

        t.hlineLong(35)
        t.circle(radius=10)

        t.display()
        t.save("output.telecran.svg")