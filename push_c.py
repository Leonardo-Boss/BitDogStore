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
    
    def push_windows(file):
        mount_points = list_mount_points()
        for mount in mount_points:
            contents = list_directory_contents(mount)
            for item in contents:
                if 'INFO_UF2.TXT' and 'INDEX.HTM' in item:
                    print(mount);
                    shutil.copy(file,mount)
                
elif sys.platform.startswith('linux'):
    def get_mount():
        try:
            # Execute lsblk command with JSON output to easily parse the information
            result = subprocess.run(['lsblk', '-o', 'NAME,MODEL,MOUNTPOINT', '-J'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
    
            if result.returncode != 0:
                print(f"Error running lsblk: {result.stderr}")
                return None
    
            # Parse the output as JSON
            lsblk_output = json.loads(result.stdout)
    
            # Traverse through the block devices to find 'rp2' and its first partition
            for device in lsblk_output.get('blockdevices', []):
                if device['model'] == 'RP2':
                    for child in device.get('children', []):
                        # Assuming the first partition is the first child
                        mountpoint = child.get('mountpoint')
                        if mountpoint:
                            return mountpoint
                        else:
                            print(f"No mount point found for {child['name']}")
                    print(f"No partitions found for device {device['name']}")
                    return None
            print("Device 'rp2' not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
            
    def push_linux(file):
        mount = get_mount()
        assert mount,"Pi Pico não encontrado, tenha certeza que está montado"
        
        contents = list_directory_contents(mount)
        for item in contents:
            if 'INFO_UF2.TXT' and 'INDEX.HTM' in item:
                print(mount);
                shutil.copy(file,mount)
                
else:
    raise(Exception("OS não suportado"))