import json
import os
import subprocess
import math
import itertools
import threading
import time
import sys
import shutil

'''
Backup loading configuration
'''
class Configuration:
    @staticmethod
    def get():
        return {
            "file": "backupOptions.json"
        }

'''
Disk operations utils
'''
class Disk:

    # Gets all files at a specified base_path.
    # If its a file, then it is returned as is in a list.
    # @param    String      A string path
    # @return   List        Returns a list of files present at 
    #                       the specified path
    @staticmethod
    def get_all_files(base_path):
        if os.path.isfile(base_path):
            return [base_path]

        output_files = []
        for root, dirs, files in os.walk(base_path):
            for each_file in files:
                output_files.append(os.path.join(root, each_file))
        return output_files

    # Gets the size in bytes for a file or a list of files
    # @param    String|List     A file path or list of file paths
    # @return   int             Size in bytes
    @staticmethod
    def get_size(path):
        if type(path) is not list:
            path = [path]
        tot_size_by = 0
        for each_path in path:
            fs_data = os.stat(each_path)
            tot_size_by = tot_size_by + fs_data.st_size
        return tot_size_by

    # Returns all files on all the add paths excluding
    # files present at/under exclude paths
    # @param    List    A list of paths to be included
    # @param    List    A list of paths to be excluded
    @staticmethod
    def get_all_paths(add=[], exclude=[]):
        i = 0
        while i < max(len(add), len(exclude)):
            if i < len(add) and add[-1] == "/":
                add = add[:-1]
            if i < len(exclude) and exclude[-1] == "/":
                exclude[i] = exclude[:-1]
            i = i + 1

        unique_files_add = {}
        add_files = []
        exclude_files = []
        for i in add:
            add_files = Disk.get_all_files(i)
        for i in exclude:
            exclude_files = Disk.get_all_files(i)

        for i in add_files:
            unique_files_add[i] = True
        for i in exclude_files:
            if i in unique_files_add:
                del unique_files_add[i]
        return unique_files_add.keys()


'''
Utilities to get simple small tasks get done
'''
class Utils:
    animating = False
    Colors = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'NONE': ''
    }

    @staticmethod
    def encapsulate_colors(msg, mode):
        if mode is None:
            mode = "NONE"
        prepend = ""
        parts = mode.split(" ")
        for each_part in parts:
            if each_part in Utils.Colors:
                prepend = prepend + Utils.Colors[each_part] + " "

        return prepend + msg + " " + Utils.Colors['ENDC']

    # Reads a file contents
    # @param    String      A file path to be read
    # @param    Bool        True if to be ready by line | False otherwise
    # @return   String|List File contents
    @staticmethod
    def get_file_contents(file_path, by_line=False):
        contents = ""
        with open(file_path, "r") as f:
            if by_line:
                contents = f.readlines()
            else:
                contents = f.read()
        return contents
    
    # Reads a json file contents
    # @param    String      A json file path to read
    # @return   JSON Obj    File contents
    @staticmethod
    def get_file_json_contents(file_path):
        json_content = {}
        file_content = Utils.get_file_contents(file_path)
        json_content = json.loads(file_content)
        return json_content

    # Logger method for easy future control
    # @param    String      Something to log
    # @param    String      mode from Colors
    @staticmethod
    def log(msg="", mode = None):
        print(Utils.encapsulate_colors(msg, mode))

    # Logger which just adds a new line after the job is done
    # @param    String      Something to log
    # @param    String      mode from Colors
    @staticmethod
    def log_ln(msg="", mode = None):
        Utils.log(msg, mode)
        Utils.log("")

    @staticmethod
    def show_wait(msg):
        Utils.log(msg)
        Utils.animating = True
        threading.Thread(target=Utils.animate)

    @staticmethod
    def done_wait():
        Utils.animating = False

    @staticmethod
    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if Utils.animating == False:
                break
            sys.stdout.write('\r Please wait.. ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
    
    # Gets user input from command line
    # @params   String      A prompt message to show
    # @param    Bool        True if to use raw_input | False for input
    # @return   Mixed       User input via command line
    @staticmethod
    def get_user_input(msg, raw = True):
        if raw:
            return raw_input(msg)
        else:
            return input(msg)

    # Exits the program if True is passed
    # @param    Bool        True if to exit | False otherwise
    @staticmethod
    def exit_if_fail(failed = True):
        if failed:
            sys.exit()


'''
A set of utils for Tabular data (List<List|*>)
'''
class Table:
    
    # Gets the max lengths of all cols
    # @param    Table       A table to be checked
    # @return   List        max lengths of data in each col
    @staticmethod
    def col_max_lengths(tabular_data):
        total_cols = len(tabular_data[0])
        total_rows = len(tabular_data)
        max_lengths = [0 for i in range(0, total_cols)]
        r = 0
        while r < total_rows:
            c = 0
            while c < total_cols:
                max_lengths[c] = max(
                    max_lengths[c], len(str(tabular_data[r][c])))
                c = c + 1
            r = r + 1
        return max_lengths

    # Gets col value in a table
    # @param    Table       The table to be examined
    # @param    int         The row number to be queried
    # @param    String|*    The row which has got this value at col 0
    # @param    int         The col index at the found row
    # @param    Bool        If all occurrences need to be returned
    @staticmethod
    def get_col_val(tabular_data, row_num=None, row_value=None, col_index=1, return_all=False):
        if row_num is not None:
            return tabular_data[row_num][col_index]
        elif row_value is not None:
            if return_all:
                val = []
                for i in len(tabular_data):
                    if i[0] == row_value:
                        val.append(i[col_index])
                return val
            else:
                for i in len(tabular_data):
                    if i[0] == row_value:
                        return i[col_index]
        else:
            return None

    # Prints a taable in a pretty way
    # @param    Table       The table to be printed
    # @param    String      Prefix at the start of each printed line
    # @param    String      Seperator between two cols
    # @param    String      padding between seperator and cell values
    @staticmethod
    def print_tabular(tabular_data, start_prefix="", seperator="|", seperator_pad=" "):
        total_cols = len(tabular_data[0])
        total_rows = len(tabular_data)
        max_lengths = Table.col_max_lengths(tabular_data)
        Utils.log(start_prefix + "".join(
            "-" for _ in range(
                0,
                (total_cols + 1)*(len(seperator) +
                                  len(seperator_pad)) + sum(max_lengths)
            )
        ))
        i = 0
        while i < total_rows:
            j = 0
            while j < total_cols:
                tabular_data[i][j] = str(tabular_data[i][j]) + "".join(
                    [
                        " " for a_space in range(0, max(
                            0, max_lengths[j] - len(str(tabular_data[i][j]))
                        ))
                    ]
                )
                j = j + 1

            op = start_prefix + \
                (seperator + seperator_pad) + \
                (seperator + seperator_pad).join(tabular_data[i]) + \
                (seperator_pad + seperator)
            Utils.log(op)
            i = i + 1
        Utils.log(start_prefix + "".join(
            "-" for _ in range(
                0,
                (total_cols + 1)*(len(seperator) +
                                  len(seperator_pad)) + sum(max_lengths)
            )
        ))


'''
Shell utilities
'''
class Shell:
    # Runs a shell command and gets back any output
    # @param    List    A command broken down into a list
    @staticmethod
    def run(args):
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        return p.communicate()

'''
Volume specific operations and data
holder for respective properties
'''
class Volume:
    # @param    String      The path of volume under scanner
    def __init__(self, path):
        if path is not None:
            self.mount_point = path
            vol_data = Volume.get_stats(path)
            self.load_df_data(vol_data)

    # Loads an file system data into the obj
    def load_df_data(self, fs_data):
        self.block_size = fs_data.f_frsize
        self.free = fs_data.f_bavail
        self.size = fs_data.f_blocks
        self.used = self.size - self.free

    def get_block_size(self):
        return self.block_size

    def get_free(self):
        return self.free * self.block_size

    def get_size(self):
        return self.size * self.block_size

    def get_used(self):
        return self.used * self.block_size

    # Gets the stats at a path
    # @param    String      The path to get the stats for
    @staticmethod
    def get_stats(path):
        vol_data = os.statvfs(path)
        return vol_data
    
    # Converts bytes to GiB data
    # @param    int     Total bytes
    # @param    int     Block size (bytes)
    @staticmethod
    def bytes_to_gb(s_bytes, block_size=1):
        return math.ceil((s_bytes / (1024.0**3))*block_size)

    # Describes a volume object and prints to console
    # @param    obj(Volume)     The object to be described
    # @param    String          A prefix to be accompanied with the op
    @staticmethod
    def desc(volume_obj, prefix=""):
        table = [
            ["Mount Point", volume_obj.mount_point],
            ["Block size (B)", volume_obj.block_size],
            ["Total Size (Gi)", Volume.bytes_to_gb(
                volume_obj.size, volume_obj.block_size)],
            ["Used (Gi)", Volume.bytes_to_gb(
                volume_obj.used, volume_obj.block_size)],
            ["Free (Gi)", Volume.bytes_to_gb(
                volume_obj.free, volume_obj.block_size)],
            ["Free %", "%.2f" % (volume_obj.free * 100.0 / volume_obj.size)]
        ]
        Table.print_tabular(table, prefix)


'''
Backup method creator and manager
'''
class Backup:
    def init(self):
        configuration = Configuration.get()
        backup_config = Utils.get_file_json_contents(configuration["file"])
        self.host_volume_destination = backup_config["recover"]["destination"]
        self.storage_destination = backup_config["storage"]["destination"]
        self.overwrite_method = backup_config["storage"]["overwrite_existing"]
        self.destination_dir = backup_config["storage"]["dir"]
        self.cleanup = backup_config["storage"]["cleanup_copied"]
        self.add_paths = backup_config["add"]
        self.exclude_paths = backup_config["ignore"]
        self.recovery_owner_id = backup_config["recover"]["owner"]
        self.recovery_group_id = backup_config["recover"]["group"]

        # Config load complete
        Utils.log("* Configuration loaded: ")
        Utils.log("\tDestination => " + self.storage_destination)
        Utils.log("\tOverwrite Existing? => " + str(self.overwrite_method))
        Utils.log_ln("\tCleanup copied? => " + str(self.cleanup))
        Utils.log("* Pending actions: ")
        Utils.log("\tPaths to add: " + str(len(self.add_paths)))
        Utils.log_ln("\tExclude Paths: " + str(len(self.exclude_paths)))

    # Loads all volumes and their properties
    # @param    Bool        True if running on create mode |
    #                       False if running on recovery mode
    def load_volumes(self, create = True):
        Utils.log("* Loading volumes: ")
        Utils.log("\t\_ External Volume..")
        self.destination_volume = Volume(self.storage_destination)
        Utils.log("\t\_ Host Volume")
        self.host_volume = Volume(self.host_volume_destination)

        if create:
            Utils.show_wait("\t\_ All files to copy..")
            self.total_add_paths = Disk.get_all_paths(
                self.add_paths, self.exclude_paths)
            Utils.done_wait()
        else:
            Utils.show_wait("\t\_ Files to recover")
            self.total_recover_paths = Disk.get_all_paths(
                [self.storage_destination + "/" + self.destination_dir], []
            )
            Utils.done_wait()
        Utils.log()

    # Checks if disks can accommodate the incoming data.
    # If in create mode, then checks the volume
    # If in recovery mode, checks the running FS from recover
    # @param    Bool        True if running on create mode |
    #                       False if running on recovery mode
    def check_disks(self, create = True):
        Utils.log("* Examining volumes: ")
        Utils.log("\t\_ External volume => ")
        Volume.desc(self.destination_volume, "\t")
        Utils.log("\t\_ Host Volume => ")
        Volume.desc(self.host_volume, "\t")
        can_copy = False
        if create:
            Utils.show_wait("\t\_ Pending files => ")
            pending_file_size = Disk.get_size(self.total_add_paths)
            Utils.log("\tSize (Gi): " +
                    str(Volume.bytes_to_gb(pending_file_size)))
            Utils.done_wait()

            if self.destination_volume.get_free() > pending_file_size:
                Utils.log("\t Sufficient space present.", 'OKGREEN')
                can_copy = True
            else:
                Utils.log("\t Insufficient space on the mounted volume!", 'FAIL')
                can_copy = False
            
        else:
            Utils.show_wait("\t\_ Pending files => ")
            pending_file_size = Disk.get_size(self.total_recover_paths)
            Utils.log("\tSize (Gi): " +
                    str(Volume.bytes_to_gb(pending_file_size)))
            Utils.done_wait()
            if self.host_volume.get_free() > pending_file_size:
                Utils.log("\t Sufficient space present.", 'OKGREEN')
                can_copy = True
            else:
                Utils.log("\t Insufficient space on the host volume!", 'FAIL')
                can_copy = False
            
        Utils.log()
        return can_copy

    # Starts data replication
    # If in create mode, then checks the volume
    # If in recovery mode, checks the running FS from recover
    # @param    Bool        True if the copy is signalled 'go-ahead'
    # @param    Bool        True if running on create mode |
    #                       False if running on recovery mode
    def start_copying(self, can_copy, create = True):
        if not can_copy:
            Utils.log("Aborting copy", "FAIL")
            sys.exit()
        
        Utils.exit_if_fail(
            Utils.get_user_input("** Proceed with copy? (y/Y | * )").lower() != "y"
        )

        if create:
            if os.path.exists(self.storage_destination + "/" + self.destination_dir):
                Utils.log("\tDestination dir already exists..", "WARNING")
                if self.overwrite_method:
                    Utils.log("\t\tRemoving dir by overwrite strategy..", "WARNING")
                    shutil.rmtree(self.storage_destination + "/" + self.destination_dir, ignore_errors=True)
            else:
                Utils.log("\tDestination dir doesnt exist.. Creating one..", "OKBLUE")
                os.makedirs(self.storage_destination + "/" + self.destination_dir)
            
            created_dirs = {}
            Utils.log("* Starting copy...", "OKBLUE")
            base_copy_path = self.storage_destination + "/" + self.destination_dir + "/"
            for each_file in self.total_add_paths:
                Utils.log("\tCopying <== "+each_file, "WARNING")
                dirname = os.path.dirname(each_file)
                cleaned_full_path = base_copy_path + dirname
                cleaned_full_path = cleaned_full_path.replace("//", "/")

                if cleaned_full_path not in created_dirs and not os.path.exists(cleaned_full_path):
                    Utils.log("\t\tCreating subdir: " + cleaned_full_path, "OKBLUE")
                    os.makedirs(cleaned_full_path)
                    created_dirs[cleaned_full_path] = True

                shutil.copy2(each_file, base_copy_path + each_file)
                Utils.log("\tCopied => "+each_file, "OKGREEN")
            
            Utils.log_ln()
            if self.cleanup:
                Utils.log("* Cleanup Strategy.. Clean", "WARNING")
                Utils.log("\tCleaning up files ", "OKWARN")
                for each_file in self.total_add_paths:
                    Utils.log("\t\tDeleting: "+each_file, "FAIL")
                    os.remove(each_file)
            else:
                Utils.log("* Cleanup Strategy.. Ignore", "OKBLUE")
        else:
            created_dirs = {}
            Utils.log("* Starting Recovery...", "OKBLUE")
            for each_file in self.total_recover_paths:
                each_file = each_file.replace("//", "/")
                Utils.log("Copying <== "+each_file, "WARNING")
                dirname = os.path.dirname(each_file)
                dirname = dirname[len((self.storage_destination + "/" + self.destination_dir).replace("//", "/")):]
                cleaned_full_path = self.host_volume_destination + dirname
                cleaned_full_path = cleaned_full_path.replace("//", "/")
                if cleaned_full_path not in created_dirs and not os.path.exists(cleaned_full_path):
                    Utils.log("Creating subdir: " + cleaned_full_path, "OKBLUE")
                    os.makedirs(cleaned_full_path)
                    created_dirs[cleaned_full_path] = True

                shutil.copy2(each_file, cleaned_full_path)
                Shell.run(["chown", self.recovery_owner_id+":"+self.recovery_group_id, cleaned_full_path])
                Utils.log("Copied => "+each_file, "OKGREEN")

    def start(self, mode):
        self.load_volumes(mode == "create")
        can_copy = self.check_disks(mode == "create")
        self.start_copying(can_copy, mode == "create")

# Doc helper
def help():
    Utils.log("Backup program usage..")
    Utils.log("Use sudo if there are files which need to be backedup/recovered with admin rights")
    Utils.log("backupCreator.py [--create | -c | --recover | -r]", "OKGREEN")
    Utils.log("where:")
    Utils.log("\t --create", "OKBLUE")
    Utils.log_ln("\t --c\t\t Create a backup with configuration", "OKBLUE")
    Utils.log("\t --recover", "OKBLUE")
    Utils.log_ln("\t -r\t\t Recover a backup from configuration", "OKBLUE")

# Main program
Utils.log("=========>> BACKUP <<==========")
Utils.log_ln("@author: Jaiwardhan Swarnakar", "HEADER")
modes = {
    "--create": "create",
    "-c": "create",
    "--recover": "recover",
    "-r": "recover"
}

desc = {
    "create": "==> CREATE\t: Creating a backup from the configuration",
    "recover": "==> RECOVER\t: Attempting to recover from a previous back with the configuration"
}

if len(sys.argv) == 0 or sys.argv[1] not in modes:
    help() 
    sys.exit()

mode = sys.argv[1]
Utils.log(desc[modes[mode]], "OKBLUE")
time.sleep(3)
bkp = Backup()
bkp.init()
bkp.start(modes[mode])
