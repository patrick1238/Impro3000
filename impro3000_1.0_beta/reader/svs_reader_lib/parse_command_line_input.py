import argparse as ap
from svs_reader_lib.image_reader_config import ImageReaderConfig as config


def parse_command_line():
	parser = ap.ArgumentParser()


	## MANDATORY ARGUMENTS:
	# example: # parser.add_argument("impro_path", metavar="impro_path", type=str, help="enter the path to your impro_dir, excluding ./ImproXY/")


	## OPTIONAL ARGUMNETS (default value is set, if not called):
	
	# specify the layer to be read:
	parser.add_argument("-l", "--layer", help="enter number of desired layer here", type=int, default=0)
	
	# set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big images with this option
	parser.add_argument("-gfi", "--get_full_image", help="set if no tiling is required", default=False, action='store_true')

	# set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big images with this option
	parser.add_argument("-pp", "--post_processing_active", help="set if NO postprocessing script shall be deployed", default=True, action='store_false')

	# set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big images with this option
	parser.add_argument("-noroi", "--region_of_interrest_active", help="set this option to ommit the region of interest computation", default=True, action='store_false')

	# set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big images with this option
	parser.add_argument("-nodb", "--no_debugging", help="annoyed by the debugging output from javabridge? so am I.", default=True, action='store_false')

	# path to image file, that will be read:
	parser.add_argument("-i", "--import_path", help="enter path to the image, including the image name (e.g. ../image.svs)", type=str, default=config.import_path)
	
	# path to the pipeline script:
	parser.add_argument("-pipe", "--pipeline_path", help="enter the path to your pipeline script, including the pipeline name", type=str, default=config.pipeline_path)

	# path to the pipeline script:
	parser.add_argument("-post_pipe", "--postprocessing_pipeline_path", help="enter the path to your postprocessing pipeline script, including the pipeline name", type=str, default=config.postprocessing_path)

	# path to the Impro Dir, including the Impro Dir name. (working title is Impro3000 -> bound to change some time after implementing this)
	parser.add_argument("-impro", "--impro_path", help="enter the path to your impro directory INCLUDING THE NAME OF THE IMPRO FOLDER", type=str, default=config.impro_path)

	# path to a directory to save image tiles to. this is required for one of the Imaging Library modules, not the SVS-Reader istself. 
	parser.add_argument("-o", "--output_path", help="enter the desired output path, not including the image name", type=str, default=config.output_path)

	# option to set primary staining
	parser.add_argument("-prim", "--primary_staining", help="enter the primary staining of the image", type=str, default=config.primary_staining)

	# option to set primary staining
	parser.add_argument("-sec", "--secondary_staining", help="enter the secondary staining of the image", type=str, default=config.secondary_staining)

	# option to set primary staining
	parser.add_argument("-tert", "--tertiary_staining", help="enter the tertiary staining of the image", type=str, default=config.tertiary_staining)

	parser.add_argument("-diag", "--diagnosis", help="enter the diagnosis of the case", type=str, default=config.diagnosis)

	# list with all parsed cammand line inputs:
	args = parser.parse_args()
	return args