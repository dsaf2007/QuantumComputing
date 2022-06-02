from math import pi
import sys
import time
import math
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import QasmSimulator
from qiskit.visualization import plot_histogram
from qiskit import Aer
from qiskit.visualization import plot_state_city
from qiskit import IBMQ

# Prior to the start of the game, Alice and Bob share the following quantum state


# 4 qubits (Alice = 2, Bob = 2)
N = 4


# Creating registers
qr = QuantumRegister(N, 'qr')

# for recording the measurement on qr
cr = ClassicalRegister(N, 'cr')


sharedEntangled = QuantumCircuit(qr, cr)

#Create uniform superposition of all strings of length 2
for i in range(2):
    sharedEntangled.h(qr[i])

#The amplitude is minus if there are odd number of 1s
for i in range(2):
    sharedEntangled.z(qr[i])

#Copy the content of the fist two qubits to the last two qubits
for i in range(2):
    sharedEntangled.cx(qr[i], qr[i+2])

#Flip the last two qubits
for i in range(2, 4):
    sharedEntangled.x(qr[i])

#------  circuits of Alice's and Bob's operations.
#we first define controlled-u gates required to assign phases


def ch(qProg, a, b):
    """ Controlled-Hadamard gate """
    qProg.h(b)
    qProg.sdg(b)
    qProg.cx(a, b)
    qProg.h(b)
    qProg.t(b)
    qProg.cx(a, b)
    qProg.t(b)
    qProg.h(b)
    qProg.s(b)
    qProg.x(b)
    qProg.s(a)
    return qProg


def cu1pi2(qProg, c, t):
    """ Controlled-u1(phi/2) gate """
    qProg.p(pi/4.0, c)
    qProg.cx(c, t)
    qProg.p(-pi/4.0, t)
    qProg.cx(c, t)
    qProg.p(pi/4.0, t)
    return qProg


def cu3pi2(qProg, c, t):
    """ Controlled-u3(pi/2, -pi/2, pi/2) gate """
    qProg.p(pi/2.0, t)
    qProg.cx(c, t)
    qProg.u(-pi/4.0, 0, 0, t)
    qProg.cx(c, t)
    qProg.u(pi/4.0, -pi/2.0, 0, t)
    return qProg


#--------------------------------------------------------------------------
# Define circuits used by Alice and Bob for each of their inputs: 1,2,3
# dictionary for Alice's operations/circuits
aliceCircuits = {}

# Quantum circuits for Alice when receiving  1, 2, 3
for idx in range(1, 4):
    circuitName = "Alice"+str(idx)
    #aliceCircuits[circuitName] = Q_program.create_circuit(circuitName, [qr], [cr])
    aliceCircuits[circuitName] = QuantumCircuit(qr, cr)
    theCircuit = aliceCircuits[circuitName]

    if idx == 1:
        #the circuit of A_1
        theCircuit.x(qr[1])
        theCircuit.cx(qr[1], qr[0])
        theCircuit = cu1pi2(theCircuit, qr[1], qr[0])
        theCircuit.x(qr[0])
        theCircuit.x(qr[1])
        theCircuit = cu1pi2(theCircuit, qr[0], qr[1])
        theCircuit.x(qr[0])
        theCircuit = cu1pi2(theCircuit, qr[0], qr[1])
        theCircuit = cu3pi2(theCircuit, qr[0], qr[1])
        theCircuit.x(qr[0])
        theCircuit = ch(theCircuit, qr[0], qr[1])
        theCircuit.x(qr[0])
        theCircuit.x(qr[1])
        theCircuit.cx(qr[1], qr[0])
        theCircuit.x(qr[1])

    elif idx == 2:
        theCircuit.x(qr[0])
        theCircuit.x(qr[1])
        theCircuit = cu1pi2(theCircuit, qr[0], qr[1])
        theCircuit.x(qr[0])
        theCircuit.x(qr[1])
        theCircuit = cu1pi2(theCircuit, qr[0], qr[1])
        theCircuit.x(qr[0])
        theCircuit.h(qr[0])
        theCircuit.h(qr[1])

    elif idx == 3:
        theCircuit.cz(qr[0], qr[1])
        theCircuit.swap(qr[0], qr[1])  # not supported in composer
        theCircuit.h(qr[0])
        theCircuit.h(qr[1])
        theCircuit.x(qr[0])
        theCircuit.x(qr[1])
        theCircuit.cz(qr[0], qr[1])
        theCircuit.x(qr[0])
        theCircuit.x(qr[1])

    #measure the first two qubits in the computational basis
    theCircuit.measure(qr[0], cr[0])
    theCircuit.measure(qr[1], cr[1])

# dictionary for Bob's operations/circuits
bobCircuits = {}

# Quantum circuits for Bob when receiving 1, 2, 3
for idx in range(1, 4):
    circuitName = "Bob"+str(idx)
    bobCircuits[circuitName] = QuantumCircuit(qr, cr)
    theCircuit = bobCircuits[circuitName]
    if idx == 1:
        theCircuit.x(qr[2])
        theCircuit.x(qr[3])
        theCircuit.cz(qr[2], qr[3])
        theCircuit.x(qr[3])
        theCircuit.p(pi/2.0, qr[2])
        theCircuit.x(qr[2])
        theCircuit.z(qr[2])
        theCircuit.cx(qr[2], qr[3])
        theCircuit.cx(qr[3], qr[2])
        theCircuit.h(qr[2])
        theCircuit.h(qr[3])
        theCircuit.x(qr[3])
        theCircuit = cu1pi2(theCircuit, qr[2], qr[3])
        theCircuit.x(qr[2])
        theCircuit.cz(qr[2], qr[3])
        theCircuit.x(qr[2])
        theCircuit.x(qr[3])

    elif idx == 2:
        theCircuit.x(qr[2])
        theCircuit.x(qr[3])
        theCircuit.cz(qr[2], qr[3])
        theCircuit.x(qr[3])
        theCircuit.p(pi/2.0, qr[3])
        theCircuit.cx(qr[2], qr[3])
        theCircuit.h(qr[2])
        theCircuit.h(qr[3])

    elif idx == 3:
        theCircuit.cx(qr[3], qr[2])
        theCircuit.x(qr[3])
        theCircuit.h(qr[3])

    #measure the third and fourth qubits in the computational basis
    theCircuit.measure(qr[2], cr[2])
    theCircuit.measure(qr[3], cr[3])

#################################################
# A quantum program for one round of the game
# backend: device name or simulator
# real_dev: Tru to run in a real device
# shots: number of shots
#################################################


def one_round(backend, real_dev, shots=1):
    #generate random integers
    a, b = random.randint(1, 3), random.randint(1, 3)
    #a, b = 3, random.randint(1,3)
    print("Magic Square  a = " + str(a) +
          " b = " + str(b) + " Device: " + backend)
    aliceCircuit = aliceCircuits["Alice" + str(a)]
    bobCircuit = bobCircuits["Bob" + str(b)]
    circuitName = "Alice" + str(a) + "Bob" + str(b)
    circuit = sharedEntangled + aliceCircuit + bobCircuit
    if real_dev:
        shots = 10
        #device_cfg = Q_program.get_backend_configuration(backend)
        #device_coupling = device_cfg['coupling_map']
        backend_sim = Aer.get_backend(backend)
        results = Q_program.execute(
            [circuitName], backend=backend, shots=shots, coupling_map=device_coupling)
    else:
        #results = Q_program.execute([circuitName], backend=backend, shots=shots)
        backend_sim = Aer.get_backend(backend)
        job = backend_sim.run(transpile(circuit,backend_sim),shots=shots)
        results =  job.result()
        
    answer = results.get_counts(circuit)
    print("Device = " + backend + " counts: " + str(answer))
    for key in answer.keys():
        aliceAnswer = [int(key[-1]), int(key[-2])]
        bobAnswer = [int(key[-3]), int(key[-4])]
        if sum(aliceAnswer) % 2 == 0:  # the sume of Alice answer must be even
            aliceAnswer.append(0)
        else:
            aliceAnswer.append(1)
        if sum(bobAnswer) % 2 == 1:  # the sum of Bob answer must be odd
            bobAnswer.append(0)
        else:
            bobAnswer.append(1)
        break
    print("Alice answer for a = ", a, "is", aliceAnswer)
    print("Bob answer for b = ", b, "is", bobAnswer)
    # check if the intersection of their answers is the same
    if(aliceAnswer[b-1] != bobAnswer[a-1]):
        print("Alice and Bob lost")
    else:
        print("Alice and Bob won")
    #############################################
    #quantum program for all rounds
    #ckend: device name or simulator
    #al_dev: Tru to run in a real device
    #ots:  # of shots
        #############################################
def all_rounds(backend, real_dev, shots=10):
    nWins = 0
    nLost = 0
    for a in range(1, 4):
        for b in range(1, 4):
            print("For a = " + str(a) + " , b = " + str(b))
            rWins = 0
            rLost = 0
            aliceCircuit = aliceCircuits["Alice" + str(a)]
            bobCircuit = bobCircuits["Bob" + str(b)]
            circuitName = "Alice" + str(a) + "Bob"+str(b)

            circuit = sharedEntangled + aliceCircuit +bobCircuit

            if real_dev:
                ibmqx2_backend = Q_program.get_backend_configuration(backend)
                ibmqx2_coupling = ibmqx2_backend['coupling_map']
                results = Q_program.execute([circuitName], backend=backend, shots=shots,
                                            coupling_map=ibmqx2_coupling, max_credits=3, timeout=240)
            else:
                backend_sim = Aer.get_backend(backend)
                job = backend_sim.run(transpile(circuit,backend_sim),shots=shots)
                results =  job.result()
        
            answer = results.get_counts(circuit)
            for key in answer.keys():
                kfreq = answer[key]  # frequencies of keys obtained from measurements
                aliceAnswer = [int(key[-1]), int(key[-2])]
                bobAnswer = [int(key[-3]), int(key[-4])]
                if sum(aliceAnswer) % 2 == 0:
                    aliceAnswer.append(0)
                else:
                    aliceAnswer.append(1)
                if sum(bobAnswer) % 2 == 1:
                    bobAnswer.append(0)
                else:
                    bobAnswer.append(1)
    			
                print(backend + " answer: " + key + " Alice: " +
    			      str(aliceAnswer) + " Bob:" + str(bobAnswer))
    			#print("Alice answer for a = ", a, "is", aliceAnswer)
    			#print("Bob answer for b = ", b, "is", bobAnswer)
                if(aliceAnswer[b-1] != bobAnswer[a-1]):
				    #print(a, b, "Alice and Bob lost")
                    nLost += kfreq
                    rLost += kfreq
                else:
				    #print(a, b, "Alice and Bob won")
                    nWins += kfreq
                    rWins += kfreq
            print("\t#wins = ", rWins, "out of ", shots, "shots")
    print("Number of Games = ", nWins+nLost)
    print("Number of Wins = ", nWins)
    print("Winning probabilities = ", (nWins*100.0)/(nWins+nLost))


#################################################
# main
#################################################
if __name__ == '__main__':
	#backend = "local_qasm_simulator"
	backend = "qasm_simulator"
	#backend = "ibmqx2"
	real_dev = False

	#one_round(backend, real_dev)
	all_rounds(backend, real_dev)
