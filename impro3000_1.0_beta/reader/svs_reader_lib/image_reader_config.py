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
    primary_staining = "actin"

	 # command line option: -sec // type str
    secondary_staining = None

	 # command line option: -tert // type str
    tertiary_staining = "Haematoxilin"

	 # TILE SETTINGS
    overlap = 		100 
    tile_size = 	3072 # tiles are stored as squares (apart from edges)

	 # PARALELLIZATION
    cores = 	5	# number of cores you want to use // 14 cores @6144 for Hodgkin // 12 cores @3072
	 #RAM = 		16 	# [GB] -> used to dynamically determine the heap size for the deployed JVMs

	 #Patrick
    import_path = "C:/Users/patri/OneDrive/Dokumente/Promotion/Tools/gcDetect/aktinImages/normal/H25556-16_I1_Aktin+PD1.svs"
    output_path = "C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0_beta/workspace3000/actin_paper/"
    pipeline_path = "C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0_beta/pipelines/actin_paper_pipeline.py"
    impro_path = "C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0_beta/"
    postprocessing_path = "C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0_beta/pipelines/postpipe_dummy.py"
    diagnosis = None