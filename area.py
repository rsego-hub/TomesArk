import random
from helper import distance
from settings import VERBOSITY_LEVEL
from entity import *
import re
from thing import *

class Area:
    """
    """
    def __init__(self, size_x, size_y, look_text=""):
        self.size_x = size_x
        self.size_y = size_y
        self.map = {}
        self.entity_list = []
        for y in range(self.size_y):
            for x in range(self.size_x):
                self.map[(x,y)] = []
        self.look_text = look_text
    
    def map_add(self, x, y, thing):
        self.map[(x,y)].append(thing)
    
    def map_remove(self, x, y, thing):
        if thing in self.map[(x,y)]:
            self.map[(x,y)].remove(thing)
            return True
        if VERBOSITY_LEVEL >= 2:
            print(str(thing) + " to be removed from " + str(x) + "," + str(y) + "not found")
        return False

    def is_walkable(self, x, y):
        if not self.in_bounds(x,y):
            return False

        for thing in self.map[(x,y)]:
            if not thing.walkable:
                return False
            
        return True

    def is_pushable(self, box_x, box_y, direction):
        # Find which tile to push box to
        dest_x = box_x
        dest_y = box_y
        if direction == "right":
            dest_x += 1
        elif direction == "up":
            dest_y -= 1
        elif direction == "left":
            dest_x -= 1
        elif direction == "down":
            dest_y += 1
        else:
            return False

        # Check if destination of box is in bounds
        if not self.in_bounds(dest_x, dest_y):
            return False

        # Check if destination has other collidable thing, if so cant push
        thing_list = self.map[(dest_x, dest_y)]
        can_push_to_list = [thing.walkable and not thing.pushable for thing in thing_list]
        if False in can_push_to_list:
            return False
        
        return True
    
    def is_exit(self, x, y):
        return True in [isinstance(thing, Exit) for thing in self.map[(x, y)]]
    
    def get_triggerables(self, x, y):
        triggerable = []

        triggerable_objects = [Pressure_Plate]
        for area_thing in self.map[(x,y)]:
            for potential_thing in triggerable_objects:
                if isinstance(area_thing, potential_thing):
                    triggerable.append(area_thing)
        return triggerable

    def in_bounds(self, x, y):
        if x < 0 or x >= self.size_x or y < 0 or y >= self.size_y:
            return False
        return True

    def get_look_text(self, in_x, in_y):
        neighbor_list = [(in_x,in_y-1), (in_x+1,in_y), (in_x,in_y+1), (in_x-1,in_y)]
        for x,y in neighbor_list:
            if not self.in_bounds(x, y) or not (x, y) in self.map.keys():
                continue
            if self.map[(x,y)] == None or len(self.map[(x,y)]) == 0:
                continue
            if self.map[(x,y)][-1].text != "":
                return self.map[(x,y)][-1].text
        return self.look_text
    


    
    ##########################################################
    #                        Pathing                         #
    ##########################################################

    def best_path_between(self, start_coord, end_coord):
        # both destination and start must be walkable, if not return empty list
        if not (self.is_walkable(start_coord[0], start_coord[1]) and self.is_walkable(end_coord[0], end_coord[1])):
            return []

        # Make path score map
        path_map = [[-1]*self.size_x for i in range(self.size_y)]

        # Fill it in starting at start_coord until end_coord is reach
        step_queue = [start_coord]
        path_map[start_coord[1]][start_coord[0]] = 0

        # Stop when destination coordinate score changes or no more steps possible
        while path_map[end_coord[1]][end_coord[0]] == -1 and len(step_queue) > 0:

            # Grab coordinate and make new score its score + 1
            curr_coord = step_queue.pop(0)
            new_score = path_map[curr_coord[1]][curr_coord[0]] + 1
            
            # Get possible coords
            new_coord_1 = (curr_coord[0]-1, curr_coord[1])
            new_coord_2 = (curr_coord[0]+1, curr_coord[1])
            new_coord_3 = (curr_coord[0], curr_coord[1]-1)
            new_coord_4 = (curr_coord[0], curr_coord[1]+1)
            new_coord_list = [new_coord_1, new_coord_2, new_coord_3, new_coord_4]
            
            # Check if they're walkable, throw out if not
            # Check if the score map has a higher value, throw out if true
            coords_to_append = []
            for coord in new_coord_list:
                # don't evaluate on unwalkable tiles
                if not self.is_walkable(coord[0], coord[1]):
                    continue
                    #new_coord_list.remove(coord)
                # don't evaluate on same tile twice
                elif coord in step_queue:
                    continue
                    #new_coord_list.remove(coord)
                # don't evaluate on tiles with lower existing scores
                elif path_map[coord[1]][coord[0]] != -1 and path_map[coord[1]][coord[0]] < new_score:
                    continue
                    #new_coord_list.remove(coord)
                coords_to_append.append(coord)
            
            # Add to step list
            step_queue = step_queue + coords_to_append

            # Fill in path map for each
            for coord in coords_to_append:
                path_map[coord[1]][coord[0]] = new_score
        
        # If path not possible, return empy path list
        if path_map[end_coord[1]][end_coord[0]] == -1:
            return []

        #Starting at end, get score
        best_path = [end_coord]
        next_score = path_map[end_coord[1]][end_coord[0]] - 1
        while next_score != -1:
            curr_coord = best_path[-1]

            # find neighboring tiles
            next_coord_1 = (curr_coord[0]-1, curr_coord[1])
            next_coord_2 = (curr_coord[0]+1, curr_coord[1])
            next_coord_3 = (curr_coord[0], curr_coord[1]-1)
            next_coord_4 = (curr_coord[0], curr_coord[1]+1)
            next_coord_list = [next_coord_1, next_coord_2, next_coord_3, next_coord_4]

            # first neighboring coord with score 1 lower append to best path list
            for coord in next_coord_list:
                if coord[0] < 0 or coord[0] >= self.size_x or coord[1] < 0 or coord[1] >= self.size_y:
                    continue
                if path_map[coord[1]][coord[0]] == next_score:
                    best_path.append(coord)
                    break
            
            # update next_score
            next_score -= 1
        
        # Flip list
        best_path.reverse()
        return best_path



    ##########################################################
    #                  Generating Loading                  #
    ##########################################################

    def random_generate_simple(self, wallchance=0.25, free_corners=True):
        # Generate map
        for y in range(self.size_y):
            for x in range(self.size_x):
                if free_corners and (y < 3 and x < 3) or (y > self.size_y-4 and x > self.size_x-4):
                    self.map_add(x, y, Floor())
                    continue
                elif random.random() < wallchance:
                    self.map_add(x, y, Wall())
                else:
                    self.map_add(x, y, Floor())
        
        # If there is a wall in the bottom right, remove it
        if Wall in self.map[self.size_x-1, self.size_y-1]:
            self.map_remove(self.size_x-1, self.size_y-1, Wall())
        
        # Add the exit
        self.map_add(self.size_x-1, self.size_y-1, Exit(self, 0, 0))

        # Add entities
        num_amps = 3
        num_sneaks = 5
        for i in range(num_amps):
            new_enemy = Enemy(random.randint(self.size_x/5, self.size_x-1), random.randint(self.size_y/5, self.size_y-1), "&")
            self.entity_list.append(new_enemy)
        for i in range(num_sneaks):
            new_enemy = SneakyEnemy(random.randint(self.size_x/5, self.size_x-1), random.randint(self.size_y/5, self.size_y-1))
            self.entity_list.append(new_enemy)
        self.entity_list.append(LibrarianEnemy(self.size_x-1, self.size_y-1))


    def load_from_file(self, path):

        def parse_options(thing, options):
            for option in options:
                if option.find("char") != -1:
                    potential_char = option[5:]
                    if potential_char[-1] == "$":
                        thing.char = chr(tcod.tileset.CHARMAP_CP437[int(potential_char[:-1])])
                    else:
                        thing.char = potential_char
                elif option.find("text") != -1:
                    thing.text = option[5:].replace("\"", "")
                elif option.find("dest_x") != -1:
                    thing.dest_x = int(option[7:])
                elif option.find("dest_y") != -1:
                    thing.dest_y = int(option[7:])
                elif option.find("area_path") != -1:
                    thing.area_path = option[10:]

        # Read in text file
        with open(path) as f:
            lines = f.readlines()

        
        player = Player(0,0)# Create default Player
        char_lookup_dict = {}  # Create lookup dict

        # Extract descriptions
        descriptors = lines.pop(0)
        descriptors = re.split(r',\s*(?![^()]*\))', descriptors)

        # Extract look text
        self.look_text = lines.pop(0)

        # Go through each description
        for descript in descriptors:
            the_char = descript[0]
            the_thing = Thing()

            # Figure out which object
            if descript[2:].find("Wall") != -1: # If making wall
                the_thing = Wall()
            elif descript[2:].find("Floor") != -1: # Floor
                the_thing = Floor()
            elif descript[2:].find("Exit") != -1: # Exit
                the_thing = Exit("", 0, 0)
            elif descript[2:].find("Box") != -1: # Box
                the_thing = Box()
            elif descript[2:].find("Window") != -1: # Window
                the_thing = Window()
            elif descript[2:].find("Pressure_Plate") != -1: # Pressure plate
                the_thing = Pressure_Plate()

            # Check for options
            options = re.findall(r'\(.*?\)', descript)
            if len(options) > 0:
                options = options[0].replace("(", "").replace(")", "").split(",")
                parse_options(the_thing, options) # Parse options
        
            # Put thing in lookup table
            char_lookup_dict[the_char] = the_thing

        # Create map itself
        max_x = 0
        max_y = 0
        for y, line in enumerate(lines):
            max_y = max(max_y, y)
            for x, char in enumerate(line):
                if char == "\n": # Ignore newlines at the end of a line
                    continue

                max_x = max(max_x, x)
                if char == "@":
                    player.x = x
                    player.y = y
                    map_things = [Floor(".")]
                elif char in char_lookup_dict.keys():
                    if isinstance(char_lookup_dict[char], Box):
                        map_things = [char_lookup_dict["."], char_lookup_dict[char]]
                    else:
                        map_things = [char_lookup_dict[char]]
                else:
                    map_things = [Floor(" ")]

                self.map[(x,y)] = map_things
        
        self.size_x = max_x+1
        self.size_y = max_y+1

        return player
        