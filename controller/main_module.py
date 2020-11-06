# run this program on the Mac to display image streams from multiple RPis
import cv2
import imagezmq
image_hub = imagezmq.ImageHub()
#print("got here 1")
while True:  # show streamed images until Ctrl-C
    #print("got here 2")
    rpi_name, image = image_hub.recv_image()
    cv2.namedWindow(rpi_name, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(rpi_name, image)  # 1 window for each RPi
    cv2.waitKey(1)
    image_hub.send_reply(b'OK')
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break
