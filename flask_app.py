""" Handles the front-end of the website"""
from time import time
from datetime import datetime
import logging
import pytest
from flask import (
    Flask,
    render_template,
    request
    )
from shared_vars_funcs import (
    scheduler,
    config,
    time_delay,
    dict2list
    )
from covid_data_handler import (
    covid_API_data,
    schedule_covid_updates
    )
from covid_news_handling import (
    news_articles,
    schedule_news_updates,
    remove_news_articles,
    removed_articles
    )

update_dict = {}
refresh_count = []
app = Flask(__name__)

# These logger alteration make the log file cleaner
# sets Flask default logger to level ERROR
logging.getLogger('werkzeug').setLevel(logging.ERROR)
# sets urllib3 loggers to level WARNING
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Configures logger
logging.basicConfig(
    filename=config["log file path"],
    level=int(config["logging level"]),
    format='[%(asctime)s]:%(module)s,line=%(lineno)d:%(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M')

# adding updates to update_dict
for update in ['covid data','news article']:
    update_dict[f'inital {update} update'] = {
        'title': f'inital {update} update',
        'content' : f'{update} will be update at '
        + f'{datetime.now().strftime("%H:%M")} everyday' }

# scheduling updates
schedule_covid_updates(
    update_name = 'inital covid data update',
    update_interval = 0
    )
schedule_news_updates(
    update_name = 'inital news article update',
    update_interval = 0
    )

def events_logger() -> None:
    """ logs all scheduled events at debug level, one update_name at a time"""
    for name in update_dict:
        logging.debug('Lits of scheduled events for update: "%s"', name)
        for event in scheduler.queue:
            if event.argument == name:
                logging.debug(event)

def user_input() -> dict:
    """ Returns possible users inputs as a dict"""
    return {
        'title': request.args.get('two'),
        'update time': request.args.get('update'),
        'repeat': request.args.get('repeat'),
        'data': request.args.get('covid-data'),
        'news': request.args.get('news'),
        'remove update': request.args.get('update_item'),
        'remove news': request.args.get('notif'),
        }

def remove_update(*update_name: str) -> None:
    """ Removes update from update_dict and all related scheduled events"""
    update_name = ''.join(update_name)

    if update_name:
        for event in scheduler.queue:
            if event.argument == update_name:
                scheduler.cancel(event)
        try:
            update_dict.pop(update_name)
        except KeyError:
            log_content = (
                'Tried to remove update %s from updat_dict,'
                + 'but update not in update_dict'
                )
            logging.error(log_content, update_name)

        logging.info('Update "%s" removed', update_name)

def testing() -> None:
    """ Runs pytest every 240 refreshes and logs at info level if test failed or passed"""
    if len(refresh_count) == 239:
        update_dict["TESTING WARNING"] = {
            'title': 'TESTING WARNING',
            'content': 'testing will take place during new refresh'
            }

    elif len(refresh_count) == 240:
        # create temp copies of data
        temp_covid_API_data = covid_API_data.copy()
        temp_news_articles = news_articles[:]
        temp_removed_articles = removed_articles[:]
        # Run all tests
        refresh_count.clear()
        logging.info('%s',  f'{"+"*30}  Test Start  {"+"*30}\n')
        result = pytest.main()
        logging.info('%s',  f'{"+"*30}  Test Ended  {"+"*30}\n')
        if str(result) == 'ExitCode.TESTS_FAILED':
            # Warns user
            logging.warning(
                'One of the tests has failed, needd to be fixed')
        elif str(result) == 'ExitCode.OK':
            # Logs that tests have passed
            logging.info("All tests passed")

        # replaces data with temp copies
        news_articles.clear()
        removed_articles.clear()
        for key, value in temp_covid_API_data.items():
            covid_API_data[key] = value
        for article in temp_news_articles:
            news_articles.append(article)
        for article in temp_removed_articles:
            removed_articles.append(article)

        remove_update('TESTING WARNING')
    # logs number of refreshes
    refresh_count.append(1)

def update_handler() -> None:
    """Schedules new updates

    Takes data from uidata (user input data)
    If enough correct data to make an update has been submitted by the user
    the function schedules the required updates and constructs a string that
    tells the user what the update does (this string will be used as the
    update content for the update widget).
    """
    update_content = str()
    uidata = user_input()
    update_name = uidata["title"]
    update_time = uidata["update time"]
    repeat = bool(uidata["repeat"])
    logging.debug('user input: %s', uidata)

    if bool(update_name): #user cannot submit an update without a title
        repeat = bool(uidata["repeat"])

        # returns True if user has ticked either the news or data boxes
        news_data_exist = bool(uidata["data"]) + bool(uidata["news"])

        # returns True if user has filled in fields required to make an update
        update_valid = news_data_exist and bool(update_time)

        if update_valid:
            current_time = datetime.now().strftime("%H:%M:%S")
            delay_time = time_delay(
                time_from = current_time,
                time_to = update_time)

            # if update with update_name exists, this removes it
            if update_name in update_dict:
                remove_update(update_name)
                # logs the replacement of an update
                logging.warning('%s',(
                        'The user has submitted an update with name '
                        + f'{update_name}. An update with this name '
                        + 'already exists and will be replaced'
                        )
                    )

            if uidata["data"]:
                schedule_covid_updates(
                    update_name = update_name,
                    update_interval = delay_time
                    )
                update_content += 'covid data'

            if uidata["news"]:
                schedule_news_updates(
                update_name = update_name,
                update_interval = delay_time
                )
                update_content += (
                    f'{" & " if bool(uidata["data"]) else ""} news articles'
                    )

            update_content += (f' will be updated at {uidata["update time"]}'
                             + f'{" everyday." if repeat else "."}')

            logging.info(
                'User created update %s',
                f'"{update_name}": {update_content}'
                )

            if not repeat:
                # cancels the defualt repeating of the news and data schedulers
                scheduler.enter(delay_time,2,remove_update,update_name)

        else:
            update_content = (
                'no update has been scheduled because no '
                + f'{"" if bool(update_time) else "time "}'
                + f'{"" if news_data_exist or bool(update_time) else "or "}'
                + 'or '*(1 - news_data_exist or bool(update_time))
                + f'{"" if news_data_exist else "Covid data or news update "}'
                + 'was submitted'
                )

            logging.info(f'Update {update_name} not created because '
                    + update_content)

            update_name += ' (update error)'
            uidata['title'] = update_name
            scheduler.enter(1,1,remove_update,update_name)

        uidata['content'] = update_content
        update_dict[update_name] = uidata

    if uidata["remove update"]:
        try:
            remove_update(uidata["remove update"])
        except KeyError:
            logging.error('user tried to remove an update, '
                          'but update did not exist in update_dict')

    # removes previously removed article from news_articles list
    remove_news_articles(article2remove = uidata['remove news'],)

@app.route('/index')
def index() -> str:
    """ Refreshes data, news, runs schedulers, and return html for website"""
    testing()
    # Makes logger easier to read when debugging
    logging.debug('%s',  f'{"+"*30} Refresh start time: {time()} {"+"*30}\n')
    # if user submits an update a new update is created
    update_handler()
    # runs the scheduler
    scheduler.run(blocking=False)
    events_logger()
    # converts updates_dict into a list (required format for template)
    updates = dict2list(update_dict)
    # Makes logger easier to read when debugging
    logging.debug('%s',  f'{"-"*30} Refresh end time: {time()} {"-"*30}\n\n')
    return render_template('index.html',
        title='Daily update',
        local_7day_infections = covid_API_data["local7days"],
        nation_location= config["data handler"]["nation"],
        national_7day_infections = covid_API_data["nat7days"],
        hospital_cases =
            f'Hospital Cases: {covid_API_data["current_hospital_cases"]}',
        deaths_total = f'Total Deaths: {covid_API_data["total_deaths"]}',
        news_articles = news_articles,
        updates = updates,
        image = "covid19.jpg"
        )

if __name__ == '__main__':
    app.run()
