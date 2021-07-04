import csv, pathlib, sqlite3

##########
#
#   Load the images from the data files into the db's image table.
#   The assumption is that all three data files are CSV files in the format
#   used by the VQG data set
#
########## 
def load_images(db, csv_file, size):
    con = sqlite3.connect(db)
    cur = con.cursor()
    rows = list(csv.DictReader(csv_file))[:size]
    
    [cur.execute("INSERT INTO image(id, data_set, img_url) VALUES(?, 'test', ?)", (row['image_id'], row['image_url'])) for row in rows]
    
    con.commit()
    con.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load image data into database')
    parser.add_argument('--db', type=pathlib.Path, default='app/vqg.db', help='the Sqlite database')
    parser.add_argument('--image_file', default='image_data/coco_test_all.csv', type=argparse.FileType('r'), help='CSV file with the image data set')
    parser.add_argument('--size', default=510, type=int, help='The number of images to include in the data set')
    #parser.add_argument('--train_file', default='image_data/coco_train_all.csv', type=argparse.FileType('r'), help='CSV file with the training set')
    #parser.add_argument('--val_file', type=argparse.FileType('r'), default='image_data/coco_val_all.csv', help='CSV file with the validation set')
    #parser.add_argument('--test_file', type=argparse.FileType('r'), default='image_data/coco_test_all.csv', help='CSV file with the testing set')

    args = parser.parse_args()
    load_images(args.db, args.image_file, args.size)