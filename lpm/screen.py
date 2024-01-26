"""Module for command-line IO."""
import curses
import curses.ascii
import locale
import os
import sys
from typing import Dict, Union

from .snippets import Snippet
from .stats import Stat


class Screen:
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    KEY_LEFT = curses.KEY_LEFT
    KEY_RIGHT = curses.KEY_RIGHT
    KEY_RESIZE = curses.KEY_RESIZE
    KEY_ENTER = curses.KEY_ENTER
    KEY_ESCAPE = curses.ascii.ESC

    def __init__(
        self, max_lines: int, max_cols: int, colors: Dict[str, tuple[int, int]]
    ) -> None:
        """Screen object used for command-line IO."""
        # min number of lines in terminal required for screen to work
        min_lines = max_lines + 6
        # min number of columns in terminal required for screen to work
        min_cols = max_cols

        # we set esc delay to 15 ms instead of leaving it at the default 1000ms, which
        # feels too slow/unresponsive when quitting out of the application
        os.environ.setdefault("ESCDELAY", str(15))

        # use the preferred system encoding
        locale.setlocale(locale.LC_ALL, "")
        self.encoding = locale.getpreferredencoding().lower()

        # initialize curses screen
        self.screen = curses.initscr()
        self.screen.nodelay(True)  # makes getch a non-blocking call

        # check that terminal is sufficiently large
        if self.lines < min_lines:
            curses.endwin()
            self.deinit()
            print(
                "lpm requires at least %d lines in terminal, please expand "
                "your terminal size or decrease MAX_LINES/MAX_COLS in the settings"
                % min_lines
            )
            sys.exit(1)
        if self.columns < min_cols:
            curses.endwin()
            self.deinit()
            print(
                "lpm requires at least %d columns in terminal, please expand "
                "your terminal size or decrease MAX_LINES/MAX_COLS in the settings"
                % min_cols
            )
            sys.exit(1)

        # screen configurations
        self.screen.keypad(True)  # makes curses return keys in form curses.KEY_
        curses.noecho()
        curses.cbreak()

        # set up colors
        self.colors = {}
        curses.start_color()
        self.setup_colors(colors)

        # initialize window
        self.window = curses.newwin(self.lines, self.columns, 0, 0)
        self.window.keypad(True)
        self.window.bkgd(" ", self.colors["background"])

    @property
    def columns(self) -> int:
        """Returns number of terminal columns."""
        return curses.COLS  # pylint: disable=no-member

    @property
    def lines(self) -> int:
        """Returns number of terminal lines."""
        return curses.LINES  # pylint: disable=no-member

    def setup_colors(self, colors: Dict[str, tuple[int, int]]):
        """Setups up terminal color."""
        for i, (k, v) in enumerate(colors.items()):
            curses.init_pair(i + 1, *v)
            self.colors[k] = curses.color_pair(i + 1)

        # # make certain colors more visible
        # if not "xterm256colors":
        #     self.colors["correct"] |= curses.A_DIM
        #     self.colors["incorrect"] |= curses.A_UNDERLINE | curses.A_BOLD
        #     self.colors["quote"] |= curses.A_BOLD
        #     self.colors["status"] |= curses.A_BOLD

    def get_key(self) -> Union[int, str, None]:
        """Gets the most recently pressed key.

        Returns
        -------
        str or int
            Returns the integer value for a special key, otherwise str value.
        """
        # pylint: disable=method-hidden
        # Install a suitable get_key based on Python version
        if sys.version_info[0:2] >= (3, 3):
            return self._get_key_py33()
        else:
            raise NotImplementedError
            # return self._get_key_py27()

    def _get_key_py33(self) -> Union[int, str, None]:
        """Python 3.3+ implementation of get_key."""

        def _is_escape(key):
            if isinstance(key, str) and len(key) == 1:
                return ord(key) == curses.ascii.ESC
            return False

        def _is_enter(key):
            if key == Screen.KEY_ENTER:
                return True
            if isinstance(key, str) and ord(key) in (curses.ascii.CR, curses.ascii.LF):
                return True
            return False

        def _is_backspace(key):
            if key == Screen.KEY_BACKSPACE:
                return True
            if isinstance(key, str) and ord(key) in (curses.ascii.BS, curses.ascii.DEL):
                return True
            return False

        # pylint: disable=too-many-return-statements
        try:
            # Curses in Python 3.3 handles unicode via get_wch
            key = self.window.get_wch()
            if _is_backspace(key):
                return Screen.KEY_BACKSPACE
            elif _is_enter(key):
                return Screen.KEY_ENTER
            elif _is_escape(key):
                return Screen.KEY_ESCAPE
            elif isinstance(key, int):
                keymap = set(
                    [
                        Screen.KEY_BACKSPACE,
                        Screen.KEY_LEFT,
                        Screen.KEY_RIGHT,
                        Screen.KEY_RESIZE,
                        Screen.KEY_ENTER,
                        Screen.KEY_ESCAPE,
                    ]
                )
                return None if key not in keymap else key
            return key
        except curses.error:
            return None

    def _addstr(
        self,
        row: int,
        col: int,
        text: str,
        color: curses.color_pair = None,
        encode: bool = True,
    ):
        """Wraps call around curses.window.addsr. Adds text at a given position.

        Parameters
        ----------
        row : int
            Row position.
        col : int
            Column position.
        text : str
            Text to display.
        color : curses.color_pair, optional
            Color setting for text, by default None
        encode : bool, optional
            Whether to encode text with self.encoding, by default True
        """
        if encode:
            text = text.encode(self.encoding)

        if self.lines > row >= 0:
            if col >= 0 and (col + len(text)) < self.columns:
                self.window.addstr(row, col, text, color)

    def chgat(self, row: int, col: int, length: int, color: curses.color_pair):
        """Wraps call around curses.window.chgat. Changes text color at given position.

        Parameters
        ----------
        row : int
            Row position.
        col : int
            Column position.
        length : int
            Number of chars after position to modify.
        color : curses.color_pair
            Color setting for text.
        """
        if self.lines > row >= 0:
            if col >= 0 and (col + length) <= self.columns:
                self.window.chgat(row, col, length, color)

    def set_cursor(self, row: int, col: int):
        """Set cursor position.

        Parameters
        ----------
        row : int
            Row position.
        col : int
            Column position.
        """
        if (row < self.lines) and (col < self.columns):
            self.window.move(row, col)

    def clear(self):
        """Clear the terminal."""
        self.window.clear()

    def deinit(self):
        """De-initializes curses."""
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()

    def render_stat(self, stat: Stat):
        """Render the top stat bar.

        Parameters
        ----------
        stat : Stat
            Stat object to display.
        """
        # if stat is none, use an empty Stat object (shows all 0s)
        top_bar = str(stat) if stat else str(Stat())

        # pad with spaces to the right to overwrite chars if the
        # stats string gets shorter
        top_bar = top_bar.ljust(self.columns - 1)

        self._addstr(0, 0, top_bar, self.colors["top_bar"])

    def render_author(self, snip: Snippet):
        """Render the author information.

        Parameters
        ----------
        snip : Snippet
            Snippet to display author information.
        """
        text = snip.url
        if len(text) > self.columns - 1:
            text = snip.author

        self._addstr(2, 0, text, self.colors["author"])

    def render_lines(self, snippet: Snippet):
        """Render the code snippet.

        Parameters
        ----------
        snippet : Snippet
            Snippet to render.
        """
        for i, line in enumerate(snippet.lines):
            self._addstr(4 + i, 0, line, self.colors["text"])

    def render_prompt(self, snip: Snippet, prompt: str):
        """Render the prompt.

        Parameters
        ----------
        snip : Snippet
            Snippet object, required since prompt occurs below snippet.
        prompt : str
            Prompt string to display.
        """
        self._addstr(len(snip.lines) + 5, 0, prompt, self.colors["prompt"])
