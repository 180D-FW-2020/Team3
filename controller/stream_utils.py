import cv2
import time

kPromptDuration = 2

class PromptManager:
    # prompt = [text, timer, expired]
    def __init__(self, max_prompts=3):
        self.max_prompts = max_prompts
        self.prompts = []
        self.promptCount = 0

    def add_prompt(self, text):
        self.prompts.append([text, time.time(), False])
        self.promptCount += 1

    def clear_expired_prompts(self):
        for prompt in self.prompts:
            if time.time() - prompt[1] >= kPromptDuration:
                prompt[2] = True
                self.promptCount -= 1

    def gather_valid_prompts(self):
        valid = []
        for prompt in self.prompts:
            if not prompt[2]:
                valid.append(prompt)
        return valid

def overlay_text(image, text, font_scale, bottom_left, thickness=2):
    cv2.putText(image, text,
                bottom_left,
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                font_scale,
                (60, 226, 69),
                thickness, 1)

def add_text_overlays(image, hud, cannon_status=None):

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

    if cannon_status:
        # add cannon status to hud
        overlay_text(image, "- Cannon Status: " + cannon_status.motor_status, 1.5, (kOffsetX, kOffsetY+320))
        overlay_text(image, "- Shot count: " + str(cannon_status.shot_count), 1.5, (kOffsetX, kOffsetY+360))
        if cannon_status.motor_status == "Warming Up":
            overlay_text(image, "- Warmup Timer: " + str((cannon_status.warmup_timer_end - cannon_status.warmup_timer)/1000.0) + "s", 1.5, (kOffsetX, kOffsetY+400))
        elif cannon_status.motor_status == "Warmed Up":
            overlay_text(image, "- Overheat Timer: " + str((cannon_status.overheat_timer_end - cannon_status.overheat_timer)/1000.0) + "s", 1.5, (kOffsetX, kOffsetY+400))
        elif cannon_status.motor_status in ["Overheated! Cooling Down", "Cooling Down"]:
            overlay_text(image, "- Cooldown Timer: " + str((cannon_status.cooldown_timer_end - cannon_status.cooldown_timer)/1000.0) + "s", 1.5, (kOffsetX, kOffsetY+400))

def overlay_prompts(image, prompts):
    kOffsetX = 20
    kOffsetY = 600
    overlay_text(image, "Notifications", 2, (kOffsetX, kOffsetY), 3)
    kOffsetY += 35
    for prompt in prompts:
        overlay_text(image, prompt[0] + " (" + str(round(time.time() - prompt[1], 2)) + "s ago)", 1.4, (kOffsetX, kOffsetY))
        kOffsetY += 35

