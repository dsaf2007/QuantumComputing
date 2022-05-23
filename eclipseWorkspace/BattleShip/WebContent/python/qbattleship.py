# Quantum Battleship

# https://docs.python.org/3/library/cgi.html
# https://www.tutorialspoint.com/python/python_cgi_programming.htm

import sys
#from qiskit import QuantumProgram
#import Qconfig
import getpass
import random
import numpy
import math

from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import QasmSimulator
from qiskit.visualization import plot_histogram
from qiskit import Aer
from qiskit.visualization import plot_state_city
from qiskit import IBMQ

import cgi
import cgitb

# solve the relative dependencies if you clone QISKit from the Git repo and use like a global.
sys.path.append('../../qiskit-sdk-py/')

# debug
cgitb.enable(display=0, logdir=".")

# The variable ship[X][Y] will hold the position of the Yth ship of player X+1
# all values are initialized to the impossible position -1|
shipPos = [[-1]*3 for _ in range(2)]

# the variable bombs[X][Y] will hold the number of times position Y has been bombed by player X+1
bomb = [[0]*5 for _ in range(2)]  # all values are initialized to zero

# CGI - parse HTTP request
form = cgi.FieldStorage()

ships1 = form["ships1"].value
ships2 = form["ships2"].value
bombs1 = form["bombs1"].value
bombs2 = form["bombs2"].value

#device = 'ibmqx_qasm_simulator'
#device = 'local_qasm_simulator'
device = str(form["device"].value)

###### TEST
#shipPos[0] = list(map(int, "0,1,2".split(","))) # [0,1,2]
#shipPos[1] = list(map(int, "0,1,2".split(","))) # [0,1,2]
#bomb[0] = list(map(int, "0,0,1,0,0".split(",")));
#bomb[1] = list(map(int, "1,0,1,0,0".split(",")));
# END TEST

shipPos[0] = list(map(int, ships1.split(",")))  # [0,1,2]
shipPos[1] = list(map(int, ships2.split(",")))  # [0,1,2]

bomb[0] = list(map(int, bombs1.split(",")))
bomb[1] = list(map(int, bombs2.split(",")))

stdout = "Ship Pos: " + str(shipPos) + " Bomb counts: " + str(bomb) + "<br>"


# note that device should be 'ibmqx_qasm_simulator', 'ibmqx2' or 'local_qasm_simulator'
# while we are at it, let's set the number of shots
shots = 1024


stdout += "Device: " + device + " Shots:" + str(shots) + "<br>"

###############################
# main loop. For this game, each interation starts by asking players where on the opposing grid they want a bomb
# The quantum computer then calculates the effects of the bombing, and the results are presented to the players


# the variable grid[player] will hold the results for the grid of each player
grid = [{}, {}]


# now we create and run the quantum programs that implement this on the grid for each player
for player in range(2):
    # now to set up the quantum program (QASM) to simulate the grid for this player
    q = QuantumRegister(5, 'q')
    c = ClassicalRegister(5,'c')
    gridScript = QuantumCircuit(q,c)
    backend = Aer.get_backend('qasm_simulator')

	# add the bombs (of the opposing player)
    for position in range(5):
		# add as many bombs as have been placed at this position
        for n in range(bomb[(player+1) % 2][position]):
            for ship in [0, 1, 2]:
                if (position == shipPos[player][ship]):
                    frac = 1/(ship+1)
                    gridScript.u(frac * math.pi, 0.0, 0.0, q[position]) 

    #finally, measure them
    for position in range(5):
        gridScript.measure(q[position], c[position])

	# to see what the quantum computer is asked to do, we can print the QASM file
	# this lines is typically commented out
	#print( Q_program.get_qasm("gridScript") )

	# compile and run the QASM
    job_sim = backend.run(transpile(gridScript,backend),shots)
    results = job_sim.result()

	# extract data
    grid[player] = results.get_counts("gridScript")

# we can check up on the data if we want
# these lines are typically commented out
#print( "grid[0]=" + str(grid[0]) )
#print( "grid[1]=" + str(grid[1]) )

# if one of the runs failed, tell the players and start the round again
if (('Error' in grid[0].values()) or ('Error' in grid[1].values())):

	stdout += "The process timed out. Try this round again.<br>"

else:

	# look at the damage on all qubits (we'll even do ones with no ships)
	# this will hold the prob of a 1 for each qubit for each player
    damage = [[0]*5 for _ in range(2)]

	# for this we loop over all 5 bit strings for each player
    for player in range(2):
        for bitString in grid[player].keys():
			# and then over all positions
            for position in range(5):
				# if the string has a 1 at that position, we add a contribution to the damage
				# remember that the bit for position 0 is the rightmost one, and so at bitString[4]
                if (bitString[4-position] == "1"):
                    damage[player][position] += grid[player][bitString]/shots

    stdout += "Damage: " + str(damage) + "<br>"

    # give results to players
    for player in [0, 1]:

		# report damage for qubits that are ships, and which have significant damange
		# ideally this would be non-zero damage, but noise means that can happen for ships that haven't been hit
		# so we choose 5% as the threshold
        display = [" ?  "]*5
		# loop over all qubits that are ships
        for position in shipPos[player]:
			# if the damage is high enough, display the damage
            if (damage[player][position] > 0.1):
                if (damage[player][position] > 0.9):
                    display[position] = "100%"
                else:
                    display[position] = str(int(100*damage[player][position])) + "% "

		# if a player has all their ships destroyed, the game is over
		# ideally this would mean 100% damage, but we go for 95% because of noise again
        if (damage[player][shipPos[player][0]] > .9) and (damage[player][shipPos[player][1]] > .9) and (damage[player][shipPos[player][2]] > .9):
			#print ("***All Player " + str(player+1) + "'s ships have been destroyed!***\n\n")
            game = False


# Resposne
print("Content-type: application/json\n\n")
print("{\"status\": 200, \"message\": \"" +
      stdout + "\", \"damage\":" + str(damage) + "}")
