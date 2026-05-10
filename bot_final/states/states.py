"""
FSM состояния для aiogram 3.x.
"""
from aiogram.fsm.state import State, StatesGroup


class ImageGenStates(StatesGroup):
    waiting_prompt = State()
    waiting_style = State()
    waiting_size = State()
    generating = State()


class MusicSearchStates(StatesGroup):
    waiting_query = State()
    showing_results = State()


class MusicRecognizeStates(StatesGroup):
    waiting_url_or_audio = State()
    recognizing = State()


class SettingsStates(StatesGroup):
    main = State()
    choosing_language = State()
    choosing_style = State()
    choosing_size = State()
