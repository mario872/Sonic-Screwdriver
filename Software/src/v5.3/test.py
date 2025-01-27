import board
import time
import array
import pulseio


f = open("/codes.txt", "r")
input()
count = 0
for line in f:
    code = eval(line)
    print(code)
    # If this is a repeating code, extract details
    try:
        repeat = code["repeat"]
        delay = code["repeat_delay"]
    except KeyError:  # by default, repeat once only!
        repeat = 1
        delay = 0
    # The table holds the on/off pairs
    table = code["table"]
    pulses = []  # store the pulses here
    # Read through each indexed element
    for i in code["index"]:
        pulses += table[i]  # and add to the list of pulses
    pulses.pop()  # remove one final 'low' pulse

    with pulseio.PulseOut(
        board.D13, frequency=code["freq"], duty_cycle=2**15
    ) as pulse:
        for i in range(repeat):
            pulse.send(array.array("H", pulses))
            time.sleep(delay)

    time.sleep(code["delay"])
    count += 1