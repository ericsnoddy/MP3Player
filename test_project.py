# third party
import pygame
import pytest
from pygame.event import *
from pygame.locals import *

# local
from project import *
from obj.console import Console

def test_event_handler():
    win, _ = init_pygame()

    console = Console(win, 'reg')

    event = Event(MOUSEBUTTONDOWN, {'pos': (203, 469), 'button': 1, 'touch': False, 'window': None})

    with pytest.raises(pygame.error):
        # Since cs50 environ cannot run pygame mixer music, I test for pygame.error 'music not loaded'
        # Which is what we expect when the play button is activated, as I ensured with the Event() obj
        event_handler(console, event)

def test_init_pygame():
    win, clock = init_pygame()
    assert win.get_height() == 600
    assert win.get_width() == 400
    assert type(clock) == type(pygame.time.Clock())

def test_parse_argv():
    assert parse_argv(['/MusicPlayer/project.py', '-r']) == 'rand'
    assert parse_argv(['/MusicPlayer/project.py', '-R']) == 'rand'
    assert parse_argv(['/MusicPlayer/project.py', '-l']) == 'loop'
    assert parse_argv(['/MusicPlayer/project.py', '-L']) == 'loop'
    assert parse_argv(['/MusicPlayer/project.py']) == 'reg'

def test_parse_argv_invalid1(capfd):
    with pytest.raises(SystemExit) as e:
        parse_argv(['/MusicPlayer/project.py', '-r', '-l'])
        out, _ = capfd.readouterr()
        assert e.type == SystemExit
        assert e.value.code == 0
        assert out == "Invalid command-line argument. '-?' for help."

def test_parse_argv_invalid2(capfd):
    with pytest.raises(SystemExit) as e:
        parse_argv(['/MusicPlayer/project.py', '-r', '-l', '-L'])
        out, _ = capfd.readouterr()
        assert e.type == SystemExit
        assert e.value.code == 0
        assert out == "Invalid command-line argument. '-?' for help."

def test_parse_argv_invalid3(capfd):
    with pytest.raises(SystemExit) as e:
        parse_argv(['/MusicPlayer/project.py', '-T'])
        out, _ = capfd.readouterr()
        assert e.type == SystemExit
        assert e.value.code == 0
        assert out == "Invalid command-line argument. '-?' for help."

def test_parse_argv_help1(capfd):
    with pytest.raises(SystemExit) as e:
        parse_argv(['/MusicPlayer/project.py', '-T', '-?'])
        out, _ = capfd.readouterr()
        assert e.type == SystemExit
        assert e.value.code == 0
        assert out == "-R or -r for random mode XOR -L or -l for loop mode."

def test_parse_argv_help2(capfd):
    with pytest.raises(SystemExit) as e:
        parse_argv(['/MusicPlayer/project.py', '-l', '-R', '-?'])
        out, _ = capfd.readouterr()
        assert e.type == SystemExit
        assert e.value.code == 0
        assert out == "-R or -r for random mode XOR -L or -l for loop mode."

def test_parse_argv_help3(capfd):
    with pytest.raises(SystemExit) as e:
        parse_argv(['/MusicPlayer/project.py', '-?'])
        out, _ = capfd.readouterr()
        assert e.type == SystemExit
        assert e.value.code == 0
        assert out == "-R or -r for random mode XOR -L or -l for loop mode."