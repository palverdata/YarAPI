from datetime import datetime
from typing import List, Dict, Any

from yarapi.config import config
from yarapi.core.constants import PROCESSOR_MAP, SITE_MAP, SUFFIX_MAP
from yarapi.models.schemas import SearchRequest, DataSource, ProfileInput, CommentsInput
from yarapi.utils.time import parse_relative_interval

from open_sea.searcher.serp_searcher import SerpSearcher
from open_sea.searcher.x_searcher import XSearcher
from open_sea.post_processing.base_serp_postprocessing import BaseSerpPostProcessing

from open_sea.post_processing.x import XPostProcessing


async def run_profile_search(datasource: DataSource, params: ProfileInput):
    """
    Retrieve a single profile from the specified data source.
    """
    # Twitter (X) uses a different searcher/post-processor signature
    if datasource == DataSource.twitter:
        searcher = XSearcher(
            queries=None,
            since=None,
            until=None,
        )
        post_processor = XPostProcessing(searcher)

        result = await post_processor.profile(params.identifier)
        return result

    # Other sources use their respective post-processing classes
    post_processor = PROCESSOR_MAP[datasource](None)

    result = await post_processor.profile(params.identifier)
    return result


async def run_comments_search(datasource: DataSource, params: CommentsInput):
    """
    Retrieve comments for a given post from the specified data source.
    """
    if datasource == DataSource.twitter:
        searcher = XSearcher(
            queries=None,
            since=None,
            until=None,
        )
        post_processor = XPostProcessing(searcher)

        results = await post_processor.comments(params.identifier, amount=params.amount)
        return results

    post_processor: BaseSerpPostProcessing = PROCESSOR_MAP[datasource](None)

    results = await post_processor.comments(params.identifier, amount=params.amount)
    return results


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
        searcher = SerpSearcher(
            queries=params.queries,
            site=SITE_MAP[datasource],
            since=since_iso,
            until=until_iso,
            step=params.step_days,
            max_results=params.max_results,
            country=params.country,
            lang=params.lang,
            query_suffix=SUFFIX_MAP.get(datasource),
        )

        post_processor: BaseSerpPostProcessing = PROCESSOR_MAP[datasource](searcher)

    # 3. Execute the process and capture the results
    results = await post_processor.process(
        raw_output_filename=None, processed_output_filename=None, save_raw=False
    )

    return results
