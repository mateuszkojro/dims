import sys
from typing import List

import numpy as np
import psycopg2 as pg

from dimscommon.trigger import Trigger


class SqlConnection:
    def __init__(self, **params) -> None:
        # if params is not None:
        #     self.connection = pg.connect(params)
        # else:
        self.connection = pg.connect(host="localhost",
                                     database="dims_events",
                                     user="admin",
                                     password="pssd123")

    def get_cursor(self):
        """ Get the sql cursor - cursor needs to be closed by the caller """
        return self.connection.cursor()

    def commit(self) -> None:
        """ Commit changes to db """
        self.connection.commit()

    def select(self, collumns, table, where=""):
        """ Create select query on connection """
        raise NotImplemented
        SQL_QUERY = (f"\n"
                     f"SELECT"
                     f" path,\n"
                     f" start_frame,\n"
                     f" end_frame,\n"
                     f" box_min_x,\n"
                     f" box_min_y,\n"
                     f" box_max_x,\n"
                     f" box_max_y\n"
                     f"{collumns}\n"
                     f"FROM\n"
                     f" {table}\n"
                     f"WHERE\n"
                     f" {where}\n")
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
        raise NotImplementedError
        SQL_QUERY = f"""
                    INSERT INTO {table}
                    VALUES {values}
                    """
        raise NotImplemented

    def __del__(self):
        if self.connection:
            self.connection.close()


class DataCollection:
    def __init__(self, collection_name: str,
                 collection_parameter_names: List[str],
                 parameter_values: List[str],
                 additional_trigger_info: List[str]):

        SUCCES_MESSAGE = "Succes!"

        self.additional_trigger_info = additional_trigger_info

        self.sql_connection = SqlConnection()

        # create a cursor
        cur = self.sql_connection.get_cursor()

        INSERT_SQL = """ INSERT INTO 
                            data_collections(name, timestamp) 
                        VALUES(%s, clock_timestamp()) RETURNING id
                    """
        try:
            # execute the INSERT statement
            print(f"Executing sql query:\n{INSERT_SQL}")
            cur.execute(INSERT_SQL, (collection_name,))
            print(SUCCES_MESSAGE)
        except Exception as e:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        # get the generated id back
        self.data_collection_id = cur.fetchone()[0]

        if collection_parameter_names == [] or parameter_values == []:
            print("No additional collection parameters - SKIPING TABLE INIT")
        else:
            props_table_name = f"props_collection_{self.data_collection_id}"
            trigger_field_type_pairs = ', '.join([
                f"{parameter} TEXT" for parameter in collection_parameter_names
            ])
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
                                VALUES({','.join([f"'{value}'" for value in parameter_values])})
                                """

            try:
                print(f"Executing sql query:\n{FILL_PROPS_TABLE}")
                cur.execute(FILL_PROPS_TABLE, ())
                print(SUCCES_MESSAGE)
            except Exception as e:
                print(f"Error running sql query:\n{e}")
                sys.exit(1)

        # ADITIONAL TRIGGER INFO

        if not additional_trigger_info:
            print("No additional trigger parameters - SKIPING TABLE INIT")
        else:
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
            except Exception as e:
                print(f"Error running sql query:\n{e}")
                sys.exit(1)

        try:
            print("Committing changes to db")
            # commit the changes to the database
            self.sql_connection.commit()
            print(SUCCES_MESSAGE)
        except Exception as e:
            print(f"Error running sql query:\n{e}")
            sys.exit(1)

        # close communication with the database
        cur.close()

    def upload_trigger(self, trigger: Trigger):

        INSERT_TRIGGER_SQL = ("INSERT INTO \n"
                              " all_triggers(\n"
                              " path, \n"
                              " box_min_x, \n"
                              " box_min_y, \n"
                              " box_max_x,\n"
                              " box_max_y, \n"
                              " start_frame, \n"
                              " end_frame, \n"
                              " data_collection_id,\n"
                              " time_stamp\n"
                              " ) \n"
                              "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, clock_timestamp())\n"
                              "RETURNING id\n")

        # create a cursor
        cur = self.sql_connection.get_cursor()

        rect = trigger.bounding_rect
        INSERT_TRIGGER_SQL = (f"INSERT INTO \n"
                              f"    all_triggers(\n"
                              f"    path, \n"
                              f"    box_min_x, \n"
                              f"    box_min_y, \n"
                              f"    box_max_x,\n"
                              f"    box_max_y, \n"
                              f"    start_frame, \n"
                              f"    end_frame, \n"
                              f"    data_collection_id,\n"
                              f"    time_stamp\n"
                              f"    )\n"
                              f"VALUES('{trigger.file}', \n"
                              f"    {rect.min_x}, \n"
                              f"    {rect.min_y}, \n"
                              f"    {rect.max_x}, \n"
                              f"    {rect.max_y}, \n"
                              f"    {trigger.start_frame}, \n"
                              f"    {trigger.end_frame}, \n"
                              f"    {self.data_collection_id}, \n"
                              f"    clock_timestamp())\n"
                              f"RETURNING id\n")
        # execute the INSERT statement
        try:
            print("Pushing trigger to db")
            print(INSERT_TRIGGER_SQL)
            cur.execute(INSERT_TRIGGER_SQL)
        except Exception as e:
            print(f"Error executig:\n{e}")
            exit(1)

        # Get the trigger id
        trigger_id = cur.fetchone()[0]

        if trigger.additional_data is not None:
            INSER_ADDITIONAL_TRIGGER_INFO = (f"INSERT INTO\n"
                                             f" {self.trigger_additional_props_table_name}\n"
                                             f"VALUES ({', '.join([str(trigger.additional_data[key]) for key in self.additional_trigger_info])}); \n")

            print(INSER_ADDITIONAL_TRIGGER_INFO)
            try:
                print("Pushing additional trigger info to db")
                cur.execute(INSER_ADDITIONAL_TRIGGER_INFO,
                            (trigger.file, rect.min_x, rect.min_y, rect.max_x,
                             rect.max_y, trigger.start_frame,
                             trigger.end_frame, self.data_collection_id))
            except Exception as e:
                print(f"Error executig:\n{e}")
                exit(1)

        # commit the changes to the database
        self.sql_connection.commit()

        # close communication with the database
        cur.close()

        return trigger_id
