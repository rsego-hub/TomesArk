import tcod

############################
# Background and Map Objects

class Thing:
    """
    Objects are placed in a narea of the map
    character: what they will render as
    is_walkable: whether enemies and players can walk over it
    """
    def __init__(self):
        self.char = "o"
        self.walkable = True
        self.text = ""
        self.pushable = False
        self.transparent = True

class Wall(Thing):
    def __init__(self, char=chr(tcod.tileset.CHARMAP_CP437[219]), text=""):
        super(Wall, self).__init__()
        self.char = char
        self.walkable = False
        self.text = text
        self.transparent = False

class Floor(Thing):
    def __init__(self, char="."):
        super(Floor, self).__init__()
        self.char = char

class Pressure_Plate(Floor):
    def __init__(self, text=""):
        super(Pressure_Plate, self).__init__()
        self.text = text

class Exit(Thing):
    def __init__(self, area_path: str, dest_x: int, dest_y: int, char=""):
        super(Exit, self).__init__()
        self.char = "!"
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.area = area_path
        self.transparent = False

class Box(Thing):
    def __init__(self, char=chr(tcod.tileset.CHARMAP_CP437[254])):
        super(Box, self).__init__()
        self.char = char
        self.pushable = True
        self.walkable = False

class Window(Wall):
    def __init__(self, char=chr(tcod.tileset.CHARMAP_CP437[186]), text=""):
        super(Window, self).__init__(char, text)
        self.transparent = True