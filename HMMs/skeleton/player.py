#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
import random
import baumWelch as bw


class Model:
    def __init__(self, species, emissions):
        # Initialises model and rounds their values to 6 decimal points
        self.Pi = [bw.rowStochastic(species)]
        self.A = [bw.rowStochastic(species) for _ in range(species)]
        self.B = [bw.rowStochastic(emissions) for _ in range(species)]

    def set_A(self, A):
        self.A = A

    def set_B(self, B):
        self.B = B

    def set_Pi(self, Pi):
        self.Pi = Pi

class PlayerControllerHMM(PlayerControllerHMMAbstract):
    def init_parameters(self):
        """
        In this function you should initialize the parameters you will need,
        such as the initialization of models, or fishes, among others.
        """

        # Initialising 7 HMM models, one for each fish specie
        self.models = []
        for i in range(N_SPECIES):
            self.models.append(Model(N_SPECIES, N_EMISSIONS))

        # Fish observations
        self.fishObv = {}

        # Current fish
        self.currentFish = []

    def guess(self, step, observations):
        """
        This method gets called on every iteration, providing observations.
        Here the player should process and store this information,
        and optionally make a guess by returning a tuple containing the fish index and the guess.
        :param step: iteration number
        :param observations: a list of N_FISH observations, encoded as integers
        :return: None or a tuple (fish_id, fish_type)
        """
        #print("--------------------------------------------------------------->", step)
        #print("model1 A:", self.models[0].A)
        #print("model2 A:", self.models[1].A)

        # Update dictionary with all fish observations
        for fish in range(0, len(observations)):
            if fish not in self.fishObv.keys():
                self.fishObv.update({fish:[observations[fish]]})
            else:
                self.fishObv[fish].append(observations[fish])
        #print("fishObv:", self.fishObv)

        # Only start guessing at time step 110
        if step > 110:
            bestProb = 0
            fishType = 0
            bestModel = None
            fishId, self.currentFish = list(self.fishObv.items())[180 - step]    # Gets observations from last to first fish with every new timestep
            #print("\ncurrentFish:", self.currentFish)
            # Performs forward algorithm on the 7 models going from fish 70 to 1
            for model in self.models:
                #_, _, _, prob2 = bw.forwardAlgorithm(model.A, model.B, model.Pi, self.currentFish)
                _, prob = bw.forwardAlgorithm2(model.A, model.B, model.Pi, self.currentFish)
                #print("prob2:", prob2)
                #print("prob:", prob)
                if prob > bestProb:
                    bestProb = prob
                    bestModel = model
                    fishType = self.models.index(bestModel)
            #print("fishId:", fishId)
            #print("fishType:", fishType)
            #print("bestModel:", bestModel)
            return fishId, fishType

        else:
            return None



        # This code would make a random guess on each step:
        #return (step % N_FISH, random.randint(0, N_SPECIES - 1))

        #return None

    def reveal(self, correct, fish_id, true_type):
        """
        This methods gets called whenever a guess was made.
        It informs the player about the guess result
        and reveals the correct type of that fish.
        :param correct: tells if the guess was correct
        :param fish_id: fish's index
        :param true_type: the correct type of the fish
        :return:
        """
        #print("\ntrue_type:", true_type)
        #print("correct:", correct)
        if correct == False:
            self.trainModel(true_type)

    def trainModel(self, modelIndex):
        model = self.models[modelIndex]
        #print("\nactual model:\n", model)
        #print("current fish:\n", self.currentFish)

        #print("\npre-A:\n", model.A)
        #print("pre-B:\n", model.B)
        #print("pre-Pi:\n", model.Pi)

        A, B, Pi = bw.baumWelchAlgorithm(model.A, model.B, model.Pi, self.currentFish)
        model.set_A(A)
        model.set_B(B)
        model.set_Pi(Pi)

        #print("\npost-A:\n", model.A)
        #print("post-B:\n", model.B)
        #print("post-Pi:\n", model.Pi)
