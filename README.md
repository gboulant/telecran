# telecran

Émulateur du célèbre jeu de télécran des années 70.
Le dessin est exécuté au moyen de commandes python
qui reproduisent les déplacements du télécran:

```python
from telecran import Telecran

t = Telecran()
        
t.moveTo(-80,-50)
t.point()
t.lineTo(0,-20)
t.vlineTo(25)

t.pencil.lineColor = "green"
t.pencil.lineWidth = 4

t.hlineLong(35)
t.circle(radius=10)

t.display()
```

La dernière instruction affiche le résultat:

![telecran](telecran.svg)
