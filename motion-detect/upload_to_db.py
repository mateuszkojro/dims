from re import A
from threading import currentThread
from typing import Collection
import psycopg2 as pg
import pandas as pd
import sys

from tqdm import tqdm

from Trigger import *


def add_data_collection(name, timestamp):
    INSERT_SQL = """ INSERT INTO data_collections(name, timestamp) VALUES(%s, %s) RETURNING id"""
    # connect to db
    conn = pg.connect(host="localhost",
                      database="dims_events",
                      user="admin",
                      password="pssd123")

    # create a cursor
    cur = conn.cursor()

    try:
        # execute the INSERT statement
        cur.execute(INSERT_SQL, (name, timestamp))

        # get the generated id back
        data_collection_id = cur.fetchone()[0]
    except pg.errors.UniqueViolation:
        print("Exaclty the same event arledy exists")
        sys.exit()

    # commit the changes to the database
    conn.commit()

    # close communication with the database
    cur.close()
    return data_collection_id


def upload_labels(file, box_min_x, box_min_y, box_max_x, box_max_y,
                  frame_start, frame_end, collection_id, timestamp):

    INSERT_SQL = """ INSERT INTO all_triggers(path, box_min_x, box_min_y, box_max_x ,box_max_y, start_frame, end_frame, time_stamp, data_collection_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    # connect to db
    conn = pg.connect(host="localhost",
                      database="dims_events",
                      user="admin",
                      password="pssd123")

    # create a cursor
    cur = conn.cursor()

    try:
        # execute the INSERT statement
        cur.execute(INSERT_SQL,
                    (file, box_min_x, box_min_y, box_max_x, box_max_y,
                     frame_start, frame_end, timestamp, collection_id))

        # get the generated id back
    except pg.errors.UniqueViolation:
        print("Exaclty the same event arledy exists")

    # commit the changes to the database
    conn.commit()

    # close communication with the database
    cur.close()


if __name__ == '__main__':
    dataset_file = sys.argv[1]

    df = pd.read_csv(str(dataset_file))
    # triggers = read_df(df)
    timestamp = '2021-08-04 15:45:00-00'
    collection_id = add_data_collection('michal ufo capture extracted events',
                                        timestamp)

    for idx, row in tqdm(df.iterrows()):
        common_path = row["common_pathname"]
        upload_labels(file=common_path,
                      box_min_x=row["rect_x_min"],
                      box_min_y=row["rect_y_min"],
                      box_max_x=row["rect_x_max"],
                      box_max_y=row["rect_y_max"],
                      frame_start=row["time_bin_10"],
                      frame_end=row["time_bin_10"],
                      collection_id=collection_id,
                      timestamp=timestamp)
