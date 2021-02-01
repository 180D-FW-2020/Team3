import cv2

def overlay_text(image, text, font_scale, bottom_left, thickness=2):
    cv2.putText(image, text,
                bottom_left,
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                font_scale,
                (60, 226, 69),
                thickness, 1)

def add_text_overlays(image, hud):

    kOffsetX = 20
    kOffsetY = 20

    overlay_text(image, "System Overview", 2,
                 (kOffsetX, kOffsetY+150), 3)
    overlay_text(image, "- Battery Level: " + str(hud.battery_level) + "V", 1.5,
                 (kOffsetX, kOffsetY+200))
    overlay_text(image, "- Throttle: " + hud.throttle_dir + str(hud.throttle) + "%", 1.5,
                 (kOffsetX, kOffsetY+240))
    overlay_text(image, "- Payload Compartment: " + hud.payload, 1.5,
                 (kOffsetX, kOffsetY+280))