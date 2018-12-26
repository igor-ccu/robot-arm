"""
cmd module:
    execute cmds by saving to commend.txt file
"""
import time

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def sums_up2_90(s):
    angle = s.split()
    return int(angle[1])+int(angle[2])+int(angle[3])==90

def execute(operation, delay=3):
    """ execute raw command from manual, e.g.
    digop 8 0 0
    """
    f = open("commend.txt", "w+")
    f.write(operation)
    f.flush()
    print("Executing {} (delay {} s)".format(operation, delay))
    time.sleep(delay)


def event(operation, delay=3):
    """>> clr
    clears errors
    >> grip_open, grip_close
    gripper switches
    >> light_on, light_off
    light switches
    >> teach_mode_on, teach_mode_off
    teach mode switches (you can move robot by pressing button on your own in this mode)
    >> init_pos
    moves to initial position (0 15 50 25 90 0)
    >> go_zero
    all angles 0 (0 0 0 0 0 0)
    """
    switcher = {
        'clr':"cmdc0",
        'grip_open':"digop 8 0 0",
        'grip_close':"digop 8 1 0",
        'light_on':"digop 8 1 3",
        'light_off':"digop 8 0 3",
        'teach_mode_on':"cmd50 0 1",
        'teach_mode_off':"cmd50 0 0", 
        #'init_pos': "cmd42 0 0 30 45 15 90 0",
        'init_pos': "cmd42 0 0 15 50 25 90 0",
        'go_zero': "cmd42 0 0 0 0 0 0 0"
    }
    if operation in switcher:
        operation_cmd=switcher.get(operation)
        execute(operation_cmd, delay)
        return 
    if operation not in switcher:
        print("No such operation!")
        return

def test_events():
    print('Testing events...')
    operations = ('clr', 'init_pos', 'grip_open', 'grip_close', 'grip_on', 'light_on', 'light_off')
    for operation in operations:
        #print('Event: {}'.format(operation))
        event(operation)
    return

def mv_deg(deg="0 30 45 15 90 0", delay=3):
    if len(deg.split())!=6:
        print("cmd42 expected {}, got {} values".format(6, len(deg.split())))
        return
    for degree in deg.split():
        if is_int(degree) is False:
            print("cmd42 expected int values, got {}".format(degree))
            return
    if sums_up2_90(deg) is False:
        print("theta2+theta3+theta4!=90")
        return
    operation = "cmd42 0"
    execute(operation+" "+deg, delay)
    return

def mv_xyz():
    """needs to be written!!! 
    this is exteremly tricky to move to xyz on the robot, be careful!"""
    return