import dcfurs
from animations import _jsonanim


class owo:
    interval = 1000

    def draw(self):
        dcfurs.set_row(0, 0x1C00E)
        dcfurs.set_row(1, 0x22011)
        dcfurs.set_row(2, 0x22851)
        dcfurs.set_row(3, 0x22B51)
        dcfurs.set_row(4, 0x22491)
        dcfurs.set_row(5, 0x22011)
        dcfurs.set_row(6, 0x1C00E)


class boop:
    interval = 1000

    def draw(self):
        dcfurs.set_row(0, 0x0E48E)
        dcfurs.set_row(1, 0x12B52)
        dcfurs.set_row(2, 0x12B52)
        dcfurs.set_row(3, 0x0EB4E)
        dcfurs.set_row(4, 0x02492)
        dcfurs.set_row(5, 0x02012)
        dcfurs.set_row(6, 0x0200E)
        # Return true to indicate that this one-shot animation is done
        return True


class inverting_boop:
    # Change the `boop` function in `emote.py` in use `inverting_boop`.
    interval = 250

    def __init__(self):
        self.count = 0

    def draw(self):
        mask = 0x3FFFF if self.count % 2 == 0 else 0
        dcfurs.set_row(0, mask ^ 0x0E48E)
        dcfurs.set_row(1, mask ^ 0x12B52)
        dcfurs.set_row(2, mask ^ 0x12B52)
        dcfurs.set_row(3, mask ^ 0x0EB4E)
        dcfurs.set_row(4, mask ^ 0x02492)
        dcfurs.set_row(5, mask ^ 0x02012)
        dcfurs.set_row(6, mask ^ 0x0200E)
        if self.count >= 6:
            # Return true to indicate that this one-shot animation is done
            return True
        else:
            self.count += 1


class deal_with_it_boop:
    # Change the `boop` function in `emote.py` in use `deal_with_it_boop`.
    def __init__(self):
        self.animation = _jsonanim("animations/DealWithIt.json")

    def draw(self):
        self.animation.draw()
        self.interval = self.animation.interval
        if self.animation.animated_once:
            # Completed the animation. we're done here
            return True

class beep:
    # Change the `boop` function in `emote.py` in use `deal_with_it_boop`.
    def __init__(self):
        self.animation = _jsonanim("animations/beep.json")

    def draw(self):
        self.animation.draw()
        self.interval = self.animation.interval
        if self.animation.animated_once:
            # Completed the animation. we're done here
            return True
