#uicontroller: event loop, screens, focus, routes keys
from collections.abc import Callable
import curses
import time

from trilobite.tui.renderer import Renderer

class UIController:
    def __init__(self, stdscr, *, on_update_all: Callable[[], None], on_quit: Callable[[], None] | None = None):
        self._stdscr = stdscr
        #Passed functions
        self._on_update_all = on_update_all
        self._on_quit = on_quit

        #Create windows
        self.create_windows()
        self.title_w = Renderer(self.title)
        self.main_w = Renderer(self.main)
        self.status_w = Renderer(self.status)
        self.title_text = "Trilobite"

    def create_windows(self) -> None:
        """
        Creates the windows to pass to renderer
        """
        #Get amount we have to play with
        h, w = self._stdscr.getmaxyx()
        #set frame sizes
        title_frame_h = 4
        title_frame_w = w

        main_frame_h = h - 10
        main_frame_w = w

        status_frame_h = 6
        status_frame_w = w

        #Create frames
        self.title_frame = self._stdscr.derwin(title_frame_h, title_frame_w, 0, 0)
        self.main_frame = self._stdscr.derwin(main_frame_h, main_frame_w, h - main_frame_h - status_frame_h, 0)
        self.status_frame = self._stdscr.derwin(status_frame_h, status_frame_w, h - status_frame_h, 0)

        #Create inner windows
        self.title = self.title_frame.derwin(title_frame_h - 2, title_frame_w - 2, 1, 1)
        self.main = self.main_frame.derwin(main_frame_h - 2, main_frame_w - 2, 1, 1)
        self.status = self.status_frame.derwin(status_frame_h - 2, status_frame_w - 2, 1, 1)
        
        #Set keypads
        self.title.keypad(True)
        self.main.keypad(True)
        self.status.keypad(True)

        #Set borders
        #cosider this in renderer later
        self.title_frame.box()
        self.main_frame.box()
        self.status_frame.box()

        self.title_frame.noutrefresh()
        self.main_frame.noutrefresh()
        self.status_frame.noutrefresh()
        curses.doupdate()

        return None

    def run(self) -> None:
        """
        Main starting point for the whole thing
        """
        cont = True
        while cont:
            cont = self.main_menu()

    def draw_title(self) -> None:
        attr = curses.color_pair(1) | curses.A_UNDERLINE | curses.A_BOLD
        self.title_w.message_centered(self.title_text, attr = attr)

    def draw_menu(self) -> None:
        self.status_w.message_centered("u: update | q: quit")

    def check_main_menu_ans(self) -> bool:
        """
        Might change this logic. Just get the key, then pass that key to
        some other function later
        """
        cont = True
        ans = self.main_w.getkey(8,1)
        try:
            if str(ans) not in [curses.KEY_ENTER ,10 , 13, "\n","", "u", "q"]:
                self.main_w.message_centered("Not an option..")
            # if ans == curses.KEY_ENTER or ans == 10 or ans == 13 or ans == "\n":
            #     #FIX FOR ENTER
            #     pass
            if str(ans) == "u":
                #FIX FOR UPDATE
                self.main_w.message_centered("Updating all ..", y = 2)
                self._on_update_all()
                pass
            if str(ans) == "q":
                self.main_w.message_centered("Exiting ..", y = 2)
                time.sleep(750/1000)
                cont = False
        except ValueError:
            print(f"Not a string")
        return cont


    def main_menu(self) -> bool:
        cont = True
        self.main_w.clear()
        self.draw_title()
        self.draw_menu()
        cont = self.check_main_menu_ans()
        return cont

    def check_if_key_is_enter(self, key: int) -> bool:
        """
        Takes a variable called key, that represents a keypress from getch().
        Check if this key is equal to several different types of values for 
        ENTER. If it is return True, if not return False.
        """
        return key in ["\n", 10, curses.KEY_ENTER]

    def check_if_key_is_backspace(self, key: int) -> bool:
        """
        Takes a variable key, that represents a keypress from getch(). Check
        if the key is equal to several different types of values for BACKSPACE.
        If it is return True, if not return False.
        """
        return key in ["ć", 263, curses.KEY_BACKSPACE, "KEY_BACKSPACE"]


