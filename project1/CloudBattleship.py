import sys
# Checking the version of PYTHON; we only support > 3.5
if sys.version_info < (3, 5):
 raise Exception('Please use Python version 3.5 or greater.')

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

sys.path.append('../../qiskit-sdk-py')

cgitb.enable(display=0,logdir =".")

shipPos = [ [-1]*3 for _ in range(2)]

bomb = [ [0]*5 for _ in range(2)]

shots = 1024

# CGI - parse HTTP request
form = cgi.FieldStorage()
ships1 = form["ships1"].value
ships2 = form["ships2"].value
bombs1 = form["bombs1"].value
bombs2 = form["bombs2"].value
# 'local_qasm_simulator', 'ibmqx_qasm_simulator'
device = str(form["device"].value)
shipPos[0] = list(map(int, ships1.split(","))) # [0,1,2]
shipPos[1] = list(map(int, ships2.split(","))) # [0,1,2]
bomb[0] = list(map(int, bombs1.split(",")))
bomb[1] = list(map(int, bombs2.split(",")))
stdout = "Ship Pos: " + str(shipPos) + " Bomb counts: " + str(bomb) + "<br>"

grid = [{},{}]

for player in range(2):
    q = QuantumRegister(5,'q')
    c = ClassicalRegister(5,'c')

    gridScript = QuantumCircuit(q,c)
    backend = Aer.get_backend('qasm_simulator')

    for position in range(5):
        # add as many bombs as have been placed at this position
        for n in range(bomb[(player+1) % 2][position]):
        # the effectiveness of the bomb
        # (which means the quantum operation we apply)
        # depends on which ship it is
            for ship in [0, 1, 2]:
                if (position == shipPos[player][ship]):
                    frac = 1/(ship+1)
                    # add this fraction of a NOT to the QASM
                    gridScript.u(frac * math.pi, 0.0, 0.0,q[position])
    
    for position in range(5):
        gridScript.measure(q[position], c[position])

job_sim = backend.run(transpile(gridScript,backend),shots)
results = job_sim.result()
# extract data
grid[player] = results.get_counts(gridScript)


# if one of the runs failed, tell the players and start the round again
if ( ( 'Error' in grid[0].values() ) or ( 'Error' in grid[1].values() ) ):
    stdout += "The process timed out. Try this round again.<br>"
else:
    # look at the damage on all qubits (we'll even do ones with no ships)
    damage = [ [0]*5 for _ in range(2)]
    # for this we loop over all 5 bit strings for each player
    for player in range(2):
        for bitString in grid[player].keys():
        # and then over all positions
            for position in range(5):
            # if the string has a 1 at that position, we add a  contribution to the damage
            # remember that the bit for position 0 is the rightmost  one, and so at bitString[4]
                if (bitString[4-position]=="1"):
                    damage[player][position] += grid[player][bitString]/shots
stdout += "Damage: " + str(damage) + "<br>"


# Response
print("Content-type: application/json\n\n")
print("{\"status\": 200, \"message\": \"" + stdout + "\", \"damage\":" + str(damage) + "}")