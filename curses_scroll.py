import re
import os
import time
import logging
import curses
from curses import panel
from logging.handlers import RotatingFileHandler

# color pair numbers

COLOR_WHITE_BLACK   = 1
COLOR_BLACK_WHITE   = 2
COLOR_RED_BLACK     = 3
COLOR_GREEN_BLACK   = 4
COLOR_YELLOW_BLACK  = 5
COLOR_CYAN_BLACK    = 6
COLOR_CYAN_CYAN     = 7
COLOR_BLACK_CYAN    = 8

LOG_FORMAT = "[%(lineno)-4d] [%(funcName)s] %(message)s"


class Logger:
    def __init__(self, name, filename, loglevel):
        self.logpath = os.path.dirname(os.path.realpath(__file__))
        self.name = name
        self.filename = filename
        self.loglevel = loglevel
        self.formatter = logging.Formatter(LOG_FORMAT)
        self.maxbytes = 209715200
        self.backupcount = 5

    def create_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.loglevel)
        logpath = os.path.join(self.logpath, self.filename)
        handler = RotatingFileHandler(logpath,
                                      maxBytes=self.maxbytes,
                                      backupCount=self.backupcount)
        handler.setLevel(self.loglevel)
        handler.setFormatter(self.formatter)
        logger.addHandler(handler)
        return logger


logger = Logger('osmon', 'osmonitor.log', "DEBUG")
LOG = logger.create_logger()


class ScrollWindow:
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1
    FOOTER = "'UP'|'DOWN' to Scroll, 'LEFT'|'RIGHT' to flip pages, 'Q' to quit"

    def __init__(self, lines, origin, *cords):
        self.lines = lines
        self.origin = origin
        self.cords = cords
        self.height = 0
        self.width = 0
        self.lines_per_page = 0
        self.current_top = 0
        self.current_bottom = 0
        self.pages = 0
        self.bar_top = 1
        self.bar_len = 0
        self.bottom = len(self.lines)
        self.window = self.init_win()
        # update bottom
        self.bottom = len(self.lines)

        if self.window:
            self.window.refresh()

        self.log_status()

    def init_win(self):
        """ Create and initialize sub window to the origin """

        try:
            window = self.origin.subwin(*self.cords)
            window.keypad(True)
            self.height, self.width = window.getmaxyx()
            self.lines_per_page = self.height - 4
            self.pages = (self.bottom // self.lines_per_page) + 1
            self.bar_len = self.lines_per_page // self.pages
            pad_list_length = self.lines_per_page - (self.bottom % self.lines_per_page)
            padding_list = [' ' * (self.width-2)] * pad_list_length
            self.lines += padding_list
            foot_pad_len = max(self.width - len(self.FOOTER)-2, 1)
            footer = self.FOOTER + ' ' * foot_pad_len
            self.FOOTER = footer[:self.width-5]
            self.bar_len = self.lines_per_page//self.pages
            if self.bar_len == 0:
                self.bar_len = 1
            return window

        except Exception as excp:
            LOG.error(f"{self.excp_reason(self.origin, *self.cords)}")
            LOG.error(f"Exception string: {str(excp)}")
            return None
        finally:
            pass

    def run(self):
        try:
            self.input_stream()
        except KeyboardInterrupt:
            LOG.info("Keyboard Interrupt")
        except Exception as excp:
            LOG.info(f"Exception: {excp}")
        finally:
            curses.endwin()

    def input_stream(self):
        while True:
            LOG.debug(f"Current TOP: {self.current_top}")
            self.display()

            key = self.window.getch()

            if key == curses.KEY_UP:
                self.scroll(self.UP)
            elif key == curses.KEY_DOWN:
                self.scroll(self.DOWN)
            elif key == curses.KEY_LEFT:
                self.paging(self.LEFT)
            elif key == curses.KEY_RIGHT:
                self.paging(self.RIGHT)
            elif key == ord('q') or key == ord('Q'):
                break

    def scroll(self, direction):
        top = self.current_top
        bottom = top + self.lines_per_page

        if ((direction == self.UP and top > 0) or
            (direction == self.DOWN and bottom < self.bottom)):
            self.current_top += direction


    def paging(self, direction):
        current_page = self.current_top // self.lines_per_page

        if ((direction == self.LEFT and current_page == 0) or
            (direction == self.RIGHT and current_page == self.pages-1)):
            # do nothing
            pass
        else:
            next_page_top = (current_page + direction) * self.lines_per_page
            self.current_top = next_page_top

            if (direction == self.LEFT and
                self.current_top < self.lines_per_page):
                self.current_top = 0

    def set_side_bar(self):
        if self.current_top == 0:
            self.bar_top = 1
        elif self.current_top == self.bottom:
            self.bar_top = (self.lines_per_page - self.bar_len)
        else:
            self.bar_top = (self.current_top // self.pages) + 1
        return self.bar_top + self.bar_len

    def display(self):
        self.window.erase()
        indx = 1
        last_entry = self.current_top + self.lines_per_page

        try:
            self.window.addstr(self.height-2, 2, self.FOOTER, curses.color_pair(COLOR_BLACK_WHITE))
            # self.window.chgat(self.height - 1, 8, 2, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))
            # self.window.chgat(self.height - 1, 13, 4, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))
            # self.window.chgat(self.height - 1, 31, 4, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))
            # self.window.chgat(self.height - 1, 38, 4, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))

            for line in self.lines[self.current_top: self.current_top + self.lines_per_page]:
                self.window.addstr(indx, 2, line[:self.width - 5], curses.color_pair(COLOR_GREEN_BLACK))
                indx += 1
        except Exception as excp:
            LOG.error(f"Exception in displaying lines from index {self.current_top}")
            LOG.error(f"Exception: {str(excp)}")
            return None

        bar_bottom = self.set_side_bar()

        try:
            for x in range(self.bar_top, bar_bottom):
                self.window.addch(x, self.width-2, curses.ACS_VLINE | curses.color_pair(COLOR_CYAN_CYAN))
        except Exception as excp:
            LOG.error(f"Exception in displaying side bar top: {self.bar_top} end: {bar_bottom}")
            LOG.error(f"Exception: {str(excp)}")
            return None

        self.window.refresh()

    def excp_reason(self, origin, *cords):
        """ Returns the reason for curses failure """

        max_height, max_width = origin.getmaxyx()
        height, width, ystart, xstart = cords
        if height >= max_height:
            err_msg = f"Height {height} exceeds max height {max_height}"
        elif width >= max_width:
            err_msg = f"Width {width} exceeds max width {max_width}"
        elif ystart + height >= max_height:
            err_msg = f"Window went beyond border. move y cordinate up"
        elif xstart + width >= max_width:
            err_msg = f"Window went beyond border. move x cordinate left"
        elif (ystart == 0 or xstart == 0):
            err_msg = f"Start cordinates can't be zero y: {ystart}, x: {xstart}"
        else:
            err_msg = f"Unknown Error: Origin: ({max_height}, {max_width}), cords: {cords}"
        return err_msg

    def log_status(self):
        LOG.debug(f"Current TOP: {self.current_top} LINES: {self.lines_per_page}")
        LOG.debug(f"lines: {self.lines}, height: {self.height}, width: {self.height}")
        LOG.debug(f"total pages: {self.pages}, bottom: {self.bottom}")
        LOG.debug(f"bar len: {self.bar_len}, bar top: {self.bar_top}")

class MainD:
    def __init__(self, stdscr):
        self.origin = stdscr
        self.lines = curses.LINES - 1
        self.cols = curses.COLS - 1
        self.init_curses()

        #
        self.mainwin_cords = (self.lines, self.cols, 1, 1)
        self.mainwin = curses.newwin(*self.mainwin_cords)

        self.init_window(self.mainwin)
        self.mainwin.box()
        self.mainwin.refresh()
        self.invoke_scroll_window()

    def init_curses(self):
        curses.curs_set(0)
        if curses.has_colors():
            curses.start_color()

        curses.start_color()

        # curses.init_pair(pair_number, fg, bg)
        curses.init_pair(COLOR_WHITE_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(COLOR_BLACK_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(COLOR_RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(COLOR_GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(COLOR_YELLOW_BLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(COLOR_CYAN_BLACK, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(COLOR_CYAN_CYAN, curses.COLOR_CYAN, curses.COLOR_CYAN)
        curses.init_pair(COLOR_BLACK_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def init_window(self, win):
        win.keypad(True)

    def invoke_scroll_window(self):
        dummy = 'X' * 2000
        lines = [f'line {i} {dummy} ' for i in range(0, 250)]
        cords = (30, 80, 5, 20)
        scrollwin = ScrollWindow(lines, self.mainwin, *cords)
        scrollwin.run()


def main():
    curses.wrapper(MainD)

if __name__ == '__main__':
    main()
