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
import distanceCalculator
from util import nearestPoint

#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'DefendAgent'):
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
  if random.random() > .5:
    swap = first
    first = second
    second = swap
  
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
  enemyPositions = {}
  turnCount = 0
    
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
    self.start = gameState.getAgentPosition(self.index)

    '''
    Your initialization code goes here, if you need any.
    '''
    for opponent in self.getOpponents(gameState):
      DefaultAgent.enemyPositions[opponent] = [gameState.getInitialAgentPosition(opponent)]
  
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    if DefaultAgent.turnCount % 2 == 0:
      self.updateEnemyPositions()
    else:
      DefaultAgent.turnCount += 1
  
    actions = gameState.getLegalActions(self.index)

    values = [self.evaluate(gameState, a) for a in actions]
    
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)
  
  
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def updateEnemyPositions(self):
    """"""
    DefaultAgent.turnCount += 1
    currentObservation = self.getCurrentObservation()
    for index, history in DefaultAgent.enemyPositions.items():
      x, y = currentObservation.getAgentPosition(index)
      px, py = history[-1]

      #possible = myLegalMoves(px, py, currentObservation)
      possible = []
      enemyActions = currentObservation.getLegalActions(index)
      for a in enemyActions:
        enemySuccessor = currentObservation.generateSuccessor(index, a)
        possible.append(enemySuccessor.getAgentState(index).getPosition())

      minspot = (px, py)
      mindist = 9999
      for spot in possible:
        dist = self.getMazeDistance((x, y), spot)
        if dist < mindist and not currentObservation.hasWall(x, y):
          mindist = dist
          minspot = spot
      history.append(minspot)

  def getClosestEnemiesPos(self, pos):
    """Returns a tuple of enemy positions (a, b) where a is closer to pos than b."""
    enemies = DefaultAgent.enemyPositions.keys()
    onepos = DefaultAgent.enemyPositions[enemies[0]][-1]
    twopos = DefaultAgent.enemyPositions[enemies[1]][-1]
    if self.getMazeDistance(pos, onepos) < self.getMazeDistance(pos, twopos):
      return (onepos, enemies[0], twopos, enemies[1])
    else:
      return (twopos, enemies[1], onepos, enemies[0])
  
  def getClosestHomeDot(self, gameState):
    pq = PriorityQueue()
    column = gameState.getWalls().width / 2
    height = gameState.getWalls().height
    if self.index % 2 == 0:
      column -= 1

    for y in range(0, height):
      if not gameState.hasWall(column, y):
        pq.push((column, y), self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), (column, y)))
    return pq.pop()


  def isInHome(self, gameState, pos):
    column = gameState.getWalls().width / 2
    if self.red:
      if pos[0] < column:
        return True
    else:
      if pos[0] >= column:
        return True
    return False

  def onBorder(self, gameState, pos):
    column = gameState.getWalls().width / 2
    if self.red:
      if pos[0] == column - 1:
        return True
    else:
      if pos[0] == column:
        return True
    return False

  def aStarSearch(self, food, gameState, heuristic=manhattanDistance):
    """Search the node that has the lowest combined cost and heuristic first."""
    pq = PriorityQueue() # Priority Queue
    expanded = [] # list of explored nodes
    startState = (gameState, [])
    pq.push(startState, heuristic(startState[0].getAgentPosition(self.index), food)) # stores states as tuple of (state, direction), initial node based on heuristic
    while not pq.isEmpty():
      state, directions = pq.pop() # gets state and direction
      position = state.getAgentPosition(self.index)
      if position == food: # returns direction if goal state
        return directions
      else:
        if position not in expanded: # checks if state has been expanded 
          expanded.append(position) # adds state to expanded list
          tmp = state.getLegalActions(self.index)
          for action in tmp: # push all non expanded nodes into priority queue
            successorState = state.generateSuccessor(self.index, action)
            if successorState.getAgentPosition(self.index) not in expanded:
              #enemyPos = [successorState.getAgentState(index).getPosition() for index in self.getOpponents(successorState)]
              enemyPos = [self.enemyPositions[index][-1] for index in self.getOpponents(successorState)]
              if successorState.getAgentPosition(self.index) not in enemyPos:
                pq.push((successorState, directions + [action]), self.getMazeDistance(gameState.getAgentPosition(self.index), successorState.getAgentPosition(self.index)) + heuristic(successorState.getAgentPosition(self.index), food))
    return [] #return empty if no goal node found
  
  
###################
## Attack Agent  ##
###################
class AttackAgent(DefaultAgent, object):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def registerInitialState(self, gameState):
    super(AttackAgent, self).registerInitialState(gameState)
    self.prevMoves = []
    self.prevLocations = []


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    if DefaultAgent.turnCount % 2 == 0:
      self.updateEnemyPositions()
    else:
      DefaultAgent.turnCount += 1

    scaredTimers = {}
    for ghost in self.enemyPositions.keys():
      scaredTimers[ghost] = gameState.getAgentState(ghost).scaredTimer
    pos = gameState.getAgentPosition(self.index)

    action = None
    if self.evalBack(gameState, scaredTimers):
      action = self.aStarSearch(self.getClosestHomeDot(gameState), gameState)
    else:
      closestDotPos, closestDotDist = self.getClosestDot(gameState, None)

      if len(self.prevLocations) > 11:
        tmpNum = 0
        for x in self.prevLocations[-10:]:
          if self.onBorder(gameState, x):
            tmpNum = tmpNum + 1
        if tmpNum > 3:
          #print "getting farthest dot"
          #print
          closestDotPos, closestDotDist = self.getFarthestDot(gameState)

      closestCapsule = self.getClosestCapsule(gameState)

      if closestCapsule is None:
        action = self.aStarSearch(closestDotPos, gameState)
      else:
        closestCap, capsDist = closestCapsule
        if closestDotDist < capsDist or closestDotDist == self.getFarthestDot(gameState)[1]:
          action = self.aStarSearch(closestDotPos, gameState)
        else:
          if any(scaredTimers[x] < 3 for x in self.enemyPositions.keys()):
            action = self.aStarSearch(closestCap, gameState)
          else:
            action = self.aStarSearch(closestDotPos, gameState)
    
    if gameState.getAgentState(self.index).numCarrying < self.maxPellets(gameState):
      ## attacks scared ghost
      if any(scaredTimers[x] > 4 for x in self.enemyPositions.keys()):
        for ghost, locations in self.enemyPositions.items():
          if not self.isInHome(gameState, locations[-1]) and scaredTimers[ghost] > 0 and self.getMazeDistance(pos, locations[-1]) < 6:
            action = self.aStarDefSearch(gameState.getAgentPosition(ghost), gameState)
    
    if self.isInHome(gameState, gameState.getAgentPosition(self.index)):
      closestEnemy, closestEnemyDist = self.getClosestEnemyDistAndPos(gameState.getAgentPosition(self.index))
      if self.isInHome(gameState, closestEnemy) and closestEnemyDist < 3:
        action = self.aStarDefSearch(closestEnemy, gameState)
      
    if action == None or len(action) == 0:
      if len(self.prevMoves) > 10 and all(self.prevMoves[x] == 'Stop' for x in range(len(self.prevMoves) - 5, len(self.prevMoves) - 2)):
        actions = gameState.getLegalActions(self.index)
        if self.index % 2 == 0:
          if 'East' in actions:
            actions.remove('East')
        else:
          if 'West' in actions:
            actions.remove('West')
        if len(actions) == 0:
          return 'Stop'
        return random.choice(actions)
      self.prevMoves.append('Stop')
      return 'Stop'
    
    self.prevMoves.append(action[0])
    self.prevLocations.append(gameState.getAgentPosition(self.index))
    #print self.onBorder(gameState, gameState.getAgentPosition(self.index))
    return action[0]

  def getClosestEnemyDist(self, pos):
    minEnemy = None
    mindist = 9999
    for index in DefaultAgent.enemyPositions.keys():
      lastLoc = DefaultAgent.enemyPositions[index][-1]
      enemydist = self.getMazeDistance(pos, lastLoc)
      if enemydist < mindist:
        minEnemy = index
        mindist = enemydist
    return mindist

  def getClosestEnemyDistAndPos(self, pos):
    minEnemy = None
    mindist = 9999
    for index in DefaultAgent.enemyPositions.keys():
      lastLoc = DefaultAgent.enemyPositions[index][-1]
      enemydist = self.getMazeDistance(pos, lastLoc)
      if enemydist < mindist:
        minEnemy = lastLoc
        mindist = enemydist
    return (minEnemy, mindist)

  def getClosestDot(self, gameState, takeOut):
    pq = PriorityQueue()
    foodList = self.getFood(gameState).asList()
    if takeOut is None:
      takeOut = self.start
    for food in foodList:
      if takeOut not in foodList:
        dist = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), food)
        pq.push((food, dist), dist)
    return pq.pop()

  def getFarthestDot(self, gameState):
    pq = PriorityQueue()
    foodList = self.getFood(gameState).asList()
    for food in foodList:
      dist = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), food)
      pq.push((food, dist), -1 * dist)
    return pq.pop()

  def getClosestCapsule(self, gameState):
    pq = PriorityQueue()
    red = (self.index % 2) == 0
    capsules = None
    if red:
      capsules = gameState.getBlueCapsules()
    else:
      capsules = gameState.getRedCapsules()
    for capsule in capsules:
      dist = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), capsule)
      pq.push((capsule, dist), dist)
    
    if(pq.isEmpty()):
      return None

    return pq.pop()

  def evalBack(self, gameState, scaredTimers):
    if gameState.getAgentState(self.index).numCarrying >= self.maxPellets(gameState) and all(scaredTimers[x] <  5 for x in self.enemyPositions.keys()):
      return True

    if len(self.getFood(gameState).asList()) <= 2:
      return True

    if all(scaredTimers[x] < 5 for x in self.enemyPositions.keys()):
      for ghost, locations in self.enemyPositions.items():
        if not self.isInHome(gameState, gameState.getAgentPosition(ghost)) and self.getMazeDistance(gameState.getAgentPosition(self.index), locations[-1]) < 4:
          return True
    
    return False

  def maxPellets(self, gameState):
    defaultMax = 4
    closestEnemy = self.getClosestEnemyDist(gameState.getAgentPosition(self.index))
    if(closestEnemy > 10):
      defaultMax += closestEnemy - 10
    return defaultMax

  def aStarDefSearch(self, food, gameState, heuristic=manhattanDistance):
    """Search the node that has the lowest combined cost and heuristic first.
This version of A* ignores enemies, so we can eat them >:)"""
    pq = PriorityQueue() # Priority Queue
    expanded = [] # list of explored nodes
    startState = (gameState, [])
    pq.push(startState, heuristic(startState[0].getAgentPosition(self.index), food)) # stores states as tuple of (state, direction), initial node based on heuristic
    while not pq.isEmpty():
      state, directions = pq.pop() # gets state and direction
      position = state.getAgentPosition(self.index)
      if position not in expanded: # checks if state has been expanded 
        expanded.append(position) # adds state to expanded list
        tmp = state.getLegalActions(self.index)
        for action in tmp: # push all non expanded nodes into priority queue
          possibleNext = nextPosition(position, action)
          if possibleNext == food: # returns direction if goal state
            return directions + [action]
          successorState = state.generateSuccessor(self.index, action)
          if successorState.getAgentPosition(self.index) not in expanded:
            pq.push((successorState, directions + [action]), self.getMazeDistance(gameState.getAgentPosition(self.index), successorState.getAgentPosition(self.index)) + heuristic(successorState.getAgentPosition(self.index), food))
    return []                   # return empty if no goal node found
    
###################
## Defend Agent  ##
###################
class DefendAgent(AttackAgent, object):
  """Gets as close to the closest enemy without leaving the home field"""

  def aStarSearch(self, food, gameState, heuristic=manhattanDistance):
    """Search the node that has the lowest combined cost and heuristic first.
This version of A* ignores enemies, so we can eat them >:)"""
    pq = PriorityQueue() # Priority Queue
    expanded = [] # list of explored nodes
    startState = (gameState, [])
    pq.push(startState, heuristic(startState[0].getAgentPosition(self.index), food)) # stores states as tuple of (state, direction), initial node based on heuristic
    while not pq.isEmpty():
      state, directions = pq.pop() # gets state and direction
      position = state.getAgentPosition(self.index)
      if position not in expanded: # checks if state has been expanded 
        expanded.append(position) # adds state to expanded list
        tmp = state.getLegalActions(self.index)
        for action in tmp: # push all non expanded nodes into priority queue
          possibleNext = nextPosition(position, action)
          if possibleNext == food: # returns direction if goal state
            return directions + [action]
          successorState = state.generateSuccessor(self.index, action)
          if successorState.getAgentPosition(self.index) not in expanded:
            pq.push((successorState, directions + [action]), self.getMazeDistance(gameState.getAgentPosition(self.index), successorState.getAgentPosition(self.index)) + heuristic(successorState.getAgentPosition(self.index), food))
    return []                   # return empty if no goal node found
  
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    if DefaultAgent.turnCount % 2 == 0:
      self.updateEnemyPositions()
    else:
      DefaultAgent.turnCount += 1

    me = gameState.getAgentPosition(self.index)      
    mescared = gameState.getAgentState(self.index).scaredTimer > 0
    possibleActions = gameState.getLegalActions(self.index)
    target, targeti, furtherGhost, furtheri = self.getClosestEnemiesPos(me)
    # if I'm scared and the closest ghost is within 5 blocks, keep distance
    if mescared and self.getMazeDistance(me, target) <= 4:
      path = self.aStarSearch(target, gameState)
      if len(path) == 0:
        return random.choice(possibleActions)
      badAction = path[0]
      runawayOptions = otherDirections(badAction)
      runawayOptions.sort(key=lambda x: rateOpenness(nextPosition(me, x), gameState))
      for action in runawayOptions:
        if action in possibleActions:
          return action
      return random.choice(possibleActions)
    # set target to an enemy in the home area
    if self.isInHome(gameState, furtherGhost) and not self.isInHome(gameState, target):
      target = furtherGhost
      targeti = furtheri
    enemyscared = gameState.getAgentState(targeti).scaredTimer > 0
    # run back home if we are in enemy teritory and the closest ghost is not scared
    if not self.isInHome(gameState, me) and not enemyscared:
      path = super(DefendAgent, self).aStarSearch(self.getClosestHomeDot(gameState), gameState)
      return path[0]
    # track the vulnerable enemy
    path = self.aStarSearch(target, gameState)
    if not enemyscared:
      for i in range(len(possibleActions) - 1, -1, -1):
        if not self.isInHome(gameState, nextPosition(me, possibleActions[i])):
          possibleActions.remove(possibleActions[i])
    finalaction = random.choice(possibleActions)
    if len(path) > 0 and path[0] in possibleActions:
      finalaction = path[0]
    return finalaction

def nextPosition(pos, action):
  x, y = pos
  if action == Directions.NORTH:
    return (x, y+1)
  elif action == Directions.EAST:
    return (x+1, y)
  elif action == Directions.SOUTH:
    return (x, y-1)
  elif action == Directions.WEST:
    return (x-1, y)
  else:
    return (x, y)

def otherDirections(action):
  if action == 'North':
    return ['South', 'East', 'West']
  elif action == 'South':
    return ['South', 'East', 'West']
  elif action == 'East':
    return ['West', 'South', 'North']
  elif action == 'West':
    return ['East', 'South', 'North']

def rateOpenness(pos, gameState):
  "lower is better"
  x, y = pos
  if gameState.hasWall(x, y):
    return 5
  openness = 0
  if gameState.hasWall(x, y + 1): # up
    openness += 1
  if gameState.hasWall(x, y - 1): # down
    openness += 1
  if gameState.hasWall(x - 1, y): # left
    openness += 1
  if gameState.hasWall(x + 1, y): # right
    openness += 1
  return openness  
