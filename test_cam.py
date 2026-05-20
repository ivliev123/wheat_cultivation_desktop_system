import cv2

cam = cv2.VideoCapture(2, cv2.CAP_V4L2)

print("opened:", cam.isOpened())

while True:

    ret, frame = cam.read()

    print(ret, frame.shape if ret else None)

    if ret:
        cv2.imshow("cam", frame)

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()
