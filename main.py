# main.py -- put your code here!
import sys
import time

import animations
import badge
import dcfurs
import emote
import micropython
import pyb
import settings
import ubinascii

print("Booting...")

EXCEPTION_FACE = [
    0x30783,  # 0b1100_0001_11_1000_0011
    0x18CC6,  # 0b0110_0011_00_1100_0110
    0x0D86C,  # 0b0011_0110_00_0110_1100
    0x07338,  # 0b0001_1100_11_0011_1000
    0x0DB6C,  # 0b0011_0110_11_0110_1100
    0x18CC6,  # 0b0110_0011_00_1100_0110
    0x30483,  # 0b1100_0001_00_1000_0011
]
UNUSABLE_FACE = [
    0x30783,  # 0b1100_0001_11_1100_0001
    0x18CC6,  # 0b0110_0011_00_0110_0011
    0x0D86C,  # 0b0011_0110_00_0011_0110
    0x07038,  # 0b0001_0100_00_0001_1100
    0x0D86C,  # 0b0011_0110_00_0011_0110
    0x18CC6,  # 0b0110_0011_00_0110_0011
    0x30483,  # 0b1100_0001_00_1100_0001
]
PYTHON_SHELL_FACE = [
    0x00222,  # 0b000_0000_01_0001_00010,
    0x00444,  # 0b000_0000_10_0010_00100,
    0x00888,  # 0b000_0001_00_0100_01000,
    0x00444,  # 0b000_0000_10_0010_00100,
    0x1E222,  # 0b011_1100_01_0001_00010,
    0,
    0,
]


## Handle events from the BLE module.
def blerx(args):
    for x in args:
        ## Locate an optional value given by an '='
        nv = x.split("=", 1)
        name = nv[0]
        value = nv[1] if len(nv) > 1 else None

        ## Handle the received stuff.
        if name == "emote":
            ## Select a random emote.
            if (not value) or (value == "random"):
                emote.random()
                pyb.delay(2500)
            ## Parse a specific emote to draw.
            else:
                emstr = ubinascii.unhexlify(value).decode("ascii")
                emote.render(emstr)
                pyb.delay(2500)
        if name == "awoo":
            from boop import beep
            delay = 0
            ## Someone started a howl
            msg = beep()
            while delay < 5000:
                draw_result = msg.draw()
                pyb.delay(msg.interval)
                delay += msg.interval
                if draw_result:
                    break # The animation indicated it was over.


def ble():
    line = badge.ble.readline().decode("ascii")
    if settings.debug:
        print(line)
    try:
        event, x = line.split(":", 1)
        args = x.rstrip().split()
        if event == "rx":
            blerx(args)
    except Exception:
        return


class Main:
    def __init__(self):
        self.available = None
        self.selected = 0
        self.ival = 0
        self.overide_anim = None
        self.anim = None
        self.interactive = settings.debug

    def get_all_animations(self):
        results = []
        module = sys.modules["animations"]
        for name in dir(module):
            x = getattr(module, name)
            if isinstance(x, type) and name[:1] != "_":
                results.append(x)
        print("ALL", results)
        return results

    def set_animation(self, sel):
        if self.available is None:
            try:
                self.available = self.get_all_animations()
            except Exception as e:
                self.available = []
                if self.interactive:
                    raise e
                else:
                    print(e)
        if not self.available:
            dcfurs.set_frame(UNUSABLE_FACE)
            return None
        try:
            self.selected = sel % len(self.available)
            while self.selected < 0:
                self.selected = len(self.available) + self.selected
            self.anim = self.available[self.selected]()
            print(self.anim.__class__.__name__)
            return
        except Exception as e:
            dcfurs.set_frame(EXCEPTION_FACE)
            if self.interactive:
                raise e
            else:
                print(e)
                return None

    def handle_events(self):
        ## Change animation on button press, or emote if both pressed.
        left = badge.left.event()
        right = badge.right.event()
        if right and left:
            emote.random()
            self.ival += 50
        elif right:
            self.set_animation(self.selected + 1)
        elif left:
            self.set_animation(self.selected - 1)
        # Service events.
        if badge.ble.any():
            ble()
        if badge.boop.event():
            badge.ble.write('tx: awoo\r\n')
            override = None
            if hasattr(self.anim, "boop") and callable(getattr(self.anim, "boop")):
                override = self.anim.boop()
            else:
                override = emote.boop()
                self.ival = 1000
            if override is not None:
                # Return an animation that is a one-shot animation.
                self.overide_anim = override
                self.ival = 0

    def main(self):
        ## Program the serial number into the BLE module, which ought
        ## to have finished booting by now.
        if badge.ble:
            badge.ble_set("serial", "0x%04x" % dcfurs.serial())
            badge.ble_set("cooldown", "%d" % settings.blecooldown)

        ## Select the user's preferred boot animation.
        self.set_animation(0)
        if settings.bootanim:
            try:
                self.set_animation(
                    self.available.index(getattr(animations, settings.bootanim))
                )
            except Exception as e:
                if self.interactive:
                    raise e
                else:
                    print(e)

        while True:
            try:
                if self.ival <= 0 and self.overide_anim:
                    draw_result = self.overide_anim.draw()
                    self.ival = self.overide_anim.interval
                    if draw_result:
                        # The animation indicated it was over.
                        self.overide_anim = None
                if self.ival <= 0 and self.anim:
                    self.anim.draw()
                    self.ival = self.anim.interval
            except Exception as e:
                dcfurs.set_frame(EXCEPTION_FACE)
                self.ival = 1000
                if self.interactive:
                    raise e
                else:
                    print(e)
            self.handle_events()

            ## Run the animation timing
            if self.ival > 50:
                pyb.delay(50)
                self.ival -= 50
            else:
                pyb.delay(self.ival)
                self.ival = 0
            ## Attempt to suspend the badge between animations
            badge.trysuspend()


main = Main()
if __name__ == "__main__":
    try:
        main.main()
    except Exception as e:
        if not main.interactive:
            dcfurs.set_frame(UNUSABLE_FACE)
        raise e
    except KeyboardInterrupt as e:
        # Shiny python shell face
        dcfurs.set_frame(PYTHON_SHELL_FACE)
        # Make life easier.
        main.interactive = True
        raise e
