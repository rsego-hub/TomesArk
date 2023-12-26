from area import *
from copy import deepcopy
import tcod
from settings import VERBOSITY_LEVEL
import helper
import render_helper
import sound



class Engine:
    def __init__(self, area: Area, player: Entity):
        self.entities = deepcopy(area.entity_list)
        self.area = area
        self.player = player
        self.text = ""

        # Statistics
        self.player_step_cnt = 0

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

        # Sound effect
        self.player_step_cnt = sound.step(self.player_step_cnt)

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

        #self.text = ""

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

        # Pull render distance from player light distance
        render_dist = self.player.light_range

        # Find the sections of the map that should be displayed
        renderable_dict = render_helper.make_inrange_coords_dict(self.player.x, self.player.y, render_dist)
        render_set = render_helper.get_visible_coords(renderable_dict, self.area)

        # Render map
        render_helper.show_map(render_set, self.player.x, self.player.y, self.area, console)
        
        # Render player, entities, and text
        console.print(console.width // 2, console.height // 2, self.player.char)
        render_helper.show_entities(self.entities, self.player.x, self.player.y, render_dist, console)
        render_helper.show_text(self.text, console)

        # Show in window/context
        context.present(console)  # Display the console on the window

    def handle_triggers(self):
        triggerables = self.area.get_triggerables(self.player.x, self.player.y)
        if len(triggerables) == 0:
            return False
        
        for triggerable in triggerables:
            if isinstance(triggerable, Pressure_Plate):
                self.text = triggerable.text

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
