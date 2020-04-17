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
from util import manhattanDistance

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
    self.pelletCount = 0
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
    pq = PriorityQueue()
    foods = self.getFood(gameState)
    me = gameState.getAgentPosition(self.index)
    for x in range(0, foods.width):
      for y in range(0, foods.height):
        if not foods[x][y]:
          continue
        _, ghostdist = self.getClosestEnemy((x, y), gameState)
        medist = self.getMazeDistance((x, y), me)
        priority = 10000
        if medist != 0:
          priority = -(ghostdist * 1 + (1.0 / medist) * 5)
        pq.push((x, y), priority)
    return pq.pop()
        
  def getSafestHome(self, gameState):
    column = gameState.getWalls().width / 2
    height = gameState.getWalls().height
    pq = PriorityQueue()
    me = gameState.getAgentPosition(self.index)
    for y in range(0, height):
      pos = (column, y)
      if not gameState.hasWall(column, y):
        priority = 10000
        _, ghostdist = self.getClosestEnemy((column, y), gameState)
        medist = self.getMazeDistance((column, y), me)
        priority = 10000
        if medist != 0:
          priority = (ghostdist * 10 + (1.0 / medist) * 1)
        pq.push((column, y), priority)
    return pq.pop()
        
  def aStarSearch(self, food, gameState, heuristic=manhattanDistance):
    """Search the node that has the lowest combined cost and heuristic first."""
    pq = PriorityQueue() # Priority Queue
    expanded = [] # list of explored nodes
    me = gameState.getAgentPosition(self.index)
    startState = (me, [])
    pq.push(startState, heuristic(startState[0], food)) # stores states as tuple of (state, direction), initial node based on heuristic
    while not pq.isEmpty():
      state, directions = pq.pop() # gets state and direction
      if state[0] == food[0] and state[1] == food[1]: # returns direction if goal state
        return directions
      else:
        if state not in expanded: # checks if state has been expanded 
          expanded.append(state) # adds state to expanded list
          tmp = myLegalMovesWithDirection(state, gameState) 
          for item in tmp: # push all non expanded nodes into priority queue
            if item[0] not in expanded:
              pq.push((item[0], directions + [item[1]]), heuristic(item[0], food))
    return [] #return empty if no goal node found

  def chooseAction(self, gameState):
    if (DefaultAgent.turnCount % 2) == 0:
      self.updateEnemyPositions()
    else:
      DefaultAgent.turnCount += 1
    me = gameState.getAgentPosition(self.index)
    if gameState.getInitialAgentPosition(self.index) == me:
      self.pelletCount = 0
    # tactions = gameState.getLegalActions(self.index)
    if self.pelletCount >= 3:
      # go home
      column = gameState.getWalls().width / 2
      bestHome = self.getSafestHome(gameState)
      actions = self.aStarSearch(bestHome, gameState)
      action = actions[0]
      nx, ny = nextPosition(me, action)
      if nx <= column:
        self.pelletCount = 0
        print "count: 0"
      return action
    else:
      # go find food
      bestFood = self.getSafestFood(gameState)
      actions = self.aStarSearch(bestFood, gameState)
      action = actions[0]
      nx, ny = nextPosition(me, action)
      if gameState.hasFood(nx, ny):
        self.pelletCount += 1
        print "count: ", self.pelletCount
      return actions[0]
  
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
def myLegalMovesWithDirection(coord, gameState):
  x, y = coord
  actions = []
  width = gameState.getWalls().width
  height = gameState.getWalls().height
  if x+1 < width and not gameState.hasWall(x+1, y):
    actions.append(((x+1, y),Directions.EAST))
  if x-1 >= 0 and not gameState.hasWall(x-1, y):
    actions.append(((x-1, y), Directions.WEST))
  if y+1 < height and not gameState.hasWall(x, y+1):
    actions.append(((x, y+1), Directions.NORTH))
  if y-1 >= 0 and not gameState.hasWall(x, y-1):
    actions.append(((x, y-1), Directions.SOUTH))
  return actions

def nextPosition(pos, action):
  x, y = pos
  if Directions.NORTH:
    return (x, y+1)
  elif Directions.EAST:
    return (x+1, y)
  elif Directions.SOUTH:
    return (x, y-1)
  elif Directions.WEST:
    return (x+1, y)
