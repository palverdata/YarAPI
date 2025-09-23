import os
from yarapi.config import config
from loguru import logger


def rename_envs():
    logger.info("Renaming environment variables...")

    # os.environ["SERP_KEY"] = config.SERPAPI_KEY
    # os.environ["APIFY_TOKEN"] = config.APIFY_KEY
