import json
import sys
import numpy as np

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


if __name__ == '__main__':
    labels = read_label_studio_output(sys.argv[1])
    print(f"Parsed: {len(labels)} datapoints")
