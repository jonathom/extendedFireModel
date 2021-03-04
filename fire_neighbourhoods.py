# based on work by http://karssenberg.geo.uu.nl/labs/index.html
from pcraster import *
from pcraster.framework import *

class Fire(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone('clone.map')

  def initial(self):
    self.fire = readmap("start")

  def dynamic(self):
    scalarFire = scalar(self.fire)
    # burningNeighbours = window4total(scalarFire)
    # neighbourBurns = burningNeighbours > 0
    # self.report(neighbourBurns, "nB")
    
    distanceToFire = spread(self.fire, 0, 1)
    
    randomMap = uniform(1)
    
    n1 = ifthenelse(pcrand(randomMap < 0.8, distanceToFire < 11), boolean(1), boolean(0))
    n2 = ifthenelse(pcrand(randomMap < 0.15, distanceToFire < 25), boolean(1), boolean(0))
    n3 = ifthenelse(pcrand(randomMap < 0.005, distanceToFire < 55), boolean(1), boolean(0))

    # neighbourBurns = pcror(n1, pcror(n2, n3))
    neighbourBurns = n1

    potentialNewFire = pcrand(pcrnot(self.fire), neighbourBurns)
    self.report(potentialNewFire, "pNF")

    realization = uniform(1) < 0.1
    self.report(realization, "r")

    newFire = pcrand(potentialNewFire, realization)
    self.report(newFire, "nF")

    self.fire = pcror(self.fire, newFire)
    self.report(self.fire, "fire")
    
    area = areaarea(self.fire)
    self.report(area, "area")

nrOfTimeSteps=30
myModel = Fire()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()

