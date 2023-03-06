"""
Provides a function which extracts news stories about a given company
"""
try:
    from transformers import pipeline
except ImportError:
    pipeline = None
from newsapi import NewsApiClient
from templates import NEWS, SENTIMENT


def get_news(company: str) -> str:
    """
    This function gets news about the provided company and returns the HTML content to
    be inserted into the final generated webpage
    :param company: the name of the company to get news about
    :return: html containing news information about the given company
    """
    newsapi = NewsApiClient(api_key="21bf39a548cc4dd6a594ee32b5b5781f")
    all_articles = newsapi.get_everything(
        q=company,
        sources='australian-financial-review,bloomberg,business-insider,business-insider-uk,financial-post,fortune,the-wall-street-journal,reuters',
        language='en',
        page_size=20,
        sort_by="relevancy"
    )['articles']
    news_results = newsapi.get_everything(
        q=company,
        sources='bbc-news,google-news-uk,google-news',
        language='en',
        page_size=20,
        sort_by="relevancy"
    )['articles']
    all_articles.extend(filter(lambda x: company.lower() in x['title'], news_results))
    all_articles.extend(filter(lambda x: company.lower() not in x['title'], news_results))
    if pipeline:
        sentiments = pipeline("sentiment-analysis")(
            [i["title"] for i in all_articles]
        )
    else:
        sentiments = []

    if len(sentiments) == 0:
        return ""
    else:
        content = "".join([NEWS.format(title=i["title"],
                                       date=i["publishedAt"].split("T")[0],
                                       author=i["author"],
                                       publisher=i["source"]["Name"],
                                       link=i["url"]) for i in all_articles[:5]]
                          )
        content += SENTIMENT.format(pos=str(int((100 * sum([i['label'] == "POSITIVE" for i in sentiments]) / len(sentiments)))))
        return content
