# Common scripts for dims project

## Installation

To install localy:

```bash
pip install ./dimscommon
```

than to use `Trigger`

```python
import dimscommon.triger as tg
```

or to use `DataCollection`:

```python
import dimscommon.datacollection as dc
```

## dimscommon.trigger



## dimscommon.datacollection

### Creating data collecton:

When creating data collection coresponding tables in db will be created

```python
import dimscommon.datacollection as dc
collection = dc.DataCollection(
    "Data collecton name", # Name of the collection 
    ["sqr_size", "min_point"], # Collection parameter names 
    ["100x100px", "4"],  # Collection parameter values
    ["speed"] # Names for additional columns for each trigger
)
```

### Uploading trigger:

```python
import dimscommon.datacollection as dc
import dimscommon.trigger as tr

conn = dc.DataCollection("Test collection", [], [],
                        ["speed"])

# ...

collection.upload_trigger(tr.create_trigger_flat(
                            file="filename",
                            start_frame=1,
                            end_frame=2,
                            box_min_x=1,
                            box_min_y=2,
                            box_max_x=3,
                            box_max_y=4,
                            additional_data={
                                "speed": 12,
                            }))
```