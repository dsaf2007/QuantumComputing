import sys,time,math
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import QasmSimulator
from qiskit.visualization import plot_histogram
from qiskit import Aer
from qiskit.visualization import plot_state_city
from qiskit import IBMQ


def main(M = 16, numberOfCoins = 8 , indexOfFalseCoin = 6, backend = "local_qasm_simulator" , shots = 1 ):
    if numberOfCoins < 4 or numberOfCoins >= M:
        raise Exception("Please use numberOfCoins between 4 and ", M-1)
    if indexOfFalseCoin < 0 or indexOfFalseCoin >= numberOfCoins:
        raise Exception("indexOfFalseCoin must be between 0 and ", numberOfCoins-1)
    
    qr = QuantumRegister(numberOfCoins+1, 'qr')
    cr = ClassicalRegister(numberOfCoins+1,'cr')
    circuit = QuantumCircuit(qr,cr)
    N = numberOfCoins
    #backend = Aer.get_backend('')

    #Create uniform superposition of all strings of length N
    for i in range(N):
        circuit.h(qr[i])

    #Perform XOR(x) by applying CNOT gates sequentially from qr[0] to qr[N-1] and storing the result to qr[N]
    for i in range(N):
        circuit.cx(qr[i],qr[N])

    # Measure qr[N] and store the result to cr[N].
    # continue if cr[N] is zero, or repeat otherwise
    circuit.measure(qr[N], cr[N])

    circuit.x(qr[N]).c_if(cr, 0)
    circuit.h(qr[N]).c_if(cr, 0)

    # rewind the computation when cr[N] is not zero
    for i in range(N):
        circuit.h(qr[i]).c_if(cr, 2**N)

    #----- Construct the quantum beam balance
    k = indexOfFalseCoin
    # Apply the quantum beam balance on the desired superposition state
    #(marked by cr equal to zero)
    circuit.cx(qr[k], qr[N]).c_if(cr, 0)

    # --- Identify the false coin
    # Apply Hadamard transform on qr[0] ... qr[N-1]
    for i in range(N):
        circuit.h(qr[i]).c_if(cr, 0)
    
    for i in range(N):
        circuit.measure(qr[i],cr[i])

    backend_sim = Aer.get_backend(backend)

    job = backend_sim.run(transpile(circuit,backend_sim),shots)
    result = job.result()
    answer = result.get_counts(circuit)

    print("Device " + backend + " counts " + str(answer))

    # Get most common label
    for key in answer.keys():
        normalFlag, _ = Counter(key[1:]).most_common(1)[0]

    for i in range(2,len(key)):
        if key[i] != normalFlag:
            print("False coin index is: ", len(key) - i - 1)


#################################################
# main
#################################################
if __name__ == '__main__':
    M = 8 #Maximum qubits available
    numberOfCoins = 4 #Up to M-1, where M is the number of qubits available
    indexOfFalseCoin = 2 #This should be 0, 1, ..., numberOfCoins - 1,
    backend = "qasm_simulator"
    
    shots = 1 # We perform a one-shot experiment
    main(M, numberOfCoins, indexOfFalseCoin, backend, shots)
