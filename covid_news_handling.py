""" Handles covid news updates """

import logging
import sys
from datetime import datetime
from newsapi import NewsApiClient
from shared_vars_funcs import (
    scheduler,
    config
    )

news_articles = []
removed_articles = []

newsapi = NewsApiClient(config["news handler"]["news api key"])

def remove_news_articles(article2remove: str='', update: bool=False) -> None:
    """Removes article with title article2remove

    If the user removes a news_article widget, the article will
    be added to the removed_articles list and the news article will be removed
    from the news_articles list.

    Because the news updates returns all news articles, even some those in the
    removed_articles list, the function removes all removed articles from the
    news_articles list, if a removed article is not in the updated
    news_articles then it is removed from the removed_articles list
    """

    # Checks if user has tried to remove an article
    if article2remove:
        for article in news_articles:
            if article['title'] == article2remove:
                removed_articles.append(article)
                news_articles.remove(article)
                break

        logging.info('User removed article with title "%s"', article2remove)

    if update:
        for article in removed_articles:
            # if True, removes article from updated articles
            if article in news_articles:
                news_articles.remove(article)
            # else, removes article from removed_articles
            else:
                removed_articles.remove(article)

def add_article(article: dict):
    """ Adds article to news_articles checking it is not already in news_articles

    This function also ammends the articles content.
    """
    article['content'] = (
            (f'{article["description"]}'
            or 'no content available from api')
            +  f'\n url: {article["url"]}'
            )
    if article not in news_articles:
        news_articles.append(article)

def news_API_request(covid_terms: str='Covid COVID-19 coronavirus') -> list[dict]: # need more doc
    """Returns list of all articles

    from the uk which have one or more of the covid_terms in it's title
    """
    # calls an API request for each word in covid_terms as the query keyword
    for term in covid_terms.split():
        try:
            top_headlines = newsapi.get_top_headlines(
                q=term,
                country=config["news handler"]["request country"]
                )
            # stops the same article being added twice
            if top_headlines['status'] == 'ok':
                for article in top_headlines['articles']:
                    add_article(article)
            elif top_headlines['status'] == 'error':
                logging.error(top_headlines['code'])
                logging.error(top_headlines['message'])
                news_articles.insert(0,
                    {'title': f'News update failed at {error_time}',
                    'content': 'You need to manually remove this widget'}
                )

        except:
            error_time = datetime.now().strftime("%H:%M")
            news_articles.insert(0,
                    {'title': f'News update failed at {error_time}',
                    'content': 'You need to manually remove this widget'}
                )
            logging.error('news update failed: \n\n%s\n',sys.exc_info())
            break

    return news_articles

def update_news(*update_name: str) -> None:
    """Updates the news_articles list

    All atricles returned from the api are added to news_articles and some
    we call remove_news_articles to remove articles already removed. Also a
    news update is scheduled to be processed in 24 hours.
    """
    update_name = ''.join(update_name)
    news_API_request(config["news handler"]["news terms"])
    remove_news_articles(update=True)
    schedule_news_updates(update_name)
    return news_articles

def schedule_news_updates(update_name: str , update_interval: int=86400) -> None:
    """Schedules the function update_news to be call in update_interval seconds"""
    scheduler.enter(update_interval,1,update_news,update_name)
