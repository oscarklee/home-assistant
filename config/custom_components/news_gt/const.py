"""All constants related to the news gt component."""

DOMAIN = "news_gt"
URL_DEFAULT = "https://newsdata.io/api/1/news?apikey=pub_69821953e1e3ae71180716408bb028c7bd25e&country=gt&language=es&category=top"
TITLE_JSON_PATH = "$.results[*].title"
LINK_JSON_PATH = "$.results[*].link"
SUMMARY_JSON_PATH = "$.results[*].description"
IMAGE_JSON_PATH = "$.results[*].image_url"
PUBLISHED_JSON_PATH = "$.results[*].pubDate"