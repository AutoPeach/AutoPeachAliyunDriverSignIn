from .main import main, add_account

MetaInfo = {
    'cron': main,
    'functions': [add_account],
    'storage': ['aliyun_driver']
}
