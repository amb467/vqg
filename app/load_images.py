import csv, pathlib, sqlite3

##########
#
#   Load the images from the data files into the db's image table.
#	The assumption is that all three data files are CSV files in the format
#	used by the VQG data set
#
########## 
def load_images(db, train_set, val_set, test_set):
    con = sqlite3.connect(db)
    cur = con.cursor()
    
    _load_csv_data_set(cur, train_set, 'train')
    _load_csv_data_set(cur, val_set, 'val')
    _load_csv_data_set(cur, test_set, 'test')
    
    con.commit()
    con.close()

##########
#
#   Helper function for load_images
#
########## 
def _load_csv_data_set(cur, csv_file, set_label):    
    [cur.execute("INSERT INTO image(id, data_set, img_url) VALUES(?, ?, ?)", (row['image_id'], set_label, row['image_url'])) for row in csv.DictReader(csv_file)]

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load image data into database')
    parser.add_argument('--db', type=pathlib.Path, default='app/vqg.db', help='the Sqlite database')
    parser.add_argument('--train_file', default='image_data/coco_train_all.csv', type=argparse.FileType('r'), help='CSV file with the training set')
    parser.add_argument('--val_file', type=argparse.FileType('r'), default='image_data/coco_val_all.csv', help='CSV file with the validation set')
    parser.add_argument('--test_file', type=argparse.FileType('r'), default='image_data/coco_test_all.csv', help='CSV file with the testing set')

    args = parser.parse_args()
    load_images(args.db, args.train_file, args.val_file, args.test_file)