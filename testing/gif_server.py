import os

import json

import flask
from flask import Flask, request
from flask.helpers import make_response
from contextlib import closing
import psycopg2
import dimscommon.trigger as tr
import dimscommon.datacollection as dc
from pathlib import Path
from configparser import ConfigParser
from dataclasses import dataclass

api = Flask(__name__)

config = None

cached_gifs_directory = Path("./")
video_files_directory = Path("./")
db_connection = None
cached_gifs = {}
cached_collections = {}


class ServerError(Exception):
    pass


class TriggerIDNotFoundError(ServerError):
    pass


class VideoFileNotFoundError(ServerError):
    pass


class GifFileError(ServerError):
    pass


class NoConfigError(ServerError):
    pass


def read_gif(filepath):
    # handle file that does not exist
    try:
        with open(filepath, "rb") as file:
            return file.read()
    except Exception:
        raise GifFileError


def generate_gif(trigger_id):
    assert type(trigger_id) == int
    if trigger_id in cached_gifs:
        return read_gif(cached_gifs[trigger_id])

    trigger = get_trigger_from_db(trigger_id)
    output_gif = cached_gifs_directory / f"{trigger_id}.gif"
    try:
        base_path = video_files_directory / trigger.file
        filename = str(base_path) + ".avi"
        print(filename)
        # TODO: add +/- 30 frames on each end
        tr.animate(
            frame_list=tr._get_frames(
                path=filename,
                start=trigger.start_frame,
                stop=trigger.end_frame,
            ),
            interactive=False,
            file=output_gif,
        )
    except AssertionError as e:
        print(e)
        raise VideoFileNotFoundError
    return read_gif(output_gif)


def get_trigger_from_db(trigger_id):
    with db_connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM all_triggers WHERE id={trigger_id}')
        row = cursor.fetchone()
        if not row:
            raise TriggerIDNotFoundError
        return tr.create_trigger_flat(
            file=row[1],
            box_min_x=int(row[2]),
            box_min_y=int(row[3]),
            box_max_x=int(row[4]),
            box_max_y=int(row[5]),
            start_frame=int(row[6]),
            end_frame=int(row[7]),
            additional_data=
            None  # FIXME: We should get that info from the other table
        )


@api.route("/err", methods=['GET'])
def error():
    pass


@api.route('/add-trigger/<int:collection_id>', methods=['POST'])
def add_trigger(collection_id):
    try:
        body = json.loads(request.data)
        collection = cached_collections[collection_id]
        raise NotImplemented
    except json.JSONDecodeError as e:
        return f"{e.msg} at {e.lineno}:{e.colno} ", 400

    print(body)
    trigger_id = 1
    return json.dumps(f"id: {trigger_id}"), 200


@api.route('/add-datacollection', methods=['POST'])
def create_datacollection():
    try:
        body = json.loads(request.data)

        collection = dc.DataCollection(
            collection_name=body["collection_name"],
            collection_parameter_names=body["collection_parameter_names"],
            parameter_values=body["collection_parameter_names"],
            additional_trigger_info=body["additional_trigger_info"]
        )

        cached_collections[collection.data_collection_id] = collection

    except json.JSONDecodeError as e:
        return f"{e.msg} at {e.lineno}:{e.colno} ", 400
    except KeyError as e:
        return f"Missing key {e.args}", 400

    print(body)
    collection_id = 1
    return json.dumps(f"collection_id: {collection_id}"), 200


@api.route('/generate-gif/<int:trigger_id>.gif', methods=['GET'])
def create_gif(trigger_id):
    # Generate binary stream
    try:
        image_bin = generate_gif(trigger_id)

        # Sending gif as a binary stream
        response = make_response(image_bin)
        response.headers.set('Content-Type', 'image/gif')
        response.headers.set('Content-Disposition',
                             'attachment',
                             filename=f"{trigger_id}.gif")
        return response

    except TriggerIDNotFoundError:
        return "Trigger id not could not be found in DB", 404

    except VideoFileNotFoundError:
        return "Gif cannot be generated video file does not exits", 500

    except GifFileError:
        return "Gif file could not be read", 500


def read_cache(cache_dir):
    file_list = os.listdir(cache_dir)
    for file in file_list:
        path = Path(file)
        if path.is_file() and path.suffix == ".gif":
            filename = path.name.split(".")[0]
            if filename.isdigit():
                cached_gifs[int(filename)] = path


def get_config():
    configuration = ConfigParser()
    if not Path("config.ini").is_file():
        raise NoConfigError
    configuration.read("config.ini")
    return configuration


if __name__ == '__main__':
    config = get_config()
    db_connection = psycopg2.connect(
        dbname=config.get("DB", "dbname"),
        user=config.get("DB", "user"),
        password=config.get("DB", "password"),
        host=config.get("DB", "host")
    )
    video_files_directory = Path(config.get("main", "video_files_directory"))
    cached_gifs_directory = Path(config.get("main", "cached_gifs_directory"))
    read_cache(cached_gifs_directory)
    print(f" * Read {len(cached_gifs)} cached gifs")
    api.run(debug=True)
    db_connection.close()
