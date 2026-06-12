"""Helper Functions for visualising pseudosections from files or tables"""
import pandas as pd
import matplotlib.pyplot as plt

def visualisePseudosectionFromFile(file_path,mode,x_coords=None,x_idx=None):
    #TODO - if x_coords is provided, use these for the x axis instead of indexes - will need electrode sequence as well
    if mode == "plpl" or mode == "pole-pole":
        data = pd.read_csv(file_path, skiprows=1, header=None,
                            sep=r"[ ]{2,}",
                           names=["measurement_number", "A", "B", "M", "N", "transfer_resistance", "R2_apparent_resistivity"],
                           index_col="measurement_number")
        data["midoint_x"] = (data["B"] + data["M"]) / 2
        data["pesudodepth"] = data["B"] - data["M"]
        plt.scatter(data["midoint_x"], data["pesudodepth"], c=data["R2_apparent_resistivity"], cmap="viridis")
        plt.colorbar(label="Apparent Resistivity (Ohm.m)")
        if x_coords is None and x_idx is None:
            plt.xlabel("Midpoint Electrode Index")
        elif x_coords is None and x_idx is not None:
            plt.xlabel("Midpoint X Index")
        else:
            plt.xlabel("Midpoint X Coordinate (m)")
        plt.ylabel("Pseudodepth (Index)")
        plt.show()

    return data

def visualisePseudosectionFromTable(data,mode,x_coords=None,x_idx=None):
    pass