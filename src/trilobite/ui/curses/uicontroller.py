#uicontroller: event loop, screens, focus, routes keys
from collections.abc import Callable
import curses
import logging
import time

from tqdm import tqdm

from trilobite.ui.curses.renderer import Renderer
from trilobite.commands.uicommands import (
    CmdNotAnOption,
    CmdQuit, 
    CmdUpdateAll,
    Command,
)
from trilobite.events.uievents import (
    EvtStartUp,
    EvtStatus,
    EvtProgress,
    Event,
)

logger = logging.getLogger(__name__)

class UIController:
    def __init__(self, stdscr) -> None:
        self._stdscr = stdscr

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

    def startup(self) -> None:
        """
        Main starting point for the whole thing
        """
        self.set_title()
        self.set_main()
        self.set_statusbar()

    def set_title(self) -> None:
        """
        Setups the title bar
        """
        self.title_w.erase()
        attr = curses.color_pair(1) | curses.A_UNDERLINE | curses.A_BOLD
        self.title_w.message_centered(self.title_text, attr = attr)

    def set_main(self) -> None:
        """
        Setups the main
        """
        self.main_w.erase()
        self.main_w.message_centered("Awaiting command..")

    def set_statusbar(self) -> None:
        """
        Setups the status bar
        """
        self.status_w.erase()
        self.status_w.message_centered("u: update | q: quit")

    def get_command(self) -> Command:
        """
        Asks the user for input
        """
        self.set_main()
        self.set_statusbar()
        cmd = CmdNotAnOption()
        ans = self.main_w.getkey(0,0)
        match ans:
            case "u":
                cmd = CmdUpdateAll()
            case "q":
                cmd =  CmdQuit()
        return cmd

    def handle_event(self, evt: Event) -> None:
        """
        Takes in events then handles them
        """
        match evt:
            case EvtStartUp():
                self.startup()
            case EvtStatus():
                self.status_w.message_centered(f"{evt.text}", y = 0)
                time.sleep(evt.waittime)
            case EvtProgress():
                self.status_w.message_centered(f"{evt.label} {evt.current}/{evt.total}",y = 1, erase=False)
                time.sleep(evt.waittime)

