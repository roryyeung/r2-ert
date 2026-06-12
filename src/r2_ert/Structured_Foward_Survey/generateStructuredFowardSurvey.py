"""Function to generate a regular 2D quadrilateral survey with specified parameters."""

import warnings
from .StructuredFowardSurvey import StructuredFowardSurvey

def generateStructuredFowardSurvey(survey_length,survey_depth, num_electrodes, cell_width=0.25,
                                         cell_depth=0.25, title="Test", topography=None,
                                          electrode_sequence=None):
    
    """
    Generates a regular 2D quadrilateral survey with the given parameters and returns
    a StructuredFowardSurvey object.
    
    Note that this survey will add an additional 14 cells of increasing width at either
    end of the survey and an additional 8 cells of increasing depth at the bottom of
    the survey to help with boundary effects.

    The width additional cells are designed to max out at 10x survey legnth, to act as
    "infinity" electrodes for the pole-pole survey, should this be selected.

    Parameters:
    - survey_length: Number of cells in the survey in the x-direction (horizontal)
        note that this is before adding extra boundrary cells
    - survey_depth: Number of cells in the survey in the z-direction (vertical)
        note that this is before adding extra boundrary cells
    - cell_width: Width of each cell in the x-direction (default: 0.25)
    - cell_depth: Depth of each cell in the z-direction (default: 0.25)
    - title: Title for the survey (R2 Line 1)
    - topography: List of topography values (length should be equal to survey_length,
        default: None, which sets topography to 0). Note that we will
        automatically select the topography of the 14 cells on either side via
        the first and last value of the topography list.
    - electrode_sequence: List of electrode positions
        - default: None, which sets electrode positions evenly across the desired range
        - "pole-pole": same as None, apart from first and last electrodes, which at set
        at "infinity" - actually the edge of the boundary cells
        - if a list of electrode positions is provided, these will be used as the electrode positions,
        and the function will check that they are valid (i.e. between 1 and survey_length inclusive)
    
    Returns:
    - survey: StructuredFowardSurvey object with the generated survey
    """

    # Calculate the number of nodes in the x and z directions
    numnp_x = survey_length + 28 # Add 28 for the extra boundary cells (14 on each side)
    numnp_z = survey_depth + 8   # Add 8 for the extra boundary cells at the bottom

    # Create the survey object
    survey = StructuredFowardSurvey(numnp_x, numnp_z, num_electrodes, title=title,
                                     job_type=job_type)
    
    ### Set X Coordinates
    # Calculate inf distance and spacings for the boundary cells
    inf_distance = cell_width * survey_length * 10
    spacing_sequence = [(inf_distance / 1000) *  (i ** 2) for i in range(1,15,1)]
    cumulative_spacing_sequence = [sum(spacing_sequence[:i]) for i in range(1, len(spacing_sequence) + 1)]

    # Generate x coordinates
    x_coords = []
    # Add extra boundary cells on the left with increasing width
    for i in range(0,14,1):
        x_coords.insert(0, -cumulative_spacing_sequence[i])
    # Add the main survey cells
    for i in range(survey_length):
        x_coords.append(i * cell_width)
    # Add extra boundary cells on the right with increasing width
    for i in range(0,14,1):
        x_coords.insert(0, cumulative_spacing_sequence[i])
    
    # Add x coordinates to the survey
    survey.set_x_coords(x_coords)

    ### Set Z Coordinates

    # Generate z coordinates
    z_coords = []
    # Add the main survey cells
    for i in range(survey_depth):
        z_coords.append(i * cell_depth)
    # Add extra boundary cells at the bottom with increasing depth
    for i in range(1,9,1):
        counter = 0
        z_coords.append((counter + cell_depth * i * 8) ** 2)
        counter += cell_depth * i
    
    # Add z coordinates to the survey
    survey.set_z_coords(z_coords)

    ### Set topography
    # Note - this uses the column numbers, not distance

    if topography is None:
        topography = [0 for _ in range(len(x_coords))]
    elif len(topography) != survey_length:
        raise ValueError(f"Length of topography should be {survey_length}.")
    else:
        # Add the topography of the extra boundary cells on either side
        left_topo = [topography[0] for _ in range(14)]
        right_topo = [topography[-1] for _ in range(14)]
        full_topo = left_topo + topography + right_topo
        survey.set_topography(full_topo)

    ### Set electrode positions
    # Note - this uses the column numbers, not distance

    if electrode_sequence is None:
        # Considers evenly spaced arrays other than pole-pole
        electode_spacing = round((survey_length-1)/(num_electrodes-1))
        if electode_spacing < 4:
            warnings.warn(f"generateRegular2dQuadrilateralSurvey: Only {electode_spacing} cells between electrodes - should be at least 4. Consider reducing number of electrodes or survey length to ensure valid pole-pole array. May be acceptable if R2 has sigularity activated.")
        electrode_sequence = [1 + i * electode_spacing for i in range(0,num_electrodes)] #TODO - check
        print(f"Electrode sequence: {electrode_sequence}")
        print(f"Electrode sequence length: {len(electrode_sequence)}")
        survey.electrode_sequence = electrode_sequence
    elif electrode_sequence == "pole-pole": #TODO - Fix this sequence generation - possible as external function
        #
        # Considers a pole-pole array
        # Set First electrode at the left edge of the boundary cells and last electrode at the
        # right edge of the boundary cells
        electode_spacing = round((survey_length-1)/(num_electrodes-3))
        if electode_spacing < 4:
            warnings.warn(f"generateRegular2dQuadrilateralSurvey: Only {electode_spacing} cells between electrodes - should be at least 4. Consider reducing number of electrodes or survey length to ensure valid pole-pole array. May be acceptable if R2 has sigularity activated.")
        electrode_sequence = [i * electode_spacing for i in range(1,num_electrodes-1)]
        # electrode_sequence = [
        #     round(1 + i * (survey_length - 1) / (num_electrodes - 3)) for i in range(num_electrodes-2) # Notice the -3, because removing the first and last
        #     ]
        electrode_sequence.insert(0,1) # Inserts the first x position at start
        electrode_sequence.append(len(x_coords)) # Appends the last x position at end
        print(f"Electrode sequence: {electrode_sequence}")
        print(f"Electrode sequence length: {len(electrode_sequence)}")
        survey.electrode_sequence = electrode_sequence
    elif len(electrode_sequence) != num_electrodes:
        # Consders error if electrode sequence is provided but has incorrect number of electrodes
        raise ValueError(f"Length of electrode_sequence should be {num_electrodes}. Legnth: {len(electrode_sequence)}")
    else:
        # Considers the case where electrode sequence is provided by the user
        # Check that electrode positions are valid
        for pos in electrode_sequence:
            if pos < 1 or pos > survey_length:
                raise ValueError(f"Electrode positions should be between 1 and {survey_length} inclusive. Invalid position: {pos}")
    # TODO - add error check if not at least spacing of 4 cells between electrodes, to ensure that the pole-pole array is valid

    
    # Add electrodes to the survey
    for i, pos in enumerate(electrode_sequence, start=1):
        survey.add_electrode(i, pos, 1)
    
    return survey