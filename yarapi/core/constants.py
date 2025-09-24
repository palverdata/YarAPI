from yarapi.models.schemas import DataSource
from open_sea.post_processing.instagram import InstagramPostProcessing
from open_sea.post_processing.facebook import FacebookPostProcessing
from open_sea.post_processing.tiktok import TikTokPostProcessing
from open_sea.post_processing.youtube import YouTubePostProcessing

SITE_MAP = {
    DataSource.instagram: "instagram.com",
    DataSource.facebook: "facebook.com",
    DataSource.tiktok: "tiktok.com",
    DataSource.youtube: "youtube.com",
}
SUFFIX_MAP = {
    DataSource.instagram: "inurl:instagram.com/p OR inurl:instagram.com/reel",
    DataSource.facebook: "inurl:photo OR inurl:photos OR inurl:video OR inurl:post OR inurl:watch",
    DataSource.tiktok: "inurl:/video/",
}
PROCESSOR_MAP = {
    DataSource.instagram: InstagramPostProcessing,
    DataSource.facebook: FacebookPostProcessing,
    DataSource.tiktok: TikTokPostProcessing,
    DataSource.youtube: YouTubePostProcessing,
}
