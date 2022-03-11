import zipfile

import os


def unzip_r(file, dest):
    path = os.path.abspath(file)
    unzip_dest = os.path.join(dest, os.path.basename(file).replace('.zip', ''))
    root_dir = unzip(path, unzip_dest)

    def recursive(parent_dir):
        if os.path.isfile(parent_dir):
            return
        for _child in os.listdir(parent_dir):
            child = os.path.join(parent_dir, _child)
            if os.path.isfile(child):
                if zipfile.is_zipfile(child):
                    child_dir = unzip(child)
                    recursive(child_dir)
                    os.remove(child)
                else:
                    recursive(child)
            else:
                recursive(child)

    recursive(root_dir)
    return unzip_dest


def unzip(zip_file, dest=None):
    dest_dir = dest
    if dest_dir is None:
        _dest = os.path.splitext(os.path.basename(zip_file))[0]
        dest_dir = os.path.join(os.path.dirname(zip_file), _dest)

    # print('dest_dir=%s' % dest_dir)
    zf = zipfile.ZipFile(zip_file)
    zf.extractall(dest_dir)
    zf.close()
    return dest_dir
