# Script for showing singular frames in YUV422 and comparing them

1. show `frame1` (file with binary data in YUV422 format  defaults to 1920x1080px)
```bash
python3 show_frame.py frame1
```

1. Compare `frame1` with `frame2` (same fromat)
```bash
python3 show_frame.py frame1 frame2
```

1. It could also be used with 2 addicional params if frame has another size
```bash
python3 show_frame.py frame 1080 1920
# or
python show_frame.py frame1 frame2 1024 720

```
