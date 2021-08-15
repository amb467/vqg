import pathlib, re, sqlite3

##########
#
#   Load the images from the data files into the db's image table.
#   The assumption is that all three data files are CSV files in the format
#   used by the VQG data set
#
########## 
def load_images(db, image_dir):
    con = sqlite3.connect(db)
    cur = con.cursor()
    
    for img_path in image_dir.glob('*.jpg'):
        img_file = str(img_path).index('app/')
        img_file = str(img_path).partition('app/')[2]
        m = re.search('(\d+).jpg', img_file)
        img_id = int(m.group(1))
        
        cur.execute("INSERT INTO image(id, img_path) VALUES(?, ?)", (img_id, img_file)) 

    
    con.commit()
    con.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load image data into database')
    parser.add_argument('--db', type=pathlib.Path, default='app/vqg.db', help='the Sqlite database')
    parser.add_argument('--image_dir', default='app/static/data_set', type=pathlib.Path, help='CSV file with the image data set')
    args = parser.parse_args()
    
    if not args.image_dir.exists():
        raise Exception(f'Invalid image directory path: {args.image_dir}')
    
    load_images(args.db, args.image_dir)