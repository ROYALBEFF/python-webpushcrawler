# WebPushCrawler

The `webpushcrawler` package allows you to automatically open URLs on incoming
WebPush notifications and process page information.

Make sure to run your code in the context of a D-BUS that hasn't registered a
`org.freedesktop.Notifications` service yet. You can run your code with a new
D-BUS running it like this:
```
dbus-run-session -- python3 webpushcrawler.py
```

## Python dependencies
The following Python 3 packages are needed:
- `setuptools`
- `dbus-python`
- `PyGObject`
- `selenium`

## Other dependencies
In addition to the above-mentioned Python dependencies you need to
install
- the [Selenium stand-alone server](https://docs.seleniumhq.org/download/)
- and the [Geckodriver](https://github.com/mozilla/geckodriver)

## Installation
When all dependencies are installed you can install the `webpushcrawler` package
with:

```
sudo python3 setup.py install
```
