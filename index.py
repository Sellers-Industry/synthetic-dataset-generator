# Sellers Industry 2020
# Aris Defense Project - Synthetic Image Generator

import os
import math 
import PIL
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import xml.etree.ElementTree as gfg
import xmltodict, json
import random

save_dir = os.path.join( os.getcwd(), "output" )
img_path = "images"
xml_path = "annotations"
bg_dir   = os.path.join( os.getcwd(), "backgrounds" )
cl_dir   = os.path.join( os.getcwd(), "objects" ) 
counter  = 0;

# config
config = {
    "file_prefix": "aris_img_",

    "scale_min": 0.20, # smallest percentage of obj
    "scale_max": 0.50, # largest percentage of obj

    "rotate_min": -45, # min rotation
    "rotate_max": 45, # max rotation
    
    "flip_hor": True, # if it will randomly flip horizontally
    "flip_ver": True, # if it will randomly flip veritcally

    "per_class_min": 5, # min number per class
    "per_class_max": 100, # max number per class (so high to deal with overlap errors)
    
    "contrast_min": 80, # min contrast
    "contrast_max": 100, # max contrast ( 100 is orginal )

    "brightness_min": 80, # min brightness
    "brightness_max": 100, # max brightness ( 100 is orginal )
}


def rotatePoint( origin, point, angle ):
    ox, oy = origin
    px, py = point
    
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def imageManipulation( image, bounding ):
    x1, y1, x2, y2 = bounding
    w, h = image.size[ 0 ], image.size[ 1 ]

    # Flip Horizontally
    if config[ "flip_hor" ] and random.randint( 0,1 ) == 1:
        image = image.transpose( PIL.Image.FLIP_LEFT_RIGHT )
        _x1 = x1
        x1 = w - x2
        x2 = w - _x1

    # Flip Vertically
    if config[ "flip_ver" ] and random.randint( 0,1 ) == 1:
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        _y1 = y1
        y1 = h - y2
        y2 = h - _y1

    # Rotation Matrixs
    if config[ "rotate_min" ] != 0:
        rotate = random.randint( config[ "rotate_min" ], config[ "rotate_max" ] );
        image  = image.rotate( rotate );
        c_TL = rotatePoint( ( w / 2, h / 2 ), ( x1, y1 ), math.radians( -rotate ) )
        c_TR = rotatePoint( ( w / 2, h / 2 ), ( x2, y1 ), math.radians( -rotate ) )
        c_BL = rotatePoint( ( w / 2, h / 2 ), ( x1, y2 ), math.radians( -rotate ) )
        c_BR = rotatePoint( ( w / 2, h / 2 ), ( x2, y2 ), math.radians( -rotate ) )
        x1 = min( c_TL[ 0 ], c_BL[ 0 ] )
        y1 = min( c_TL[ 1 ], c_TR[ 1 ] )
        x2 = max( c_TR[ 0 ], c_BR[ 0 ] )
        y2 = max( c_BL[ 1 ], c_BR[ 1 ] )

    # Contrast Changes
    if config[ "contrast_min" ] != 100:
        image = ImageEnhance.Contrast( image ).enhance( random.uniform( config[ "contrast_min" ], config[ "contrast_max" ] ) / 100 );

    # Brightness Changes
    if config[ "brightness_min" ] != 100:
        image = ImageEnhance.Brightness( image ).enhance( random.uniform( config[ "brightness_min" ], config[ "brightness_max" ] ) / 100 );

    return image, ( x1, y1, x2, y2 )


def axis_overlap( s1, e1, s2, e2 ):
    return e1 >= s2 and e2 >= s1


# _bbox => all older bbox
# bbox => new bbox to compare
def overlap( _bbox, bbox ):
    for i in range( 0, len( _bbox ) ):
        if axis_overlap( _bbox[ i ][ 0 ], _bbox[ i ][ 2 ], bbox[ 0 ], bbox[ 2 ] ) and axis_overlap( _bbox[ i ][ 1 ], _bbox[ i ][ 3 ], bbox[ 1 ], bbox[ 3 ] ):
            return True
    return False;


def xml_basic( file_name, image_size ):
    root = gfg.Element( "annotation" );

    folder = gfg.Element( "folder" ) 
    folder.text = "images"
    root.append( folder )

    filename = gfg.Element( "filename" ) 
    filename.text = file_name
    root.append( filename )

    path = gfg.Element( "path" ) 
    path.text = str( img_path + "/" + file_name );
    root.append( path )

    size = gfg.Element( "size" ) 
    root.append ( size )

    size_width = gfg.SubElement( size, "width" ) 
    size_width.text = str( image_size[ 0 ] )
    size_height = gfg.SubElement( size, "height" ) 
    size_height.text = str( image_size[ 1 ] )
    size_depth = gfg.SubElement( size, "depth" ) 
    size_depth.text = "3"

    return root


def xml_append( root, obj_class, bbox ):
    _object = gfg.Element( "object" )

    object_name = gfg.SubElement( _object, "name" ) 
    object_name.text = obj_class

    object_bndbox = gfg.SubElement( _object, "bndbox" ) 

    object_bndbox_xmin = gfg.SubElement( object_bndbox, "xmin" ) 
    object_bndbox_xmin.text = str( int( bbox[ 0 ] ) )

    object_bndbox_ymin = gfg.SubElement( object_bndbox, "ymin" ) 
    object_bndbox_ymin.text = str( int( bbox[ 1 ] ) )

    object_bndbox_xmax = gfg.SubElement( object_bndbox, "xmax" ) 
    object_bndbox_xmax.text = str( int( bbox[ 2 ] ) )

    object_bndbox_ymax = gfg.SubElement( object_bndbox, "ymax" ) 
    object_bndbox_ymax.text = str( int( bbox[ 3 ] ) )

    root.append( _object );

    return root



for background_img in os.listdir( bg_dir ):
    if background_img.endswith( ".jpg" ) or background_img.endswith( ".png" ):

        background = Image.open( os.path.join( bg_dir, background_img ) );
        name       = config[ "file_prefix" ] + str( counter );
        img_name   = name + ".jpg"
        xml_name   = name + ".xml"
        boundings  = []; # each bounding added

        xml_annotation = xml_basic( img_name, ( background.size[ 0 ], background.size[ 1 ] ) )

        for obj_class in os.listdir( cl_dir ):
            if os.path.isdir( os.path.join( cl_dir, obj_class ) ):
                for interation in range( 0, random.randint( config[ "per_class_min" ], config[ "per_class_max" ] ) ):

                    image      = random.choice( os.listdir( os.path.join( cl_dir, obj_class, "images" ) ) )
                    annotation = os.path.splitext( image )[ 0 ] + ".xml"
                    foreground = Image.open( os.path.join( cl_dir, obj_class, "images", image ) )

                    # If has annotation
                    if os.path.exists( os.path.join( cl_dir, obj_class, "annotations" ) ) and os.path.exists( os.path.join( cl_dir, obj_class, "annotations", annotation ) ):
                        file = json.loads( json.dumps( xmltodict.parse( gfg.tostring( gfg.parse( os.path.join( cl_dir, obj_class, "annotations", annotation ) ).getroot() ) ) ) )[ "annotation" ]
                    
                        # Set Original Bounding Boxes
                        bbox = (
                            int( file[ "object" ][ "bndbox" ][ "xmin" ] ),
                            int( file[ "object" ][ "bndbox" ][ "ymin" ] ),
                            int( file[ "object" ][ "bndbox" ][ "xmax" ] ),
                            int( file[ "object" ][ "bndbox" ][ "ymax" ] )
                        )

                    else:
                        bbox = (
                            0,
                            0,
                            foreground.size[ 0 ],
                            foreground.size[ 1 ]
                        )

                    foreground, bbox = imageManipulation( foreground, bbox )

                    # Set Position and size of object
                    _width  = random.randint( int( background.size[ 0 ] * config[ "scale_min" ] ), int( background.size[ 0 ] * config[ "scale_max" ] ) )
                    _height = int( ( _width / foreground.size[ 0 ] ) * foreground.size[ 1 ] )
                    _x      = random.randint( 0, background.size[ 0 ] - _width )
                    _y      = random.randint( 0, background.size[ 1 ] - _height )
                    _bbox   = (
                        _x + bbox[ 0 ] * ( _width / foreground.size[ 0 ] ),
                        _y + bbox[ 1 ] * ( _height / foreground.size[ 1 ] ),
                        _x + bbox[ 2 ] * ( _width / foreground.size[ 0 ] ),
                        _y + bbox[ 3 ] * ( _height / foreground.size[ 1 ] ),
                    )

                    if not overlap( boundings, ( _x, _y, _x + _width, _y + _height ) ):
                        foreground     = foreground.resize( ( _width, _height ) )
                        xml_annotation = xml_append( xml_annotation, obj_class, _bbox )

                        background.paste( foreground, ( _x, _y ), foreground )
                        boundings.append( ( _x, _y, _x + _width, _y + _height ) )

        counter += 1
        background.save( os.path.join( save_dir, img_path, img_name ) );

        with open( os.path.join( save_dir, xml_path, xml_name ), "wb") as f: 
            f.write( gfg.tostring( xml_annotation ) )
