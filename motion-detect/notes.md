# Ideas

## Check how acuratly we can fit the line between points in cluster


__*Normally, Hough Transform is used for line detection.*__

But if it doesn't work for you, fitting line is also a good alternative.

```python
import cv2
# Load image, convert to grayscale, threshold and find contours
img = cv2.imread('lail.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
contours,hier = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
cnt = contours[0]

# then apply fitline() function
[vx,vy,x,y] = cv2.fitLine(cnt,cv2.cv.CV_DIST_L2,0,0.01,0.01)

# Now find two extreme points on the line to draw line
lefty = int((-x*vy/vx) + y)
righty = int(((gray.shape[1]-x)*vy/vx)+y)

#Finally draw the line
cv2.line(img,(gray.shape[1]-1,righty),(0,lefty),255,2)
cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

## Create polygon and check if the point is within bounds

- <https://users.fmrib.ox.ac.uk/~steve/asset/asset2/node6.html>
- <https://www.researchgate.net/publication/221575507_A_Novel_Automatic_Cluster_Tracking_Algorithm>
