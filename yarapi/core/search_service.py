from datetime import datetime
from typing import List, Dict, Any

from yarapi.config import config
from yarapi.models.schemas import SearchRequest, DataSource
from yarapi.utils.time import parse_relative_interval

from open_sea.searcher.serp_searcher import SerpSearcher
from open_sea.searcher.x_searcher import XSearcher
from open_sea.post_processing.instagram import InstagramPostProcessing
from open_sea.post_processing.facebook import FacebookPostProcessing
from open_sea.post_processing.tiktok import TikTokPostProcessing
from open_sea.post_processing.youtube import YouTubePostProcessing
from open_sea.post_processing.x import XPostProcessing


async def run_search(
    datasource: DataSource, params: SearchRequest
) -> List[Dict[str, Any]]:
    """
    Orchestrates the search and post-processing for the specified data source.
    """
    # 1. Calculate the date range
    if params.relative_interval:
        until_date = datetime.utcnow()
        since_date = until_date - parse_relative_interval(params.relative_interval)
    else:
        until_date = params.until
        since_date = params.since

    # Convert dates to the ISO string format expected by the searchers
    since_iso = since_date.isoformat()
    until_iso = until_date.isoformat()

    # cache_key = serialize_params(params)

    # @lru cache with auto expiry of 1h
    # if mycache["cache_key"]:
    #     return cached

    # 2. Select the Searcher and Post-Processor based on the data source
    if datasource == DataSource.twitter:
        searcher = XSearcher(
            queries=params.queries,
            since=since_iso,
            until=until_iso,
            sort=params.sort,
            max_results=params.max_results,
        )
        post_processor = XPostProcessing(searcher)
    else:
        site_map = {
            DataSource.instagram: "instagram.com",
            DataSource.facebook: "facebook.com",
            DataSource.tiktok: "tiktok.com",
            DataSource.youtube: "youtube.com",
        }
        suffix_map = {
            DataSource.instagram: "inurl:instagram.com/p OR inurl:instagram.com/reel",
            DataSource.facebook: "inurl:photo OR inurl:photos OR inurl:video OR inurl:post OR inurl:watch",
            DataSource.tiktok: "inurl:/video/",
        }

        searcher = SerpSearcher(
            queries=params.queries,
            site=site_map[datasource],
            since=since_iso,
            until=until_iso,
            step=params.step_days,
            max_results=params.max_results,
            country=params.country,
            lang=params.lang,
            query_suffix=suffix_map.get(datasource),
        )

        processor_map = {
            DataSource.instagram: InstagramPostProcessing,
            DataSource.facebook: FacebookPostProcessing,
            DataSource.tiktok: TikTokPostProcessing,
            DataSource.youtube: YouTubePostProcessing,
        }
        post_processor = processor_map[datasource](searcher)

    # 3. Execute the process and capture the results
    results = await post_processor.process(
        raw_output_filename=None, processed_output_filename=None, save_raw=False
    )

    # stored the results in cache
    # mycache["cache_key"] = results

    return results
