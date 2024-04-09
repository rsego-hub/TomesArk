import tcod.console
import tcod.event
from area import *
from settings import VERBOSITY_LEVEL
from engine import Engine

def main() -> None:
    # Pull tileset and declare console parameters
    tileset = tcod.tileset.load_tilesheet(
        "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    console_char_width = 48
    console_char_height = 27
    console = tcod.console.Console(console_char_width+1, console_char_height+1)

    # Create player, and area to walk around in
    area = Area(0,0)
    player = area.load_from_file("maps/entrance.txt")
    player.light_range = 10
    engine = Engine(area, player)

    # Open display
    context = tcod.context.new(width=console_char_width*32, height=console_char_height*32, console=console, tileset=tileset) 
    redraw = True # Redraw only when necessary

    # Loop until game over status reached
    while not engine.is_game_over(console, context):  # Main loop

        # Redraw only if necessary
        if redraw:
            engine.render(console, context)  # Render and show game
            redraw = False

        # Check inputs and do player move logic, then check enemies and move them
        redraw = redraw or engine.handle_events(tcod.event.get(), context)
        redraw = redraw or engine.entity_cycle()

        # Handle triggers
        redraw = redraw or engine.handle_triggers(console, context)
        
        #animation.play_animation("./animation/fall/", console, context)

    # Wait for player to quit
    engine.handle_events(tcod.event.wait(), context)
    context.close()

if __name__ == "__main__":
    main()