#!/usr/bin/python
# http://ironalbatross.net/wiki/index.php?title=Python_Curses

import curses

# -----------------------------------------------------------------------------
class curses_screen:
    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        self.stdscr.keypad(1)
        return self.stdscr
    def __exit__(self,a,b,c):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

# -----------------------------------------------------------------------------
with curses_screen() as stdscr:
    key = 'X'
    while key != ord('q'):
        key = stdscr.getch()
        stdscr.addch(0,0,key)
        stdscr.refresh()