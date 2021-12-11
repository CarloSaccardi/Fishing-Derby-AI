import sys

# Creates a matrix of size rows x columns
def createMatrix(data, rows, columns):
    return [data[i:i+columns] for i in range(0, len(data), columns)]

# Turns matrix of strings into floats or ints
def stringChange(A, choice):
    for i in range(0, len(A)):
        if choice == "float":
            A[i] = float(A[i])
        elif choice == "int":
            A[i] = int(A[i])
    return A

# Forward algorithm (alpha-pass)
def forwardAlgorithm(A, B, Pi, O):

    numStates = len(A)
    numObvs = len(O)
    alphas = [[]] # Holds the alphas for each observation

    # Computing alpha0
    #c0 = 0
    Pi = Pi[0] # Access the single row contained in Pi
    for i in range(0, numStates): # Go through all states
        alpha0 = Pi[i] * B[i][O[0]] # Using first observation
        #c0 = c0 + alpha0
        alphas[0].append(alpha0)

    # Computing alphaT
    for t in range(1, numObvs): # Go through all observations but the first one
        #cT = 0
        currentAlpha = [] # alpha for this observation
        for i in range(0, numStates):
            aT = 0
            for j in range(0, numStates):
                aT = aT + alphas[t-1][j] * A[j][i] * B[i][O[t]]
            #print("---------->",aT)
            currentAlpha.append(aT)
            #print(print("------------->",currentAlpha))
            #cT = cT + aT
        alphas.append(currentAlpha)

    lastAlpha = alphas[-1]
    result = round(sum(lastAlpha), 6)

    return alphas, result

# Gets input from console and seperates them by line, then turns their values into floats or ints
A_in = stringChange(sys.stdin.readline().split(), "float")
B_in = stringChange(sys.stdin.readline().split(), "float")
Pi_in = stringChange(sys.stdin.readline().split(), "float")
O = stringChange(sys.stdin.readline().split(), "int")[1:]
#print("A_in:", A_in)
#print("B_in:", B_in)
#print("Pi_in:", Pi_in)
#print("O:", O)

# Creates matrices A, B and Pi
A = createMatrix(A_in[2:], int(A_in[0]), int(A_in[1]))
B = createMatrix(B_in[2:], int(B_in[0]), int(B_in[1]))
Pi = createMatrix(Pi_in[2:], int(Pi_in[0]), int(Pi_in[1]))
#print("A:", A)
#print("B:", B)
#print("Pi:", Pi)

alphas, result = forwardAlgorithm(A, B, Pi, O)

print(result)
