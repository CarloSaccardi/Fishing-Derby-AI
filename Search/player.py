#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE
from time import time
import math
TIME_THRESHOLD = 75*1e-3

diz_scores = {} # List with scores for layer 1
#diz_nodes = {} # List with nodes for layer 1

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        #model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver()
            self.start_time = time()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)


            score, best_move = self.iteration(num_interation = 9, node = node)

            #global diz_nodes
            #diz_nodes={}

            self.sender({"action": best_move, "search_time": None})


    # Iteration with max depth given
    def iteration(self, num_interation, node):

        diz_nodes={}
        global diz_scores

        for i in range(1, num_interation):
            #print("Iteration ---------------------------------------------------------> ", i)
            score, move, goal = self.search_best_next_move(diz_nodes=diz_nodes,
                                                    currentNode = node,
                                                      depth = i,
                                                      alpha = -1000,
                                                      beta = 1000,
                                                      player = 0,
                                                      maxDepth = i)

            diz_nodes = self.sorting(diz_nodes, diz_scores)

            diz_scores={}
            if goal:
                break


        return score, move

    def sorting(self, diz1, diz2):
        # Orders children by their highest score value from left to right
        for key in diz2.keys():
            list1 = diz1[key]
            list2 = diz2[key]
            keydict = dict(zip(list1, list2)) # We only get last 5 of list to avoid the 5 scores that get appened from the first iteration which we don't need
            list1.sort(key=keydict.get)
            diz1[key]=list1

        return diz1


    def search_best_next_move(self, diz_nodes, currentNode, depth, alpha, beta, player, maxDepth):

        #global diz_nodes
        global diz_scores

        if time() - self.start_time > (TIME_THRESHOLD - 0.01):
            print("Maxdepth -------------------------------->", maxDepth)
            evaluation, goal = self.heuristic(currentNode)
            if currentNode.move is not None:
                bestMove = currentNode.move
            else:
                bestMove = 0
            #print('PROBLEMAPROBLEMAPROBLEMA')
            return evaluation, ACTION_TO_STR[bestMove], True # Returns heuristic value + move needed to get to node


        children = currentNode.compute_and_get_children()
        #print('----------------')
        #print(children)
        #print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

        if depth > 1 and maxDepth == depth:
            children = diz_nodes[depth-1]
            #print(diz_nodes)
            #print(depth)
            #print(maxDepth)
            #print('----------------')

        elif depth >1 and maxDepth != depth:
            children_ordered = []
            for move in diz_nodes[depth-1]:
                if move in children:
                    children_ordered.append(move)
            if children_ordered:
                children = children_ordered
                #print(diz_nodes)
                #print(depth)
                #print(maxDepth)
                #print(children)
                #print('----------------')




        if depth == 0:
            #print("Maxdepth -------------------------------->", maxDepth)
            evaluation, goal = self.heuristic(currentNode)
            return evaluation, ACTION_TO_STR[currentNode.move], goal #returns heuristic value + move needed to get to node

        if player == 0:
            maxVal = -1000 # Want to maximise, give worst possible value to start
            bestMove = -1
            for child in children:
                childVal, returnMove, goal = self.search_best_next_move(diz_nodes, child, depth-1, alpha, beta, 1, maxDepth)
                if depth not in diz_scores.keys():
                    diz_nodes.update({depth:[child]})
                    diz_scores.update({depth:[childVal]})
                else:
                    #if child not in diz_nodes[depth]:
                    diz_nodes[depth].append(child)
                    diz_scores[depth].append(childVal)
                if childVal > maxVal:
                    bestMove = returnMove
                    maxVal = childVal
                alpha = max(alpha, maxVal)
                if beta <= alpha or goal:
                    break
            return maxVal, bestMove, goal
        else:
            minVal = 1000 # Want to minimise, give worst possible value to start
            bestMove = -1
            for child in children:
                childVal, returnMove, goal = self.search_best_next_move(diz_nodes, child, depth-1, alpha, beta, 0, maxDepth)
                if depth not in diz_scores.keys():
                    diz_nodes.update({depth:[child]})
                    diz_scores.update({depth:[childVal]})
                else:
                    #if child not in diz_nodes[depth]:
                    diz_nodes[depth].append(child)
                    diz_scores[depth].append(childVal)
                if childVal < minVal:
                    bestMove = returnMove
                    minVal = childVal
                beta = min(beta, minVal)
                if beta <= alpha or goal:
                    break
            return minVal, bestMove, goal


    def heuristic(self, currentNode):

        # Current player scores --> (0, 10)
        playerScore =  currentNode.state.get_player_scores()
        # Returns type of fish that is currently caught on players hook --> (None, 2)
        fishCaught = currentNode.state.get_caught()
        # Fish positions --> {0: (6, 16), 1: (1, 14), 3: (8, 13), 4: (19, 6)}
        fishPos = currentNode.state.get_fish_positions()
        # Hook positions --> {0: (6, 12), 1: (11, 16)}
        hookPos = currentNode.state.get_hook_positions()
        # Fish scores --> {0: 11, 1: 2, 2: 10, 3: 2, 4: 11}
        fishScore = currentNode.state.get_fish_scores()

        #print("fishPos:", fishPos)
        #print("fishScore:", fishScore)
        #print("playerScore[0]:", playerScore[0])
        #print("playerScore[1]:", playerScore[1])

        fishPos_keys = fishPos.keys()

        fishDis0 = {}            # list containing all fish ditances to hook of player 0
        fishDis1 = {}
        fishSide = {} # holds bools saying True if fish is on other side of boat, and false if else
        fishPoints = {}

        evaluation = 0
        closestDistance0 = 0

        # If player 0 has found a fish with positive points
        if fishCaught[0] is not None:
            fishScore0 = TYPE_TO_SCORE[fishCaught[0]]
            if fishScore0 > 0:
                goal = True
            else:
                goal=False

        else:
            fishScore0 = 0
            goal = False
            fishDis = {}            # list containing all fish ditances to hook of player 0
            if fishPos:
                for key in fishPos_keys:
                    if fishScore[key]>0:
                        x_dis_zero=min(abs(fishPos[key][0] - hookPos[0][0]), 20-abs(fishPos[key][0] - hookPos[0][0]))
                        x_dis_one=min(abs(fishPos[key][0] - hookPos[1][0]), 20-abs(fishPos[key][0] - hookPos[1][0]))
                        y_dis_zero = fishPos[key][1]-hookPos[0][1]
                        y_dis_one = fishPos[key][1]-hookPos[1][1]
                        fishDis0[key] = ((x_dis_zero)**2 + (y_dis_zero)**2)**0.5
                        fishDis1[key] = ((x_dis_one)**2 + (y_dis_one)**2)**0.5
                        fishPoints[key] = fishScore[key]

            # Make sure fishDis is populated, aka nonzero score fish are remaining:
            if fishDis0:
                #if
                closestDistance0 = min(fishDis0.values())
                #closestDistance1 = max(fishDis1.values())

                #closestDistances0 = sum(fishDis0.values())
                #closestDistances1 = sum(fishDis1.values())

                playerFishScore0 = sum({key: fishPoints[key] / (fishDis0.get(key, 0) + 0.01) for key in fishDis0 if key in fishPoints}.values())
                playerFishScore1 = sum({key: fishPoints[key] / (fishDis1.get(key, 0) + 0.01) for key in fishDis1 if key in fishPoints}.values())
            """
            if fishDis0:
                closestDistance0, index = min(fishDis0.values()), min(fishDis0, key = fishDis0.get)
                closestDistance0 = closestDistance0 if fishSide[index] == False else -closestDistance0
                #for key in fishDis0:
                #    closestDistance = min(fishDis0.values()) if fishSide[key] == False else -min(fishDis0.values())
            """


        #print("fishDis0", fishDis0)
        #print("fishPoints", fishPoints)
        #print("playerFishScore0:", playerFishScore0)
        #print("playerFishScore1:", playerFishScore1)
        #print("fishSide", fishSide)


        #fishScore1 = fishCaught[1] if fishCaught[1] is not None else 0

        evaluation =  0.5 * (playerScore[0] - playerScore[1]) + 0.5 *(playerFishScore0 - playerFishScore1) - closestDistance0

        return evaluation, goal
