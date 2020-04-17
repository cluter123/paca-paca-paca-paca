# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import PriorityQueue

#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefaultAgent', second = 'DefaultAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

###################
## Default Agent ##
###################
class DefaultAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  # dictionary of two items (enemy1 & enemy 2) which each contain a list of tuples (corrdinates)
  enemyPositions = {}
  turnCount = 0 
  
  def updateEnemyPositions(self):
    """"""
    DefaultAgent.turnCount += 1
    currentObservation = self.getCurrentObservation()
    for index, history in DefaultAgent.enemyPositions.items():
      x, y = currentObservation.getAgentPosition(index)
      px, py = history[-1]
      possible = myLegalMoves(px, py, currentObservation)
      minspot = (x, y)
      mindist = 99
      for spot in possible:
        dist = self.getMazeDistance((x, y), spot)
        if dist < mindist:
          mindist = dist
          minspot = spot
      history.append(minspot)
    
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    for opponent in self.getOpponents(gameState):
      DefaultAgent.enemyPositions[opponent] = [gameState.getInitialAgentPosition(opponent)]
      
    self.start = gameState.getAgentPosition(self.index)

  def getClosestEnemy(self, pos, gameState):
    minEnemy = None
    mindist = 9999
    for index in DefaultAgent.enemyPositions.keys():
      lastLoc = DefaultAgent.enemyPositions[index][-1]
      enemydist = self.getMazeDistance(pos, lastLoc)
      if enemydist < mindist:
        minEnemy = index
        mindist = enemydist
    return (minEnemy, mindist)
      
  def getSafestFood(self, gameState):
    foods = self.getFood(gameState)
    me = gameState.getAgentPosition(self.index)
    backupFood = None
    bestFood = None
    minMeDistance = 9999
    maxFoeDistance = -1
    for x in range(0, foods.width):
      for y in range(0, foods.height):
        # skip non-food spots
        if not foods[x][y]:
          continue
        closeFoe, foeDistance = self.getClosestEnemy((x, y), gameState)
        distance = self.getMazeDistance(me, (x, y))
        if distance < minMeDistance and foeDistance > maxFoeDistance:
          if distance < foeDistance:
            bestFood = (x, y)
          backupFood = (x, y)
          minMeDistance = distance
          maxFoeDistance = foeDistance
    if bestFood == None:
      bestFood = backupFood
    return bestFood
      
  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    if (DefaultAgent.turnCount % 2) == 0:
      self.updateEnemyPositions()
    else:
      DefaultAgent.turnCount += 1
    print "bestFood: ", self.getSafestFood(gameState)
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    return random.choice(actions)

###################
## Attack Agent  ##
###################
class AttackAgent(DefaultAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def __init__(self, index, timeForComputing = .1):
    super().__init__(self, index, timeForComputing)
    self.pelletCount = 0

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

###################
## Defend Agent  ##
###################
class DefendAgent(DefaultAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

  
def myLegalMoves(x, y, gameState):
  actions = [(x+1, y), (x-1, y), (x,y+1), (x, y-1), (x,y)]
  for index in range(len(actions) - 1, -1, -1):
    a, b = actions[index]
    if gameState.hasWall(a, b):
      actions.remove((a,b))
  return actions
  
