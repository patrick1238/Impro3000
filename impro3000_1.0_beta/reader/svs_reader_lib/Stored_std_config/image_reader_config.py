 # config class 

class ImageReaderConfig():


	# enter here all paths you wish to have set as default paths. 
	# if one or more paths are not specified, they have to be passed via the command line
	# command line option can be found in the comments

	# command line option: -i
	import_path = ""
	
	# coammand line option: -o
	output_path = None # if not specified, output will be in the workspace3000
	
	# command line option: -pipe
	pipeline_path = ""

	# command line option: -post_pipe
	postprocessing_path = ""
	
	# command line option: -lib
	library_path = ""
	
	# command line option: -impro
	impro_path = ""

	# command line option: -prim // type str
	primary_staining = "CD30"

	# command line option: -sec // type str
	secondary_staining = None

	# command line option: -tert // type str
	tertiary_staining = None

	# TILE SETTINGS
	overlap = 		100 
	tile_size = 	3072 # tiles are stored as squares (apart from edges)

	# PARALELLIZATION
	cores = 	5	# number of cores you want to use // 14 cores @6144 for Hodgkin // 12 cores @3072
	#RAM = 		16 	# [GB] -> used to dynamically determine the heap size for the deployed JVMs





###################################################################################################################
####################### custom content, not neccessary for successful SVS-Reader deployment #######################


	## specific workstation paths for testing and easy deployment:


	# FRIDAY
#	import_path  = "C:/Users/FRIDAY/Documents/test_data/K1147-04_CD30.svs"
#	output_path  = "C:/Users/FRIDAY/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta/workspace3000/"
#	pipeline_path = "C:/Users/FRIDAY/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta/pipelines/pipeline_HGL.py"
#	pipeline_path = "C:/Users/FRIDAY/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta/pipelines/preprocessing_alisa.py"
#	impro_path = "C:/Users/FRIDAY/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta"
#	postprocessing_path = "C:/Users/FRIDAY/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta/pipelines/post_pipe_HGL.py"




	# D.Va
	#import_path  = "C:/Users/D.Va/Desktop/test_data/K1147-04_CD30.svs"
#	import_path  = "C:/Users/D.Va/Desktop/test_data/probably_gcb_images/"
	#output_path  = "C:/Users/D.Va/Documents/Sourceforge/Impro/code/branches/impro3000_1.0_beta/workspace3000/"
#	pipeline_path = "C:/Users/D.Va/Documents/Sourceforge/Impro/code/branches/impro3000_1.0_beta/pipelines/pipeline_HGL.py"
	#pipeline_path = "C:/Users/D.Va/Documents/Sourceforge/Impro/code/branches/impro3000_1.0_beta/pipelines/pipeline_testing_HGL.py"
	#impro_path = "C:/Users/D.Va/Documents/Sourceforge/Impro/code/branches/impro3000_1.0_beta"
	#postprocessing_path = "C:/Users/D.Va/Documents/Sourceforge/Impro/code/branches/impro3000_1.0_beta/pipelines/post_pipe_HGL.py"

	# Artemis
#	import_path  = "C:/Users/Artemis/Documents/Sourceforge/test_data/K1147-04_CD30.svs"
#	output_path  = "C:/Users/Artemis/Documents/Sourceforge/image_folder/"
#	pipeline_path = "C:/Users/Artemis/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta/pipelines/pipeline_HGL.py"
#	impro_path = "C:/Users/Artemis/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta"
#	postprocessing_path = "C:/Users/Artemis/Documents/Sourceforge/Impro/branches/impro3000_1.0_beta/pipelines/post_pipe_HGL.py"


	# Hodgkin Bad Homburg
#	import_path  = "D:/Users/Hodgkin/Documents/Sourceforge/test_data/K1147-04_CD30.svs"
#	output_path  = "D:/Users/Hodgkin/Documents/Sourceforge/image_folder/"
#	pipeline_path = "D:/Users/Hodgkin/Documents/Sourceforge/Impro3000/branches/impro3000_1.0_beta/pipelines/pipeline_HGO.py"
#	impro_path = "D:/Users/Hodgkin/Documents/Sourceforge/Impro3000/branches/impro3000_1.0_beta"

	# Hodgkin Bockenheim
	# HENRY:
#	import_path = "E:/Users/Hodgkin/svs_images/probably_gcb_images/20874-10_2_CD30.svs" # 700mb
#	import_path = "E:/Users/Hodgkin/svs_images/probably_gcb_images/12727-05_CD30.svs"
#	import_path = "E:/Users/Hodgkin/Desktop/AlisaImages/noGC/K1330-15_HE.svs"
	import_path = "E:/Users/Hodgkin/svs_images/testing_svs_reader/K1147-04_CD30.svs"
#	import_path = "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/test_files/test_cd/20874-10_CD30_0_1_26.tif"
#	output_path = "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/workspace3000/"
#	output_path = "E:/Users/Hodgkin/Desktop/AlisaImages/noGC/tiles/"
	#pipeline_path = "E:/Users/Hodgkin/Desktop/develop/impro3000/branches/impro3000_1.0_beta/pipelines/pipeline_save_as_tiff.py"
#	pipeline_path = "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/pipelines/preprocessing_alisa"
	impro_path = "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/"
#	postprocessing_path = "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/pipelines/post_pipe_alisa.py"
	postprocessing_path = "E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/pipelines/post_pipe_communities_HGL.py"

	#TOBI:
	#import_path = "E:/Users/Hodgkin/Desktop/test_img/"
	output_path = "E:/Users/Hodgkin/Desktop/develop/impro3000/branches/impro3000_1.0_beta/workspace3000/"
	pipeline_path = "E:/Users/Hodgkin/Desktop/develop/impro3000/branches/impro3000_1.0_beta/pipelines/prepipe_tobi.py"
	impro_path = "E:/Users/Hodgkin/Desktop/develop/impro3000/branches/impro3000_1.0_beta/"
	postprocessing_path = "E:/Users/Hodgkin/Desktop/develop/impro3000/branches/impro3000_1.0_beta/pipelines/post_pipe_tobi.py"



###################################################################################################################
##################################################### BENCHMARKS ##################################################

