import os



for x in os.listdir(path):
    if x in ['desktop.ini', 'Thumbs.db']:
        continue

    f_path = os.path.join(path, x)
    files_in_cat = os.listdir(f_path)

    for file in files_in_cat:
        if file.startswith('SAP'):
            src = os.path.join(f_path, file)
            new_name = f'{x} {file}'
            dst = os.path.join(f_path, new_name)
            os.rename(src=src, dst=dst)