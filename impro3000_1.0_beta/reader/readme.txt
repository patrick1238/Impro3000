##############################################

		HOW TO DEPLOY svs_reader.py 

##############################################

TLDR VERSION:


cd E:\Users\Hodgkin\Desktop\develop\branches\impro3000_1.0_beta\reader

python .\svs_reader.py -i "E:/Users/Hodgkin/svs_images/probably_gcb_images/14098-10_2_CD30.svs" -o "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/workspace3000/" -pipe "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/pipelines/prepipe_save_as_tiff.py" -impro "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/" -post_pipe "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/pipelines/postpipe_dummy.py" -l 3 -noroi -gfi




COPY & PASTE Windows POWERSHELL:

copy from powershell: mark text with mouse, hit enter (... the obvious way to go)
paste into powershell: right klick




A LITTLE BIT MORE BACKGROUND:

1. change into the reader directory. for the workstation in bockenheim this would be:
	
	> cd E:\Users\Hodgkin\Desktop\develop\branches\impro3000_1.0_beta\reader


2. start the svs_reader.py with python and all mandatory flags (see 3.):

	> python .\svs_reader.py -[all mandatory flags]



3. in the current state of work it is advised to use the image_reader_config.py in the reader_lib 
   to set all the following flags that are mandatory (layer is set to 0 by default, see 5.):

	a) import_path (where is your desired svs?)
	b) output_path (where to write the results?)
	c) pipeline_path (path to your preprocessing pipeline)
	d) impro_path (path to the impro3000_1.0_beta directory)
	c) postprocessing_path (path to your postprocessing pipeline)

   please mind: absolute path (e.g. "E:/Users/Hodgkin/ ...") without backslashes required, 
   realative ones do not work.

   all of the above parameters can also be typed in during the terminal call, 
   omitting the necessity to edit the config (still: inly absolute paths work). The tags are:

	a) -i ["path"]
	b) -o ["path"]
	c) -pipe ["path"]
	d) -impro ["path"]
	e) -post_pipe ["path"]


4. parameters that can only be set in the config: 

	a) "paralleization": the svs_reader's apralleization works by deploying a submodule severeal times simultaniously, 
	   with sublistst of the image tiles. the number of running sunbumodules at the same time is set via:

	   	cores = [int]

	b) size of the tiles, this should be an int of the size 2^n:

		tile_size = [int]


5. some more flags that might be usefull:

	-l [int]		-> select the layer that shall be worked on. default value is 0.
	-noroi			-> does not calculate the region of interest (saves quite some time if you want to test sth small)
	-nodb			-> supresses the exhaustive debugging messages from javabridge. may cause errors, seems to depend 
					   on the javabridge and/or OS version. just try it on your PC. not working on the bockenheim 
					   workstation.
	-gfi			-> forces the svs_reader to skip tiling. the svs_image will be read as one numpy array. the resulting 
					   numpy array will not be coreccted into square format. works on every layer, limiting factor is 
					   obviously RAM.

