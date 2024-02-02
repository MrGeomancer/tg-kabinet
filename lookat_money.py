import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
import logging

import parsing

router = Router()
