"""Helper function to visualise resistivity in the foward model"""
import numpy as np
import matplotlib.pyplot as plt

def visualiseResistivity(survey, coordinates = False, electrode_sequence=False):
    grid = np.zeros((survey.numnp_z - 1, survey.numnp_x - 1), dtype=None, order='F') # Create array of zeros - note that R2 uses Fortran ordering
    for region in survey.regions:
        start_element, end_element, value = region

        for element in range(start_element, end_element + 1):
            # Calculate the row and column indices for the element
            row = (element - 1) % (survey.numnp_z - 1)
            col = (element - 1) // (survey.numnp_z - 1)
            grid[row, col] = value

    #TODO - add conversion to coodinates for x and z axes if coordinates=(x_coords,z_coords)

    # plt.imshow(grid, extent=(survey.x_coords[0], survey.x_coords[-1], survey.z_coords[-1], survey.z_coords[0]), cmap='viridis')
    plt.imshow(grid)
    if electrode_sequence: #Allows for electrode cordinates to be plotted if desired
        plt.scatter(electrode_sequence,np.zeros(len(electrode_sequence)), color='black', label='Electrodes')
    plt.colorbar(label='Resistivity')
    plt.xlabel('X_Index')
    plt.ylabel('Z_Index')
    plt.title('Survey Regions')
    plt.show()