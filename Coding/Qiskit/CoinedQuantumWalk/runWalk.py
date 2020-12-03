import sys
sys.path.append('../Tools')
from IBMTools import( 
        simul,
        savefig,
        saveMultipleHist)
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from qiskit import( ClassicalRegister,
        QuantumRegister,
        QuantumCircuit,
        execute,
        Aer)
from qiskit.visualization import( plot_histogram,
                        plot_state_city)
plt.rcParams['figure.figsize'] = 11,8
matplotlib.rcParams.update({'font.size' : 15})

#CNot decomposition
def cnx(qc,*qubits):
    if len(qubits) >= 3:
        last = qubits[-1]
        #A matrix: (made up of a  and Y rotation, lemma4.3)
        qc.crz(np.pi/2, qubits[-2], qubits[-1])
        #cry
        qc.cu(np.pi/2, 0, 0,0, qubits[-2],qubits[-1])
        #Control not gate
        cnx(qc,*qubits[:-2],qubits[-1])
        #B matrix (cry again, but opposite angle)
        qc.cu(-np.pi/2, 0, 0,0, qubits[-2], qubits[-1])
        #Control
        cnx(qc,*qubits[:-2],qubits[-1])
        #C matrix (final rotation)
        qc.crz(-np.pi/2,qubits[-2],qubits[-1])
    elif len(qubits)==3:
        qc.ccx(*qubits)
    elif len(qubits)==2:
        qc.cx(*qubits)
    return qc

def incr(qwc,q,subnode,n):
    for j in range(-1,n-1):
        if(j==-1):
            cnx(qwc,subnode[0],*q[-1::-1])
            qwc.barrier()
        else:
            cnx(qwc,subnode[0],*q[-1:j:-1])
            qwc.barrier()
    return qwc

def decr(qwc,q,subnode,n):
    qwc.x(subnode[0])
    c=0
    qwc.x(q[-1:0:-1])
    for j in range(-1,n-1):
        if(j==-1):
            c+=1
            cnx(qwc,subnode[0],*q[-1::-1])
            qwc.x(q[c])
            qwc.barrier()
        else:
            c+=1
            cnx(qwc,subnode[0],*q[-1:j:-1])
            if(c==n):
                break
            qwc.x(q[c])
            qwc.barrier()
    qwc.x(subnode[0])
    return qwc

def runWalk(N,times,stateVec):
    qreg = QuantumRegister(N)
    qsub = QuantumRegister(1)
    creg = ClassicalRegister(N)
    qwc = QuantumCircuit(qreg,qsub,creg)
    for i in range(0,times):
        qwc.h(qsub[0])
        decr(qwc,qreg,qsub,N)
        incr(qwc,qreg,qsub,N)
        if not stateVec:
            qwc.barrier()
            qwc.measure(qreg,creg)
            qwc.barrier()
    return qwc

def runMultipleWalks(N,steps,stateVec):
    circList = []
    circListAux = []
    for n in N:
        qreg = QuantumRegister(n)
        qsub = QuantumRegister(1)
        creg = ClassicalRegister(n)
        for step in steps:
            circ = QuantumCircuit(qreg,qsub,creg)
            circ = runWalk(n,step,stateVec)
            circListAux.append(circ)
            #circ.reset()
        circList.append(circListAux)
        circListAux = []
    return circList

filePath = 'CoinedQuantumWalk/'
defaultFileName = "CoinedQW_N"

singleN = 10
singleSteps = 5

N=[2,3]
steps=[1,2]

#TODO: Estes graficos nao estao a ficar grande coisa, tenho que pensar numa ideia melhor.
#singleWalk = runWalk(singleN, singleSteps,True)
#results = simul(singleWalk, True)
#plt.plot(results)
#plot_state_city(results)
#plt.show()

multipleWalks = runMultipleWalks(N,steps,False)
saveMultipleHist(N,steps,multipleWalks,filePath,defaultFileName)