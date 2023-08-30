from area import *
from copy import deepcopy
import tcod
from settings import VERBOSITY_LEVEL
import helper

class Engine:
    def __init__(self, area: Area, player: Entity):
        self.entities = deepcopy(area.entity_list)
        self.area = area
        self.player = player
        self.text = ""

    def push(self, new_x, new_y, thing):
        direction = ""

        # Get direction of push
        if new_x > self.player.x:
            direction = "right"
        elif new_x < self.player.x:
            direction = "left"
        elif new_y > self.player.y:
            direction = "down"
        elif new_y < self.player.y:
            direction = "up"
        
        # Check if that pushable can be pushed
        if self.area.is_pushable(new_x, new_y, direction):
            push_dest_x = new_x
            push_dest_y = new_y

            # Then push it
            self.area.map_remove(new_x, new_y, thing)
            if direction == "right":
                push_dest_x += 1
            elif direction == "up":
                push_dest_y -= 1
            elif direction == "left":
                push_dest_x -= 1
            elif direction == "down":
                push_dest_y += 1
            self.area.map_add(push_dest_x, push_dest_y, thing)

    def move_player(self, new_x, new_y):
         # Check if dest in_bounds
        if not self.area.in_bounds(new_x, new_y):
            return False
        
        # Get pushable from location if present
        thing_list_at_dest = self.area.map[(new_x, new_y)]
        pushable = None
        for thing in thing_list_at_dest:
            if thing.pushable:
                pushable = thing

        # Check if there is pushable
        if pushable is not None:
            self.push(new_x, new_y, thing)

        # Check for walkability, then move
        # Note: move_entity calls is_walkable which also checks for inbounds, which is unnecessary for the player since it's already been checked during
        # push checks but required for other entity pathing currently        
        return self.move_entity(self.player, new_x, new_y)

    def move_entity(self, entity, new_x, new_y):
        if self.area.is_walkable(new_x, new_y):
            entity.x = new_x
            entity.y = new_y
            return True
        return False

    def on_input(self, event: tcod.event.Event) -> None:
        """Move the player on events and handle exiting. Movement is hard-coded."""
        if not isinstance(event, tcod.event.KeyDown):
            return False

        self.text = ""

        next_x, next_y = self.player.x, self.player.y
        if event.sym == tcod.event.KeySym.LEFT:
            next_x -= 1
        elif event.sym == tcod.event.KeySym.RIGHT:
            next_x += 1
        elif event.sym == tcod.event.KeySym.UP:
            next_y -= 1
        elif event.sym == tcod.event.KeySym.DOWN:
            next_y += 1
        elif event.sym == tcod.event.KeySym.a:
            next_x -= 1
        elif event.sym == tcod.event.KeySym.d:
            next_x += 1
        elif event.sym == tcod.event.KeySym.w:
            next_y -= 1
        elif event.sym == tcod.event.KeySym.s:
            next_y += 1
        elif event.sym == tcod.event.KeySym.SPACE:
            self.text = self.area.get_look_text(self.player.x, self.player.y)
        self.move_player(next_x, next_y)

    def handle_events(self, events: list, context: tcod.context.Context):
        event_handled = False
        for event in events:  # Event loop, get all inputs/events
            if VERBOSITY_LEVEL >= 2:
                print(event)
            self.on_input(event)  # Pass events to the state

            # End if player quit
            if isinstance(event, tcod.event.Quit):
                context.close()
                raise SystemExit()
            
            event_handled = True
        return event_handled

    def render(self, console: tcod.console.Console, context: tcod.context.Context) -> None:
        """Draw the player glyph."""
        console.clear()  # Clear the console before any drawing

        console_center_x = console.width // 2
        console_center_y = console.height // 2

        # Pull render distance from player light distance
        render_dist = self.player.light_range
        #render_dist = 20

        # Get farthest points as dicts key
        farthest_dict = {}
        for y_offset in range(-1*render_dist, render_dist+1):
            for x_offset in range(-1*render_dist, render_dist+1):

                x_area = self.player.x - x_offset
                y_area = self.player.y - y_offset

                # Get outermost ring of tiles and get list of rows of tiles to them
                # line function becomes innacurate above 13, so check all squares if further than that
                distance = helper.distance([self.player.x, self.player.y], [x_area, y_area])
                if distance <= render_dist:
                    #value is a list of points in a line leading to it (inclsive of it as well)
                    farthest_dict[(x_area,y_area)] = helper.line((self.player.x, self.player.y), (x_area,y_area))

        #Go through each dict value, append coord to set if transparent, append then stop if it is
        render_set = set()
        for key in farthest_dict:
            for coord in farthest_dict[key]:
                if not self.area.in_bounds(coord[0], coord[1]):
                    break
                if self.area.map[coord][-1].transparent:
                    render_set.add(coord)
                else:
                    render_set.add(coord)
                    break

        # Make sure entries are unique in list, then go through each coord and render map
        for coord in render_set:
            x_console = console_center_x + coord[0] - self.player.x
            y_console = console_center_y + coord[1] - self.player.y
            thing_list = self.area.map[coord]
            if len(thing_list) > 0:
                console.print(x_console, y_console, self.area.map[coord][-1].char)
            else:
                console.print(x_console, y_console, " ")
        
        # Render player
        console.print(console_center_x, console_center_y, self.player.char)

        # Render entities
        for entity in self.entities:
            x_offset_from_player = (entity.x - self.player.x)
            y_offset_from_player = (entity.y - self.player.y)
            if abs(x_offset_from_player) < render_dist and abs(y_offset_from_player) < render_dist:
                x_console = (console.width // 2) + x_offset
                y_console = (console.height // 2) + y_offset
                console.print(x_console, y_console, entity.char)
        
        # Split look text
        split_test_list = [""]
        split_test_list_ind = 0
        for word in self.text.split(" "):
            # If text is longer than screen width, split into lines
            if len(split_test_list[split_test_list_ind]) + len(word) + 1 < console.width:
                split_test_list[split_test_list_ind] += word + " "
            else:
                split_test_list_ind += 1
                split_test_list.append(word)

        # Render text
        for ind,line in enumerate(split_test_list):
            console.print(console_center_x+1-(len(line)//2), console.height-len(split_test_list)+ind, line)

        # Show in window/context
        context.present(console)  # Display the console on the window

    def entity_cycle(self):
        enemy_moved = False

       # Move enemies
        for entity in self.entities:
            # Only move if time move interval has passed
            if (time.time() - entity.last_move_time) < entity.move_interval:
                continue
            
            # WIP #
            if type(entity) == LibrarianEnemy:
                new_x, new_y = entity.next_move(self.player.x, self.player.y, self.area)
                self.move_entity(entity, new_x, new_y)
                entity.last_move_time = time.time()
                if distance((self.player.x, self.player.y), (entity.x, entity.y)) < self.player.light_range + 1:
                    enemy_moved = True
                continue
            # WIP #

            new_x, new_y = entity.next_move(self.player.x, self.player.y)
            if abs(entity.y - self.player.y) > abs(entity.x - self.player.x):
                if self.area.is_walkable(entity.x, new_y):
                    self.move_entity(entity, entity.x, new_y)
                elif self.area.is_walkable(new_x, entity.y):
                    self.move_entity(entity, new_x, entity.y)
            elif abs(entity.y - self.player.y) <= abs(entity.x - self.player.x):
                if self.area.is_walkable(new_x, entity.y):
                    self.move_entity(entity, new_x, entity.y)
                elif self.area.is_walkable(entity.x, new_y):
                    self.move_entity(entity, entity.x, new_y)
            entity.last_move_time = time.time()

            if distance((self.player.x, self.player.y), (entity.x, entity.y)) < self.player.light_range + 1:
                enemy_moved = True
            
        return enemy_moved

    def is_game_over(self, console: tcod.console.Console, context: tcod.context.Context):
        # Game Over if player and enemy share coordinates
        """
        if self.area.is_exit(self.player.x, self.player.y):
            console.clear()  # Clear the console before any drawing
            console.print(int(console.width//2-(44/2)),(console.height//2)-1,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            console.print(int(console.width//2-(44/2)),(console.height//2),  "!              !! You Win !!              !")
            console.print(int(console.width//2-(44/2)),(console.height//2)+1,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            context.present(console)  # Display the console on the window
            return True
        """
        # Win if player and Exit share coordinates
        if True in [issubclass(type(thing), Enemy) for thing in self.area.map[(self.player.x, self.player.y)]]:
            console.clear()  # Clear the console before any drawing
            console.print(int(console.width//2-(44/2)),(console.height//2)-1,"###########################################")
            console.print(int(console.width//2-(44/2)),(console.height//2),  "#              & You Died &               #")
            console.print(int(console.width//2-(44/2)),(console.height//2)+1,"###########################################")
            context.present(console)  # Display the console on the window
            return True
        
        return False
        
    def exit_check_and_load(self):
        # If on an exit
        if self.area.is_exit(self.player.x, self.player.y):
            exit = self.area.map[(self.player.x, self.player.y)][-1] # get the exit
            self.player.x = exit.dest_x # update player info
            self.player.y = exit.dest_y
            self.load_area(exit.area_path)
            return True
        return False

    def load_area(self, area_path):
        new_area = Area(0,0)
        new_area.load_from_file(area_path)
        self.area = new_area
        self.entities = new_area.entity_list
    
    #def 