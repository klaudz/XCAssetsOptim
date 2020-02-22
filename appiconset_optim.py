#!/usr/bin/python3

import sys, os

# pragma mark - Global Defines

_script_dir = sys.path[0]

# pragma mark - Main

def main():
    iconset_path = obtain_iconset_path(sys.argv[1])

# pragma mark - Paths
    
def obtain_iconset_path(path):
    path = os.path.abspath(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == '.appiconset':
        iconset_path = path
    elif ext == '.xcassets':
        image_assets_path = path
        iconset_name = 'AppIcon.appiconset'
        iconset_path = os.path.join(image_assets_path, iconset_name)
    else:
        iconset_path = None
    return iconset_path

# pragma mark -

if __name__ == "__main__":
    main()
