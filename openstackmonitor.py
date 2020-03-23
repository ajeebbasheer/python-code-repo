import re
import os
import sys
import time
import logging
import curses
import pathlib
from curses import panel
from fabric import Connection
import threading
from logging.handlers import RotatingFileHandler

########################################
# Open stack server configurations.    #
# OSTACK_SERV_IP = '10.189.146.70'
# OSTACK_USER = 'root'
# OSTACK_SECRET = 'STRANGE-EXAMPLE-neither'
CONFIG_FILE_NAME = 'ostackmon.ini'
########################################

# color pair numbers
COLOR_WHITE_BLACK = 1
COLOR_BLACK_WHITE = 2
COLOR_RED_BLACK = 3
COLOR_GREEN_BLACK = 4
COLOR_YELLOW_BLACK = 5
COLOR_CYAN_BLACK = 6
COLOR_CYAN_CYAN = 7
COLOR_BLACK_CYAN = 8
COLOR_MAGENTA_BLACK = 9
COLOR_BLACK_RED = 10
COLOR_BLACK_GREEN = 11
COLOR_BLACK_MAGENTA = 12

OPT_HELP = 111
OPT_QUIT = 222
OPT_BREAK = 999

LOG_FORMAT = "[%(lineno)-4d] [%(funcName)s] %(message)s"

ASCII_BAR = '█'  # an extended ASCII 'fill' character
LOAD_BAR = f"{ASCII_BAR * 5}| Updating..."

MULT_FACTOR = {
    'GB': 1,
    'MB': 1024,
    'KB': 1024 * 1024
}

MENU = [
    "dashboard",
    "services",
    "nova services",
    "nova instances",
    "network agents",
    "ceph status",
    "openvswitch",
    "ovs-vswitchd",
    "rabbitmq"
]

ostack_commands = {
    1: "source admin-openrc && openstack-status",
    2: "source admin-openrc && nova service-list",
    3: "source admin-openrc && openstack network agent list",
    4: "ceph status",
    5: "clush -g compute 'service openvswitch status'",
    6: "clush -g compute 'systemctl status ovs-vswitchd.service'",
    7: "systemctl status rabbitmq-server.service"
}

# what should be the custom headings?
manual_table_fields = {
    1: ["Name", "Type", "State"],
    2: [" "],
    3: ["Host", "Service", "Active", "Main PID"],
    4: ["Service", "Active"]
}

# This defines the structure of a window. 'def' contain the (item index, max length)
table_meta = {
    1: {"name": "SERVICES", "cmd": 1, "fid": 1,
        "def": [(0, 10), (1, 25), (2, 30)]
        },
    2: {"name": "NOVA MANAGED SERVICES", "cmd": 2, "fid": -1,
        "def": [(0, 4), (1, 25), (2, 17), (4, 8), (5, 6)]
        },
    3: {"name": "NOVA INSTANCES", "cmd": 1, "fid": -1,
        "def": [(1, 25), (3, 9), (5, 11), (6, 52)]
        },
    4: {"name": "NETWORK AGENT LIST", "cmd": 3, "fid": -1,
        "def": [(1, 20), (2, 17), (4, 8), (5, 7)]
        },
    5: {"name": "CEPH STATUS", "cmd": 4, "fid": 2,
        "def": [(0, 80)]
        },
    6: {"name": "OPENVSWITCH STATUS", "cmd": 5, "fid": 3,
        "def": [(0, 17), (1, 12), (2, 60)]
        },
    7: {"name": "OVS-VSWITCHD SERVICE STATUS", "cmd": 6, "fid": 3,
        "def": [(0, 17), (1, 12), (2, 60)]
        },
    8: {"name": "RABBITMQ-SERVER STATUS", "cmd": 7, "fid": 4,
        "def": [(0, 40), (1, 50)]
        }
}


# Global Variables
class GlobalVars:
    OSTACK_SERV_IP = '10.189.146.70'
    OSTACK_USER = 'root'
    OSTACK_SECRET = None
    NEW_LOAD = False
    ceph_status = {}
    resize_detected = False
    reload_requested = False
    backfromhelp = False
    help_or_quit = False
    dash_reload = {'1': False, '2': False}
    dashboard_updated_at = str(time.asctime(time.localtime(time.time())))


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


logger = Logger('osmon', 'ostackmon_log', 'DEBUG')
LOG = logger.create_logger()


class OStackTable:
    def __init__(self, id):
        self.id = id
        if id == 0:
            self.name = "dashboard"
        else:
            self.name = table_meta[id].get("name")
            self.command = table_meta[id].get("cmd")
            self.table_def = table_meta[id].get("def")
            self.values = []
            self.fields = self.get_fields()
            self.index_list, self.width_dict = self.get_table_layout()

        self.updated_at = str(time.asctime(time.localtime(time.time())))
        self.reloading = False
        self.loaded_values = False
        self.reload_started = False

    def get_fields(self):
        fields_id = table_meta.get(self.id).get("fid")
        if fields_id != -1:
            fields = manual_table_fields.get(fields_id)
        else:
            fields = []
            LOG.error(f"fields will be extracted dynamically for {self.name}")
        return fields

    def get_format_string(self, item):
        disp_str = ''
        try:
            for indx in self.index_list:
                val = item[indx]
                # LOG.debug(f"item: {item}, width_dict: {self.width_dict}")
                max_len = self.width_dict.get(indx)
                if len(val) > max_len:
                    val = val[:max_len]
                text = "{} ".format(val.ljust(max_len))
                disp_str += text
            return disp_str

        except Exception as excp:
            LOG.error(f"Could not get formatted text. {str(excp)}")
            text = "Something went wrong"
            return text

    def disp_details(self):
        LOG.info(f"id: {self.id}")
        LOG.info(f"name: {self.name}")
        LOG.info(f"command: {ostack_commands[self.command]}")
        LOG.info(f"table definition: {self.table_def}")
        LOG.info(f"updated_at: {self.updated_at}")
        LOG.info(f"fields: {self.fields}")
        LOG.info(f"index list: {self.index_list}")
        if self.values:
            for val in range(len(self.values)):
                val_str = f"{self.values[val]}"
                LOG.info(val_str[:100])
        else:
            LOG.info(f"Values: None")

    def get_table_layout(self):
        index_list = []
        width_dict = {}
        for tup in self.table_def:
            index_list.append(tup[0])
            width_dict[tup[0]] = tup[1]
        return index_list, width_dict


class OStackStatusProcessor:
    recent_results = {}

    def __init__(self, tables, main):
        self.main = main
        self.ip = GlobalVars.OSTACK_SERV_IP
        self.user = GlobalVars.OSTACK_USER
        self.secret = GlobalVars.OSTACK_SECRET
        self.tables = tables
        self.cmd_run_status = {}

    def get_connection(self):
        env_kwargs = {'password': self.secret,
                      'timeout': 60}
        try:
            if self.secret:
                conn = Connection(self.ip,
                                  user=self.user,
                                  connect_kwargs=env_kwargs)
            else:
                conn = Connection(self.ip,
                                  user=self.user)

        except Exception as excp:
            LOG.info(f"Unable to reach server {self.user}@{self.ip}")
            return None
        return conn

    def process(self):
        threads = []
        self.cmd_run_status = {x: False for x in range(1, len(ostack_commands) + 1)}
        LOG.info(f"Processing starts. tables: {self.tables}")

        for tid in self.tables:
            table = self.main.os_tables[tid]
            if table.loaded_values:
                table.reload_started = True

            try:
                thread = threading.Thread(target=self.update_table, args=(table,))
                LOG.info(f"Starting thread: {tid}")
                thread.start()
                threads.append(thread)

            except KeyboardInterrupt:
                curses.endwin()
                LOG.info("Keyboard Interrupt")
                sys.exit(1)
            except Exception as excp:
                LOG.error(f"Thread failed. os_table[{tid}].updated_table. {str(excp)}")
                for thread in threads:
                    thread.join()
                return None

        LOG.info(f"Joining threads..")

        for thread in threads:
            thread.join(1)

        LOG.info(f"Joined threads.")

    def update_table(self, table):
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

        try:
            if self.cmd_run_status.get(table.command, False):
                LOG.info(f"Command is recently done. Taking the previous output")
                result = self.recent_results.get(table.command)
            else:
                command = ostack_commands.get(table.command)
                LOG.info(f"Running command {command}")
                result = self.run_command(command)
                self.recent_results[table.command] = result
                self.cmd_run_status[table.command] = True
                # LOG.info(f"RAW RESULT: {result}")

            if table.command == 1:
                if table.id == 1:
                    values = result[0]
                elif table.id == 3:
                    values = result[2]
                    for val in values:
                        # LOG.info(f"val: {val}")
                        new_val = "-".join(re.findall(ip_pattern, val[6]))
                        # LOG.debug(f"updated to: {new_val}")
                        val[6] = new_val
            elif table.command == 7:
                values = [result]
            elif (table.command == 2 or
                  table.command == 3):
                values = list(result[1:][0])
            else:
                values = result

            # LOG.info(f"fields of {table.name}: {table.fields}")

            if len(table.fields) == 0:
                if table.id == 3:
                    table.fields = result[1]
                if table.id == 2:
                    table.fields = result[0]
                if table.id == 4:
                    table.fields = result[0]
            table.values = values
            table.updated_at = str(time.asctime(time.localtime(time.time())))

            if table.id in (1, 5):
                GlobalVars.dashboard_updated_at = str(time.asctime(time.localtime(time.time())))

            table.loaded_values = True
            if table.id == 1:
                GlobalVars.dash_reload['1'] = True
            elif table.id == 5:
                GlobalVars.dash_reload['5'] = True

            if table.reload_started:
                table.reload_started = False
            LOG.debug(f"TABLE: {table.id} has been loaded")
            table.reloading = False
            self.main.publisher.disp_subscribers()
            self.main.publisher.change_status = table.id

        except Exception as excp:
            LOG.error(f"Exception in updating tables. {str(excp)}")

        return None

    def run_command(self, command):
        LOG.info(f"Connecting server {self.ip}")

        conn = self.get_connection()
        if conn is None:
            LOG.error(f"Unable to run command.")
            return None

        try:
            resp = conn.run(command, hide="both", warn=True)
            result = resp.stdout.strip('\n').split('\n')
        except Exception as excp:
            LOG.error(f"Could not run command. {str(excp)}")
            return None

        if command == ostack_commands[1]:
            tables, lists = self.parse_os_status_stdout(result)
            nova_instances = tables[0]
            fields, values = self.extract_table_data(nova_instances[1:])
            return [lists, fields, values]

        elif command == ostack_commands[2]:
            table = self.extract_table_data(result)
            return table
        elif command == ostack_commands[3]:
            table = self.extract_table_data(result)
            return table
        elif command == ostack_commands[4]:
            table = self.parse_ceph_out(result)
            return table
        elif (command == ostack_commands[5] or
              command == ostack_commands[6]):
            table = self.parse_clush_commands(result)
            return table
        elif command == ostack_commands[7]:
            table = self.parse_systemctl_stdout(result)
            return table
        else:
            pass
        return command

    def extract_table_data(self, table_str):
        try:
            fields = [x.strip() for x in table_str[1].split('|')][1:-1]
            values = []
            for row in table_str[3:]:
                if row.startswith('|'):
                    values.append([x.strip() for x in row.split('|')][1:-1])
                else:
                    break

            return fields, values
        except Exception as excp:
            LOG.error(f"Could not extract table data. {str(excp)}")
            return None

    def parse_ceph_out(self, out):
        common_pattern = re.compile(r'\s+(\w+): \s*(.*)', re.IGNORECASE)
        table = []

        try:
            for line in out:
                table.append([line])
                m = common_pattern.search(line)
                if m:
                    GlobalVars.ceph_status[m.group(1)] = m.group(2)

            LOG.info(f"ceph_status: {GlobalVars.ceph_status}")
            return table
        except Exception as excp:
            LOG.error(f"Could not parse ceph output. {str(excp)}")
            return None

    def parse_clush_commands(self, out):
        pattern = r'([\w-]+):.*service - Open vSwitch'
        p1 = re.compile(pattern, re.IGNORECASE)
        index = 0
        out_len = len(out)
        table = []
        try:
            while index < out_len:
                match = p1.search(out[index])
                if match:
                    host = match.group(1)
                    status_table = []
                    index += 1
                    while (index < out_len and
                           p1.search(out[index]) is None):
                        status_table.append(out[index])
                        index += 1
                    entry = [host] + self.parse_systemctl_stdout(status_table)
                    table.append(entry)
                else:
                    index += 1
            return table
        except Exception as excp:
            LOG.error(f"Could not parse clush output. {str(excp)}")
            return None

    def parse_systemctl_stdout(self, out):
        pat_service = r'Loaded: loaded \(.*/([\w-]+).service;'
        pat_status = r'Active:\s+(\w+)'
        pat_status_active = r'Active:\s+active .* (since .*) '
        pat_mainpid = r'Main PID:\s+(\d+) '
        p1 = re.compile(pat_service, re.IGNORECASE)
        p2 = re.compile(pat_status, re.IGNORECASE)
        p2a = re.compile(pat_status_active, re.IGNORECASE)
        p3 = re.compile(pat_mainpid, re.IGNORECASE)
        data = [None, None, None]

        try:
            for line in out:
                if data[0] is None:
                    m1 = p1.search(line)
                    data[0] = m1.group(1) if m1 else None
                if data[1] is None:
                    m2 = p2.search(line)
                    if m2:
                        status = m2.group(1)
                        data[1] = status
                        if status.strip() == "active":
                            m2a = p2a.search(line)
                            if m2a:
                                data[1] += f" [{m2a.group(1)}]"
                        else:
                            pass
                if data[2] is None:
                    m3 = p3.search(line)
                    data[2] = m3.group(1) if m3 else " "
            return data
        except Exception as excp:
            LOG.error(f"Could not parse systemctl output. {str(excp)}")
            return None

    def parse_os_status_stdout(self, out):
        pattern1 = r'== ([\w\s]+) =='
        pattern2 = r'^\+-+'
        pattern3 = r'^([\w\-\s]+):\s+(\w+)'
        pattern4 = r'^\|[\w\s\|]+'
        required_tables = ["Nova instances"]
        p1 = re.compile(pattern1, re.IGNORECASE)
        p2 = re.compile(pattern2, re.IGNORECASE)
        p3 = re.compile(pattern3, re.IGNORECASE)
        p4 = re.compile(pattern4, re.IGNORECASE)

        tables = []
        lists = []

        index = 0
        list_size = len(out)

        try:
            while index < list_size:
                match = p1.search(out[index])
                if (match):
                    # LOG.info(f"found a match at {out[index]}")
                    index += 1
                    table_match = p2.search(out[index])
                    list_match = p3.search(out[index])

                    if table_match:
                        table_name = match.group(1)
                        if table_name in required_tables:
                            table_list = []
                            table_list.append(table_name)
                            while (p2.search(out[index]) or p4.search(out[index])):
                                table_list.append(out[index])
                                index += 1
                                if index >= list_size:
                                    break
                            tables.append(table_list)
                        else:
                            pass
                            # LOG.info(f"ignored table {table_name}")

                    elif list_match:
                        while (list_match):
                            serv_list = [match.group(1).split()[0]]
                            serv_list += list(list_match.groups())
                            index += 1
                            if index >= list_size:
                                break
                            lists.append(serv_list)
                            list_match = p3.search(out[index])
                    else:
                        LOG.info(f"Found another pattern. Ignore/Investigate")
                else:
                    index += 1

            return tables, lists

        except Exception as excp:
            LOG.error(f"Could not parse openstack-status output. {str(excp)}")
            return None


class CephStatus:
    def __init__(self):
        self.health = 'HEALTH_OK'
        self.health_details = ''
        self.monitors = ''
        self.mon_details = ''
        self.osd_status = {}
        self.pools = ''
        self.pgs = ''
        self.pg_status = ''
        self.total_capacity = ''
        self.used_capacity = ''
        self.available_capacity = ''

    def update_ceph_status(self):
        p_usage = re.compile(
            r'([\d\.]+\s\w{0,3}) used,\s+([\d\.]+\s\w{0,3})\s+\/\s+([\d\.]+\s\w{0,3})\s+avail')
        p_health = re.compile(r'(\w+)\s*(.*)')
        p_monitor = re.compile(r'(\d+)\s+daemons, (.*)')
        p_osds = re.compile(r'(\d+) osds:\s+(.*)')
        p_pools = re.compile(r'(\d+) pools')
        p_pgs = re.compile(r'(\d+) (.*)')

        try:
            match = p_usage.search(GlobalVars.ceph_status.get('usage'))
            if match:
                self.used_capacity, self.available_capacity, self.total_capacity \
                    = match.groups()

            match = p_health.search(GlobalVars.ceph_status.get('health'))
            if match:
                self.health, self.health_details = match.groups()

            match = p_monitor.search(GlobalVars.ceph_status.get('mon'))
            if match:
                self.monitors, self.mon_details = match.groups()

            match = p_osds.search(GlobalVars.ceph_status.get('osd'))
            if match:
                osds, status = match.groups()
                self.osd_status['osds'] = int(osds)
                stat_list = status.split(',')
                for item in stat_list:
                    num, state = item.split()
                    state = state.strip().lower()
                    self.osd_status[state] = int(num)

            match = p_pools.search(GlobalVars.ceph_status.get('pools'))
            if match:
                self.pools = match.groups()[0]

            match = p_pgs.search(GlobalVars.ceph_status.get('pgs', ' '))
            if match:
                self.pgs, self.pg_status = match.groups()

        except Exception as excp:
            LOG.error(f"exception in updating ceph status. {str(excp)}")
            return None


class GatherContent:
    def __init__(self, mainscreen, table_id):
        self.table = mainscreen.os_tables[table_id]
        self.values = self.table.values
        self.fields = self.table.fields
        self.updated_at = self.table.updated_at
        self.dispwin = mainscreen.dispwin
        self.max_width = mainscreen.dispwin_cords[1]
        self.footerwin = mainscreen.footerwin

    def gather_items_in_a_list(self):
        input_list = []
        try:
            heading = self.table.get_format_string(self.fields)
            input_list.append(heading)
            blank_line = ' ' * self.max_width
            input_list.append(blank_line)
            for value in self.values:
                line_text = self.table.get_format_string(value)
                input_list.append(line_text)
            return input_list
        except Exception as excp:
            LOG.error(f"Exception in gathering items.{str(excp)}")
        return None

class ScrollWindow:
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1
    FOOTER = "'UP'|'DOWN' to Scroll, 'LEFT'|'RIGHT' to flip pages, 'Q' to quit"

    def __init__(self, lines, menu_content_win, origin, *cords):
        self.lines = lines
        self.menu_cont_win = menu_content_win
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
            self.window.erase()
            self.window.refresh()

        # self.log_status()

    def init_win(self):
        """ Create and initialize sub window to the origin """

        try:
            window = self.origin.subwin(*self.cords)
            window.keypad(True)
            self.height, self.width = window.getmaxyx()
            self.lines_per_page = self.height - 2
            self.pages = (self.bottom // self.lines_per_page) + 1
            self.bar_len = self.lines_per_page // self.pages
            pad_list_length = self.lines_per_page - (self.bottom % self.lines_per_page)
            padding_list = [' ' * (self.width - 2)] * pad_list_length
            self.lines += padding_list
            foot_pad_len = max(self.width - len(self.FOOTER) - 2, 1)
            footer = self.FOOTER + ' ' * foot_pad_len
            self.FOOTER = footer[:self.width - 5]
            self.bar_len = self.lines_per_page // self.pages
            if self.bar_len == 0:
                self.bar_len = 1

            return window

        except curses.error as excp:
            LOG.error(f"{self.excp_reason(self.origin, *self.cords)}")
            LOG.error(f"{str(excp)}")
            curses.endwin()
            # sys.exit(1)
            return None
        finally:
            pass

    def run(self):
        try:
            self.input_stream()
        except KeyboardInterrupt:
            curses.endwin()
            LOG.info("Keyboard Interrupt")
        except Exception as excp:
            LOG.info(f"Exception: {excp}")
        finally:
            curses.endwin()

    def break_scroll_win(self):
        if self.pages == 1:
            return True
        if GlobalVars.NEW_LOAD:
            GlobalVars.NEW_LOAD = False
            return True
        if GlobalVars.help_or_quit:
            GlobalVars.help_or_quit = False
            return True
        if GlobalVars.backfromhelp:
            GlobalVars.backfromhelp = False
            return True
        if GlobalVars.reload_requested:
            return True
        if GlobalVars.resize_detected:
            return True

        return False

    def input_stream(self):
        GlobalVars.resize_detected = False
        GlobalVars.reload_requested = False
        while True:
            LOG.debug(f"Current TOP: {self.current_top} New Load? {GlobalVars.NEW_LOAD}")
            self.display()

            if self.break_scroll_win():
                break

            # If more than one page, then refresh the menu window so that the
            # seleceted option will remain Yellow.
            if self.pages > 1:
                self.menu_cont_win.refresh()

            key = self.window.getch()
            self.window.erase()

            if key == curses.KEY_UP:
                self.scroll(self.UP)
            elif key == curses.KEY_DOWN:
                self.scroll(self.DOWN)
            elif key == curses.KEY_LEFT:
                self.paging(self.LEFT)
            elif key == curses.KEY_RIGHT:
                self.paging(self.RIGHT)
            elif key == 27:
                break
            elif key == curses.KEY_RESIZE:
                GlobalVars.resize_detected = True
                break
            elif key == ord('r') or key == ord('R'):
                GlobalVars.reload_requested = True
                try:
                    self.origin.addstr(1, 1, LOAD_BAR, curses.color_pair(COLOR_YELLOW_BLACK))
                    self.origin.refresh()
                except Exception as excp:
                    LOG.error(f"Exception in showing loading bar. {str(excp)}")
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
                (direction == self.RIGHT and current_page == self.pages - 1)):
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

    def set_color(self, indx, line, win):

        green_patterns = [r' enabled ', r' up ', r' active ',
                          r'HEALTH_OK', r' Running ', r' active\+clean', r' True']
        red_patterns = [r' down ', r' Something went wrong', r' Shutdown ',
                        r' inactive ', r' False', r'HEALTH_ERR']

        yellow_patterns = [r'HEALTH_WARN']

        try:
            match = re.search(r'-[\.]+', line)
            if match:
                win.chgat(indx, match.start() + 2, len(match.group()),
                          curses.A_BOLD | curses.color_pair(COLOR_BLACK_GREEN))

            match = re.search(r'\s[\-]+', line)
            if match:
                win.chgat(indx, match.start() + 2, len(match.group()),
                          curses.A_BOLD | curses.color_pair(COLOR_BLACK_RED))

            for pattern in green_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    win.chgat(indx, match.start() + 2, len(match.group()),
                              curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))

            for pattern in red_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    win.chgat(indx, match.start() + 2, len(match.group()),
                              curses.A_BOLD | curses.color_pair(COLOR_RED_BLACK))

            for pattern in yellow_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    win.chgat(indx, match.start() + 2, len(match.group()),
                              curses.A_BOLD | curses.color_pair(COLOR_YELLOW_BLACK))
        except curses.error:
            LOG.info("Curses error in settting color")
        except Exception as excp:
            LOG.error(f"{str(excp)}")

        return None

    def create_bar_lines(self, line, indx, win):
        try:
            arr = line.split()
            max_len = int(arr[2])
            bar_length = self.cords[1] // 2 - 5

            up = int(arr[3])
            down = int(arr[4])
            max_total = int(arr[5])
            times = bar_length // max_total
            bar_length = times * (up + down)
            extra_space = ' ' * (times * (max_total - (up + down)))

            text = arr[1] + ": " + ' ' * (max_len - len(arr[1] + ": ")) + (ASCII_BAR * (bar_length - 2))

            green_len = (bar_length * up) // (up + down)
            red_len = bar_length - green_len

            full_text = text + f"{extra_space} {up} UP, {down} DOWN"
            win.addstr(indx, 2, full_text[:self.cords[1] - 2])

            if up == 0 and down == 0:
                pass
            else:
                win.chgat(indx, max_len, green_len, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))
                win.chgat(indx, max_len + green_len, red_len, curses.A_BOLD | curses.color_pair(COLOR_RED_BLACK))
        except Exception as excp:
            LOG.info(f"Exception in drawing bars: {str(excp)}")

    def drawline(self, line, indx, win):
        arr = line.split()
        line_start = int(arr[1])
        line_len = int(arr[2])

        for i in range(line_start, line_start + line_len):
            win.addch(indx, i, curses.ACS_HLINE)

    def display(self):
        indx = 1

        try:

            for line in self.lines[self.current_top: self.current_top + self.lines_per_page]:
                temp_line = line[:self.width - 5]
                if line.startswith('BAR'):
                    self.create_bar_lines(line, indx, self.window)
                elif line.startswith('LINE'):
                    self.drawline(line, indx, self.window)
                elif line.startswith('BIG'):
                    self.big_message(line, indx, self.window)
                    self.window.clear()
                    return None
                else:
                    self.window.addstr(indx, 2, temp_line)
                    if indx != 1:
                        self.set_color(indx, temp_line, self.window)
                indx += 1
        except Exception as excp:
            LOG.error(f"Exception in displaying lines from index {self.current_top}")
            LOG.error(f"Exception: {str(excp)}")
            return None

        bar_bottom = self.set_side_bar()
        LOG.debug(f"BAR TOP: {self.bar_top} BAR BOTTOM: {bar_bottom}")

        try:
            for x in range(self.bar_top, bar_bottom):
                self.window.addch(x, self.width - 2, curses.ACS_VLINE | curses.color_pair(COLOR_CYAN_CYAN))
        except Exception as excp:
            LOG.error(f"Exception in displaying side bar top: {self.bar_top} end: {bar_bottom}")
            LOG.error(f"Exception: {str(excp)}")
            return None

        if self.window:
            LOG.info("Refreshing Window")
            self.window.refresh()
        else:
            LOG.info("No window to refresh")

    def big_message(self, line, indx, win):
        arr = line.split()
        big = arr[1]
        if big == 'Quit?':
            msg = "Press Q to Quit, C to Cancel"
            color = COLOR_RED_BLACK
        else:
            msg = f"Please wait a while... Loading {' '.join(arr[2:])}"
            color = COLOR_GREEN_BLACK

        win.addstr(1, 3, big[:self.width - 4], curses.color_pair(color))
        win.addstr(2, 3, msg[:self.width - 4], curses.color_pair(COLOR_WHITE_BLACK))
        win.refresh()

    def excp_reason(self, origin, *cords):
        """ Returns the reason for curses failure """

        max_height, max_width = origin.getmaxyx()
        LOG.debug(f"origin.getmaxyx(): Y, X = {max_height}, {max_width}")
        LOG.debug(f"CORDS: {self.cords}")

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


class Publisher:
    def __init__(self, x=0):
        self._updated = x
        self._subscribers = []

    def add_subscriber(self, sub):
        self._subscribers.append(sub)

    def disp_subscribers(self):
        LOG.info(f"_subscribers:{len(self._subscribers)}")
        for subscriber in self._subscribers:
            LOG.info(f"subscriber: {subscriber.__name__}")

    @property
    def change_status(self):
        LOG.info("getter called")
        return self._updated

    @change_status.setter
    def change_status(self, status):
        LOG.info("Setter called")
        self._updated = status
        for subscriber in self._subscribers:
            subscriber(self._updated)


class MenuDriver:
    def __init__(self, options, mainscreen, *cords):
        self.mainscreen = mainscreen
        self.menuwin = mainscreen.menuwin
        self.menuwin_cords = mainscreen.menuwin_cords
        self.dispwin = mainscreen.dispwin
        self.window = None
        self.panel = None
        self.cords = cords
        self.init_win_panels(*cords)
        self.position = 0
        self.curr_selection = 0
        self.items = options
        self.items.append("[?] Help")
        self.items.append("[Q] Quit")
        self.initialized = False
        self.contentwin_cords = self.mainscreen.scrollwin_cords
        self.asciinums = list(map(ord, [str(x) for x in range(10)]))
        self.quit = False
        self.blankline = ' ' * 200

    def init_win_panels(self, *cords):
        self.window = self.menuwin.subwin(*cords)
        self.window.keypad(True)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def display(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()
        dashboard = True
        last_selection = 0

        f_stop = threading.Event()
        # self.mainscreen.load_ostack_tables(f_stop)

        while True:
            try:
                menu_height, menu_width = self.mainscreen.menuwin_cords[:2]
                self.window.refresh()
                # curses.doupdate()
                # LOG.debug(f"---------CORDS-------------")
                # LOG.debug(f"MAIN:         {self.mainscreen.lines} X {self.mainscreen.cols}")
                # LOG.debug(f"MENU:         {self.mainscreen.menuwin_cords}")
                # LOG.debug(f"MENU CONTENT: {self.cords}")
                # LOG.debug(f"DISP:         {self.mainscreen.dispwin_cords}")
                # LOG.debug(f"CONTENT:      {self.contentwin_cords}")
                startx = 1

                LOG.info("Displaying menu options")
                for index, item in enumerate(self.items[:menu_height]):
                    msg = f"{index}. {item}"
                    if index >= len(self.items) - 2:
                        startx = self.cords[1] // 2 - 3
                        msg = f"{item}"

                    if index == self.position:
                        mode = curses.A_REVERSE
                    elif index == len(self.items) - 1:
                        mode = curses.A_NORMAL | curses.color_pair(COLOR_RED_BLACK)
                    elif index == len(self.items) - 2:
                        mode = curses.A_NORMAL | curses.color_pair(COLOR_GREEN_BLACK)
                    else:
                        mode = curses.A_NORMAL

                    self.window.addstr(1 + index, startx, msg[:menu_width - 4], mode)

                # display dashboard on first load without user input.
                if dashboard:
                    LOG.info("Loading dashboard for the first time")
                    # time.sleep(1)
                    self.dashbord()
                    dashboard = False

                LOG.info("Waiting for user intervention")
                key = self.window.getch()

                if key in [curses.KEY_ENTER, ord('\n')]:
                    LOG.info(f"Selected table: {self.position}")

                    # user may navigate up and down, but we still need to save the
                    # choosen window.
                    self.curr_selection = self.position
                    startx = 1

                    # just make the choosen option yellow. This will be shown only if
                    # the contents are more than one page.
                    msg = f"{self.curr_selection}. {self.items[self.curr_selection]}"
                    if self.position >= len(self.items) - 2:
                        startx = self.cords[1] // 2 - 3
                        msg = f"{self.items[self.curr_selection]}"

                    self.window.addstr(1 + self.curr_selection, startx, msg[:menu_width - 4],
                                       curses.color_pair(COLOR_YELLOW_BLACK))

                    # handle quit and help selections.
                    if self.position == len(self.items) - 1:
                        if self.help_or_quit(last_selection, OPT_QUIT) == OPT_BREAK:
                            f_stop.set()
                            sys.exit(1)
                            break
                    elif self.position == len(self.items) - 2:
                        GlobalVars.help_or_quit = True
                        self.help_or_quit(last_selection, OPT_HELP)

                    self.key_press_operation()

                elif key == curses.KEY_UP:
                    self.navigate(-1)

                elif key == curses.KEY_DOWN:
                    self.navigate(1)

                elif key == ord('r') or key == ord('R'):
                    GlobalVars.reload_requested = True
                    self.reload_data()

                elif key == ord('q') or key == ord('Q'):
                    self.position = len(self.items) - 1

                elif key == ord('h') or key == ord('H'):
                    self.position = len(self.items) - 2

                elif key == ord('c') or key == ord('C'):
                    self.quit = False
                    self.window.clear()

                elif key in self.asciinums:
                    self.position = key - 48

                elif key == curses.KEY_RESIZE:
                    LOG.info(f"Window Resized")
                    self.resize_window()

                # these global variables are set by the Scrollwindow. This is to
                # handle 'resize' and 'reload' requests while scrolling.

                if GlobalVars.resize_detected:
                    GlobalVars.resize_detected = False
                    self.resize_window()

                if GlobalVars.reload_requested:
                    self.key_press_operation()
                    GlobalVars.reload_requested = False
                    self.reload_data()

                last_selection = self.curr_selection

            except Exception as excp:
                LOG.info(f"Exception in Menu Navigation: {str(excp)}")
                return None

        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    def reload_data(self):
        try:
            if self.curr_selection == 0 or self.position == 0:
                GlobalVars.dash_reload['1'] = False
                GlobalVars.dash_reload['5'] = False

            self.show_loading_bar(self.position, LOAD_BAR, 1, 1)

            if self.position == 0:
                tids = []
                rtable = self.mainscreen.os_tables.get(1)
                if not rtable.reloading:
                    rtable.reloading = True
                    tids.append(1)
                else:
                    LOG.info(f"Already a reload in progress. Ignoring table 1 reload")

                rtable = self.mainscreen.os_tables.get(5)
                if not rtable.reloading:
                    rtable.reloading = True
                    tids.append(5)
                else:
                    LOG.info(f"Already a reload in progress. Ignoring table 5 reload")

            else:
                rtable = self.mainscreen.os_tables.get(self.position)
                if rtable.reloading:
                    LOG.info(f"Already a reload in progress. Ignoring table {self.position} reload")
                    return None

                rtable.reloading = True
                tids = [self.position]

            processor = OStackStatusProcessor(tids, self.mainscreen)
            processor.process()
        except Exception as excp:
            LOG.error(f"Exception in reloading. {str(excp)}")
        return None

    def resize_window(self):
        try:
            # these two lines are required to change curses.LINES and COLS.
            y, x = self.mainscreen.origin.getmaxyx()
            curses.resize_term(y, x)

            self.window.clear()
            self.mainscreen.origin.clear()
            self.mainscreen.dispwin.clear()
            self.mainscreen.menuwin.clear()
            self.mainscreen.footerwin.clear()

            curses.doupdate()
            cords = self.mainscreen.config_main_windows()
            self.cords = cords
            self.mainscreen.update_menudriver()

            LOG.info(f"new cords: {cords}")

            # Update changes in all windows
            self.dispwin = self.mainscreen.dispwin
            self.contentwin_cords = self.mainscreen.scrollwin_cords
            self.menuwin = self.mainscreen.menuwin
            self.menuwin_cords = self.mainscreen.menuwin_cords

            LOG.debug(f"---------CORDS AFTER-------------")
            LOG.debug(f"MAIN:         {self.mainscreen.lines} X {self.mainscreen.cols}")
            LOG.debug(f"MENU:         {self.mainscreen.menuwin_cords}")
            LOG.debug(f"MENU CONTENT: {self.cords}")
            LOG.debug(f"DISP:         {self.mainscreen.dispwin_cords}")
            LOG.debug(f"CONTENT:      {self.contentwin_cords}")
            if cords:
                self.init_win_panels(*cords)
                GlobalVars.NEW_LOAD = True
                self.key_press_operation()
                self.mainscreen.menuwin.refresh()
        except Exception as excp:
            LOG.error(f"Exception is processing resize request: {str(excp)}")

        return None

    def any_ready(self):
        try:
            for table in [1, 5]:
                table_obj = self.mainscreen.os_tables.get(table)
                if table_obj is None:
                    return False
                if table_obj.loaded_values:
                    return True
        except Exception as excp:
            LOG.info(f"Exception in checking any ready. {str(excp)}")
            return False
        return False

    def observer(self, table):
        LOG.info(f"Table {table} updated.Observer called. position= {self.position}")
        GlobalVars.NEW_LOAD = True
        if self.curr_selection == 0:
            if table == 1 or table == 5:
                self.dashbord()
        elif self.position in range(1, 9):
            if table == self.position:
                self.key_press_operation()

    def show_loading_bar(self, tid, msg, ystart, xstart):
        try:
            self.mainscreen.dispwin.addstr(ystart, xstart,
                                           msg, curses.color_pair(COLOR_YELLOW_BLACK))
            self.mainscreen.dispwin.refresh()
        except Exception as excp:
            LOG.error(f"Exception in showing loading bar. {str(excp)}")
        return None

    def key_press_operation(self):
        # display loading bar if the data requested is in loading in the background.
        try:
            tab = self.mainscreen.os_tables.get(self.curr_selection)
            disp_len = self.mainscreen.dispwin_cords[1] - 4

            if tab:
                tablename = f"{tab.name.upper()}{' ' * (30 - len(tab.name))}"
                self.show_loading_bar(self.curr_selection, tablename[:disp_len], 3, 4)

                if tab.reload_started:
                    self.show_loading_bar(self.curr_selection, LOAD_BAR, 1, 1)
                else:
                    if self.curr_selection == 0:
                        if GlobalVars.dash_reload['1'] and GlobalVars.dash_reload['5']:
                            LOG.debug(f"erase bars: {GlobalVars}")
                            self.show_loading_bar(self.curr_selection, f"{' ' * len(LOAD_BAR)}", 1, 1)
                        else:
                            self.show_loading_bar(self.curr_selection, LOAD_BAR, 1, 1)
                    else:
                        self.show_loading_bar(self.curr_selection, f"{' ' * len(LOAD_BAR)}", 1, 1)
                        LOG.info(f"erase bars..")

        except Exception as excp:
            LOG.error(f"Exception in loading bars: {str(excp)}")

        # Display dashboard
        try:
            if self.curr_selection == 0:
                if self.any_ready():
                    self.display_time_updated(GlobalVars.dashboard_updated_at)
                    self.dashbord()
                else:
                    input_list = [f"BIG Loading... Dashboard"]
                    LOG.debug("Calling Scroll Window for dashboard")
                    scrollwin = ScrollWindow(input_list, self.window, self.dispwin, *self.contentwin_cords)
                    if scrollwin.window:
                        scrollwin.run()
                    else:
                        LOG.info(f"Window is NULL")
        except Exception as excp:
            LOG.error(f"Exception in displaying dashboard: {str(excp)}")

        # Display other windows as requested
        try:
            item = self.items[self.curr_selection]
            if self.curr_selection in range(1, 9):
                table_obj = self.mainscreen.os_tables.get(self.curr_selection)
                LOG.debug(f"curr_selection = {self.curr_selection}")
                if table_obj is None:
                    LOG.debug(f"table object is NONE. curr_selection = {self.curr_selection}")
                elif table_obj.loaded_values:
                    content = GatherContent(self.mainscreen, self.curr_selection)
                    input_list = content.gather_items_in_a_list()
                    LOG.debug("Calling Scroll Window for specific option")
                    LOG.debug(f"MENU CONT: {self.cords}, DISP CONT: {self.contentwin_cords}")
                    scrollwin = ScrollWindow(input_list, self.window, self.dispwin, *self.contentwin_cords)
                    if scrollwin.window:
                        scrollwin.run()
                    else:
                        LOG.info(f"Window is NULL")

                    if self.curr_selection == 0:
                        updated_time = GlobalVars.dashboard_updated_at
                    else:
                        updated_time = table_obj.updated_at

                    self.display_time_updated(updated_time)

                else:
                    input_list = [f"BIG Loading... {item}"]
                    scrollwin = ScrollWindow(input_list, self.window, self.dispwin, *self.contentwin_cords)
                    if scrollwin.window:
                        scrollwin.run()
                    else:
                        LOG.info(f"Window is NULL")

        except Exception as excp:
            LOG.error(f"Exception in diplaying individual windows: str{excp}")

        return None

    def display_time_updated(self, updated_at):
        text = f"Updated at: {updated_at}"

        try:
            total_len = self.mainscreen.footerwin_cords[1] - 4
            if total_len > len(text):
                LOG.debug(f"ADDSTR 5 {text}")
                self.mainscreen.footerwin.addstr(1, total_len - len(text),
                                                 text, curses.color_pair(COLOR_YELLOW_BLACK))
                self.mainscreen.footerwin.refresh()
        except Exception as excp:
            LOG.error(f"Exception in displaying time. {str(excp)}")

        return None

    def put_help_contents(self, help_win):
        try:
            help_win.addstr(2, 1, "[Q]: Quit    [Esc]: Exit scroll", curses.color_pair(COLOR_GREEN_BLACK))
            help_win.addstr(3, 1, "[H]: Help    [Enter]: Select", curses.color_pair(COLOR_GREEN_BLACK))
            help_win.addstr(4, 1, "[R]: Reload  [UP/DOWN]: Scroll", curses.color_pair(COLOR_GREEN_BLACK))
            help_win.addstr(5, 1, "[0-9]: Jump  [LEFT/DOWN]: Paging", curses.color_pair(COLOR_GREEN_BLACK))
            help_win.addstr(7, 1, "Press Enter to close this window", curses.color_pair(COLOR_YELLOW_BLACK))
        except Exception as excp:
            LOG.error(f"can't put help info: {str(excp)}")
        return None

    def put_quit_contents(self, win, mid):
        try:
            win.addstr(2, (mid - 3), "Quit?", curses.color_pair(COLOR_RED_BLACK))
            win.addstr(4, (mid - 8), "[Y] Yes  [N] No", curses.color_pair(COLOR_YELLOW_BLACK))
            win.addstr(5, (mid - 10), "[Enter your option]", curses.color_pair(COLOR_WHITE_BLACK))
        except Exception as excp:
            LOG.error(f"can't put quit info: {str(excp)}")
        return None

    def help_or_quit(self, last_selection, operation):
        temp_ht, temp_wd, tempy, tempx = self.mainscreen.dispwin_cords

        try:
            ystart = tempy + temp_ht // 2 - 4
            xstart = tempx + temp_wd // 2 - 18
            win_cords = (9, 36, ystart, xstart)

            win = self.mainscreen.dispwin.subwin(*win_cords)
            win.clear()
            win.box()
            if operation == OPT_HELP:
                self.put_help_contents(win)
            elif operation == OPT_QUIT:
                self.put_quit_contents(win, 18)

            GlobalVars.help_or_quit = True

            win.refresh()
            option = win.getch()

            if operation == OPT_QUIT:
                if option == ord('y') or option == ord('Y'):
                    return OPT_BREAK
                else:
                    pass

            win.clear()
            win.refresh()
            self.window.refresh()
            self.curr_selection = last_selection
            self.position = last_selection
            GlobalVars.backfromhelp = True
            self.key_press_operation()

        except Exception as excp:
            LOG.debug(f"Unable to display HELP: {str(excp)}")

    def dashbord(self):
        input_lines = []
        blank_line = self.blankline
        input_lines.append(blank_line)

        try:
            table_obj = self.mainscreen.os_tables.get(1)
            if table_obj:
                LOG.info(f"services object found")
                services = table_obj
                up_count = {}
                down_count = {}
                LOG.info(f"services loaded: {services.loaded_values}")
                if services.loaded_values:
                    if GlobalVars.dash_reload['1'] and GlobalVars.dash_reload['5']:
                        self.show_loading_bar(self.position, f"{' ' * len(LOAD_BAR)}", 1, 1)

                    content = GatherContent(self.mainscreen, 1)
                    pattern = re.compile(r'(\w+)\s+[\w\-]+\s+([\w\d]+)')
                    input_list = content.gather_items_in_a_list()
                    for line in input_list:
                        match = pattern.search(line)
                        if match:
                            service, status = match.group(1).strip(), match.group(2).strip()
                            if status == 'active':
                                if up_count.get(service):
                                    up_count[service] += 1
                                else:
                                    up_count[service] = 1
                            else:
                                if down_count.get(service):
                                    down_count[service] += 1
                                else:
                                    down_count[service] = 1

                    serv_list = ['Nova', 'Glance', 'Keystone', 'Horizon', 'neutron',
                                 'Cinder', 'Ceilometer', 'Heat', 'Support']
                    max_total = 0
                    for item in serv_list:
                        total = up_count.get(item, 0) + down_count.get(item, 0)
                        if total > max_total:
                            max_total = total

                    barlen = self.contentwin_cords[1] // 5
                    input_lines.append(f"BAR Nova {barlen} {up_count.get('Nova', 0)}"
                                       f" {down_count.get('Nova', 0)} {max_total}")
                    input_lines.append(f"BAR Glance {barlen} {up_count.get('Glance', 0)}"
                                       f" {down_count.get('Glance', 0)} {max_total}")
                    input_lines.append(f"BAR Keystone {barlen} {up_count.get('Keystone', 0)}"
                                       f" {down_count.get('Keystone', 0)} {max_total}")
                    input_lines.append(f"BAR Horizon {barlen} {up_count.get('Horizon', 0)}"
                                       f" {down_count.get('Horizon', 0)} {max_total}")
                    input_lines.append(f"BAR neutron {barlen} {up_count.get('neutron', 0)}"
                                       f" {down_count.get('neutron', 0)} {max_total}")
                    input_lines.append(f"BAR Cinder {barlen} {up_count.get('Cinder', 0)}"
                                       f" {down_count.get('Cinder', 0)} {max_total}")
                    input_lines.append(f"BAR Ceilometer {barlen} {up_count.get('Ceilometer', 0)}"
                                       f" {down_count.get('Ceilometer', 0)} {max_total}")
                    input_lines.append(f"BAR Heat {barlen} {up_count.get('Heat', 0)}"
                                       f" {down_count.get('Heat', 0)} {max_total}")
                    input_lines.append(f"BAR Support {barlen} {up_count.get('Support', 0)}"
                                       f" {down_count.get('Support', 0)} {max_total}")
                else:
                    self.show_loading_bar(self.position, LOAD_BAR.replace('Updat', 'Load'), 1, 1)
                    self.add_blank_line(input_lines, 9)

            self.add_blank_line(input_lines, 2)

        except Exception as excp:
            LOG.error(f"Exception in displaying service data: {str(excp)}")

        try:
            table_obj = self.mainscreen.os_tables.get(5)
            if table_obj:
                if table_obj.loaded_values:
                    ceph = CephStatus()
                    ceph.update_ceph_status()
                    ceph_status = f"Overall status: {ceph.health}"
                    ceph_osds = ceph.osd_status.get('osds')
                    ceph_osds_up = ceph.osd_status.get("up", 0)
                    ceph_osds_in = ceph.osd_status.get("in", 0)
                    ceph_osds_down = ceph.osd_status.get("down", 0)
                    ceph_osds_out = ceph.osd_status.get("out", 0)
                    ceph_capacity_total, unit = ceph.total_capacity.split()
                    LOG.info(f"total: {ceph_capacity_total} {unit}, {MULT_FACTOR.get(unit, 1)}")
                    ceph_capacity_total = int(ceph_capacity_total) / MULT_FACTOR.get(unit, 1)
                    ceph_capacity_used, unit = ceph.used_capacity.split()
                    LOG.info(f"used: {ceph_capacity_used} {unit}, {MULT_FACTOR.get(unit, 1)}")
                    ceph_capacity_used = int(ceph_capacity_used) / MULT_FACTOR.get(unit, 1)
                    ceph_capacity_avail, unit = ceph.available_capacity.split()
                    LOG.info(f"avail: {ceph_capacity_avail} {unit}, {MULT_FACTOR.get(unit, 1)}")
                    ceph_capacity_avail = int(ceph_capacity_avail) / MULT_FACTOR.get(unit, 1)

                    ceph_monitors = ceph.monitors
                    ceph_placement_groups = ceph.pgs
                    ceph_pg_status = ceph.pg_status
                    ceph_pools = ceph.pools

                    ceph_text_section = self.contentwin_cords[1] // 2 - 2
                    ceph_storage_rect = (self.contentwin_cords[1] - ceph_text_section) // 2 - 2
                    used = int((ceph_capacity_used / ceph_capacity_total) * ceph_storage_rect)
                    if used == 0:
                        used = 1
                    avail = ceph_storage_rect - used
                    LOG.debug(f"total: {ceph_capacity_total}, {used} {avail}")
                    input_lines.append(f"LINE 2 {ceph_text_section}")
                    input_lines.append(f"CEPH STATUS")
                    input_lines.append(blank_line)
                    input_lines.append(f"{ceph_status}{' ' * (ceph_text_section - len(ceph_status))}"
                                       f"Total Capacity: {ceph.total_capacity}")
                    input_lines.append(blank_line)
                    text = f"OSDs: {ceph_osds}"
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}{'-' * used}{'.' * avail}")
                    text = ' '
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}{'-' * used}{'.' * avail}")
                    text = f"OSDs UP:   ==> {ceph_osds_up}"
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}{'-' * used}{'.' * avail}")
                    text = f"OSDs IN:   ==> {ceph_osds_in}"
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}{'-' * used}{'.' * avail}")
                    text = f"OSDs DOWN: ==> {ceph_osds_down}"
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}{'-' * used}{'.' * avail}")
                    text = f"OSDs OUT:  ==> {ceph_osds_out}"
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}{'-' * used}{'.' * avail}")
                    text = ' '
                    input_lines.append(f"{text}{' ' * (ceph_text_section - len(text))}Used: {ceph.used_capacity}")
                    text = ' '
                    input_lines.append(
                        f"{text}{' ' * (ceph_text_section - len(text))}Available: {ceph.available_capacity}")

                    input_lines.append(blank_line)
                    input_lines.append(blank_line)
                    input_lines.append(f"ceph monitors:         {ceph_monitors}")
                    input_lines.append(f"ceph placement groups: {ceph_placement_groups}")
                    input_lines.append(f"ceph pg status:        {ceph_pg_status}")
                    input_lines.append(f"ceph pools:            {ceph_pools}")

            input_lines.append(f"LINE 2 {ceph_text_section + ceph_storage_rect}")
            input_lines.append(blank_line)

        except Exception as excp:
            LOG.error(f"Exception in displaying CEPH status: {str(excp)}")

        LOG.debug("Calling Scroll Window on DashBoard")

        scrollwin = ScrollWindow(input_lines, self.window, self.dispwin, *self.contentwin_cords)
        if scrollwin.window:
            scrollwin.run()
        else:
            LOG.info(f"Window is NULL")

        self.window.refresh()

    def add_blank_line(self, input_lines, count):
        for x in range(count):
            input_lines.append(self.blankline)


class MainDriver:
    """
    Main Class.
    This class keeps the variables and methods which are required
    at any time globally.

    self.os_tables: cache the data to be displayed. Each window has an entry in this dict.
    self.origin: main curses window, which is divided into menu and display in 1:6 ratio.
    """

    MENU_DISP_RATIO = 6
    TEXT_MENU = "MENU"
    TEXT_HEADER = "OPENSTACK MONITOR"
    TEXT_FOOTER = "'Q': Quit |'Esc': Exit scroll window |'R': Reload " \
                  "|'Arrows': Scroll/Paging"
    HEIGHT_MINI_WIN = 3
    WIDTH_BORDER = 1
    BORDER_SPACE = 2
    # Minimum dimensions required.
    MIN_HEIGHT_MAIN = 25
    MIN_WIDTH_MAIN = 80

    def __init__(self, stdscr):
        """ Initialize main template windows"""

        self.origin = stdscr
        self.lines = 0
        self.cols = 0
        self.height_menu = 0
        self.height_disp = 0
        self.width_menu = 0
        self.width_disp = 0
        self.os_tables = {}
        self.menuwin_cords = ()
        self.menuwin = None
        self.dispwin_cords = ()
        self.dispwin = None
        self.footerwin_cords = ()
        self.footerwin = None
        self.menudriver = None

        if self.import_configs() is None:
            LOG.info("Config file not found or incorrect")
            return None

        self.publisher = Publisher(0)
        self.init_curses()


        # Invoke MENU options on menuwindow
        menu_cords = self.config_main_windows()
        if menu_cords is None:
            LOG.info("Cound not configure windows")
            return None

        if self.check_connection() == False:
            return None

        # Create menu driver object running which invokes all contents
        self.menudriver = MenuDriver(MENU, self, *menu_cords)
        # Add observer class so that upon updating os_table, this function will get called.
        self.publisher.add_subscriber(self.menudriver.observer)
        self.publisher.disp_subscribers()

        # Load the contents to os_tables for the first time. This is the cache.
        self.initialize_ostack_tables()
        # Run the menudirver object.
        self.invoke_menu()

    def invoke_menu(self):
        LOG.info(f"Invoking main menu. starting display.")
        self.menudriver.display()

    def load_ostack_tables(self, f_stop):
        LOG.info("reloading tables..")
        tables = list(range(1, 9))

        try:
            processor = OStackStatusProcessor(tables, self)
            processor.process()

        except KeyboardInterrupt:
            curses.endwin()
            LOG.info("Keyboard Interrupt")
            sys.exit(1)

        except Exception as excp:
            LOG.error(f"Exception in loading tables: {str(excp)}")

        if not f_stop.is_set():
            threading.Timer(120.0, self.load_ostack_tables, [f_stop]).start()

    def initialize_ostack_tables(self):
        # cache all the data in the os_table on first run.

        LOG.info(f"Initializing ostack tables")

        # initialize dashboard ('0')
        self.os_tables[0] = OStackTable(0)
        tables = list(range(1, 9))

        for tid in tables:
            self.os_tables[tid] = OStackTable(tid)

        try:
            processor = OStackStatusProcessor(tables, self)
            processor.process()

        except KeyboardInterrupt:
            curses.endwin()
            LOG.info("Keyboard Interrupt")
            sys.exit(1)

        except Exception as excp:
            LOG.error(f"Exception in Initializing tables: {str(excp)}")
            return None

        # for tid in tables:
        #     self.os_tables[tid].disp_details()

        return self.os_tables

    def init_curses(self):
        # configure curses here.
        try:
            curses.curs_set(0)
            curses.start_color()

            # (pair_number, fg, bg)
            curses.init_pair(COLOR_WHITE_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(COLOR_BLACK_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(COLOR_RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(COLOR_GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(COLOR_YELLOW_BLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(COLOR_CYAN_BLACK, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(COLOR_CYAN_CYAN, curses.COLOR_CYAN, curses.COLOR_CYAN)
            curses.init_pair(COLOR_BLACK_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(COLOR_MAGENTA_BLACK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(COLOR_BLACK_RED, curses.COLOR_BLACK, curses.COLOR_RED)
            curses.init_pair(COLOR_BLACK_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)
            curses.init_pair(COLOR_BLACK_MAGENTA, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        except Exception as excp:
            LOG.error(f"Exception in initializing curses. {str(excp)}")
            return None

    def import_configs(self):

        creds = {}
        item_no = 1
        cfgfile = pathlib.Path(CONFIG_FILE_NAME)
        if (not cfgfile.exists() or
            not cfgfile.is_file()):
            LOG.error(f"Config file {CONFIG_FILE_NAME} does not exists")
            return None

        filepath = f"{pathlib.Path(__file__).parent.absolute()}/{CONFIG_FILE_NAME}"
        with open(filepath, 'r') as f:
            line = f.readline()
            while line:
                arr = [x.strip() for x in line.split('=')]
                LOG.info(f"arr: {arr}")
                if len(arr) == 2:
                    creds[str(arr[0])] = str(arr[1])
                elif len(arr) == 1:
                    creds[str(arr[0])] = None
                else:
                    pass
                line = f.readline()
                item_no += 1
                if item_no > 50:
                    LOG.debug(f"config has more entries")
                    break

        LOG.info(f"creds: {creds}")

        GlobalVars.OSTACK_SERV_IP = creds.get('OSTACK_SERV_IP')
        GlobalVars.OSTACK_USER = creds.get('OSTACK_USER')
        GlobalVars.OSTACK_SECRET = creds.get('OSTACK_SECRET')

        LOG.debug(f"IP: {GlobalVars.OSTACK_SERV_IP}, USER: {GlobalVars.OSTACK_USER}")

        if (GlobalVars.OSTACK_SERV_IP is None or
            GlobalVars.OSTACK_USER is None):
            LOG.info(f"no user or ip provided")
            return None

        return creds


    def pop_up_window(self, message, color):
        cords = (curses.LINES, curses.COLS, 1, 1)
        try:
            popup = curses.newwin(*cords)

            message = message[:curses.COLS - 2]

            popup.addstr((curses.LINES // 2) + 1, (curses.COLS - len(message)) // 2, message,
                         curses.color_pair(color))
            popup.noutrefresh()
            curses.doupdate()
            key = popup.getch()
            return key
        except Exception as excp:
            LOG.debug(f"LINES: {curses.LINES }, COLS: {curses.COLS} ")
            LOG.error(f"Pop up window crashed: {str(excp)}")
            return None

    def config_main_windows(self):

        LOG.info("Configuring Windows")
        main_dim = (curses.LINES, curses.COLS)

        try:
            size_ok = self.minimum_win_size(main_dim)
            while not size_ok:
                message = f"Minimum screen size is {self.MIN_HEIGHT_MAIN} X {self.MIN_WIDTH_MAIN}. Increase window"
                LOG.info(message)
                key = self.pop_up_window(message, COLOR_WHITE_BLACK)
                if key is None:
                    break
                elif key == curses.KEY_RESIZE:
                    y, x = self.origin.getmaxyx()
                    curses.resize_term(y, x)
                    main_dim = (curses.LINES, curses.COLS)
                    size_ok = self.minimum_win_size(main_dim)
        except Exception as excp:
            LOG.error(f"Exception in resizing window: {str(excp)}")
            return None

        try:
            self.lines = curses.LINES
            self.cols = curses.COLS
            self.height_menu = self.lines - self.HEIGHT_MINI_WIN - (2 * self.WIDTH_BORDER)
            self.height_disp = self.height_menu
            self.width_menu = (self.cols // self.MENU_DISP_RATIO) + (self.MENU_DISP_RATIO // 2) - (2 * self.WIDTH_BORDER)
            self.width_disp = self.cols - self.width_menu - (3 * self.WIDTH_BORDER)

            # create two curses windows. One for menu and one to display contents.
            self.menuwin_cords = (self.height_menu,
                                  self.width_menu,
                                  self.WIDTH_BORDER,
                                  self.WIDTH_BORDER)

            self.dispwin_cords = (self.height_disp,
                                  self.width_disp,
                                  self.WIDTH_BORDER,
                                  self.width_menu + self.WIDTH_BORDER * 2)

            self.footerwin_cords = (self.HEIGHT_MINI_WIN,
                                    self.width_menu + self.width_disp + self.WIDTH_BORDER,
                                    self.height_menu + self.WIDTH_BORDER,
                                    self.WIDTH_BORDER)

            ht, wd, ystart, xstart = self.dispwin_cords
            self.scrollwin_cords = (ht - 6, wd - 5, ystart + 5, xstart + 2)

        except Exception as excp:
            LOG.error(f"exception is configuring cordinates: {str(excp)}")
            return None

        try:
            self.menuwin = curses.newwin(*self.menuwin_cords)
            self.dispwin = curses.newwin(*self.dispwin_cords)
            self.footerwin = curses.newwin(*self.footerwin_cords)

            self.init_window(self.menuwin)
            self.init_window(self.dispwin)
            self.init_window(self.footerwin)
        except Exception as excp:
            LOG.info(f"Exception in configuring window screens: {str(excp)}")
            # self.pop_up_window(str(excp), COLOR_RED_BLACK)
            return None

        try:
            LOG.debug(f"ADDSTR 8 : {self.TEXT_MENU}")
            self.menuwin.addstr(1, (self.width_menu - len(self.TEXT_MENU)) // 2, self.TEXT_MENU)
            self.dispwin.addstr(1, (self.width_disp - len(self.TEXT_HEADER)) // 2, self.TEXT_HEADER)

            foot_width = self.footerwin_cords[1] - self.WIDTH_BORDER * 2
            self.footerwin.addstr(1, 1, self.TEXT_FOOTER[:foot_width])

            if foot_width > 3:
                self.footerwin.chgat(1, 2, 1, curses.A_BOLD | curses.color_pair(COLOR_RED_BLACK))
            if foot_width > 16:
                self.footerwin.chgat(1, 13, 3, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))
            if foot_width > 41:
                self.footerwin.chgat(1, 40, 1, curses.A_BOLD | curses.color_pair(COLOR_RED_BLACK))
            if foot_width > 60:
                self.footerwin.chgat(1, 53, 6, curses.A_BOLD | curses.color_pair(COLOR_GREEN_BLACK))

        except Exception as excp:
            LOG.info(f"Exception in adding strings: {str(excp)}")
            # self.pop_up_window(str(excp))
            return None

        # Refresh the windows.
        try:
            self.origin.noutrefresh()
            self.menuwin.noutrefresh()
            self.dispwin.noutrefresh()
            self.footerwin.noutrefresh()
            curses.doupdate()
        except Exception as excp:
            LOG.info(f"Exception in refreshing screens. {str(excp)}")
            # self.pop_up_window(str(excp))
            return None

        # MENU CONTENT WINDOW----

        try:
            # -1: Heading
            max_menu_height = self.menuwin_cords[0] - self.BORDER_SPACE - 1
            # 2: 'exit' and 'help'
            menu_ht = min(len(MENU) + 2 + self.BORDER_SPACE, max_menu_height)

            menu_wd = max(self.width_menu - self.BORDER_SPACE, 5)
            menu_ystart = (self.height_menu - menu_ht) // 2
            menu_xstart = self.BORDER_SPACE

            menu_cords = (menu_ht - 1,
                          menu_wd - 1,
                          menu_ystart,
                          menu_xstart)

            LOG.info(f"MENU CORDS: {menu_cords}")

        except Exception as excp:
            LOG.error(f"Exception in configuring menu cords: {str(excp)}")
            return None

        return menu_cords

    def update_menudriver(self):
        self.menudriver.mainscreen = self

    def minimum_win_size(self, main):
        LOG.debug(f"Dimension: Main: {main}")
        if main:
            LOG.debug(f"LIMIT MAIN: {self.MIN_HEIGHT_MAIN}, {self.MIN_WIDTH_MAIN}")
            height, width = main[0], main[1]
            if (height < self.MIN_HEIGHT_MAIN or
                    width < self.MIN_WIDTH_MAIN):
                return False
        return True

    def check_connection(self):
        env_kwargs = {'password': GlobalVars.OSTACK_SECRET,
                      'timeout': 60}
        try:
            if GlobalVars.OSTACK_SECRET:
                conn = Connection(GlobalVars.OSTACK_SERV_IP,
                                  user=GlobalVars.OSTACK_USER,
                                  connect_kwargs=env_kwargs)
            else:
                conn = Connection(GlobalVars.OSTACK_SERV_IP,
                                  user=GlobalVars.OSTACK_USER)
            return True
        except Exception as excp:
            msg = f"{str(excp)}"
            LOG.info(f"Unable to reach server {msg}-{GlobalVars.OSTACK_USER}@{GlobalVars.OSTACK_SERV_IP}")
            self.pop_up_window(msg, COLOR_RED_BLACK)
            return False
        finally:
            conn.close()

    def init_window(self, win):
        try:
            win.keypad(True)
            win.box()
        except Exception as excp:
            LOG.error(f"Exception in drawing box.{str(excp)}")
        return None


def main():
    curses.wrapper(MainDriver)


if __name__ == '__main__':
    main()
