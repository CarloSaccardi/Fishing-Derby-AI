import sys

# Creates a matrix of size rows x columns
def createMatrix(data, rows, columns):
    return [data[i:i+columns] for i in range(0, len(data), columns)]

# Element-wise multiplication
def multiply(A, B):
    return [a*b for a,b in zip(A, B)]

# Turns matrix of strings into floats or ints
def stringChange(A, choice):
    for i in range(0, len(A)):
        if choice == "float":
            A[i] = float(A[i])
        elif choice == "int":
            A[i] = int(A[i])
    return A

# Returns column of matrix A
def getColumn(A, column):
    return [row[column] for row in A]

# Viterbi Algorithm
def viterbiAlgorithm(A, B, Pi, O):

    delta1 = multiply(Pi[0], getColumn(B, O[0])) # Getting initial delta
    previousDelta = delta1

    stateSequence = []

    numberOfStates = len(A)

    # Start at 1 because 0 was used for delta1
    for i in range (1, len(O)):
        # Gets all probabilities --> 4 x 4 matrix
        probabilites = [[previousDelta[j] * A[j][k] * B[k][O[i]] for j in range(numberOfStates)] for k in range(numberOfStates)]
        # Gets max of each row --> stored in a 1 x 4 matrix
        newDelta = [max(probabilites[i]) for i in range(0, len(probabilites))]
        # Gets index of the max value from its respective row --> stored in a 1 x 4 matrix // These values essentially hold the states
        newDeltaIndex = [probabilites[i].index(max(probabilites[i])) for i in range(0, len(probabilites))]

        # The index from newDeltaIndex associated with the highest value in newDelta is the most likely previous state
        stateSequence.append(newDeltaIndex[newDelta.index(max(newDelta))])

        previousDelta = newDelta
    print(newDelta)
    print(newDeltaIndex)

    # Last state is just the index of the max value in the last delta
    lastState = previousDelta.index(max(previousDelta))
    stateSequence.append(lastState)

    #print(' '.join([str(x) for x in stateSequence]))
    print(' '.join(map(str, stateSequence)))

    return


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
#print("O:", O)

"""
A: [[0.0, 0.8, 0.1, 0.1],
    [0.1, 0.0, 0.8, 0.1],
    [0.1, 0.1, 0.0, 0.8],
    [0.8, 0.1, 0.1, 0.0]]

B: [[0.9, 0.1, 0.0, 0.0],
    [0.0, 0.9, 0.1, 0.0],
    [0.0, 0.0, 0.9, 0.1],
    [0.1, 0.0, 0.0, 0.9]]

Pi: [[1.0, 0.0, 0.0, 0.0]]

O: [1, 1, 2, 2]
"""
viterbiAlgorithm(A, B, Pi, O)
