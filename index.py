# Sellers Industry 2020
# Aris Defense Project - Sythetic Image Generator

import os
import PIL
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import xml.etree.ElementTree as gfg
import random
from rectangles import *
# import rectangles

bg_dir = os.path.join( os.getcwd(), "backgrounds" )
cl_dir = os.path.join( os.getcwd(), "objects" ) 

# config
config = {
    "file_prefix": "aris_img_",

    "scale_min": 0.20, # smallest percentage of obj
    "scale_max": 0.50, # largest percentage of obj

    "rotate_min": -45, # min rotation
    "rotate_max": 45, # max rotation
    
    "flip_hor": True, # if it will randomly flip horizontally
    "flip_ver": False, # if it will randomly flip veritcally

    "per_class_min": 1, # min number per class
    "per_class_max": 3, # max number per class
    
    "contrast_min": 80, # min contrast
    "contrast_max": 100, # max contrast ( 100 is orginal )

    "brightness_min": 80, # min brightness
    "brightness_max": 100, # max brightness ( 100 is orginal )
}


counter = 0;

for background_img in os.listdir( bg_dir ):
    if background_img.endswith( ".jpg" ) or background_img.endswith( ".png" ):

        try:

            x_placed = [];
            y_placed = [];

            background = Image.open( os.path.join( bg_dir, background_img ) );
            root = gfg.Element( "annotation" );

            folder = gfg.Element( "folder" ) 
            folder.text = "images"
            root.append( folder )

            filename = gfg.Element( "filename" ) 
            filename.text = config[ "file_prefix" ] + str( counter ) +  ".png"
            root.append( filename )

            path = gfg.Element( "path" ) 
            path.text = "images/" + config[ "file_prefix" ] + str( counter ) +  ".png"
            root.append( path )

            size = gfg.Element( "size" ) 
            root.append ( size )

            size_width = gfg.SubElement( size, "width" ) 
            size_width.text = str( background.size[ 0 ] )
            size_height = gfg.SubElement( size, "height" ) 
            size_height.text = str( background.size[ 1 ] )
            size_depth = gfg.SubElement( size, "depth" ) 
            size_depth.text = "3"

            # print( gfg.tostring( root ) )
            

            for class_dir in os.listdir( cl_dir ):

                if os.path.isdir( os.path.join( cl_dir, class_dir ) ):

                    for interation in range( 0, random.randint( config[ "per_class_min" ], config[ "per_class_max" ] ) ):

                        foreground = Image.open( os.path.join( cl_dir, class_dir, random.choice( os.listdir( os.path.join( cl_dir, class_dir )  ) ) ) )

                        if config[ "flip_hor" ] and random.randint( 0,1 ) == 1:
                            foreground = foreground.transpose(PIL.Image.FLIP_LEFT_RIGHT)

                        if config[ "flip_ver" ] and random.randint( 0,1 ) == 1:
                            foreground = foreground.transpose(PIL.Image.FLIP_TOP_BOTTOM)

                        width = random.randint( background.size[ 0 ] * config[ "scale_min" ], background.size[ 0 ] * config[ "scale_max" ] )
                        height = int( ( width / foreground.size[ 0 ] ) * foreground.size[ 1 ] )
                        x = random.randint( 0, background.size[ 0 ] - width )
                        y = random.randint( 0, background.size[ 1 ] - height )

                        stop = False;

                        for placed_pos in range( 0, len( x_placed ) ):
                            if Rect( x_placed[ placed_pos ][ 0 ], y_placed[ placed_pos ][ 0 ], x_placed[ placed_pos ][ 1 ], y_placed[ placed_pos ][ 1 ] ).overlaps_with( Rect( x, y, width, height ) ):
                                stop = True;

                        if stop:
                            continue
                        
                        x_placed.append( ( x, width ) )
                        y_placed.append( ( y, height ) )

                        foreground = foreground.rotate( random.randint( config[ "rotate_min" ], config[ "rotate_max" ] ), expand=True )
                        foreground = foreground.resize( ( width, height ) )

                        foreground = ImageEnhance.Contrast( foreground ).enhance( random.uniform( config[ "contrast_min" ], config[ "contrast_max" ] ) / 100 );
                        foreground = ImageEnhance.Brightness( foreground ).enhance( random.uniform( config[ "brightness_min" ], config[ "brightness_max" ] ) / 100 );

                        background.paste( foreground, (x, y), foreground )

                        object_ = gfg.Element( "object" ) 

                        object_name = gfg.SubElement( object_, "name" ) 
                        object_name.text = class_dir

                        object_bdnbox = gfg.SubElement( object_, "bdnbox" ) 

                        object_bdnbox_xmin = gfg.SubElement( object_bdnbox, "xmin" ) 
                        object_bdnbox_xmin.text = str( x )

                        object_bdnbox_ymin = gfg.SubElement( object_bdnbox, "ymin" ) 
                        object_bdnbox_ymin.text = str( y )

                        object_bdnbox_xmax = gfg.SubElement( object_bdnbox, "xmax" ) 
                        object_bdnbox_xmax.text = str( x + width )

                        object_bdnbox_ymax = gfg.SubElement( object_bdnbox, "ymax" ) 
                        object_bdnbox_ymax.text = str( y + height )

                        root.append ( object_ );


            background.save( os.path.join( os.getcwd(), "output/images/" + config[ "file_prefix" ] + str( counter ) +  ".png" ) );

            with open( os.path.join( os.getcwd(), "output/annotations/" + config[ "file_prefix" ] + str( counter ) +  ".xml" ), "wb") as f: 
                f.write( gfg.tostring( root ) )

            counter += 1
                
        
        except Exception as e:
            print( e )


    else:
        continue