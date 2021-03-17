import sys
import traceback

sys.path.append('MCWorldlib.egg')
import mcworldlib as mc
import math
import json
import os
import pandas as pd
import numpy as np
from IPython.display import Image as iImage
from PIL import Image
from os.path import isfile, join

default_output_folder = 'outputs'
default_json_file = 'blocks_in_building.json'
ipy_display = True


def set_ipy_display(val):
    global ipy_display
    ipy_display = val


def create_collage(width, height, cols, rows, name, listofimages):
    """
        take in a list of images and make a collage with the specified width and height
    """

    thumbnail_width = width//cols
    thumbnail_height = height//rows
    size = thumbnail_width, thumbnail_height
    new_im = Image.new('RGB', (width, height))
    ims = []
    for p in listofimages:
        im = Image.open(p)
        im.thumbnail(size)
        ims.append(im)
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            if len(listofimages) == 16 * 16:
                new_im.paste(ims[i], (width-x-int(width/cols), y))
            else:
                new_im.paste(ims[i], (x, y))
            i += 1
            y += thumbnail_height
        x += thumbnail_width
        y = 0

    if len(listofimages) == 16 * 16:
        new_im = new_im.rotate(90)

    new_im.save(name)

# first version of the Singleplayer world
# all_blocks = generate_maps(region, (23, 26, 9, 11, 12, 14, 1))
def generate_maps(world, region, ranges, output_folder=default_output_folder, gen_images=True):

    x_low, x_high, z_low, z_high, y_low, y_high = ranges
    x_ind_low = int(x_low / 16 - region[0] * 32)  # int((2560 + x_low)/16)
    x_ind_high = int(x_high / 16 - region[0] * 32)
    z_ind_low = int(z_low / 16 - region[1] * 32)
    z_ind_high = int(z_high / 16 - region[1] * 32)
    y_ind = math.floor(y_low / 16)
    y_ind_low = int(y_low - y_ind * 16)
    y_ind_high = int(y_high - y_ind * 16)
    # print(x_ind_low, x_ind_high, z_ind_low, z_ind_high, y_ind_low, y_ind_high)
    region_blocks = world.regions[region[0], region[1]]
    # mc.pretty(region_blocks)
    # ---------------------------------------------------------
    # get the mapping from block id to block type
    block_dict = {}
    with open(join('resources','block_id.json')) as json_file:
        entries = json.load(json_file)
        for entry in entries:
            if entry['type'] not in block_dict:
                block_dict[entry['type']] = entry['text_type']

    with open(join('resources','block_to_texture.json')) as json_file:
        images = json.load(json_file)

    # ---------------------------------------------------------
    ## read all blocks in region and store in all_blocks, where 'x' 'y' 'z' specifies patch index
    ## e.g., all_blocks[(-2176, 52, 144)] = {'block_type': 'air', 'y': 4, 'z': 0, 'x': 0}
    all_blocks = {}
    cannot_find_blocks = []
    collage_layers = {}

    for x_ind in range(x_ind_low, x_ind_high+1):
        for z_ind in range(z_ind_low, z_ind_high+1):

            # only look at the floor level
            # print(x_ind, z_ind)
            # if x_ind == 20 and z_ind == 5:
            #     print('y_ind', y_ind)

            blocks = list()
            if y_ind <= (len(region_blocks[x_ind, z_ind]['']['Level']['Sections']) - 1):
                blocks = region_blocks[x_ind, z_ind]['']['Level']['Sections'][y_ind]['Blocks']
                blocks = list(blocks)

            # offsets in the game world
            x_0 = 16* (x_ind + region[0]*32)
            y_0 = 16*y_ind
            z_0 = 16* (z_ind + region[1]*32) #+ 15

            # store all blocks in an array to be printed on a 16 by 16 image
            image_layer = []
            for i in range(len(blocks)):

                # to be stored about each block
                stats = {}

                # 'block_type'
                num = int(blocks[i])
                if num < 0:
                    num = 256+num
                stats['block_type'] = block_dict[num]

                # coordinates 'x' 'y' 'z'
                stats['y'] = math.floor(i/16/16)
                i = i % (16*16)
                stats['z'] = math.floor(i/16)
                stats['x'] = i % 16

                # collect blocks and print images
                if stats['y'] >= y_ind_low and stats['y'] <= y_ind_high:
                    all_blocks[(stats['x'] + x_0, stats['y'] + y_0, stats['z'] + z_0)] = stats

                    # generate image pathes of the region
                    if stats['block_type'] in images.keys():
                        texture = join('resources','myblocks',images[stats['block_type']])
                    else:
                        texture = join('resources','myblocks','nether_brick.png')
                        cannot_find_blocks.append(stats['block_type'])

                    image_layer.append(texture)
                    if gen_images:
                        if stats['x'] == 15 and stats['z'] == 15:
                            floor_level = stats['y'] - y_ind_low
                            name = '[' + str(x_ind) + ',' + str(z_ind)
                            name += ',' + str(floor_level) + ']'
                            name = join(output_folder, 'floors', name + "_floor.jpg")
                            create_collage(16 * 16, 16 * 16, 16, 16, name, image_layer)
                            if floor_level not in collage_layers:
                                collage_layers[floor_level] = []
                            collage_layers[floor_level].append(name)
                            image_layer = []

    for block in set(cannot_find_blocks):
        print('cannot find image in resources/myblocks/',block)

    # ---------------------------------------------------------
    ## We merge multiple floor plans to prioritize showing the important objects.
    ## This way we will get one floor plan as the base for visualizing human trajectories
    important_blocks = {}

    if gen_images:
    ## create the dict for one block each (x,z) location
        for key in all_blocks.keys():
            x,y,z = key

            block_type = all_blocks[key]['block_type']
            WRITTEN = False
            if y == y_low + 2 and (block_type == 'wall_sign'):
                important_blocks[x, z] = all_blocks[(x, y_low + 2, z)]
                WRITTEN = True
            elif y == y_low + 1 and (block_type == 'lever' or block_type == 'wall_sign'):
                important_blocks[x, z] = all_blocks[(x, y_low + 1, z)]
                WRITTEN = True
            elif y == y_low:
                if block_type == 'stained_hardened_clay' and all_blocks[(x, y_low + 2, z)]['block_type'] == 'air':
                    important_blocks[x, z] = all_blocks[(x, y_low + 2, z)]
                    WRITTEN = True
                elif block_type == 'stained_hardened_clay' and all_blocks[(x, y_low + 1, z)]['block_type'] == 'air':
                    important_blocks[x, z] = all_blocks[(x, y_low + 1, z)]
                    WRITTEN = True
                else:
                    important_blocks[x, z] = all_blocks[(x, y_low, z)]
                    WRITTEN = True

            if WRITTEN:
                if all_blocks[(x, y_low + 1, z)]['block_type'] == 'air':
                    important_blocks[x, z]['open_top'] = True
                else:
                    important_blocks[x, z]['open_top'] = False

    ## generate collage
    if gen_images:
        for key in important_blocks.keys():
            x, z = key
            stats = important_blocks[key]
            image_lookup = stats['block_type']
            # print('image lookup', image_lookup)
            if image_lookup in images:
                image_layer.append(join('resources', 'myblocks', images[stats['block_type']]))
            else:
                print('not found:', image_lookup, 'in', json_file.name)

            if stats['x'] == 15 and stats['z'] == 15:
                floor_level = 9
                name = '[' + str(round(x / 16 - region[0] * 32)) + ',' + str(round(z / 16 - region[1] * 32))
                name += ',' + str(floor_level) + ']'
                name = join(output_folder, 'floors', name + "_floor.jpg")
                try:
                    create_collage(16 * 16, 16 * 16, 16, 16, name, image_layer)
                except Exception as e:
                    # print(e)
                    print(traceback.print_exc())

                if floor_level not in collage_layers:
                    collage_layers[floor_level] = []
                collage_layers[floor_level].append(name)
                image_layer = []

    # ---------------------------------------------------------
    ## make collage out of smaller patches
    x_len = x_ind_high - x_ind_low + 1
    z_len = z_ind_high - z_ind_low + 1
    if gen_images:
        for key in collage_layers.keys():
            name = join(output_folder, str(key) + '_map.png')
            try:
                create_collage(16 * 16 * x_len, 16 * 16 * z_len, x_len, z_len, name, collage_layers[key])
                for image in collage_layers[key]:
                    os.remove(image)
            except Exception as e:
                print(traceback.print_exc())

            if ipy_display is True and key == 9:  display(iImage(filename=name))

    return all_blocks, important_blocks

def generate_json(all_blocks, ranges, output_folder=default_output_folder, jsn_file=default_json_file):

    blocks_in_building = {}

    ## includes the types of all blocks
    blocks_to_json = {}
    for key,value in all_blocks.items():
        key = str(key).replace('(','').replace(')','').replace(' ','')
        blocks_to_json[key] = value['block_type']

    blocks_in_building['blocks'] = blocks_to_json

    ## includes the range limites of the region
    region = {}
    region['x_low'] = ranges[0]
    region['x_high'] = ranges[1]
    region['z_low'] = ranges[2]
    region['z_high'] = ranges[3]
    region['y_low'] = ranges[4]
    region['y_high'] = ranges[5]
    blocks_in_building['region'] = region
    print('Current Working Dir', os.getcwd())
    print('Writing json file:', join(output_folder, jsn_file))
    print()
    with open(join(output_folder, jsn_file), 'w') as outfile:
        json.dump(blocks_in_building, outfile)

def generate_csv(important_blocks, indices, output_folder=default_output_folder):

    x_low, x_high, z_low, z_high, y_low, y_high = indices

    count = 0
    objects = []
    objects2grids = {
        'wool':'V',
        'prismarine':'V',
        'gold_block':'VV',
        'wooden_door':'D',
        'dark_oak_door':'D',
        'gravel':'G',
        'fire':'F',
        'lever':'',
        'wall_sign':'',
        'standing_sign':''
    #     'air': '',
    #     'end_portal_frame':'',
    #     'cauldron':'',
    #     'dispenser':'',
    #     '':'',
    #     'stained_hardened_clay': 'W',
    #     'anvil': 'W',
    #     'hopper': 'W',
    #     'cobblestone_wall':'W',
    #     'monster_egg':'W',
    #     'cobblestone':'W',
    #     'quartz_stairs':'W',
    #     'clay':'W',
    #     '':'W',
    }
    data = pd.DataFrame('', index=np.arange(z_high - z_low + 1), columns=np.arange(x_high - x_low + 1))
    for key in important_blocks.keys():
        count += 1
        block = important_blocks[key]
        x = key[0] - x_low
        z = key[1] - z_low
        block_type = block['block_type']
        if block_type in objects2grids.keys():
            csv_block = objects2grids[block_type]
        else:
            if block['open_top']:
                csv_block = ''
            else:
                csv_block = 'W'
        data[x][z] = csv_block
    data.to_csv(join(output_folder,'maze.csv'), index=False, header=False)


def merge_folders(folder1, folder2, output_folder=default_output_folder, jsn_file=default_json_file):
    print('Merging folder', folder1, folder2, jsn_file)
    def get_concat_h(im1, im2):
        dst = Image.new('RGB', (im1.width + im2.width, im1.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        return dst

    def get_concat_v(im1, im2):
        dst = Image.new('RGB', (im1.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
        return dst

    # ----------------------------
    # json
    # ----------------------------

    with open(join(folder1, jsn_file)) as json_file: json1 = json.load(json_file)
    with open(join(folder2, jsn_file)) as json_file: json2 = json.load(json_file)
    # json2 = json.loads(join(folder2, jsn_file))
    json3 = {}
    json3['blocks'] = dict(json1['blocks'])
    json3['blocks'].update(json2['blocks'])
    print('number of blocks',len(json1['blocks'].keys()),len(json2['blocks'].keys()), len(json3['blocks'].keys()))

    X_CHANGED = False
    Z_CHANGED = False

    json3['region'] = {}
    for key in ['x_low','x_high','z_low','z_high','y_low','y_high']:
        if 'low' in key:
            json3['region'][key] = min(json1['region'][key], json2['region'][key])
        else:
            json3['region'][key] = max(json1['region'][key], json2['region'][key])

        if json1['region'][key] != json2['region'][key]:
            if 'x' in key: X_CHANGED = True
            if 'z' in key: Z_CHANGED = True

    print('merge_folder writing jsn file')
    print('Current Working Dir', os.getcwd())
    print(join(output_folder, jsn_file))
    with open(join(output_folder, jsn_file), 'w') as outfile:
        json.dump(json3, outfile)

    # ----------------------------
    # png
    # ----------------------------

    for level in [0,1,2,9]:
        map_img = str(level) + '_map.png'
        try:
            im1 = Image.open(join(folder1, map_img))
            im2 = Image.open(join(folder2, map_img))
            if X_CHANGED: get_concat_h(im1, im2).save(join(output_folder, map_img))
            if Z_CHANGED: get_concat_v(im1, im2).save(join(output_folder, map_img))
        except FileNotFoundError as e:
            print('File not found:', e)


def show_blocks_in_building(output_folder=default_output_folder, jsn_file=default_json_file):
    objects2grids = {
        'wool':'v',
        'prismarine':'v',
        'gold_block':'vv',
        'wooden_door':'w',
        'gravel':'w',
        'fire':'',
        'air':''
    }

    with open(join(output_folder, jsn_file)) as json_file:
        data = json.load(json_file)
        blocks = data['blocks']

        print(data['region'].values())
        x_low, x_high, z_low, z_high, y_low, y_high = data['region'].values()

        ## for Singleplayer
        # x_high = -2142

        world = []
        for z in range(z_low, z_high):
            row = []
            for x in range(x_low, x_high):

                ## we visualize the floor that's one level above the ground
                key = str((x,y_low+1,z)).replace('(','').replace(' ','').replace(')','')
                type = blocks[key]
                if type not in objects2grids.keys():
                    type = 'w'
                else:
                    type = objects2grids[type]
                row.append(type)
            world.append(row)

        df = pd.DataFrame(world, index = range(z_low, z_high), columns = range(x_low, x_high))

        return df
