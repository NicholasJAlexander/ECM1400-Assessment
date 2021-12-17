""" Tests functions in covid_news_handling.py"""
from time import time
from shared_vars_funcs import scheduler_assertions
from covid_news_handling import remove_news_articles , removed_articles
from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import news_articles
from covid_news_handling import schedule_news_updates

def article_assertions() -> None:
    """ Checks non-emptyness, type and content of news_articles"""
    assert news_articles
    assert isinstance(news_articles,list)
    for article in news_articles:
        assert isinstance(article,dict)
        assert 'title' in article
        assert 'content' in article

def test_news_API_request():
    """ Tests output of news_API_request"""
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()
    article_assertions()

def test_update_news():
    """ Check that update_news works correctly"""
    # clears news articles
    news_articles.clear()
    update_news('test')
    scheduler_assertions('test')
    article_assertions()

def test_schedule_news_update():
    """ Schedules update and tests it with scheduler_assertions"""
    correct_sched_time = time() + 100
    schedule_news_updates(update_interval = 100,
                          update_name = 'update test')
    scheduler_assertions(update_name = 'update test',
                         event_time = correct_sched_time)

def test_remove_news_articles():
    """ Checks that the function can remove news articles"""
    news_articles.clear()
    test_article = {
        'title': 'test title',
        'content': 'test content'
        }
    prev_removed_article = {
        'title': 'previously removed',
        'content': 'previously removed'
        }
    news_articles.append(test_article)
    news_articles.append(prev_removed_article)
    removed_articles.append(prev_removed_article)
    # This should only remove the test article, because update=False
    remove_news_articles(article2remove = 'test title', update = False)
    assert test_article not in news_articles
    # Since update=True this should remove prev_removed_article from
    # news_articles, but not from removed_articles
    remove_news_articles(update = True)
    assert prev_removed_article not in news_articles
    # Finally since prev_removed_article in not in news_articles and
    # update=True, prev_removed_article is removed from removed_articles
    remove_news_articles(update = True)
    assert prev_removed_article not in removed_articles
