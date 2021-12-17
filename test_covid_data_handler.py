""" Tests covid_data_handler module"""
from time import time
from shared_vars_funcs import scheduler_assertions
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import process_API_data
from covid_data_handler import covid_API_request
from covid_data_handler import update_covid_data
from covid_data_handler import schedule_covid_updates

def test_parse_csv_data():
    """ Checks length of parse_csv_data output"""
    data = parse_csv_data('nation_2021-10-28.csv')
    file_not_found =  parse_csv_data('nation_2021-10-29.csv')
    wrong_format = parse_csv_data('nation_2021-10-29.txt')
    assert len(data) == 639
    assert file_not_found is False
    assert wrong_format is False

def test_process_covid_csv_data():
    """ Checks knows output, with parse_csv_data() as argument"""
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    """ Checks the output type of function"""
    data = covid_API_request()
    assert isinstance(data, dict)
    for key, value in data.items():
        assert isinstance(value, list)
        assert isinstance(key, str)
        for day in value:
            assert isinstance(day, dict)

def test_process_API_data():
    """ Calls an API request, processes it and check output types"""
    processed_data = process_API_data(covid_API_request())
    assert isinstance(processed_data, dict)
    assert len(processed_data) == 4
    for key, value in processed_data.items():
        assert isinstance(key, str)
        assert isinstance(value, int)

def test_update_covid_data():
    """ Calls a covid update"""
    processed_data = update_covid_data('update test')
    scheduler_assertions(update_name = 'update test')
    assert isinstance(processed_data, dict)
    for key, value in processed_data.items():
        assert isinstance(key, str)
        assert isinstance(value, int)
    # First creates 2 updates, then calls scheduler_assertions() for each one
    # Tests that calling multiple updates won't cause an error
    for num in range(2):
        update_covid_data(f'update test {num}')
    for num in range(2):
        scheduler_assertions(f'update test {num}')

def test_schedule_covid_updates():
    """ Schedules update and tests it with scheduler_assertions"""
    correct_sched_time = time() + 10
    schedule_covid_updates(update_interval = 10,
                           update_name = 'sched test')
    scheduler_assertions(update_name = 'sched test',
                         event_time = correct_sched_time)
    schedule_covid_updates(update_interval = 0,
                           update_name = 'sched test')
