import tcod
import os
import re
import time
# Head floating on this, gotta brainstorm
# Animation takes control from user, no new events should be queued after this happens, and ideally 
# it happens before the next tcod event can be processed, lends itself to an sdl event but I don't
# know how that works, and it seems weird that an in-game event would interfere with the control
# scheme

# Player or timer or enemy does something, triggers animation
# animation proceeds at set timing, each trigger changes map, makes redraw, and waits some set time
# before map is changed again
# once animation complete, actual playable map is returned and it allows normal event processing to 
# proceed

def play_animation(animation_folder, console: tcod.console.Console, context: tcod.context.Context) -> None:
    console.clear()

    animation_files = [os.path.join(animation_folder, file) for file in os.listdir(animation_folder)]

    # Find the rule file
    rule_file = ""
    for file in animation_files:
        if file.find("rule") != -1:
            rule_file = file

    # Sort animation frames
    sorted_animation_files = animation_files.copy()
    sorted_animation_files.remove(rule_file)
    sorted_animation_files.sort()
    frames = [Frame(file, rule_file) for file in sorted_animation_files]

    # Center of console for display centering
    center_x = console.width // 2
    center_y = console.height // 2

    # Run animation
    for frame in frames:
        # Go through each coord and render frame
        for x in range(frame.size_x):
            for y in range(frame.size_y):
                centered_print_x = center_x + (x - (frame.size_x // 2))
                centered_print_y = center_y + (y - (frame.size_y // 2))
                console.print(centered_print_x , centered_print_y, frame.map[(x, y)])

        # Display and wait according to frame time length
        context.present(console)  # Display the console on the window
        time.sleep(frame.frame_time)
    
    # Clear event queue
    print(tcod.event.get())

class Frame():
    
    def __init__(self, frame_file, rule_file):
        self.char_lookup_dict = self.get_char_lookup_dict(rule_file)
        self.frame_time = self.get_frame_time(frame_file, rule_file)
        self.map, self.size_x, self.size_y = self.load_frame_map(frame_file)


    def get_char_lookup_dict(self, rule_path):

        def get_display_char(option):
            char = ''

            # Check if character is a representation of a different symbol
            if option.find("char") != -1:
                char = option[5:]

                # Check for dollar sign at end, indicating special character
                if char[-1] == "$":
                    char = chr(tcod.tileset.CHARMAP_CP437[int(char[:-1])])
                
            return char
        
        # Read in text file
        with open(rule_path) as f:
            rule_text = f.readlines()

        # Get descriptors of animation file symbols
        descriptors = rule_text.pop(0)
        descriptors = re.split(r',\s*(?![^()]*\))', descriptors)

        # Process rule file
        char_lookup_dict = {}
        for descript in descriptors:
            representation_char = descript[0]

            # Grab all options, should only be one, remove parenthesis
            options = re.findall(r'\(.*?\)', descript)
            option = options[0].replace("(", "").replace(")", "")
        
            # Put thing in lookup table
            char_lookup_dict[representation_char] = get_display_char(option)
            if char_lookup_dict[representation_char] == '':
                char_lookup_dict[representation_char] = representation_char
        
        return char_lookup_dict
    

    def get_frame_time(self, frame_file, rule_file):

        with open(rule_file) as f:
            rule_text = f.readlines()
        
        # Look for line with frame name
        for line in rule_text:
            if line.find(frame_file) != -1:
                return float(line.split(",")[1])

        # Default frame time is 1/10 of a second
        return 0.1
    

    def load_frame_map(self, frame_file):
        with open(frame_file) as f:
            lines = f.readlines()

        # Create map itself
        max_x = 0
        max_y = 0
        frame_map = {}
        for y, line in enumerate(lines):
            max_y = max(max_y, y)
            for x, char in enumerate(line):
                if char == "\n": # Ignore newlines at the end of a line
                    continue

                max_x = max(max_x, x)

                # Get display char
                if char in self.char_lookup_dict.keys():
                    map_char = self.char_lookup_dict[char]
                else:
                    map_char = "?"

                frame_map[(x,y)] = map_char
        
        size_x = max_x+1
        size_y = max_y+1
        return frame_map, size_x, size_y