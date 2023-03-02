try:
    from transformers import pipeline
except:
    pass
from newsapi import NewsApiClient
from templates import NEWS, SENTIMENT


def get_news(company):
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
    try:
        sentiment_pipeline = pipeline("sentiment-analysis")
        sentiments = sentiment_pipeline(
            [i["title"] for i in all_articles]
        )
    except:
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
