import argparse
from argparse import RawTextHelpFormatter
from webpushcrawler.WebPushCrawler import WebPushCrawler
import time


def __logger(url, title, content):
    with open('log.txt', 'a') as f:
        f.write(url+'\n')
        f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl web page contents on incoming WebPush notifications.\n'
                                                 'In order to register the notification service, this script must be '
                                                 'executed in the context of a new D-BUS.\n\n'
                                                 'dbus-run-session -- python3 example.py',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('--jar', metavar='PATH', type=str, required=True, help='Path to Selenium server JAR file.')
    parser.add_argument('--profile', metavar='PATH', type=str, required=True, help='Path to Firefox profile directory.')
    parser.add_argument('--gui', action='store_true', default=False, help='Run Firefox with GUI.')
    args = parser.parse_args()

    wpc = WebPushCrawler(__logger, args.jar, args.profile, not args.gui)
    time.sleep(100)
    wpc.close()
