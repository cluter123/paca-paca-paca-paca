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
      return (onepos, twopos)
    else:
      return (twopos, onepos)
  
  def isInHome(self, gameState, pos):
    column = gameState.getWalls().width / 2
    if self.red:
      if pos[0] < column:
        return True
    else:
      if pos[0] >= column:
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
              enemyPos = [successorState.getAgentPosition(index) for index in self.getOpponents(successorState)]
              if successorState.getAgentPosition(self.index) not in enemyPos:
                pq.push((successorState, directions + [action]), heuristic(successorState.getAgentPosition(self.index), food))
    return [] #return empty if no goal node found
  
###################
## Attack Agent  ##
###################
class AttackAgent(DefaultAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    if DefaultAgent.turnCount % 2 == 0:
      self.updateEnemyPositions()
    else:
      DefaultAgent.turnCount += 1

    action = None
    if self.evalBack(gameState):
      action = self.aStarSearch(self.getClosestHomeDot(gameState), gameState)
    else:
      action = self.aStarSearch(self.getClosestDot(gameState), gameState)
    
    if len(action) == 0:
      return 'Stop'
    
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

  def getClosestDot(self, gameState):
    pq = PriorityQueue()
    for food in self.getFood(gameState).asList():
      pq.push(food, self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), food))
    return pq.pop()
  
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

  def evalBack(self, gameState):
    if gameState.getAgentState(self.index).numCarrying >= 4:
      return True

    for ghost, locations in self.enemyPositions.items():
      if not self.isInHome(gameState, locations[-1]) and self.getMazeDistance(gameState.getAgentPosition(self.index), locations[-1]) < 5:
        return True
    
    return False

###################
## Defend Agent  ##
###################
class DefendAgent(DefaultAgent, object):
  """Gets as close to the closest enemy without leaving the home field"""
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

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
            pq.push((successorState, directions + [action]), heuristic(successorState.getAgentPosition(self.index), food))
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
    target, furtherGhost = self.getClosestEnemiesPos(me)
    enemyscared = gameState.getAgentState(DefaultAgent.enemyPositions.keys()[0]).scaredTimer > 0
    # run back home if we are in danger
    if not self.isInHome(gameState, me) and not enemyscared:
      path = super(DefendAgent, self).aStarSearch(gameState.getInitialAgentPosition(self.index), gameState)
      return path[0]
    # track the vulnerable enemy
    if self.isInHome(gameState, furtherGhost) and not self.isInHome(gameState, target):
      target = furtherGhost
    path = self.aStarSearch(target, gameState)
    possibleActions = gameState.getLegalActions(self.index)
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
