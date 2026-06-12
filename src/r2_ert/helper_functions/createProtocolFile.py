"""Helper function to create protocol file for R2 ERT survey"""
import pandas as pd

def createProtocolFile(num_electrodes, mode=None):
    if mode == "pole-pole" or mode == "plpl":
        protocol = pd.DataFrame(columns=["N", "M", "A", "B"])
        N = 1
        B = num_electrodes
        M = [i for i in range(2, num_electrodes-1)]
        print(M)
        A = [i for i in range(3, num_electrodes)] 
        print(A)
        for idx,m in enumerate(M):
            for a in A[idx:]:
                protocol = pd.concat([protocol, pd.DataFrame({"N": N, "M": m, "A": a, "B": B}, index=[1])], ignore_index=True)
    return protocol   