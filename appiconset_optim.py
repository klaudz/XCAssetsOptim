#!/usr/bin/python3

import sys, os

# pragma mark - Global Defines

_script_dir = sys.path[0]
_appicons_path = None

# pragma mark - Main

def main():
    global _appicons_path
    _appicons_path = obtain_appicons_path(sys.argv[1])

# pragma mark - Paths
    
def obtain_appicons_path(path):
    path = os.path.abspath(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == '.appiconset':
        appicons_path = path
    elif ext == '.xcassets':
        image_assets_path = path
        appicons_name = 'AppIcon.appiconset'
        appicons_path = os.path.join(image_assets_path, appicons_name)
    else:
        appicons_path = None
    return appicons_path

# pragma mark -

if __name__ == "__main__":
    main()
