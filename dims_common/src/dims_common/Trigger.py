import pathlib
from collections import namedtuple
from typing import List

import cv2
import sys
from configparser import ConfigParser
import cython
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2 as pg
"""
Object representing a 2 dimentional vector
"""
Vec2 = namedtuple('Vec2', ['x', 'y'])
"""
Object repersenting Rectangle
"""
Rect = namedtuple('Rect', ['min_x', 'min_y', 'max_x', 'max_y'])
"""
Names used to extract information from csv to Trigger object
"""
field_names = [
    'file',  # Path: file
    'start_frame',  # int: First frame on which event was recorded
    'end_frame',  # int: Last frame on which event was recorded
    'bounding_rect',  # @Rect: bounding rectangle
    'additional_data'  # dictionary of algorithm specific information about the trigger
]
"""
Common interface object for a trigger
"""
Trigger = namedtuple('Trigger', field_names)


def _assert(condition: bool, msg: str):
    """
    Assertion that survives cython compilation
    """
    if not condition:
        print("Assertion failed: \n")
        raise AssertionError(msg)


@cython.wraparound(False)
@cython.boundscheck(False)
def _get_frames(path, start=None, stop=None) -> np.array:
    """
    Read frames from given file you can pass start and end frame
    """
    capture = cv2.VideoCapture(str(path))

    start = start if start is not None else 0
    stop = stop if stop is not None else capture.get(cv2.CAP_PROP_FRAME_COUNT -
                                                     1)

    N = int(stop) - int(start) + 1

    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = []
    for _ in range(N):
        status, frame = capture.read()
        _assert(status, "Error reading frame")
        frames.append(frame)

    return frames


def create_trigger(file, start_frame, end_frame, rect, additional_data):
    """ Simple create trigger (only for future possible extension) """
    return Trigger(file=file,
                   start_frame=start_frame,
                   end_frame=end_frame,
                   bounding_rect=rect,
                   additional_data=additional_data)


def create_trigger_flat(file, start_frame, end_frame, box_min_x, box_min_y,
                        box_max_x, box_max_y, additional_data):
    """ Create trigger without need to manualy create Rect object """
    return Trigger(file=file,
                   start_frame=start_frame,
                   end_frame=end_frame,
                   bounding_rect=Rect(min_x=box_min_x,
                                      min_y=box_min_y,
                                      max_x=box_max_x,
                                      max_y=box_max_y),
                   additional_data=additional_data)


def create_trigger_dict(dictionary):
    """ Creates trigger from dictionary field names need to be the same as @field_names """
    print("Check correctness")
    return Trigger(file=dictionary['file'],
                   start_frame=dictionary['start_frame'],
                   end_frame=dictionary['end_frame'],
                   bounding_rect=Rect(min_x=dictionary['box_min_x'],
                                      min_y=dictionary['box_min_y'],
                                      max_x=dictionary['box_max_x'],
                                      max_y=dictionary['box_max_y']),
                   additional_data=dictionary['additional_data'])


def trigger_to_dict(trigger):
    """ Convert trigger to flat dict """
    resulting_dict = {
        'file': trigger.file,
        'start_frame': trigger.start_frame,
        'end_frame': trigger.end_frame,
        'box_min_x': trigger.box_min_x,
        'box_min_y': trigger.box_min_y,
        'box_max_x': trigger.box_max_x,
        'box_max_y': trigger.box_max_y,
    }
    for key, value in trigger.additional_data.items():
        resulting_dict[key] = value
    return resulting_dict


@cython.wraparound(False)
@cython.boundscheck(False)
def read_row(row, base_path="./") -> Trigger:
    """ Convert row of a df to Trigger obj """
    # FIXME: Path conversion
    base_path = pathlib.Path(base_path)

    file = row.get("file")

    # if diffrent format backtrack
    if file is None:
        file = pathlib.Path(row.get("common_pathname"))
        file = base_path / file

    file = pathlib.Path(file)

    bounding_rect = Rect(
        min_x=row.get("rect_min_x"),
        min_y=row.get("rect_min_y"),
        max_x=row.get("rect_max_x"),
        max_y=row.get("rect_max_y"),
    )

    if bounding_rect.min_x is None:
        bounding_rect = Rect(min_x=row.get("box_up_left_x"),
                             max_y=row.get("box_up_left_y"),
                             max_x=row.get("box_down_right_x"),
                             min_y=row.get("box_down_right_y"))

    if bounding_rect.min_x is None:
        bounding_rect = Rect(min_x=row.get("box_min_x"),
                             max_y=row.get("box_max_y"),
                             max_x=row.get("box_max_x"),
                             min_y=row.get("box_min_y"))

    return Trigger(file=file,
                   length=row.get("length"),
                   start_frame=row.get("start_frame"),
                   end_frame=row.get("end_frame"),
                   bounding_rect=bounding_rect,
                   section=row.get("section"),
                   time_block=row.get("time_block"),
                   line_fit=row.get("line_fit"))


@cython.wraparound(False)
@cython.boundscheck(False)
def read_df(df: pd.DataFrame, base_path="./") -> np.array:
    """ Convert df int numpy arry containing @Triggers """
    base_path = pathlib.Path(base_path)
    N = df.shape[0]
    all_triggers = np.empty(N, dtype=object)

    for idx, row in df.iterrows():
        all_triggers[idx] = read_row(row, base_path)

    return all_triggers


def combine_frames(frame_list: np.array):
    """
    Get the arr of frames and combine them into one
    (by getting max pixel value)
    """
    return np.amax(frame_list, axis=0)


@cython.wraparound(False)
@cython.boundscheck(False)
def cut_rect_from_frame(frame: np.array, r: Rect) -> np.array:
    """ Cuts out the rect from given frame """
    return frame[int(r.min_y):int(r.max_y + 1), int(r.min_x):int(r.max_x + 1)]


def get_center(trigger: Trigger) -> Vec2:
    """ Calculate center of a @Trigger """
    min_x, min_y, max_x, max_y = trigger.bounding_rect
    x = min_x + abs(max_x - min_x) / 2
    y = min_y + abs(max_y - min_y) / 2

    return Vec2(x, y)


def get_section(trigger: Trigger) -> int:
    """ Calculate number of a section containing center of the @Trigger """
    x, y = get_center(trigger)

    x = x // 120
    y = y // 120

    return int(y * (1920 // 120)) + int(x)


def section_rect(trigger: Trigger) -> Rect:
    """ Cutout section Rect """
    section = trigger.section
    min_x = ((section % (1920 // 120)) * 120) - 1
    min_y = ((section // (1920 // 120)) * 120) - 1
    max_x = (min_x + 120) - 1
    max_y = (min_y + 120) - 1
    return Rect(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)


def center_rect(trigger: Trigger, size: Vec2, crop_method="move") -> Rect:
    """ Creates Rect with some offeset from the center """
    center = get_center(trigger)
    min_x = center.x - size.x
    max_x = center.x + size.x - 1
    min_y = center.y - size.y
    max_y = center.y + size.y - 1

    if min_x < 0:
        min_x = 0

    if min_y < 0:
        min_y = 0

    if max_x > 1919:
        max_x = 1919

    if max_y > 1079:
        max_y = 1079

    rect = Rect(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)

    return rect


def get_frames(trigger: Trigger) -> np.array:
    """ Get frames from Trigger """
    return _get_frames(trigger.file, trigger.start_frame, trigger.end_frame)


@cython.wraparound(False)
@cython.boundscheck(False)
def animate(frame_list: np.array, interactive=True, file="out.mp4", size=None):
    """
    Given an array of frames creates and animation
    TODO: make it faster with:
    https://github.com/vrabelmichal/dims_experimentation/blob/207f37ef4d41dbae366570a9a58ae58ce724f3af/visualization.py#L95-L142
    """

    fig = plt.figure(figsize=size)
    # for storing the generated images
    N = len(frame_list)
    animation_frames = np.arange(N, dtype=object)
    for i in range(N):
        animation_frames[i] = [plt.imshow(frame_list[i], animated=True)]

    ani = animation.ArtistAnimation(fig,
                                    animation_frames,
                                    interval=100,
                                    blit=True,
                                    repeat_delay=10)

    if interactive:
        from IPython.core.display import HTML, display
        return HTML(ani.to_jshtml())

    else:
        ani.save(file)
        plt.close()
        del fig
        del ani
        return None


def mark_rect(frame: np.array, rect: Rect, color=(0, 255, 0), thickness=2):
    """ Draw a rectangle on a bigger image """
    marked_frame = frame
    min_x, min_y, max_x, max_y = rect
    cv2.rectangle(marked_frame, (int(min_x), int(min_y)),
                  (int(max_x), int(max_y)), color, thickness)
    return marked_frame


def get_id(trigger: Trigger):
    """ Unique id of an event """
    return f"{trigger.file.name}_{trigger.section}_{trigger.start_frame}_{trigger.end_frame}"
    # return str(trigger.file).replace('/', '_') + '_' + \
    #     str(trigger.section) + '_' + str(trigger.time_block)


class SqlConnection:
    def __init__(self, **params) -> None:
        if params is not None:
            self.connection = pg.connect(params)
        else:
            self.connection = pg.connect(host="localhost",
                                         database="dims_events",
                                         user="admin",
                                         password="pssd123")

    def get_cusrosr(self):
        """ Get the sql cursor - cursor needs to be closed by the caller """
        return self.connection.cursor()

    def commit(self) -> None:
        """ Commit changes to db """
        self.connection.commit()

    def select(self, collumns, table, where=""):
        """ Create select query on connection """
        SQL_QUERY = f""""
                    SELECT  path,
                            start_frame,
                            end_frame,
                            box_min_x,
                            box_min_y,
                            box_max_x,
                            box_max_y
                            {collumns}
                    FROM
                            {table}
                    WHERE
                            {where}
                    """
        cursor = self.connection.cursor()
        cursor.execute(SQL_QUERY)

        query_result = np.array([])
        row = cursor.fetchone()

        while row is not None:
            query_result = np.append(row)

        cursor.close()

        return query_result

    def insert(self, table, values):
        """ Insert into db """
        SQL_QUERY = f"""
                    INSERT INTO {table}
                    VALUES {values}
                    """

    def __del__(self):
        self.connection.close()


def spllit_stringify_dict(dictionary: dict, spliiter=','):
    keys, values = "", ""
    for key, value in dictionary.items():
        keys += spliiter + key
        values += spliiter + value
    return keys, values


class DataCollection:
    def __init__(self, collection_name: str,
                 collection_parameter_names: List[str],
                 parameter_values: List[str],
                 additional_trigger_info: List[str]) -> None:

        SUCCES_MESSAGE = "Succes!"

        self.additional_trigger_info = additional_trigger_info

        self.sql_connection = SqlConnection

        # create a cursor
        cur = self.sql_connection.get_cusrosr()

        INSERT_SQL = """ INSERT INTO 
                            data_collections(name, timestamp) 
                        VALUES(%s, clock_timestamp()) RETURNING id
                    """
        try:
            # execute the INSERT statement
            print(f"Executing sql query:\n{INSERT_SQL}")
            cur.execute(INSERT_SQL, collection_name)
            print(SUCCES_MESSAGE)
        except Exception as e:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        # get the generated id back
        self.data_collection_id = cur.fetchone()[0]

        props_table_name = f"props_collection_{self.data_collection_id}"
        trigger_field_type_pairs = ', '.join(
            [f"{parameter} TEXT" for parameter in collection_parameter_names])
        CREATE_PROPS_TABLE = f"""
                            CREATE TABLE {props_table_name}
                            ({trigger_field_type_pairs})
                            """
        try:
            # execute the INSERT statement
            print(f"Executing sql query:\n{CREATE_PROPS_TABLE}")
            cur.execute(CREATE_PROPS_TABLE, ())
            print(SUCCES_MESSAGE)
        except Exception as e:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        FILL_PROPS_TABLE = f"""
                            INSERT INTO {props_table_name}({','.join(collection_parameter_names)})
                            VALUES(','.join{parameter_values})
                            """

        try:
            print(f"Executing sql query:\n{FILL_PROPS_TABLE}")
            cur.execute(FILL_PROPS_TABLE, ())
            print(SUCCES_MESSAGE)
        except Exception:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        # ADITIONAL TRIGGER INFO

        self.trigger_additional_props_table_name = f"additional_trigger_props_{self.data_collection_id}"
        CREATE_ADDITIONAL_TRIGGER_INFO_TABLE = f"""
                                                CREATE TABLE {self.trigger_additional_props_table_name}
                                                ({', '.join([f"{parameter} TEXT" for parameter in self.additional_trigger_info])})
                                                """

        try:
            print(
                f"Executing sql query:\n{CREATE_ADDITIONAL_TRIGGER_INFO_TABLE}"
            )
            cur.execute(CREATE_ADDITIONAL_TRIGGER_INFO_TABLE, ())
            print(SUCCES_MESSAGE)
        except Exception:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        try:
            print("Commiting changes to db")
            # commit the changes to the database
            self.sql_connection.commit()
            print(SUCCES_MESSAGE)
        except Exception:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        # close communication with the database
        cur.close()

    def upload_trigger(self, trigger: Trigger):

        INSERT_TRIGGER_SQL = """ 
                            INSERT INTO 
                                all_triggers(
                                    path, 
                                    box_min_x, 
                                    box_min_y, 
                                    box_max_x,
                                    box_max_y, 
                                    start_frame, 
                                    end_frame, 
                                    data_collection_id
                                    time_stamp, 
                                    ) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, clock_timestamp()) 
                                RETURNING id
                            """

        # create a cursor
        cur = self.sql_connection.cursor()

        rect = trigger.bounding_rect
        # execute the INSERT statement
        try:
            print("Pushing trigger to db")
            cur.execute(INSERT_TRIGGER_SQL,
                        (trigger.file, rect.min_x, rect.box_min_y, rect.max_x,
                         rect.max_y, trigger.frame_start, trigger.frame_end,
                         self.collection_id))
        except Exception as e:
            print(f"Error executig:\n{e}")

        INSER_ADDITIONAL_TRIGGER_INFO = f"""
                                        INSERT INTO 
                                            {self.trigger_additional_props_table_name}
                                            ({self.additional_trigger_info})
                                        VALUES ({', '.join([val for (key, val) in trigger.additional_data])})
                                        """

        try:
            print("Pushing additional trigger info to db")
            cur.execute(INSER_ADDITIONAL_TRIGGER_INFO,
                        (trigger.file, rect.min_x, rect.box_min_y, rect.max_x,
                         rect.max_y, trigger.frame_start, trigger.frame_end,
                         self.collection_id))
        except Exception as e:
            print(f"Error executig:\n{e}")

        # Get the trigger id
        trigger_id = cur.fetchone()[0]

        # commit the changes to the database
        self.sql_connection.commit()

        # close communication with the database
        cur.close()