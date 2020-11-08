#
#   Copyright (C) 2020 Sellers Industry - All Rights Reserved
#   Unauthorized copying of this file, via any medium is strictly
#   prohibited. Proprietary and confidential.
#
#   author: Evan Sellers <sellersew@gmail.com>
#   date: Sat Nov 07 2020
#   file: crop.py
#   project: Sythetic Dataset Generator
#   purpose: Will take the output data from the generator and crop
#       an image around each object.
#
#

import os
import xml.etree.ElementTree as ET
import xmltodict, json
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

directory = os.path.join( os.getcwd(), "output" )
images_dir = os.path.join( directory, "images" )
annotations_dir = os.path.join( directory, "annotations" )
output_dir = os.path.join( directory, "crop" )

for annotation in os.listdir( annotations_dir ):
    file = json.loads( json.dumps( xmltodict.parse( ET.tostring( ET.parse( os.path.join( annotations_dir, annotation ) ).getroot() ) ) ) )[ "annotation" ]

    bbox = []
    source_img = Image.open( os.path.join( images_dir, file[ "filename" ] ) ).convert("RGB")

    if isinstance( file[ "object" ], list ):
        bbox = file[ "object" ]
    else:
        bbox.append( file[ "object" ] )

    crop_count = 0

    for bounding in range( 0, len( bbox ) ):
        img_crop = source_img.copy()
        img_crop = img_crop.crop( ( int( bbox[ bounding ][ "bndbox" ][ "xmin" ] ), int( bbox[ bounding ][ "bndbox" ][ "ymin" ] ), int( bbox[ bounding ][ "bndbox" ][ "xmax" ] ), int( bbox[ bounding ][ "bndbox" ][ "ymax" ] ) ) ) 
        img_crop.save( os.path.join( output_dir, os.path.splitext( file[ "filename" ] )[ 0 ] + "_c" + str( crop_count ) + os.path.splitext( file[ "filename" ] )[ 1 ] ) )
        crop_count += 1