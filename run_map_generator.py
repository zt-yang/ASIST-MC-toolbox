## pip3 install nbtlib
import map_generator as mg
import sys
sys.path.append('MCWorldlib.egg')
import mcworldlib as mc
from os.path import join

world_name = 'Saturn_Training_Feb4' ## 'Falcon v1.02' ## name of the Minecraft world folder in input/worlds/
region = (-5,0) ## name of the .mca file where you can find the building  22, 25 or 60, 63

building_ranges = { ## x_low, x_high, z_low, z_high, y_low, y_high
    'Singleplayer': (-2192, -2129, 144, 191, 28, 30),
    'Sparky v3.03': (-2176, -2097, 144, 207, 52, 54),
#     'Saturn_Feb4': (-2240, -2065, -96, -1, 60, 64), # r.-5.-1.mca
    'Saturn_Training_Feb4': (-2240, -2065, 0, 143, 60, 63), # r.-5.0.mca
#     'Falcon v1.02': (-2112, -2049, 128, 207, 60, 62)   # r.-5.0.mca
#     'Falcon v1.02': (-2048, -2017, 128, 207, 60, 62)   # r.-4.0.mca
}
ranges = building_ranges[world_name]


## load the world folder, which takes a while but only need to do it once
world = mc.load(join('inputs', 'worlds', world_name))

all_blocks, important_blocks = mg.generate_maps(world, region, ranges)
mg.generate_json(all_blocks, ranges)
mg.generate_csv(important_blocks, ranges)
