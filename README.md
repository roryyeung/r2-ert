# r2-ert
A python wrapper around the R2 series of codes for the modelling of Electrical Resistivity Tomography in Geophysics.

Note - you will need to install the R2 package directly.

Structure - each survey type has a survey class and a generator function. This generator function creates an instance of the class with the required features. The class stores all state.