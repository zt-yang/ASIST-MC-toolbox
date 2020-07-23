#!/usr/bin/env python3

# Dependencies
# pip3 install --user nbtlib tqdm


import map_generator as mg
import argparse
import sys
from pprint import pprint
import json
import os
from os.path import join

sys.path.append('MCWorldlib.egg')
import mcworldlib as mc

testbed = os.getenv('asist_testbed')
mg.set_ipy_display(False)
if testbed is None:
    print('Environment value `asist_testbed` is required. Got:', testbed)
    sys.exit(1)

maps_base = 'Local/CLEAN_MAPS/'

# Falcon data comes from multiple region files.
mc_worlds = {
    'Falcon':  # reference to world in maps_base = 'Local/CLEAN_MAPS/' and also the output folder container artifacts
        {
            'Falcon5':  # Intermediate folder where we generate artifacts
                {'region': (-5, 0),
                 'ranges': (-2112, -2049, 128, 207, 60, 62)},
            'Falcon4': {'region': (-4, 0),
                        'ranges': (-2048, -2017, 128, 207, 60, 62)}
        },
    'Sparky': {'Sparky': {'region': (-5, 0),
                          'ranges': (-2176, -2097, 144, 207, 52, 54)}}}


def make_world_path(world_name):
    return join(testbed, maps_base, world_name)


def ensure_dir_exists(path):
    print('Current Working Dir', os.getcwd())
    print('Ensuring Dir exists', path)
    if os.path.exists(path):
        return True
    try:
        os.makedirs(path)
    except Exception as e:
        print('Exception creating:', path)
        pprint(e)
        return False


def make_world(from_world, region, ranges, to_world=None):
    if to_world is None:
        to_world = from_world
    print(from_world, region, ranges, to_world)
    ensure_dir_exists(to_world + '/floors')
    jsn_file = from_world + '.json'
    world = mc.load(make_world_path(from_world))
    all_blocks, important_blocks = mg.generate_maps(world, region, ranges, to_world)
    mg.generate_json(all_blocks, ranges, to_world, jsn_file)


def make_falcon_world():
    make_world('Falcon', 'Falcon4')
    make_world('Falcon', 'Falcon5')


def make_world_wrapper(world_name):
    if world_name not in mc_worlds:
        print('World not found in config:', world_name)
        sys.exit(1)
    worlds = mc_worlds[world_name]
    ensure_dir_exists(world_name)
    if len(worlds) == 1:
        make_world(world_name, mc_worlds[world_name][world_name]['region'], mc_worlds[world_name][world_name]['ranges'])
    elif len(worlds) == 2:
        for to_world, data in worlds.items():
            print(to_world, data)
            make_world(world_name, data['region'], data['ranges'], to_world)
        worlds_idx = list(worlds.keys())
        print(worlds_idx)
        mg.merge_folders(worlds_idx[0], worlds_idx[1], world_name, world_name + '.json')
    else:
        print('TODO: merge worlds with data spread over regions:', len(worlds))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to create minecraft world in json format')
    parser.add_argument('mc_world')
    args = parser.parse_args()
    world_name = args.mc_world
    print('Creating JSON file for world {}'.format(world_name))
    if world_name not in mc_worlds:
        print('World not found in internal config. Options are:')
        pprint(mc_worlds)
        sys.exit(1)
    make_world_wrapper(world_name)
