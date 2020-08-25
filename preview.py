# Sellers Industry 2020
# Aris Defense Project - Synthetic Image Generator

import os
import xml.etree.ElementTree as ET
import xmltodict, json
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

directory = os.path.join( os.getcwd(), "output" );
images_dir = os.path.join( directory, "images" );
annotations_dir = os.path.join( directory, "annotations" );
output_dir = os.path.join( directory, "preview" );
outlineColor = "red"

for annotation in os.listdir( annotations_dir ):
    file = json.loads( json.dumps( xmltodict.parse( ET.tostring( ET.parse( os.path.join( annotations_dir, annotation ) ).getroot() ) ) ) )[ "annotation" ];

    bbox = [];
    source_img = Image.open( os.path.join( images_dir, file[ "filename" ] ) ).convert("RGB");

    if isinstance( file[ "object" ], list ):
        bbox = file[ "object" ]
    else:
        bbox.append( file[ "object" ] )

    for bounding in range( 0, len( bbox ) ):
        draw = ImageDraw.Draw(source_img)
        draw.rectangle( ( int( bbox[ bounding ][ "bndbox" ][ "xmin" ] ), int( bbox[ bounding ][ "bndbox" ][ "ymin" ] ), int( bbox[ bounding ][ "bndbox" ][ "xmax" ] ), int( bbox[ bounding ][ "bndbox" ][ "ymax" ] ) ), outline=outlineColor, width=max( int( source_img.size[ 0 ] / 500 ), 1 ) )
        draw.text((int( bbox[ bounding ][ "bndbox" ][ "xmin" ] ), int( bbox[ bounding ][ "bndbox" ][ "ymin" ] )), bbox[ bounding ][ "name" ] )

    draw.text( ( 0, 0 ), "Aris Defense Project - Synthetic Image Generator (Sellers Industry 2020)" )
    source_img.save( os.path.join( output_dir, file[ "filename" ] ) );