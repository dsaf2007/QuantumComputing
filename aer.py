import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import QasmSimulator
from qiskit.visualization import plot_histogram
from qiskit import Aer
from qiskit.visualization import plot_state_city

circ = QuantumCircuit(3)

circ.h(0)
circ.cx(0,1)
circ.cx(0,2)


backend = Aer.get_backend('statevector_simulator')

job = backend.run(circ)

result = job.result()

outputstate = result.get_statevector(circ,decimals=3)
#print(outputstate)

#plot_state_city(outputstate, filename='outputstate.png')


#create quantum circuit
meas = QuantumCircuit(3,3)
meas.barrier(range(3))
meas.measure(range(3),range(3))

circ.add_register(meas.cregs[0])
qc = circ.compose(meas)

print(qc)
qc.draw(output='mpl',filename="qc_circuit.png")