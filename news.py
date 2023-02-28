try:
    from transformers import pipeline
except:
    pass
from newsapi import NewsApiClient

def get_news(company):
    newsapi = NewsApiClient(api_key='c818a98d769b414e8df42930ecdd6910')
    all_articles = newsapi.get_everything(q=company.split(' ')[0]+"company",
                                        from_param='2023-01-27',
                                        to='2023-02-26',
                                        language='en',
                                        sort_by='relevancy',
                                        page=2)

    try:
        sentiment_pipeline = pipeline("sentiment-analysis")
        sentiments = sentiment_pipeline([i["title"] for i in all_articles["articles"][:5]])
    except:
        sentiments = []

    if len(sentiments) == 0:
      return f"could not find any mention of {company} in the news\n<br><br>\n"

    return f"<h2>{company} in the news</h2>\n\n"+"\n<hr>\n".join(["<b>" \
         + i["source"]["Name"]+f": <a href={i['url']}>{i['title']}</a></b>  " \
         + f"(sentiment: {j['label']})\n" for i, j in zip(all_articles["articles"][:5],
           sentiments)]) + "\n<br>\n"


if __name__ == "__main__":  
    print(get_news("Google"))
