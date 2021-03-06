# Ported from PRAW 3 to 4 and Modified by /u/k_Reign from
# https://github.com/matchu/reddit-countdown 

import praw
import time
from datetime import datetime
from configparser import SafeConfigParser
import re

# This is the name of the config file that the account and subreddit info
# is pulled from.
ConfigFileName = "countdown.cfg"

# This should have one of the following values:
# "every_day"
# "every_hour"
# "every_minute"
UpdateFrequency = "every_minute"

# This will let you print to the console a reminder of the frequency every ReminderUpdate updates
ReminderUpdate = 5

# Computes the new countdown and returns a string with the value.
def compute_time_delta_string(target, targetname):
    countdown_delta = target - datetime.now()
    days = countdown_delta.days
    hours = countdown_delta.seconds // 3600
    minutes = (countdown_delta.seconds - (hours * 3600)) // 60

    # This is just stupid code to make the units plural or singular.
    units = ["days", "hours", "minutes"]
    if days is 1:
        units[0] = "day"
    if hours is 1:
        units[1] = "hour"
    if minutes is 1:
        units[2] = "minute"

    # Starting here, the result string is built depending on how many units we want to display.
    result_string = "["

    if UpdateFrequency is "every_day":
        result_string += str(days) + " " + units[0]
    elif UpdateFrequency is "every_hour":
        result_string += str(days) + " " + units[0] + " " + str(hours) + " " + units[1]
    else:
        result_string += str(days) + " " + units[0] + " " + str(hours) + " " + units[1] + " " + str(minutes) + " " + units[2]

    result_string += "](#" + targetname +")"

    return result_string

# Updates the countdown on the subreddit sidebar
def update_countdown(subreddit, target, targetname):

    description = subreddit.description

    pattern = "\\[[^\\]]*\\]\\(#{0}\\)".format(targetname)
    repl = compute_time_delta_string(target, targetname)
    description = re.sub(pattern, repl, description)

    subreddit.mod.update(description = description)
    print("Updated " + targetname + " to: " + repl)
    
def main():
    config_parser = SafeConfigParser()
    config_parser.read(ConfigFileName)

    # Grab the OAuth info from the config file.
    u_username = config_parser.get('reddit', 'username')
    u_password = config_parser.get('reddit', 'password')
    c_useragent = config_parser.get('reddit', 'user_agent')
    c_id = config_parser.get('reddit', 'id')
    c_secret = config_parser.get('reddit', 'secret')
    
    subreddit_name = config_parser.get('reddit', 'subreddit')
    TargetElementName = config_parser.get('reddit', 'target_element')

    # Login and get our reddit instance.
    reddit = praw.Reddit(client_id = c_id,
                         client_secret = c_secret,
                         password = u_password,
                         user_agent = c_useragent,
                         username = u_username)
    
    target = config_parser.get('reddit', 'target')
    target_datetime = datetime.strptime(target, '%B %d %Y %H:%M')


    # Calculate how long we'll wait depending on the frequency specified.
    num_seconds_to_wait = 60.0
    
    if UpdateFrequency is "every_day":
        num_seconds_to_wait = 60.0 * 60.0 * 24.0
    elif UpdateFrequency is "every_hour":
        num_seconds_to_wait = 60.0 * 60.0
    else:
        num_seconds_to_wait = 60.0

    # Updates according to the frequency specified at the top of the script.
    frequency_reminder_counter = 0
    starttime=time.time()
    while True:
        subreddit = reddit.subreddit(subreddit_name)
        update_countdown(subreddit, target_datetime, TargetElementName)
        
        frequency_reminder_counter += 1
        if frequency_reminder_counter is ReminderUpdate:
            print("Reminder: Updating with this frequency: " + UpdateFrequency)
            frequency_reminder_counter = 0
        
        sleep_time = num_seconds_to_wait - ((time.time() - starttime) % num_seconds_to_wait)         
        time.sleep(sleep_time)
    
if __name__ == '__main__':
    main()
 
