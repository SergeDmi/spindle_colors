# spindle_colors
A utility to plot color-coded spindle extension.

python plot_spindle.py file_name [other file_names] [-colorbar]

Example :  
python plot_spindle.py example.txt -colorbar

plots the data in file_name into plot_name.pdf (+.eps)
into a beautiful schematic hightlighting the relevant information
i.e. the length, coded both in length and color

The data into file_name should be space-separated data :
Anterior pole-kinetochore distance | Posterior kinetochore-pole distance | Anterior 95% confidence interval | Posterior 95% confidence interval

Options : 
-colorbar : also plots a reference colorbar

This code relies on python PyX : https://pyx-project.org/
This codes requires python modules pyx & numpy (pip install pyx numpy)
pyx requires a latex distribution

Copyright Serge Dmitrieff, www.biophysics.dev
Please acknowledge/cite the relevant article if you use this code.