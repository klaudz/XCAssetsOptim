#!/usr/bin/python3

import sys, os, shutil
import time
import collections
import re
import json

# pragma mark - Global Defines

_script_dir = sys.path[0]
_contents_json_name = 'Contents.json'
_contents_json_template_path = os.path.join(_script_dir, 'appiconset_Contents.json')
_icon_name_prefix = ''

# pragma mark - Main

def main():
    while True:
        iconset_path = obtain_iconset_path(sys.argv[1])
        if iconset_path is None: break
        fulfill_iconset(iconset_path)
        remove_alpha_for_iconset(iconset_path)
        compress_iconset(iconset_path)
        break
    complete()

# pragma mark - Paths
    
def obtain_iconset_path(path):
    print()
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
    
    if iconset_path is None:
        log_failure('Failed to obtain the app iconset in path "' + path + '", reason: invalid path')
    elif not os.path.exists(iconset_path):
        log_failure('Failed to obtain the app iconset in path "' + iconset_path + '", reason: not exist')
        iconset_path = None
    elif not os.path.isdir(iconset_path):
        log_failure('Failed to obtain the app iconset in path "' + iconset_path + '", reason: not a directory')
        iconset_path = None
    else:
        log_success('Obtained the app iconset in path "' + iconset_path + '"')

    return iconset_path

# pragma mark - Fulfill

def fulfill_iconset(path):
    print()
    log_info('Fulfilling the app iconset...')
    icon_names = search_icons(path)
    path_tmp = path + '.tmp'
    path_new = path + '.new'
    path_bak = path + '.bak'
    fullsize_icon_names = create_fullsize_icons(path, path_tmp, icon_names)
    if fullsize_icon_names is None:
        log_failure('Failed')
        return 1
    ret = create_new_icons(path_tmp, path_new, fullsize_icon_names)
    if ret != 0:
        log_failure('Failed')
        return ret
    shutil.rmtree(path_tmp)
    shutil.rmtree(path)
    shutil.move(path_new, path)
    log_success('Succeeded')
    return 0

def search_icons(path):
    icon_names = {}
    files = os.listdir(path)
    for f in files:
        file_path = os.path.join(path, f)
        if not os.path.isfile(file_path):
            continue
        ext = os.path.splitext(file_path)[1]
        if ext.lower() != ".png":
            continue
        icon_path = file_path
        size = parse_size_from_icon(icon_path)
        icon_name = os.path.basename(icon_path)
        icon_names[size] = icon_name
    return icon_names

def parse_size_from_icon(path):
    name = os.path.basename(path)
    props = os.popen('sips -1 --getProperty pixelWidth --getProperty pixelHeight "' + path + '"').read()
    widthObj = re.search('pixelWidth: (\d+)', props)
    if not widthObj:
        log_failure("'" + name + "' is invalid")
        return 1
    width = int(widthObj.group(1))
    heightObj = re.search('pixelHeight: (\d+)', props)
    if not heightObj:
        log_failure("'" + name + "' is invalid")
        return 1
    height = int(heightObj.group(1))
    if width != height:
        log_failure("'" + name + "' is invalid, size: (" + str(width) + " x " + str(height) + ")")
        return 1
    return width

def create_fullsize_icons(src_path, dst_path, icon_names):
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    os.mkdir(dst_path)
    last_size = 0
    size_list = [ 20, 29, 40, 50, 57, 58, 60, 72, 76, 80, 87, 100, 114, 120, 144, 152, 167, 180, 1024 ]
    size_list.reverse()
    if not size_list[0] in icon_names:
        log_failure('Icon (1024) is not found')
        return None
    icon_names_new = {}
    for size in size_list:
        name_tmp = 'tmp_' + str(size) + '.png'
        if size in icon_names:
            name = icon_names[size]
            src_icon_path = os.path.join(src_path, name)
            dst_icon_path = os.path.join(dst_path, name_tmp)
            shutil.copy(src_icon_path, dst_icon_path)
            log_info("Copied to '" + name_tmp + "' (" + str(size) + ")")
        else:
            src_icon_path = os.path.join(dst_path, icon_names_new[last_size])
            dst_icon_path = os.path.join(dst_path, name_tmp)
            os.popen('sips --resampleHeightWidth ' + str(size) + ' ' + str(size) + ' "' + src_icon_path + '" --out "' + dst_icon_path + '"').read()
            log_info("Resized to '" + name_tmp + "' (" + str(last_size) + " -> " + str(size) + ")")
        icon_names_new[size] = name_tmp
        last_size = size
    return icon_names_new

def create_new_icons(src_path, dst_path, icon_names):
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    os.mkdir(dst_path)
    new_contents_json_path = os.path.join(dst_path, _contents_json_name)
    shutil.copy(_contents_json_template_path, new_contents_json_path)
    with open(new_contents_json_path, 'r') as f:
        icon_json = json.load(f)
    for item in icon_json['images']:
        idiom = item['idiom']
        sizeStr = re.match('\d+(\.\d+)?', item['size']).group()
        scaleStr = re.match('\d+', item['scale']).group()
        size = float(sizeStr)
        scale = int(scaleStr)
        realsize = int(size * scale)
        if not realsize in icon_names:
            log_failure('Generated icon (' + sizeStr + '@' + scaleStr + 'x) failed')
            continue
        src_name = icon_names[realsize]
        src_icon_path = os.path.join(src_path, src_name)
        new_name = _icon_name_prefix + 'icon-' + sizeStr + ('@' + scaleStr + 'x' if scale > 1 else '') + '-' + idiom + os.path.splitext(src_name)[1].lower()
        log_info(dst_path)
        log_info(new_name)
        new_icon_path = os.path.join(dst_path, new_name)
        shutil.copy(src_icon_path, new_icon_path)
        log_info("Generated icon '" + new_name + "' successfully")
        item['filename'] = new_name
    f.close()
    with open(new_contents_json_path, 'w') as f:
        json.dump(icon_json, f, indent=2)
    f.close()
    return 0

# pragma mark - Remove Alpha Channel

def remove_alpha_for_iconset(path):
    print()
    log_info('Removing alpha channel for the app iconset...')
    icon_names = search_icons(path)
    icon_1024_name = icon_names[1024]
    icon_1024_path = os.path.join(path, icon_1024_name)
    ret = remove_alpha_for_image(icon_1024_path)
    if ret == 0:
        log_success('Succeeded')
    else:
        log_failure('Failed')
    return ret

def remove_alpha_for_image(path):
    name = os.path.basename(path)
    props = os.popen('sips -1 --getProperty hasAlpha "' + path + '"').read()
    hasAlphaObj = re.search('hasAlpha: (\w+)', props)
    if not hasAlphaObj:
        log_failure("'"+ name + "' is invalid")
        return 1
    hasAlpha = hasAlphaObj.group(1) != "no"
    if not hasAlpha:
        log_info("'" + name + "' has no alpha channel")
        return 0
    log_info("'" + name + "' has alpha channel")
    bmp_path = path + '.bmp'
    os.popen('sips -s format bmp "' + path + '" --out "' + bmp_path + '"').read()
    os.popen('sips -s format png "' + bmp_path + '" --out "' + path + '"').read()
    log_info("Removed alpha channel from '" + name + "'")
    return 0

# pragma mark - Compress

def compress_iconset(path):
    print()
    log_info('Compressing the app iconset...')
    os.popen('/Applications/ImageOptim.app/Contents/MacOS/ImageOptim "' + path + '" >/dev/null 2>&1').read()
    log_info('Finished')

# pragma mark - Complete

def complete():
    print()

# pragma mark - Logs

def log(msg):
    print(msg)

def log_info(msg):
    print('[Info] ' + msg)

def log_success(msg):
    print('[SUCCESS] ' + msg)

def log_failure(msg):
    print('[FAILURE] ' + msg)

# pragma mark -

if __name__ == "__main__":
    main()
