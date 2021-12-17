""" This module test the config file"""
from json import load
import os.path
from ast import literal_eval

def test_config_file_exists():
    """" Tests existance of config file"""
    assert os.path.exists('config.json')

def test_config_contents():
    """ Test content types of config file"""
    with open("config.json", encoding="utf8") as file:
        config = load(file)

    assert isinstance(config["log file path"], str)
    assert isinstance(config["logging level"], str)
    assert isinstance(literal_eval(config["logging level"]), int)

    assert isinstance(config["data handler"], dict)
    assert isinstance(config["data handler"]["location type"], str)
    assert isinstance(config["data handler"]["location"], str)
    assert isinstance(config["data handler"]["nation"], str)

    assert isinstance(config["news handler"], dict)
    assert isinstance(config["news handler"]["news terms"], str)
    assert isinstance(config["news handler"]["request country"], str)
    assert isinstance(config["news handler"]["news api key"], str)
