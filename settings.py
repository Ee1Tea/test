import os
import pathlib
from dotenv import load_dotenv
from logging.config import dictConfig

load_dotenv()

LOL_API_SECRET = os.getenv("LOL_API_TOKEN")

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-10s -  %(name)-15s : %(message)s"
        }
    },
    "handlers": {
        "console": {
            'level': "DEBUG",
            'class': "logging.StreamHandler",
            'formatter': "standard"
        },
        "console2": {
            'level': "WARNING",
            'class': "logging.StreamHandler",
            'formatter': "standard"
        },
        "file": {
            'level': "INFO",
            'class': "logging.FileHandler",
            'filename': "logs/infos.log",
            'mode': "w",
            'formatter': "verbose"
        }
    },
    "loggers": {
        "bot": {
            'handlers': ["console"],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            'handlers': ["console2", "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

BASE_DIR = pathlib.Path(__file__).parent

GENERAL_IMAGE_DIR = 'images/general/'

FONT_DIR = 'images/fonts/'

GENERATED_IMAGE_DIR = 'images/temporary/'

dictConfig(LOGGING_CONFIG)

SUMMONERS = {
    '3': "SummonerExhaust",
    '4': "SummonerFlash",
    '6': "SummonerHaste",
    '7': "SummonerMana",
    '11': "SummonerSmite",
    '12': "SummonerTeleport",
    '13': "SummonerMana",
    '14': "SummonerDot",
    '21': "SummonerBarrier",
    '32': "SummonerSnowball"
}
