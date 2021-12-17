""" This module handles all the schedulers"""
import sched
import time
from json import load

scheduler = sched.scheduler(time.time, time.sleep)
print(type(scheduler))
with open("config.json", encoding="utf8") as file:
    config = load(file)

def hhmmss_to_seconds(hhmmss: str) -> int: #need more doc
    """Converts time from 24 hour to seconds elapsed from 00:00

    This function assumes 24 hour input format, but can take time in forma
    hh, hh:mm or hh:mm:ss
    """
    power = 2
    seconds = 0
    for num in hhmmss.split(':'):
        seconds += int(num)*(60**power)
        power -= 1
    return seconds

def time_delay(time_from: str, time_to: str) -> int:
    """Returns as an integer the number of second from time_from to time_to.

    If time_from is hh:mm:ss and time_to is hh:mm the function returns the
    number of seconds between hh:mm:ss and next time the 24 hour time is hh:mm

    Examples:
    HHMMSS=12:00 and hhmm =13:00 , return value = 3600
    HHMMSS=13:00 and hhmm=12:00, return value = 82800
    """
    current_time_secs = hhmmss_to_seconds(time_from)
    update_time_secs = hhmmss_to_seconds(time_to)
    return (update_time_secs - current_time_secs)%86400

def dict2list(dictionary: dict) -> list:
    """Returns all the values in dictonary as a list"""
    return [v for k,v in dictionary.items()]

def scheduler_assertions(update_name: str, event_time: int=0) -> None:
    """ For event with argument = update_name, checks event info

    For every use of this function make sure upadte_name is different.
    """
    # Used to count how many evens there are with arg = update_name
    count = 0
    # searches for event with argument = update_name
    for event in scheduler.queue:
        if event.argument == update_name:
            count += 1
            if event_time:
                # Checks that scheduler has scheduled event at correct time
                assert event.time == event_time
            assert event.priority == 1
            assert event.kwargs == {}
            # Removes event from scheduled event queue
            scheduler.cancel(event)
    # Checks that only one event with argument = update_name was created
    assert count == 1
