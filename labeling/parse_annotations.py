import json
try:
    from tqdm import *
except Exception:
    tqdm = lambda x: x

import time

if __name__ == '__main__':

    content = None
    with open("annotations.json") as f:
        content = f.read()

    data = json.loads(content)

    for row in tqdm(data):
        filename = row["data"]["image"]
        print(f"=== NEW FILE ===")
        for annotation in row["annotations"]:
            for result in annotation["result"]:
                for label in result["value"]["choices"]:
                    print(f"{label=}")
