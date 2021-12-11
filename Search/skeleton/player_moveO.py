#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE
from time import time
import math
TIME_THRESHOLD = 75*1e-3




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


            # Possible next moves: "stay", "left", "right", "up", "down"
            #best_move = self.search_best_next_move(
            #   model=model, initial_tree_node=node)

            # Initial call of minimax
               # Iterative Deepening Search
            #for maxDepth in range(1,4):
            #for i in range(1,4):

            score, best_move = self.iteration(num_interation=6, node= node)


            self.sender({"action": best_move, "search_time": None})



    def iteration(self, num_interation, node):
        for i in range(1,num_interation):
            score, move = self.search_best_next_move(
                                                      currentNode=node,
                                                      depth =i,
                                                      alpha = -math.inf,
                                                      beta = math.inf,
                                                      player = 0)


        return score, move


    def search_best_next_move(self,  currentNode, depth, alpha, beta, player):

        if time() - self.start_time > (TIME_THRESHOLD - 0.005):
            #print("Threshold Reached")
            evaluation = self.heuristic(currentNode)
            return evaluation, ACTION_TO_STR[currentNode.move]

        children=currentNode.compute_and_get_children()


        if depth == 0: #or len(currentNode.children) == 0:
            evaluation = self.heuristic(currentNode)
            #print(maxDepth)
            return evaluation, ACTION_TO_STR[currentNode.move] #returns heuristic value + move needed to get to node

        else:
            if player == 0:
                maxVal = -math.inf # Want to maximise, give worst possible value to start
                for child in children:
                    childVal, returnMove = self.search_best_next_move(child, depth-1, alpha, beta, 1)
                    if childVal > maxVal:
                        bestMove = returnMove
                        maxVal = childVal
                    alpha = max(alpha, maxVal)
                    if beta <= alpha:
                        break
                return maxVal, bestMove
            else:
                minVal = math.inf # Want to minimise, give worst possible value to start
                for child in children:
                    childVal, returnMove = self.search_best_next_move(child, depth-1, alpha, beta, 0)
                    if childVal < minVal:
                        bestMove = returnMove
                        minVal = childVal
                    beta = min(beta,minVal)
                    if beta <= alpha:
                        break
                return minVal, bestMove


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


        fishPos_keys = fishPos.keys()
        list_evaluation = []

        if fishPos:
            for key in fishPos_keys:
                if fishScore[key]>0:
                    x_dis_zero=min(abs(fishPos[key][0] - hookPos[0][0]), 20-abs(fishPos[key][0] - hookPos[0][0]))
                    x_dis_one=min(abs(fishPos[key][0] - hookPos[1][0]), 20-abs(fishPos[key][0] - hookPos[1][0]))
                    y_dis_zero = fishPos[key][1]-hookPos[0][1]
                    y_dis_one = fishPos[key][1] - hookPos[1][1]
                    dis_zero=math.hypot(x_dis_zero,y_dis_zero)
                    dis_one=math.hypot(x_dis_one,y_dis_one)
                    fish_value=(fishScore[key])**2
                    list_evaluation.append((fish_value/(dis_zero+0.5))**3 -(fish_value/(dis_one+1)))

        evaluation=playerScore[0]-playerScore[1]+sum(list_evaluation)
        return evaluation
