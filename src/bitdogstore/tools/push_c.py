import os
import string
import shutil
import subprocess
import sys
import json

def list_directory_contents(drive):
    # List the contents of the drive
    contents = os.listdir(drive)
    return contents
        
if os.name == 'nt': 
    def list_mount_points():
        drives = [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]
        return drives

    def get_mounts():
        mount_points = list_mount_points()
        correct = []
        for mount in mount_points:
            contents = list_directory_contents(mount)
            for item in contents:
                if 'INFO_UF2.TXT' and 'INDEX.HTM' in item:
                    correct.append(mount)
        return correct

    def push(file, mount):
        shutil.copy(file,mount)

elif sys.platform.startswith('linux'):
    def get_mounts():
        try:
            # Execute lsblk command with JSON output to easily parse the information
            result = subprocess.run(['lsblk', '-o', 'NAME,MODEL,MOUNTPOINT', '-J'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
    
            if result.returncode != 0:
                print(f"Error running lsblk: {result.stderr}")
                return []
    
            # Parse the output as JSON
            lsblk_output = json.loads(result.stdout)
    
            # Traverse through the block devices to find 'rp2' and its first partition
            correct = []
            for device in lsblk_output.get('blockdevices', []):
                if device['model'] == 'RP2':
                    for child in device.get('children', []):
                        # Assuming the first partition is the first child
                        mountpoint = child.get('mountpoint')
                        if mountpoint:
                            contents = list_directory_contents(mountpoint)
                            for item in contents:
                                if 'INFO_UF2.TXT' and 'INDEX.HTM' in item:
                                    correct.append(mountpoint)
                        else:
                            print(f"No mount point found for {child['name']}")
            return correct
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def push(file, mount):
        print(mount)
        shutil.copy(file,mount)

else:
    raise(Exception("OS não suportado"))