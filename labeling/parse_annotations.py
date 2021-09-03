import json
import sys
import numpy as np

import psycopg2 as pg

try:
    from tqdm import tqdm
except Exception:
    tqdm = lambda x: x


def read_label_studio_output(file_path):
    with open(file_path) as f:
        content = f.read()

        data = json.loads(content)

        lables_for_events = np.array([], dtype=object)

        for row in tqdm(data):
            labels = np.array([], dtype=object)
            for annotation in row["annotations"]:
                for result in annotation["result"]:
                    for label in result["value"]["choices"]:
                        labels = np.append(labels, label)
            filename = row["data"]["image"]
            lables_for_events = np.append(lables_for_events,
                                          (filename, labels))

        return lables_for_events


def get_corresponding_trigger():
    pass


def connect_to_db():
    try:
        # connect to db
        conn = pg.connect(host="localhost",
                          database="dims_events",
                          user="admin",
                          password="pssd123")

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()

        return conn
    except (Exception, pg.DatabaseError) as error:
        print(error)
        sys.exit(1)


def upload_labels(file, box_min_x, box_min_y, box_max_x, box_max_y,
                  frame_start, frame_end, label):

    INSERT_SQL = """ INSERT INTO all_events VALUES(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING 0"""
    # connect to db
    conn = pg.connect(host="localhost",
                      database="dims_events",
                      user="admin",
                      password="pssd123")

    # create a cursor
    cur = conn.cursor()

    try:
        # execute the INSERT statement
        cur.execute(INSERT_SQL, (file, box_min_x, box_min_y, box_max_x,
                                 box_max_y, frame_start, frame_end, label))

        # get the generated id back
        return_value = cur.fetchone()[0]
        print(return_value)
    except pg.errors.UniqueViolation:
        print("Exaclty the same event arledy exists")

    # commit the changes to the database
    conn.commit()

    # close communication with the database
    cur.close()


if __name__ == '__main__':
    # labels = read_label_studio_output(sys.argv[1])
    # print(f"Parsed: {len(labels)} datapoints")
    upload_labels('file', 1, 2, 3, 4, 5, 6, 'cos')
