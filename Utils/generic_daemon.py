import sys
import os
import time
import atexit
import signal
from fastvrpdlogging import logger

class Daemon:
    """
    A generic daemon class.
    Usage: subclass the daemon class and override the run() method.
    """
    
    def __init__(self, pidfile):
        self.pidfile = pidfile
    
    def daemonize(self):
        """
        Deamonize class. UNIX double fork mechanism. i.e. create a grand
        child and exit it's parent. This makes the grand child an orphan
        and get it adopted by init process. Exit the grand parent as well
        as it is no longer required.
        """
        
        logger.info("Daemonizing.")
        
        try:
            # Create the first child.
            pid = os.fork()
            if pid > 0:
                # Exit first parent.
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #1 failed: {err}\n")
            sys.exit(1)
        
        # Decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)
        
        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #2 failed: {err}\n")
            sys.exit(1)
        
        # Redirect standard file descriptors to null device[/dev/null]
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Create file descriptors with null device.
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        
        # Duplicate the standard file descriptors using the descriptors
        # created above so that stdin, stdout, and stderr outputs will 
        # be silently discarded as they are writing to null device.
        
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        atexit.register(self.delete_pid)
        
        pid = str(os.getpid())
        
        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n')
            
    def delete_pid(self):
        os.remove(self.pidfile)
        
    def start(self):
        """
        Start the daemon.
        """
        
        # Check for a pidfile to see if the daemon already runs
        logger.info("check for a pidfile to see if the daemon already runs")
        
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
            
        if pid:
            message = f"pidfile {self.pidfile} already exist. " \
                       "Daemon already running?"
            sys.stderr.write(message)
            logger.info(message)
            sys.exit(1)
        
        # Start the daemon
        logger.info("Starting daemon.")
        self.daemonize()
        self.run()
        
    def stop(self):
        """
        Stop the daemon.
        """
        
        # Get the pid from the pidfile
        logger.info("Stopping daemon.")
        
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
            
        if not pid:
            message = f"pidfile {self.pidfile} does not exist. " \
                      "Daemon not running?\n"
            
            sys.stderr.write(message)
            logger.info(message)
            return None
    
    
        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                logger.error("No such process")
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                logger.error(str(err.args))
                sys.exit(1)
            
    
    def restart(self):
        """
        Restart the daemon.
        """
        
        self.stop()
        self.start()
        
    
    def run(self):
        """
        Override this method when you subclass Daemon.
        It will be called after the process has been daemonized by
        start() or restart().
        """

        
def get_arg_parser():
    """
    Argument parser for the command-line entry.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--command",
        choices=("start", "restart", "stop"),
        help="Deamon management command.",
    )
    return parser

class MyDaemon(Daemon):
    def run(self):
        while True:
            sleep(10)
            processing_logic()
            
def main():
    print("Starting")
    args = get_arg_parser().parse_args()
    print(f"Command: {args.command}")
    
    daemon = FastDaemon(config.PID_FILE_PATH)
    
    if (args.command == "start"):
        daemon.start()
    elif (args.command == "stop"):
        daemon.stop()
    elif (args.command == "restart"):
        daemon.restart()
    else:
        logger.error("Command not recognized")

if __name__ == "__main__":
    main()            
