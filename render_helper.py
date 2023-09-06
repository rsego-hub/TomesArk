import tcod
import helper

def make_inrange_coords_dict(x, y, render_dist):
    # Get renderable points as dicts key
    renderable_dict = {}
    for y_offset in range(-1*render_dist, render_dist+1):
        for x_offset in range(-1*render_dist, render_dist+1):

            x_area = x - x_offset
            y_area = y - y_offset

            # Get circle of tiles in render dist and get list of rows of tiles to them
            distance = helper.distance([x, y], [x_area, y_area])
            if distance <= render_dist:
                # value is a list of points in a line leading to it (inclsive of it as well)
                renderable_dict[(x_area,y_area)] = [tuple(coord) for coord in tcod.los.bresenham((x, y), (x_area,y_area)).tolist()]
    
    return renderable_dict

def get_visible_coords(renderable_dict, area):
    #Go through each dict value, append coord to set if transparent, append then stop if it iss
    render_set = set()
    for key in renderable_dict:
        for coord in renderable_dict[key]:
            if not area.in_bounds(coord[0], coord[1]):
                break
            if area.map[coord][-1].transparent:
                render_set.add(coord)
            else:
                render_set.add(coord)
                break
    
    return render_set

def show_map(render_set, x_player_offset, y_player_offset, area, console):
    console_center_x = console.width // 2
    console_center_y = console.height // 2

    # Go through each coord and render map
    for coord in render_set:
        x_console = console_center_x + coord[0] - x_player_offset
        y_console = console_center_y + coord[1] - y_player_offset
        thing_list = area.map[coord]
        if len(thing_list) > 0:
            console.print(x_console, y_console, area.map[coord][-1].char)
        else:
            console.print(x_console, y_console, " ")

def show_entities(entities, x_player_offset, y_player_offset, render_dist, console):
    # Render entities
    for entity in entities:
        x_offset_from_player = (entity.x - x_player_offset)
        y_offset_from_player = (entity.y - y_player_offset)
        if abs(x_offset_from_player) < render_dist and abs(y_offset_from_player) < render_dist:
            x_console = (console.width // 2) + x_offset_from_player
            y_console = (console.height // 2) + y_offset_from_player
            console.print(x_console, y_console, entity.char)

def show_text(text, console: tcod.console.Console):
    # Split look text
    split_test_list = [""]
    split_test_list_ind = 0
    for word in text.split(" "):
        # If text is longer than screen width, split into lines
        if len(split_test_list[split_test_list_ind]) + len(word) + 1 < console.width:
            split_test_list[split_test_list_ind] += word + " "
        else:
            split_test_list_ind += 1
            split_test_list.append(word)

    # Render text
    console_center_x = console.width // 2
    for ind,line in enumerate(split_test_list):
        console.print(console_center_x+1-(len(line)//2), console.height-len(split_test_list)+ind, line)
