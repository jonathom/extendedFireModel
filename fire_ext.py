# extended fire model from pcraster workshop, based on work by http://karssenberg.geo.uu.nl/labs/index.html
from pcraster import *
from pcraster.framework import *

class Fire(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone('clone.map')

  def initial(self):
    start = readmap("start")
    start = nominal(start)

    inputMap = uniform(1)

    # start the fire at random location (doesn't matter if empty or not)
    # fireStarter = ifthenelse(inputMap == mapmaximum(inputMap), boolean(1), boolean(0))
    
    # 0 empty, 1 fire, 5, 6 ... tree species
    # distribution of empty and tree cells
    # self.all = ifthenelse(inputMap < 0, nominal(0), nominal(5)) # empty or species 5
    # self.all = ifthenelse(inputMap > 0.5, nominal(6), self.all) # species 6 or as defined above
    # self.all = ifthenelse(fireStarter, nominal(1), self.all) # set fire

    # use original starter map instead for continuous fire starting point
    self.all = ifthenelse(pcrnot(boolean(start)), nominal(5), start)
    self.all = ifthenelse(pcrand(self.all == 5, inputMap < 0.5), nominal(6), self.all)
    
    self.report(self.all, "input")

    # fire = self.all == 1
    # self.report(fire, "fire")



  def dynamic(self):
    # currently burning
    fire = self.all == 1
    self.report(fire, "fire")
    # burn
    self.all = ifthenelse(self.all == 1, nominal(0), self.all)

    # distance to fire
    if (maptotal(scalar(fire)) > 0):
      print("fire")
      distanceToFire = spread(fire, 0, 1)
      self.report(distanceToFire, "dist")

      randomMap = uniform(1)

      # new fire, based on distance
      n1 = ifthenelse(pcrand(randomMap < 0.9, distanceToFire < 11), boolean(1), boolean(0))
      n2 = ifthenelse(pcrand(randomMap < 0.4, distanceToFire < 25), boolean(1), boolean(0))
      n3 = ifthenelse(pcrand(randomMap < 0.1, distanceToFire < 55), boolean(1), boolean(0))

      newFireDist = pcror(n1, pcror(n2, n3))
      # newFireDist = n1
      self.report(newFireDist, "nFD")

      # or, model depending on quadratic spread
      # distanceToFire = spread(fire, 0, 1.1) * spread(fire, 0, 1.1)
      # distanceToFire = 1 / distanceToFire
      # newFireDist = ifthenelse(randomMap < distanceToFire, boolean(1), boolean(0))
      # self.report(newFireDist, "dist")

      # new fire, based on trees
      species5 = self.all == 5
      species6 = self.all == 6

      # draw again
      randomMap = uniform(1)

      s1 = ifthenelse(pcrand(randomMap < 0.8, species5), boolean(1), boolean(0))
      s2 = ifthenelse(pcrand(randomMap < 0.7, species6), boolean(1), boolean(0))

      newFireSpecies = pcror(s1, s2)
      self.report(newFireSpecies, "nFS")

      # bring together both distributions
      newFire = pcrand(newFireDist, newFireSpecies)
      self.report(newFire, "nF")

      # empty cells can not burn
      newFireNotEmpty = pcrand(scalar(self.all) > 0, newFire)
      self.report(newFireNotEmpty, "nFnE")

      # change in self.all: if newFire, set as 1, others stay the same
      self.all = ifthenelse(newFireNotEmpty, nominal(1), self.all)
    else:
      # self.all should remain constant
      print("no fire")
    self.report(self.all, "all")
    area = areaarea(self.all)
    self.report(area, "area")

nrOfTimeSteps=30
myModel = Fire()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()

