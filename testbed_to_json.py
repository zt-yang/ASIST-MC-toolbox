#!/usr/bin/env python3

import map_generator as mg
import argparse
import sys
from pprint import pprint
import json

sys.path.append('MCWorldlib.egg')
import mcworldlib as mc
from os.path import join

# Dependencies
# pip3 install --user nbtlib tqdm

testbed = '/Users/prakash/projects/asist-rita/testbed-v5-gitlab/testbed'
maps_base = 'Local/CLEAN_MAPS/'
mc_worlds = {'Falcon': {'region': (-5, 0),
                        'ranges': (-2112, -2049, 128, 207, 60, 62)}
             }


def make_world_path(world_name):
    return join(testbed, maps_base, world_name)


def to_json(world_name):
    ## load the world folder, which takes a while but only need to do it once
    region = mc_worlds[world_name]['region']
    ranges = mc_worlds[world_name]['ranges'] #{world_name: }
    world = mc.load(make_world_path(world_name))
    all_blocks, important_blocks = mg.generate_maps(world, region, ranges)
    blocks = mg.make_building_blocks(all_blocks, ranges)
    with open(world_name + '.json', 'w') as outfile:
        json.dump(blocks, outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plant Sim (Python)')
    parser.add_argument('mc_world')
    args = parser.parse_args()
    world_name = args.mc_world
    print('Creating JSON file for world {}'.format(world_name))
    if world_name not in mc_worlds:
        print('World not found in internal config. Options are:')
        pprint(mc_worlds)
        sys.exit(1)
    to_json(world_name)
