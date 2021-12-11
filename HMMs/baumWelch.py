import sys
import math
import numpy as np

epsilon = sys.float_info.epsilon

# Creates a matrix of size rows x columns
def createMatrix(data, rows, columns):
    return [data[i:i+columns] for i in range(0, len(data), columns)]

# Creates stochastic rows
def rowStochastic(size):
        M = [(1 / size) + np.random.rand() / 1000 for _ in range(size)]
        s = sum(M)
        return [m / s for m in M]

# Forward algorithm (alpha-pass)
def forwardAlgorithm(A, B, Pi, O):
    
    numStates = len(A)
    numObvs = len(O)
    alphas = [[]] # Holds the alphas for each observation
    alphasNormed = [[]] # Holds the normalised alphas for each observation
    c = []
    
    # Computing alpha0
    c0 = 0
    Pi = Pi[0] # Access the single row contained in Pi
    for i in range(0, numStates): # Go through all states
        alpha0 = Pi[i] * B[i][O[0]] # Using first observation
        alphas[0].append(alpha0)

        #print("a:", alpha0)
        c0 = c0 + alpha0
        #print("c", c0)
    # Scaling
    c0 = 1 / (c0 + epsilon)
    c.append(c0)
    alphasNormed[0] = [alphas[0][i]*c0 for i in range(0, len(alphas[0]))]

        
    # Computing alphaT
    for t in range(1, numObvs): # Go through all observations but the first one
        
        cT = 0
        currentAlpha = [] # alpha for this observation
        for i in range(0, numStates):
            #print("B[i]:", B[i])
            #print("O[t]:", O[t])
            alphaT = 0
            for j in range(0, numStates):
                alphaT = alphaT + alphasNormed[t-1][j] * A[j][i] * B[i][O[t]]
            currentAlpha.append(alphaT)
            cT = cT + alphaT
            #print("a", alphaT)
            #print("c", cT)
        alphas.append(currentAlpha)
        # Scaling
        cT = 1 / (cT + epsilon)
        c.append(cT)
        alphasNormed.append([alphas[t][i]*cT for i in range(0, len(alphas[t]))])
        
    lastAlpha = alphas[-1]
    result = round(sum(lastAlpha), 6)
        
    return alphas, alphasNormed, c, result

# Forward algorithm (alpha-pass)
def forwardAlgorithm2(A, B, Pi, O):
    
    numStates = len(A)
    numObvs = len(O)
    alphas = [[]] # Holds the alphas for each observation
    
    # Computing alpha0
    c0 = 0
    Pi = Pi[0] # Access the single row contained in Pi
    for i in range(0, numStates): # Go through all states
        alpha0 = Pi[i] * B[i][O[0]] # Using first observation
        c0 = c0 + alpha0
        alphas[0].append(alpha0)
     
    # Computing alphaT
    for t in range(1, numObvs): # Go through all observations but the first one
        cT = 0
        currentAlpha = [] # alpha for this observation
        for i in range(0, numStates):
            aT = 0
            for j in range(0, numStates):
                aT = aT + alphas[t-1][j] * A[j][i] * B[i][O[t]]
            #print("---------->",aT)
            currentAlpha.append(aT)
            #print(print("------------->",currentAlpha))
            cT = cT + aT
        alphas.append(currentAlpha)
                        
    lastAlpha = alphas[-1]
    #result = round(sum(lastAlpha), 6)
    result = sum(lastAlpha)
        
    return alphas, result

# Backward algorithm (beta-pass)
def backwardAlgorithm(A, B, Pi, O, c):
    
    numStates = len(A)
    numObvs = len(O)
    betas = [[]]
    Pi = Pi[0] # Access the single row contained in Pi
    
    # First beta
    for i in range(0, numStates):
        beta0 = c[0]
        betas[0].append(beta0)
     
    # Remaining beta
    for t in range(1, numObvs):
        currentBeta = []
        for i in range(0, numStates):
            betaSum = 0
            for j in range(0, numStates):
                betaSum = betaSum + betas[t-1][j] * A[i][j] * B[j][O[t-1]]
            currentBeta.append(betaSum)
            currentBeta[i] = c[t] * currentBeta[i]
        betas.append(currentBeta)
            
    return betas

# Computing gama and digama
def computeGama(A, B, O, alphasNormed, betas):
    
    numStates = len(A)
    numObvs = len(O)
    gamas = []
    digamas = []
    
    for t in range(0, numObvs - 1):
        currentGamas = []
        currentDigamas = []
        for i in range(0, numStates):
            # Gama is the sum of the digamas at every state within the observation
            currDigamas = []
            gama = 0
            for j in range(0, numStates):
                digama = alphasNormed[t][i] * A[i][j] * B[j][O[t+1]] * betas[t+1][j]
                currDigamas.append(digama)
            gama = sum(currDigamas)
            currentGamas.append(gama)
            currentDigamas.append(currDigamas)
        gamas.append(currentGamas)
        digamas.append(currentDigamas)

    # Special case for T-1   
    currentGamas = []
    alphas = alphasNormed[numObvs-1]
    for i in range(0, numStates):
        currentGamas.append(alphas[i])
    gamas.append(currentGamas)
                
    return gamas, digamas

# Re-estimating model
def reEstimate(gamas, digamas, A, B, O):
    
    numStates = len(A)
    numObvs = len(O)
    diffObvs = 8 #len(set(O))
    
    newPi = [[]]
    # Re-estimate Pi
    for i in range(0, numStates):
        newPi[0].append(gamas[0][i]) 
    
    newA = []
    # Re-estimate A
    for i in range(0, numStates):
        denom = 0
        currentA = []
        for t in range(0, numObvs - 1):
            denom = denom + gamas[t][i]
        for j in range(0, numStates):
            numer = 0
            for t in range(0, numObvs - 1):
                gamai = digamas[t][i]
                numer = numer + gamai[j]
            a = numer / (denom + epsilon)
            currentA.append(a)
        newA.append(currentA)
            
    newB = []
    # Re-estimate B
    for i in range(0, numStates):
        denom = 0
        currentB = []
        for t in range(0, numObvs):
            denom = denom + gamas[t][i]
        for j in range(0, diffObvs):
            numer = 0
            for t in range(0, numObvs):
                if O[t] == j:
                    numer = numer + gamas[t][i]
            b = numer / (denom + epsilon)
            currentB.append(b)
        newB.append(currentB)
            
    return newPi, newA, newB

# Computing logprob
def computeLogProb(c, O):
    
    numObvs = len(O)
    logProb = 0
    
    for i in range(0, numObvs):
        logProb = logProb + math.log(c[i])
    logProb = -logProb
    
    return logProb

# Matrix formatting
def formatMatrix(matrix):
    
    # Rounding elements
    for i in range(0, len(matrix)):
        matrix[i] = [round(elem, 6) for elem in matrix[i]]

    return matrix
    
# Baum-Welch algorithm
def baumWelchAlgorithm(A, B, Pi, O):
    
    maxIters = 10
    iters = 0
    oldLogProb = -math.inf
    logProb = 1
    
    
    while (iters < maxIters and logProb > oldLogProb):
        #print("---------------------------->", iters)
        #print("logProb:", logProb)

        oldLogProb = logProb if iters != 0 else oldLogProb
        
        # Forward
        _, alphasNormed, c, _ = forwardAlgorithm(A, B, Pi, O)
        # Backward
        betas = backwardAlgorithm(A, B, Pi, O[::-1], c[::-1]) # Need to reverse c and O as we're going backwards
        # Gamas and digamas
        gamas, digamas = computeGama(A, B, O, alphasNormed, betas[::-1])
        #print("--------> iters:", iters)
        #print("\nPre-B:", B)
        # Re-estimating model
        Pi, A, B = reEstimate(gamas, digamas, A, B, O)
        #print("\nPost-B:", B)
        # Computing logprob
        logProb = computeLogProb(c, O)
        # Next iteration
        iters = iters + 1
        
    A = formatMatrix(A)
    B = formatMatrix(B)
    Pi = formatMatrix(Pi)
    
    return A, B, Pi
    