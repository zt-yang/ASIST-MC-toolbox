# ASIST-MC-toolbox
Tools for extracting block types from Minecraft world folder and for generating videos of player trajectories

## Required Python Libraries

This tool depends on the following python libraries:

```python
Pillow, imageio ## for generating map, visualizing trajectory
json, csv ## for writing and reading JDON and CSV formet
cv2 ## for generating videos
pprint ## for pretty print dictionary structure in debugging
numpy ## for converting angle to radian
tqdm ## for displaying a progress bar when running loops
```

---

## Tool A - Extract map as PNG, CSV, and JSON

We have a tool for extracting the 2D floor plan of structures built in Minecraft and for visualizing human trajectory data on the map as a mp4 file.

This folder includes the following components:

* `run_map_generator.ipynb` is the place to run the codes
* `map_generator.py` defines the functions used by `run_map_generator.ipynb`
* `outputs/` stores the outputmaps and traces
* `resources/` stores the icons and distionaries used to generate the maps
* `Singleplayer/` is the the Minecraft world folder to be extracted from
* `MCWorldLib.egg` is a package we use for extracting region files ([source in Github](https://github.com/MestreLion/mcworldlib))

The input to map_generator.py include two parts:

* Minecraft world folder that's located in your Malmo folder `MalmoPlatform/Minecraft/run/saves/` (using Malmo) or `/Users/USER_NAME/Library/Application\ Support/minecraft/saves/` (using licenced Minecraft Java Version).
```
world = mc.load('Singleplayer')
region = world.regions[-5,0]
```

Inside the `Singleplayer/region` folder, there are `.mca` files. Each `.mca` file specifies 32 x 32 chunks. Each chunk specifies 16 x 16 x 16 blocks. In the above example, we located an SAR building in `r.-5.0.mca`, which we found using online tool [Chunk viewer](https://pessimistress.github.io/minecraft/) (as shown in the image below). On the interface, adjust the bar on the left to the highest, click the minimap on the bottom right side, and navigate to the light-colored areas representing artificial structures. After we found the .mca file, we need to further narrow down the blocks.

![](resources/imgs/tools-chunk.png)

* the second part of the input is the ranges of x,y,z that specify the region of interests. This can be found by locating the building in the .mca file, then record down the coordinates of the top right and bottom left corner block on the ground (as the yellow/blue block shown in the image above). Then record down the lowest and highest level as y values.

```
x_low = -2176  # x of the bottom left block
x_high = -2097  # x of the top right block
z_low = 144     # z of the top right block
z_high = 207  # z of the bottom left block
y_low = 52
y_high = 54
```

The outputs include three parts:

* images of the 2D floor plans on different levels of the region of interest at `world-builder/outputs/*_map.png` where * = 0,1,2,9
![](resources/imgs/tools-map.png)

* a json file specifying the block type of all blocks within the region of interest at `world-builder/outputs/blocks_in_building.json`
```
# key = "x,y,z", value = block_type
"-2152,52,160": "air",
"-2151,52,160": "stained_hardened_clay",
"-2150,52,160": "anvil", ...
```
* a csv file that represent the region of interest that can be used as input to our gridworld framework at `world-builder/outputs/darpa_maze.csv`
![](resources/imgs/tools-csv.png)

## Tool B - Visualize human trajectories as MP4

Given DARPA testbed messages in the following format:

```
raw-data 1.58507E+12 {
  app-id:"TestbedBusInterface",
  mission-id:"6483fec4-153c-4994-8f42-a2e9b00d4db3",
  routing-key:"testbed-message",
  testbed-message:{
    msg:{
      trial_id:"6483fec4-153c-4994-8f42-a2e9b00d4db3",
      sub_type:"state", source:"simulator",
      timestamp:"2020-03-24T16:07:18.140779Z"
    },
    data:{
      name:"Player396", entity_type:"human", life:20.0,
      x:-2193.5, y:23.0, z:194.6328125,
      pitch:0.0, yaw:0.0,
      motion_x:0.0, motion_y:0.0, motion_z:0.11038550616085588
    }
  },
  timestamp:1585066038141
}
```

The codes visualize the location of the player on the map and infer the object that the player is interacting with.

![](resources/imgs/tools-continuous.png)

The codes further discretize the continuous position changes to generate a step by step trajectory that can be used as input to the inverse planning framework.

![](resources/imgs/tools-discretized.png)