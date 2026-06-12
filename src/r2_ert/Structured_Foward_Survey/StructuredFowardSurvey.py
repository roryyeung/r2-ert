"""Module for representing a structured 2D forward ERT survey."""

import os
import warnings

class StructuredFoward_Survey:
    """
    Class to represent a structured 2D quadrilateral ERT survey.
    This class can write itself to an R2 input file format.

    See R2 documentation for more details on the input file format:
    http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2_readme.pdf
    """
    def __init__(self, numnp_x, numnp_z, num_electrodes, title="", singular_type=1):
        """
        Initialize the survey with the given parameters.
        Parameters:
        - numnp_x: Number of nodes in the x-direction (horizontal)
        - numnp_z: Number of nodes in the z-direction (vertical)
        - num_electrodes: Number of electrodes in the survey line
        - title: Title for the survey (R2 Line 1)
        - singular_type: Siginals R2 whether or not to apply signularity removal.
        This reduces error but requires both flat topography and an infinite half space.
        Set to 1 to apply singularity removal, set to 0 to not apply singularity removal.
        """
        # R2 Line 1 - Header
        self.title = title
        # R2 Line 2 - Job Information
        self.job_type = 0
        self.mesh_type = 4
        self.flux_type = 3.0
        self.singular_type = singular_type #Note - set to 1 but assumes both no topography and infinite half space
        self.res_matrix = 0
        # R2 Line 3 - Mesh Information
        self.numnp_x = numnp_x
        self.numnp_z = numnp_z
        # R2 Line 4 - X Coordinates (Initially set to empty list, will be generated later)
        self.x_coords = []
        # R2 Line 5 - Topography (Initially set to zero but can be updated later)
        self.topo = [0 for _ in range(numnp_x)]
        # R2 Line 6 - Z Coordinates (Initially set to empty list, will be generated later)
            # Here, z refers to the depth - z[0] is the surface and should be set to 0,
            # and z[numnp_z-1] is the bottom of the model and should be set to the maximum depth.
        self.z_coords = []
        # R2 Line 11 - Num Regions (Initially set to None, to generate error if not set)
        self.num_regions = None
        # R2 Line 12 - Region Information - file_name (Initially set to None, to generate error if not set)
        self.file_name = None
        # R2 Line 13 - Region Information (Initially set to empty list, will be generated later)
        self.regions = []
        # R2 Line 25 - num_xz_poly (Set to 0 - can be added later)
        self.num_xz_poly = 0
        # R2 Line 26 - num_xz_poly
        self.xz_poly = []
        # R2 Line 27 - Number of Electrodes
        self.num_electrodes = num_electrodes
        # R2 Line 28 - List of electrodes
        self.electrodes = []

        ## Additional Attributes To make Python Easier - not used in R2 input file
        self.electrode_sequence = [] # List of x indices for the electrodes
        
    def set_x_coords(self, x_coords):
        """
        Set the x coordinates for the survey.
        Parameters:
        - x_coords: List of x coordinates (length should be equal to numnp_x)
        """
        if len(x_coords) != self.numnp_x:
            raise ValueError(f"Length of x_coords should be {self.numnp_x}")
        self.x_coords = x_coords

    def set_topography(self, topo):
        """
        Set the topography for the survey.
        Parameters:
        - topo: List of topography values (length should be equal to numnp_x)
        """
        if len(topo) != self.numnp_x:
            raise ValueError(f"Length of topo should be {self.numnp_x}")
        self.topo = topo
        self.singular_type = 0 # If topography is set, then singularity removal cannot be applied

    def set_z_coords(self, z_coords):
        """
        Set the z coordinates for the survey.
        Parameters:
        - z_coords: List of z coordinates (length should be equal to numnp_z)
        """
        if len(z_coords) != self.numnp_z:
            raise ValueError(f"Length of z_coords should be {self.numnp_z}")
        self.z_coords = z_coords 

    def import_res_file(self, res_file):
        """
        Import resitivity data from a res.dat file
        Parameters:
        - res_file: name of the res.dat file (<15 characters)
        """
        if len(res_file) > 15:
            raise ValueError("res_file name should be less than 15 characters.")
        if self.num_regions is None:
            self.num_regions = 0
        elif self.num_regions >= 1:
            raise ValueError("Regions already defined. Cannot import res file.")
        # R2 Line 12 - file_name
        self.file_name = res_file
    
    def create_region(self, start_element, end_element, region_value):
        """
        Create a new region for the survey and sets its value.
        Elements are numbered from top left to bottom right, going down first, then to the right.
    
        e.g. for a 3x3 grid:

        1 4 7
        2 5 8
        3 6 9

        Use this function multiple times to create multiple or irregular regions.

        Parameters:
        - start_element: Starting element number for the region (inclusive)
        - end_element: Ending element number for the region (inclusive)
        - region_value: Value to assign to the region (e.g. resistivity value)

        NOTE:
        You must assign all elements a starting value. The number of elements in the mesh
        is (numnp_x-1) x (numnp_y-1) for a structured quadrilateral mesh. All these elements
        must be assigned a resistivity. Note also that if you assign an element a value,
        it will overwrite any previous assignment.
        """
        if self.num_regions == 0:
            raise ValueError("Res file already defined.")
        elif self.num_regions is None:
            self.num_regions = 0
        self.num_regions += 1

        # R2 Line 12 - elem_1, elem_2, value
        self.regions.append((start_element, end_element, region_value))

    def add_poly_lines(self,xz_poly):
        """
        Creates a bounding box where described xz_poly, tuples of x,z co-ordinates that
        define a polyline bounding the output volume.
        
        If xz_poly is set to zero then no bounding is done in the x-z plane. 
        
        Parameters:
        - xz_poly: List of tuples of (x,z) co-ordinates that define the otside of the box

        NOTE:You may need to set this high, to be above topography
        NOTE: the first and last pair of co-ordinates must be identical
        """
        for poly in xz_poly:
            if len(poly) != 2:
                raise ValueError("Each element in xz_poly should be a tuple of (x,z) co-ordinates.")
            self.xz_poly.append(poly)
            self.num_xz_poly += 1
        if self.xz_poly[0] != self.xz_poly[-1]:
            raise ValueError("The first and last pair of co-ordinates in xz_poly should be identical to create a closed bounding box.")

    def add_electrode(self, electrode_num,x_index,z_index):
        """
        Add an electrode to the survey.
        Parameters:
        - electrode_num: Electrode number (starting from 1)
        - x_index: Index of the x index for the electrode (starting from 1)
        - z_index: Index of the z index for the electrode (starting from 1)
        """
        if electrode_num < 1 or electrode_num > self.num_electrodes:
            raise ValueError(f"Electrode number should be between 1 and {self.num_electrodes} inclusive.")
        if x_index < 1 or x_index > self.numnp_x:
            raise ValueError(f"x_index should be between 1 and {self.numnp_x} inclusive.")
        if z_index < 1 or z_index > self.numnp_z:
            raise ValueError(f"z_index should be between 1 and {self.numnp_z} inclusive.")
        self.electrodes.append((electrode_num, x_index, z_index))

    def write_to_file(self, directory):
        """
        Write the survey data to an R2 input file.
        Parameters:
        - directory: Directory to write the R2 input file to (should end with /)
        """
        filepath = os.path.join(directory, "R2.in")
        # Remove existing R2.in file if it exists
        try:
            os.remove(filepath)
        except OSError:
            pass
        # File Handling - Write the R2 input file
        with open(filepath, "w") as file:
            # R2 Line 1 - Header
            file.write(f"{self.title}\n")
            file.write("\n")
            file.write("\n")
            # R2 Line 2 - Job Information
            file.write(f"    {int(self.job_type)}    {int(self.mesh_type)}  {self.flux_type:.1f}    {int(self.singular_type)}    {int(self.res_matrix)}\n")
            file.write("\n")
            if self.singular_type ==1:
                warnings.warn("Regular2dQuadrilateralSurvey: Singularity removal is activated. Ensure that topography is flat and model is an infinite half space for valid results.")
            # R2 Line 3 - Mesh Information
            file.write(f"       {int(self.numnp_x)}  {int(self.numnp_z)} << numnp_x, numnp_y\n")
            file.write("\n")
            # R2 Line 4 - X Coordinates
            if len(self.x_coords) == 0:
                raise ValueError("x_coords not set. Use set_x_coords() to set the x coordinates before writing to file.")
            if len(self.x_coords) != self.numnp_x:
                raise ValueError(f"Length of x_coords should be {self.numnp_x}. Use set_x_coords() to set the x coordinates before writing to file.")
            for i in range(len(self.x_coords)//10+1):
                for j in range(0,10):
                    if i*10+j < len(self.x_coords):
                        file.write(f"{self.x_coords[i*10+j]:.3f}   ")
                file.write("\n")      
                # file.write(" ".join(map(str, self.x_coords[i*10:(i+1)*10])) + "\n")  ## OLD APPROACH
            file.write("\n")
            # R2 Line 5 - Topography
            if len(self.topo) == 0:
                raise ValueError("topo not set. Use set_topography() to set the topography before writing to file.")
            if len(self.topo) != self.numnp_x:
                raise ValueError(f"Length of topo should be {self.numnp_x}. Use set_topography() to set the topography before writing to file.")
            for i in range(len(self.topo)//10+1):
                for j in range(0,10):
                    if i*10+j < len(self.topo):
                        file.write(f"{self.topo[i*10+j]:.3f}   ")
                file.write("\n")   
                # file.write(" ".join(map(str, self.topo[i*10:(i+1)*10])) + "\n") ## OLD APPROACH
            file.write("\n")
            # R2 Line 6 - Z Coordinates
            if len(self.z_coords) == 0:
                raise ValueError("z_coords not set. Use set_z_coords() to set the z coordinates before writing to file.")
            if len(self.z_coords) != self.numnp_z:
                raise ValueError(f"Length of z_coords should be {self.numnp_z}. Use set_z_coords() to set the z coordinates before writing to file.")
            for i in range(len(self.z_coords)//10+1):
                for j in range(0,10):
                    if i*10+j < len(self.z_coords):
                        file.write(f"{self.z_coords[i*10+j]:.3f}   ")
                file.write("\n")   
                # file.write(" ".join(map(str, self.z_coords[i*10:(i+1)*10])) + "\n") ## OLD APPROACH
            file.write("\n")
            # R2 Line 11 - Num Regions
            if self.num_regions is None:
                raise ValueError("num_regions not set. Use create_region() to create regions before writing to file.")
            file.write(f"{int(self.num_regions)} << num_regions\n")
            # R2 Line 12 - Region Information - file_name
            if self.num_regions == 0:
                if self.file_name is None:
                    raise ValueError("file_name should be set if num_regions is 0. Use import_res_file() to set the file name before writing to file.")
                file.write(f"{self.file_name} << file_name\n")
                file.write("\n")
            # R2 Line 13 - Region Information
            if self.num_regions > 0:
                for region in self.regions:
                    file.write(f"{int(region[0])} {int(region[1])} {region[2]}\n")
                file.write("\n")
            # R2 Line 25 - num_xz_poly
            file.write(f"{int(self.num_xz_poly)} << num_poly\n")
            # R2 Line 26 - num_xz
            if self.num_xz_poly > 0:
                for poly in self.xz_poly:
                    file.write(f"{poly[0]:.1f} {poly[1]:.1f}\n")
            file.write("\n")
            # R2 Line 27 - Number of Electrodes
            file.write(f"{int(self.num_electrodes)} << num_electrodes\n")
            # R2 Line 28 - List of electrodes
            for electrode in self.electrodes:
                file.write(f"{int(electrode[0])} {int(electrode[1])} {int(electrode[2])}\n")
            file.write("\n")
                