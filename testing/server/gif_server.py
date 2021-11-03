import os

import json

import requests

from flask import Flask, request
from flask.helpers import make_response
import psycopg2
import dimscommon.trigger as tr
import dimscommon.datacollection as dc
from pathlib import Path
import sys
import enum
from configparser import ConfigParser

api = Flask(__name__)


class Config:
    _cached_gifs_directory = Path("./")
    _video_files_directory = Path("./")

    def __init__(self):
        pass

    @property
    def video_files_directory(self):
        return self._video_files_directory

    @property
    def cached_gifs_directory(self):
        return self._cached_gifs_directory


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
        print(f"-- Using cache for {trigger_id}.gif")
        return read_gif(cached_gifs[trigger_id])

    print(f"-- Getting information about trigger#{trigger_id} from db")
    trigger = get_trigger_from_db(trigger_id)
    output_gif = cached_gifs_directory / f"{trigger_id}.gif"
    try:
        base_path = video_files_directory / trigger.file
        filename = str(base_path) + ".avi"
        # TODO: add +/- 30 frames on each end
        print(f"-- Generating gif image for trigger#{trigger_id}")

        frames = tr._get_frames(
                path=filename,
                start=trigger.start_frame,
                stop=trigger.end_frame,
            )

        for frame in frames:
            frame = tr.mark_rect(frame, trigger.bounding_rect)

        tr.animate(
            frame_list=frames,
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
    trigger_id = -1
    trigger = None
    try:
        body = json.loads(request.data)
        collection = cached_collections[collection_id]
        trigger = tr.create_trigger_dict(body)
        trigger_id = collection.upload_trigger(trigger)

    except json.JSONDecodeError as e:
        return f"{e.msg} at {e.lineno}:{e.colno} ", 400
    except Exception:
        return "Trigger could not be pushed to db", 400
    create_label_studio_task(trigger_id, trigger)
    return json.dumps({"id": trigger_id}), 200


@api.route('/add-datacollection', methods=['POST'])
def create_datacollection():
    try:
        body = json.loads(request.data)

        collection = dc.DataCollection(
            collection_name=body["collection_name"],
            collection_parameter_names=body["collection_parameter_names"],
            parameter_values=body["collection_parameter_names"],
            additional_trigger_info=body["additional_trigger_info"])

        cached_collections[collection.data_collection_id] = collection

    except json.JSONDecodeError as e:
        return f"{e.msg} at {e.lineno}:{e.colno} ", 400
    except KeyError as e:
        return f"Missing key {e.args}", 400

    print(body)
    collection_id = collection.data_collection_id
    return json.dumps({"collection_id": collection_id}), 200


class TransmitMode(enum.Enum):
    ATACHMENT = enum.auto()
    INLINE = enum.auto()


def send_binary_data(binary_data,
                     target_filename,
                     extension='gif',
                     content_type='image/gif'):
    # Sending gif as a binary stream
    response = make_response(binary_data)
    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.set('Content-Type', content_type)
    response.headers.set(
        'Content-Disposition',
        # 'attachment',
        'inline',
        filename=f"{target_filename}.{extension}")
    return response


@api.route('/generate-gif/<int:trigger_id>.gif', methods=['GET'])
def create_gif(trigger_id):
    # Generate binary stream
    try:
        image_bin = generate_gif(trigger_id)
        return send_binary_data(image_bin, target_filename=trigger_id)

    except TriggerIDNotFoundError:
        return "Trigger id not could not be found in DB", 404

    except VideoFileNotFoundError:
        return "Gif cannot be generated video file does not exits", 500

    except GifFileError:
        return "Gif file could not be read", 500


@api.route('/webhook', methods=['GET', 'POST'])
def webhook_call():
    print("Webhook hit")
    print(request.method)
    body = json.loads(request.body)
    print(f"{body=}")


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

label_studio_url = None
def get_label_studio_url():
    return label_studio_url # "http://localhost/label/api/"

hostname = None
def get_host_name():
    return hostname # "http://localhost:8090/"


def label_studio_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": "Token 2e8fca1341c9a00475a73556768695aeea469a30"
    }


# Should work but the server from inside of a docker compose
# cannot make requests to the outside
def add_webhook():
    generated_json = json.dumps({
        "project":
        2,
        "url":
        get_host_name() + "webhook",
        "actions":
        ["ANNOTATION_CREATED", "ANNOTATION_UPDATED", "ANNOTATIONS_DELETED"]
    })
    response = requests.post(get_label_studio_url() + "/webhooks",
                             data=generated_json,
                             headers=label_studio_headers())
    print(f"{response.json()=}")


def get_labeled_tasks():
    pass


def create_label_studio_task(trigger_id, trigger):
    generated_json = json.dumps({
        "data": {
            "image": get_host_name() + f"generate-gif/{trigger_id}.gif"
        },
        "project": 2
    })

    print(f"{generated_json=}")
    response = requests.post(get_label_studio_url() + "/tasks",
                             data=generated_json,
                             headers=label_studio_headers())
    response = response.json()
    label_studio_id = response['id']
    print(f"{response=}, {label_studio_id=}")

    return label_studio_id


def create_annotation(label_studio_id, annotation_score, annotation_result):
    requests.post(get_label_studio_url() + "/annotations",
                  data={
                      "model_version": "v0.1",
                      "result": annotation_result,
                      "score": annotation_score,
                      "task": label_studio_id
                  },
                  headers=label_studio_headers())


if __name__ == '__main__':
    # create_label_studio_task(21, 1)
    config = get_config()
    db_connection = psycopg2.connect(dbname=config.get("DB", "dbname"),
                                     user=config.get("DB", "user"),
                                     password=config.get("DB", "password"),
                                     host=config.get("DB", "host"))
    label_studio_url = config.get("main", "label_stduio_url")
    hostname = config.get("main", "hostname")
    video_files_directory = Path(config.get("main", "video_files_directory"))
    cached_gifs_directory = Path(config.get("main", "cached_gifs_directory"))
    read_cache(cached_gifs_directory)
    print(f" * Read {len(cached_gifs)} cached gifs")
    api.run(debug=True, port=8090)
    db_connection.close()
