from math import gamma
from tkinter.constants import BOTH, BOTTOM, NUMERIC, TOP, TRUE
from typing import Text
from a3_support import *
import tkinter as tk
import random
from tkinter import Button, Frame, Tk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk

class Entity:
    '''Entity is an abstract class that is used to represent any element that can appear on the game’s grid.'''
    def display(self) -> str:
        '''Return the character used to represent this entity in a text-based grid.'''
        raise NotImplementedError()

    def __repr__(self) -> str:
        '''Return a representation of this entity.'''
        return f'{self.__class__.__name__}()'


class Player(Entity):
    '''A subclass of Entity representing a Player within the game.'''
    def display(self) -> str:
        '''Return the character representing a player: ’P’'''
        return PLAYER


class Destroyable(Entity):
    '''A subclass of Entity representing a Destroyable within the game.'''
    def display(self) -> str:
        '''Return the character representing a destroyable: ’D’'''
        return DESTROYABLE


class Collectable(Entity):
    '''A subclass of Entity representing a Collectable within the game.'''
    def display(self) -> str:
        '''Return the character representing a collectable: ’C’'''
        return COLLECTABLE


class Blocker(Entity):
    '''A subclass of Entity representing a Blocker within the game.'''
    def display(self) -> str:
        '''Return the character representing a blocker: ’B’'''
        return BLOCKER


class Bomb(Entity):
    '''A subclass of Entity representing a Bomb within the game.'''
    def display(self) -> str:
        '''Return the character representing a bomb: ’O’'''
        return BOMB


class Grid:
    '''The Grid class is used to represent the 2D grid of entities.'''
    def __init__(self, size: int) -> None:
        '''
        A grid is constructed with a size representing the number of rows 
        (equal to the number of columns) in the grid.

        Parameters:
            size: The size of the grid.
        '''
        self._size = size
        self._board_dict: Dict[Position, Entity] = {}
        self._board_dict[Position(3,0)] = Player()

    def get_size(self) -> int:
        '''Return the size of the grid.'''
        return self._size

    def add_entity(self, position: Position, entity: Entity) -> None:
        '''
        Add a given entity into the grid at a specified position.
        
        Parameters:
            position: The specific position of the grid.
            entity: The entity at this position.
        '''
        # If an entity already exists at the specified position.
        if self.in_bounds(position):
            self._board_dict[position] = entity
        else:
            pass 

    def get_entities(self) -> Dict[Position, Entity]:
        '''Return the dictionary containing grid entities.'''
        # Add entity into entities dictionary.
        result ={}
        for position, entity in self._board_dict.items():
            result[position] = entity
        return result

    def get_entity(self, position: Position) -> Optional[Entity]:
        '''
        Return a entity from the grid at a specific position or None if the position does not have a mapped entity.
        
        Parameters:
            position: The specific position of the grid.            
        '''
        return self._board_dict[position]

    def remove_entity(self, position: Position) -> None:
        '''
        Remove an entity from the grid at a specified position.
        
        Parameters:
            position: The specific position of the grid.  
        '''
        del self._board_dict[position]

    def serialise(self) -> Dict[Tuple[int, int], str]:
        '''
        Convert dictionary of Position and Entities into a simplified, 
        serialised dictionary mapping tuples to characters.
        '''
        # Change the form of entities dictionary.
        result = {}
        for position, entity in self._board_dict.items():
            result[(position.get_x(), position.get_y())] = entity.display()
        return result

    def in_bounds(self, position: Position) -> bool:
        '''
        Return a boolean based on whether the position is valid in terms of the dimensions of the grid.

        Parameters:
            position: The specific position of the grid.          
        '''
        if position.get_x() >= 0 and position.get_x() < GRID_SIZE and position.get_y() >= 1 and position.get_y() < GRID_SIZE:
            return True
        else:
            return False

    def __repr__(self) -> str:
        '''Return a representation of this Grid.'''
        return f'{self.__class__.__name__}({self._size})'


class Game:
    '''The Game handles the logic for controlling the actions of the entities within the grid.'''
    def __init__(self, size: int) -> None:
        '''
        A game is constructed with a size representing the dimensions of the playing grid.
        
        Parameters:
            size: A size representing the dimensions of the playing grid.
        '''
        self._grid: Grid = Grid(size)
        self._collected = 0
        self._destroyed = 0
        self._total_shots = 0
    
    def get_grid(self) -> Grid:
        '''Return the instance of the grid held by the game.'''
        return self._grid

    def get_player_position(self) -> Position:
        '''Return the position of the player in the grid (top row, centre column).'''
        return Position(3,0)

    def get_num_collected(self) -> int:
        '''Return the total of Collectables acquired.'''
        return self._collected

    def get_num_destroyed(self) -> int:
        '''Return the total of Destroyables removed with a shot.'''
        return self._destroyed

    def get_total_shots(self) -> int:
        '''Return the total of shots taken.'''
        return self._total_shots

    def rotate_grid(self, direction: str) -> None:
        '''
        Rotate the positions of the entities within the grid depending on the direction they are being rotated.
        
        Parameters:
            direction: The rotation direction of the entities' positions.
        '''
        new_grid = Grid(self._grid.get_size())

        # Traverse each entity and change their position.
        if direction == LEFT:
            rotation = ROTATIONS[0]
        else:
            rotation = ROTATIONS[1]
        for position, entity in self._grid.get_entities().items():
            if position == self.get_player_position():
                new_position = position
            else:
                new_position = position.add(Position(rotation[0], rotation[1]))
            if new_position.get_x() < 0:
                new_position = Position(GRID_SIZE - 1, new_position.get_y())
            elif new_position.get_x() >= GRID_SIZE:
                new_position = Position(0, new_position.get_y())
            else:
                pass
            new_grid.add_entity(new_position, entity)
        self._grid = new_grid
        
    def _create_entity(self, display: str) -> Entity:
        '''
        Uses a display character to create an Entity.

        Parameters:
            display: The entities' display.
        '''
        if display == PLAYER:
            return Player()
        elif display == COLLECTABLE:
            return Collectable()
        elif display == DESTROYABLE:
            return Destroyable()        
        elif display == BLOCKER:
            return Blocker()
        else:
            raise NotImplementedError()

    def generate_entities(self) -> None:
        """
        Method given to the students to generate a random amount of entities to
        add into the game after each step.
        """
        # Generate amount
        entity_count = random.randint(0, self.get_grid().get_size() - 3)
        entities = random.choices(ENTITY_TYPES, k=entity_count)

        # Blocker in a 1 in 4 chance
        blocker = random.randint(1, 4) % 4 == 0

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # bomb = False
        # if not blocker:
        #     bomb = random.randint(1, 4) % 4 == 0

        total_count = entity_count
        if blocker:
            total_count += 1
            entities.append(BLOCKER)

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # if bomb:
        #     total_count += 1
        #     entities.append(BOMB)

        entity_index = random.sample(range(self.get_grid().get_size()),
                                     total_count)
                                     
        # Add entities into grid
        for pos, entity in zip(entity_index, entities):
            position = Position(pos, self.get_grid().get_size() - 1)
            new_entity = self._create_entity(entity)
            self.get_grid().add_entity(position, new_entity)
          
    def step(self) -> None:
        '''This method moves all entities on the board by an offset of (0, -1).'''
        new_grid = Grid(self._grid.get_size())

        # Keep the position (3, 0) unchanged, change the position of other entities.
        for position, entity in self._grid.get_entities().items():
            if position == self.get_player_position():
                new_position = position
            else:
                new_position = position.add(Position(MOVE[0], MOVE[1]))           
            new_grid.add_entity(new_position, entity)
        self._grid = new_grid
        self.generate_entities()

    def fire(self, shot_type: str) -> None:
        '''
        Handles the firing/collecting actions of a player towards an entity within the grid.
        
        Parameters:
            shot_type: The type of bomb.
        '''
        fire_entities = self._grid.get_entities()
        for position, entity in fire_entities.items():
            if position.get_x() == 3 and position.get_y() >= 1:

                # Shoot the corresponding entity according to the bullet type and clear the bullet.
                if entity.display() == COLLECTABLE and shot_type == SHOT_TYPES[1]:
                    self._grid.remove_entity(position)
                    self._collected += 1
                    self._total_shots += 1

                elif entity.display() == DESTROYABLE and shot_type == SHOT_TYPES[0]:
                    self._grid.remove_entity(position)
                    self._destroyed += 1
                    self._total_shots += 1

                elif entity.display() == BOMB:
                    self._grid.remove_entity(position)
                break
                
    def has_won(self) -> bool:
        '''Return True if the player has won the game.'''
        if self.get_num_collected() == COLLECTION_TARGET:
            return True
        else:
            return False

    def has_lost(self) -> bool:
        '''Returns True if the game is lost (a Destroyable has reached the top row).'''
        for position, entity in self.get_grid().get_entities().items():
            if position.get_y() == 1 and entity.display() == DESTROYABLE:
                return True
        return False


class AbstractField(tk.Canvas):
    '''AbstractFieldis an abstract view class which inherits fromtk.Canvasand provides base func-tionality for other view classes.'''
    def __init__(self, master: tk.Tk, rows, cols, width, height) -> None:
        '''
        The AbstractField class is constructed from the rows, cols, width and height.
        
        Parameters:
            rows: The number of rows in the grid.
            cols: The number of cols in the grid.
            width: The width of the grid.
            height: The height of the grid.        
        '''
        super().__init__(master, width = width, height = height)
        self._master = master
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height   

    def get_bbox(self, position: Position) -> Tuple[int, int, int, int]:
        '''
        Returns the bounding box for the position.
        
        Parameters:
            position: The specific position of the grid.
        '''
        single_width = self._width / self._cols
        single_height = self._height / self._rows
        x_min = position.get_x() * single_width
        y_min = position.get_y() * single_height
        x_max = (position.get_x() + 1) * single_width
        y_max = (position.get_y() + 1) * single_height
        return (x_min, y_min, x_max, y_max)

    def pixeltoposition(self, pixel) -> Tuple[int, int]:
        '''
        Converts the (x, y) pixel position (in graphics units) to a (row, column) position.
        
        Parameters:
            pixel: The pixel position of the grid.
        '''
        x = pixel[0] // (self._width / self._cols)
        y = pixel[1] // (self._height / self._rows)
        return (x, y)

    def get_position_center(self, position) -> Tuple[int, int]:
        '''
        Gets the graphics coordinates for the center of the cell at the given (row, column) position.

        Parameters:
            position: The specific position of the grid.
        '''
        x_center = (self.get_bbox(position)[0] + self.get_bbox(position)[2]) / 2 
        y_center = (self.get_bbox(position)[1] + self.get_bbox(position)[3]) / 2
        return (x_center, y_center)

    def annotate_position(self, position, text) -> None:
        '''
        Annotates the center of the cell at the given (row, column) position with the provided text.
        
        Parameters:
            position: The specific position of the grid.
            text: The specific text of the grid.
        '''
        self.create_text(self.get_position_center(position)[0], self.get_position_center(position)[1], text = text)


class GameField(AbstractField):
    '''GameFieldis a visual representation of the game grid which inherits from AbstractField. '''
    def __init__(self, master, size, width = MAP_WIDTH, height = MAP_HEIGHT):
        '''
        The GameField class is constructed from the size, width and height.
        
        Parameters:
            size: The number of rows in the gamefield.
            width: The width of the gamefield.
            height: The height of the gamefield.
        '''
        super().__init__(master, rows = size, cols = size, width = width, height = height)

    def draw_grid(self, entities:Dict[Position, Entity]) -> None:
        '''
        Draws the entities in the game grid at their given position.
        
        Parameters:
            entities: The dictionary containing grid entities.
        '''
        for position, entity in entities.items():
            x_min = self.get_bbox(position)[0]
            y_min = self.get_bbox(position)[1]
            x_max = self.get_bbox(position)[2]
            y_max = self.get_bbox(position)[3]   

            # Create a grid at the location corresponding to the entity.
            if entity.display() == COLLECTABLE:         
                self.create_rectangle(x_min, y_min, x_max, y_max, fill = COLOURS[COLLECTABLE])
            elif entity.display() == DESTROYABLE:         
                self.create_rectangle(x_min, y_min, x_max, y_max, fill = COLOURS[DESTROYABLE])
            elif entity.display() == BLOCKER:         
                self.create_rectangle(x_min, y_min, x_max, y_max, fill = COLOURS[BLOCKER])
            elif entity.display() == PLAYER:          
                self.create_rectangle(x_min, y_min, x_max, y_max, fill = COLOURS[PLAYER])
            elif entity.display() == BOMB:         
                self.create_rectangle(x_min, y_min, x_max, y_max, fill = COLOURS[BOMB])
            self.annotate_position(position, entity.display())

    def draw_player_area(self) -> None:
        '''Draws the grey area a player is placed on.'''
        self.create_rectangle(0, 0, MAP_WIDTH, MAP_HEIGHT / GRID_SIZE, fill = PLAYER_AREA)


class ScoreBar(AbstractField):
    '''ScoreBaris a visual representation of shot statistics from the player which inherits fromAbstractField.'''
    def __init__(self, master, rows) -> None:
        '''
        The ScoreBar class is constructed from the row.
        
        Parameters:
            roww: The number of rows contained in the ScoreBar canvas.        
        '''
        super().__init__(master, rows = rows, cols = 2, width = SCORE_WIDTH, height = MAP_HEIGHT)

       
class HackerController(object):
    '''HackerControlleracts as the controller for the Hacker game.'''
    def __init__(self, master: tk.Tk, size) -> None:
        '''
        The HackerController class is constructed from the size.

        Parameters:
            size: Represents the number of rows (= number of columns) in the game map.        
        '''
        self._size = size
        self._master = master

        # Create title.
        self._title = tk.Label(self._master, text= TITLE, background = TITLE_BG, font = TITLE_FONT)
        self._title.pack(side = TOP, expand = tk.TRUE, fill = tk.BOTH)

        # Create game, gamefield and scorebar.
        self._game = Game(size)
        self._gamefield = GameField(self._master, size, MAP_WIDTH, MAP_HEIGHT)
        self._gamefield.pack(side = 'left')
        self._scorebar = ScoreBar(self._master, size)
        self._scorebar.pack(side = 'left')
        self._master.bind("<Key>", self.handle_keypress)
        self.draw(self._game)
        self._master.after(2000, self.step)

    def handle_keypress(self, event) -> None:
        '''
        This method should be called when the user presses any key during the game.
        
        Parameters:
            event: Event component.
        '''
        keysym = event.keysym.lower()
        if keysym == 'a':
            self.handle_rotate(LEFT)

        if keysym == 'd':
            self.handle_rotate(RIGHT)

        if keysym == 'return':
            
            self.handle_fire(COLLECT)
        
        if keysym == 'space':
            self.handle_fire(DESTROY)  

    def draw(self, game: Game) -> None:
        '''
        Clears and redraws the view based on the current game state.
        
        Parameters:
            game: Instantiated game.
        '''
        self._gamefield.delete(tk.ALL)
        self._scorebar.delete(tk.ALL)
        self._gamefield.create_rectangle(0, 0, MAP_WIDTH, MAP_HEIGHT, fill = FIELD_COLOUR)
        self._gamefield.draw_player_area()
        self._gamefield.draw_grid(game.get_grid().get_entities())

        # Draw the scorebar.
        collected_num = self._game.get_num_collected()
        destroyed_num = self._game.get_num_destroyed()
        scorebar_height = BAR_HEIGHT
        scorebar_width = SCORE_WIDTH
        self._scorebar.create_rectangle(0, 0, self._scorebar._width, self._scorebar._height, fill = SCORE_COLOUR)
        self._scorebar.create_text(int(scorebar_width / 2), int(scorebar_height / 4), text = "Score", font = ('Arial', 24))
        self._scorebar.create_text(int(scorebar_width / 4 * 1.5), int(scorebar_height / 4 * 2), text = "Collected:", font = ('Arial', 24))
        self._scorebar.create_text(int(scorebar_width / 4 * 1.5), int(scorebar_height / 4 * 3), text = "Destroyed:", font = ('Arial', 24))
        self._scorebar.create_text(int(scorebar_width / 4 * 3.5), int(scorebar_height / 4 * 2), text = f"{collected_num}", font = ('Arial', 24))
        self._scorebar.create_text(int(scorebar_width / 4 * 3.5), int(scorebar_height / 4 * 3), text = f"{destroyed_num}", font = ('Arial', 24))

    def handle_rotate(self, direction) -> None:
        '''
        Handles rotation of the entities and redrawing the game.
        
        Parameters:
            direction: The rotation direction of the entities' positions.
        '''
        self._game.rotate_grid(direction)
        self.draw(self._game)

    def handle_fire(self, shot_type) -> None:
        '''
        Handles the firing of the specified shot type and redrawing of the game.
        
        Parameters:
            shot_type: The type of bomb.
        '''
        self._game.fire(shot_type)
        if self._game.has_won():
            answer = messagebox.askquestion(title = None, message = "Do you still want to play?")
            if answer == 'yes':
                self.new_game()
            else:
                self._master.destroy()
                exit(0)
        self.draw(self._game)

    def step(self) -> None:
        '''The step method is called every 2 seconds.'''
        if self._game.has_lost():
            answer = messagebox.askquestion(title = None, message = "Do you still want to play?")
            if answer == 'yes':
                self.new_game()
            else:
                self._master.destroy()
                exit(0)                
        self._game.step()
        self.draw(self._game)
        self._master.after(2000, self.step)
              
    def new_game(self) -> None:
        '''Refresh the game and enter a new round.'''
        self._game = Game(self._size)
        self.draw(self._game)


class ImageGameField(GameField):
    '''Create a new view class, ImageGameField, that extends your existing GameField class.'''
    def __init__(self, master, size, width, height) -> None:
        '''
        The ImageGameField class is constructed from the size, width and height.
        
        Parameters:
            size: Represents the number of rows (= number of columns) in the game map. 
            width: The width of the imagegamefield.
            height: The width of the imagegamefield.
        '''
        super().__init__(master, size, width, height)
        cell_size = int(width / size)
        self._blocker = ImageTk.PhotoImage(Image.open("images/B.png").resize((cell_size, cell_size)))
        self._collectable = ImageTk.PhotoImage(Image.open("images/C.png").resize((cell_size, cell_size)))
        self._destroyable = ImageTk.PhotoImage(Image.open("images/D.png").resize((cell_size, cell_size)))
        self._player = ImageTk.PhotoImage(Image.open("images/P.png").resize((cell_size, cell_size)))
        self._bomb = ImageTk.PhotoImage(Image.open("images/O.png").resize((cell_size, cell_size)))

    def draw_grid(self, entities: Dict[Position, Entity]) -> None:
        '''
        Draws the entities' image in the game grid at their given position.
        
        Parameters:
            entities: The dictionary containing grid entities.
        '''
        for position, entity in entities.items():
            position_center = self.get_position_center(position)
            entity_display = entity.display()

            # Stick images of different entities in its position.
            if entity_display == BLOCKER:
                self.create_image(position_center[0], position_center[1], image = self._blocker)
            elif entity_display == COLLECTABLE:
                self.create_image(position_center[0], position_center[1], image = self._collectable)
            elif entity_display == DESTROYABLE:
                self.create_image(position_center[0], position_center[1], image = self._destroyable)
            elif entity_display == PLAYER:
                self.create_image(position_center[0], position_center[1], image = self._player)
            elif entity_display == BOMB:
                self.create_image(position_center[0], position_center[1], image = self._bomb)


class StatusBar(tk.Frame):
    '''Add a StatusBar class that inherits from tk.Frame.'''
    def __init__(self, master: tk.Tk) -> None:
        '''The StatusBar class is constructed from the master'''
        self._time_counter = 0 
        self._shots_counter = 0
        self._master = master
        super().__init__(master)
        self._frame_list: List[Frame] = []
        for _ in range(3):
            self._frame_list.append(Frame(self))

        # Create shots label.
        self._total_shots = tk.Label(self._frame_list[0], text = "Total Shots")
        self._total_shots_num = tk.Label(self._frame_list[0], text = str(self._shots_counter))
        self._total_shots.pack(side = TOP)
        self._total_shots_num.pack(side = TOP)

        # Create timer label.
        self._timer = tk.Label(self._frame_list[1], text = "Timer")
        self._timer_num = tk.Label(self._frame_list[1], text = f"{self._time_counter // 60}m {self._time_counter % 60}s")
        self._timer.pack(side = TOP)
        self._timer_num.pack(side = TOP)

        # Create pause button.
        self._pause = False
        self._button = tk.Button(self._frame_list[2], text = "Pause", command = self.pause)    
        self._button.pack()

        self.pack(side = BOTTOM)
        for frame in self._frame_list:
            frame.pack(side = 'left')
        self.step()

    def step(self) -> None:
        '''The step method is called every 1 seconds.'''
        if not self._pause:
            self._timer_num.configure(text = f"{self._time_counter // 60}m {self._time_counter % 60}s")
            self._time_counter += 1
        else:
            pass
        self._master.after(1000, self.step)

    def refresh_shots_num_label(self) -> None:
        '''Refresh the number of shots.'''
        self._shots_counter += 1
        self._total_shots_num.configure(text = str(self._shots_counter))

    def pause(self) -> None:
        '''Pause the game.'''
        if self._pause:
            self._pause = False
        else:
            self._pause = True

    def get_total_shots(self) -> int:
        '''Return the number of total shots.'''
        return self._shots_counter

    def get_time(self) -> int:
        '''Return the number of time counter.'''
        return self._time_counter

    def get_pause(self) -> bool:
        '''Return the status of pause.'''
        return self._pause


class AdvancedHackerController(HackerController):
    '''AdvancedHackerController as the controller for the Hacker game, which inherits from HackerController.'''
    def __init__(self, master, size) -> None:
        '''
        The AdvancedHackerController class is constructed from the size.

        Parameters:
            size: Represents the number of rows (= number of columns) in the game map.        
        '''
        self._size = size
        self._master = master

        # Create title.
        self._title = tk.Label(self._master, text= TITLE, background = TITLE_BG, font = TITLE_FONT)
        self._title.pack(side = TOP, expand = tk.TRUE, fill = tk.BOTH)
    
        # Create game and scorebar.
        self._game = Game(size)

        # Create imagegamefield
        self._gamefield = ImageGameField(self._master, size, MAP_HEIGHT, MAP_WIDTH)
        self._gamefield.create_rectangle(0, 0, MAP_WIDTH, MAP_HEIGHT, fill = FIELD_COLOUR)
        self._gamefield.draw_grid(self._game.get_grid().get_entities())
        self._gamefield.draw_player_area()
        self._gamefield.pack(side='left')

        # Create scorebar.
        self._scorebar = ScoreBar(self._master, size)
        self._scorebar.pack(side = 'left')
        self._master.bind("<Key>", self.handle_keypress)
        self.draw(self._game)
        self._master.after(2000, self.step)

        # Create statusbar.
        self._status_bar = StatusBar(self._master)
        menu_bar = tk.Menu(self._master)
        self._master.config(menu = menu_bar)
        file_menu = tk.Menu(menu_bar)

        # Creat different functions in the menu.
        menu_bar.add_cascade(label = "File", menu = file_menu)
        file_menu.add_command(label = "New game", command = self.new_game)
        file_menu.add_command(label = "Save game", command = self.save_game)
        file_menu.add_command(label = "Load game", command = self.load_game)
        file_menu.add_command(label = "Quit", command = self.quit_game)

        self._filename = None
        self._status_bar.pack(side='bottom')

    def save_game(self) -> None:
        '''Prompt the user for the location to save their file,
        and save all necessary information to replicate the current state of the game.'''
        if self._filename is None:
            filename = filedialog.asksaveasfilename()
            if filename:
                self._filename = filename

        # Save game information.
        if self._filename:
            with open(self._filename, 'w', encoding = 'utf-8') as f:
                for item in [
                    self._game.get_grid().serialise(),
                    self._game.get_num_collected(),
                    self._game.get_num_destroyed(),
                    self._status_bar.get_total_shots(),
                    self._status_bar.get_time()
                ]:
                    f.write(str(item) + '\n')
                
    def load_game(self) -> None:
        '''Prompt the user for the location of the file to load a game from and load the game described in that file.'''
        filename = filedialog.askopenfilename()

        # Load game information.
        if filename:
            self._filename = filename
            with open(filename, 'r') as f:
                lines = f.readlines()
            field_string, collected, destroyed, total_shots, time = lines

            # Load entities.
            field: Dict[Tuple[int, int], str] = eval(field_string)
            self.new_game()
            for key, value in field.items():
                self._game.get_grid().add_entity(Position(key[0], key[1]), self._game._create_entity(value))
            
            # Load scorebar.
            self._game._collected = int(collected)
            self._game._destroyed = int(destroyed)

            # Load statusbar.
            self._status_bar._shots_counter = int(total_shots)
            self._status_bar._total_shots_num.configure(text = str(self._status_bar._shots_counter))            
            self._status_bar._time_counter = int(time)
            self._status_bar._timer_num.configure(text = f"{self._status_bar._time_counter // 60}m {self._status_bar._time_counter % 60}s")
            self.draw(self._game)
                 
    def quit_game(self) -> None:
        '''Prompt the player via a messagebox to ask whether they are sure they would like to quit. '''
        self._master.destroy()
        exit(0)

    def step(self) -> None:
        '''The step method is called every 2 seconds.'''
        if self._status_bar.get_pause():
            self._master.after(2000, self.step)
        else:
            super().step()

    def new_game(self) -> None:
        '''Start a new Hacker game.'''
        super().new_game()
        self._status_bar._shots_counter = 0
        self._status_bar._time_counter = 0
        self._status_bar._pause = False
        self._status_bar._total_shots_num.configure(text = str(self._status_bar._shots_counter))
        self._status_bar._timer_num.configure(text = f"{self._status_bar._time_counter // 60}m {self._status_bar._time_counter % 60}s")

    def handle_fire(self, shot_type):
        '''
        Handles the firing of the specified shot type and redrawing of the game.
        
        Parameters:
            shot_type: The type of bomb.
        '''
        self._status_bar.refresh_shots_num_label()
        return super().handle_fire(shot_type)


def start_game(root, TASK = TASK):
    '''Used to start the game.

    Parameters:
        Task: Differentiate different tasks and use different control classes.
    '''
    if TASK != 1:
        controller = AdvancedHackerController
    else:
        controller = HackerController
    app = controller(root, GRID_SIZE)
    return app


def main():
    root = tk.Tk()
    root.title(TITLE)
    app = start_game(root, TASK = 0)
    root.mainloop()


if __name__ == '__main__':
    main()
