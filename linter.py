import pylint.lint
pylint_opts = [
    'test_config.py', # 10
    'shared_vars_funcs.py', # 10
    'test_shared_vars_funcs.py', # 10
    'flask_app.py', # 10
    'covid_data_handler.py', # 9.55
    'test_covid_data_handler.py', # 9.65
    'covid_news_handling.py', # 9.56
    'test_covid_news_handling.py', # 9.77
    ]
pylint.lint.Run(pylint_opts)
