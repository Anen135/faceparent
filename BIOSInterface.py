import curses


class MenuItem:
    def __init__(self, name, action=None, submenu=None, back=False):
        self.name = name
        self.action = action
        self.submenu = submenu
        self.back = back


def add_input(stdscr, x, y, text):
    stdscr.addstr(y, x, text)
    name = stdscr.getstr(y, x + len(text)).decode().strip()
    return name

def with_message(stdscr, x, y, msg, wait=True):
    if type(msg) == list:
        for i in range(msg.__len__()):
            stdscr.addstr(x+i, y, msg[i])
    else:
        stdscr.addstr(x, y, msg)
    stdscr.refresh()
    if wait:
        curses.flushinp()
        stdscr.getch()

class BIOSInterface:
    def __init__(self, stdscr, root_menu):
        self.stdscr = stdscr
        self.current_menu = root_menu
        self.menu_stack = []
        self.selected_index = 0
        self.app_name = "PhoenixBIOS"
        self.app_version = "4.0 Release 6.0"
        self.footer = "↑/↓: Move Enter: Select Esc: Back/Quit"
        self.header = f" {self.app_name} {self.app_version} "
        self.running = True

        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

        curses.curs_set(1)
        self.stdscr.bkgd(' ', curses.color_pair(1))
        self.height, self.width = self.stdscr.getmaxyx()
    
    def set_header(self, app_name = None, app_version = None):
        app_name = app_name if app_name else self.app_name
        app_version = app_version if app_version else self.app_version
        self.header = f" {app_name} {app_version} "

    def draw_header(self):
        self.stdscr.addstr(0, (self.width - len(self.header)) // 2, self.header, curses.color_pair(2))

    def draw_footer(self):
        self.stdscr.addstr(self.height - 2, (self.width - len(self.footer)) // 2, self.footer)

    def draw_menu(self):
        self.stdscr.clear()
        self.stdscr.bkgd(' ', curses.color_pair(1))
        for idx, item in enumerate(self.current_menu):
            y = 5 + idx * 2
            x = 10
            prefix = "> " if idx == self.selected_index else "  "
            style = curses.A_REVERSE if idx == self.selected_index else curses.A_NORMAL
            self.stdscr.addstr(y, x, f"{prefix}{item.name}", style)
        self.draw_header()
        self.draw_footer()
        self.stdscr.refresh()
    
    def back_to_menu(self):
        if self.menu_stack:
            self.current_menu, self.selected_index = self.menu_stack.pop()
        else:
            self.running = False

    def run(self):
        while self.running:
            self.draw_menu()
            key = self.stdscr.getch()

            if key == curses.KEY_UP and self.selected_index > 0:
                self.selected_index -= 1
            elif key == curses.KEY_DOWN and self.selected_index < len(self.current_menu) - 1:
                self.selected_index += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                selected_item = self.current_menu[self.selected_index]
                if selected_item.submenu:
                    self.menu_stack.append((self.current_menu, self.selected_index))
                    self.current_menu = selected_item.submenu
                    self.selected_index = 0
                elif selected_item.action:
                    selected_item.action(self.stdscr, selected_item.name)
                elif selected_item.back:
                    self.back_to_menu()
            elif key == 27:  # ESC
                self.back_to_menu()
