import cv2

# 從攝影機讀取一個畫面
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# 如果成功讀到影像，就儲存
if ret:
    cv2.imwrite("photo.jpg", frame)
    print("已儲存為 photo.jpg")

cap.release()
