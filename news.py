try:
    from transformers import pipeline
except:
    pass
from newsapi import NewsApiClient
from datetime import date, timedelta
from templates import NEWS, SENTIMENT


def get_news(company):
    newsapi = NewsApiClient(api_key="3382308b482b428b83a8fddf4ea6e611")
    today = date.today().strftime("%Y-%m-%d")
    last_month = (date.today() - timedelta(days=28)).strftime("%Y-%m-%d")
    all_articles = newsapi.get_everything(
        q=company.split(" ")[0],
        from_param=last_month,
        to=today,
        language="en",
        sort_by="relevancy",
        page=2,
    )

    try:
        sentiment_pipeline = pipeline("sentiment-analysis")
        sentiments = sentiment_pipeline(
            [i["title"] for i in all_articles["articles"][:5]]
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
                                       link=i["url"]) for i in all_articles["articles"][:5]]
        )
        content += SENTIMENT.format(pos=str(int((100 * sum([i=="POSITIVE" for i in sentiments]) / len(sentiments)))))
        return content


if __name__ == "__main__":
    print(get_news("Google"))