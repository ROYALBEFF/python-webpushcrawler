import os
import subprocess
from multiprocessing import Process

import gi.repository.GLib
from dbus.mainloop.glib import DBusGMainLoop

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from webpushcrawler.NotificationHandler import NotificationHandler


class WebPushCrawler:
    def __init__(self, handler, selenium_jar, firefox_profile, headless=True):
        """
        Create new WebPushCrawler. Automatically registers the D-BUS notification service and starts both the Selenium
        server and Firefox.

        :param handler:
            Function. Takes three arguments:
                1. Page URL
                2. Page title
                3. Page source
            Return values will be rejected.
        :param selenium_jar:
            String. Path to Selenium server JAR file.
        :param firefox_profile:
            String. Path to Firefox profile directory.
        :param headless:
            Boolean. Run Firefox in headless mode (default: True).
        """
        # get address of current D-BUS
        self.__dbus_address = os.environ['DBUS_SESSION_BUS_ADDRESS']

        # start D-BUS notification service
        self.__notification_service = Process(target=self.__dbus_notification_service)
        self.__notification_service.start()

        # start Selenium
        self.__selenium_server = self.__selenium(selenium_jar)

        # start Firefox
        self.__browser = Process(target=self.__firefox, args=(handler, firefox_profile, headless))
        self.__browser.start()

    @property
    def dbus_address(self):
        """
        :return:
            Address of current D-BUS.
        """
        return self.__dbus_address.split(',')[0]

    def __dbus_notification_service(self):
        """
        Start org.freedesktop.Notifications service and register a NotificationHandler object that implements the
        org.freedesktop.Notifications interface.
        """
        # start notification service on D-BUS
        DBusGMainLoop(set_as_default=True)
        NotificationHandler(self.__dbus_address)
        mainloop = gi.repository.GLib.MainLoop()
        mainloop.run()

    def __firefox(self, handler, firefox_profile, headless):
        """
        Start Firefox (GeckoDriver).
        Waits for new pages to be loaded, extracts their contents and closes them afterwards.

        :param handler:
            Function. Takes three arguments:
                1. Page URL
                2. Page title
                3. Page source
            Return values will be rejected.
        :param firefox_profile:
            String. Path to Firefox profile directory.
        :param headless:
            Boolean. Run Firefox in headless mode (default: True).
        """
        # load Firefox profile with WebPush subscriptions
        profile = webdriver.FirefoxProfile(firefox_profile)
        # set headless option
        options = webdriver.FirefoxOptions()
        options.set_headless(headless)

        # start Firefox
        browser = webdriver.Firefox(firefox_options=options, firefox_profile=profile)
        browser_wait = WebDriverWait(browser, timeout=100)

        while True:
            for window in browser.window_handles[1:]:
                # open new window and load the corresponding url
                browser.switch_to.window(window)

                # the browser will open a new about:blank window when opening a new url
                # wait until the page url is no longer about:blank
                browser_wait.until_not(ec.url_matches('about:blank'))
                # wait until page is loaded
                browser_wait.until(ec.presence_of_all_elements_located)

                # call handler function to process page data
                handler(browser.current_url, browser.title, browser.page_source)
                # close current window
                browser.close()

    def __selenium(self, selenium_jar):
        """
        Start Selenium server.

        :param selenium_jar:
            String. Path to Selenium server JAR file.
        :return:
            POpen (process) object for further process management.
        """
        # start Selenium server
        return subprocess.Popen(['java', '-jar', selenium_jar])

    def close(self):
        """
        Terminate Selenium/Firefox and notification service processes.
        """
        # terminate Firefox process and close process object to release all corresponding resources
        self.__browser.terminate()
        # wait for Selenium/Firefox to be terminated
        while self.__browser.is_alive():
            pass
        self.__browser.close()

        # try to terminate selenium server three times, kill selenium server when terminating wasn't successful
        for i in range(3):
            try:
                self.__selenium_server.terminate()
                self.__selenium_server.wait(5)
                break
            except subprocess.TimeoutExpired:
                if i == 2:
                    self.__selenium_server.kill()

        # terminate D-BUS notification service and close process object to release all corresponding resources
        self.__notification_service.terminate()
        # wait for the notification service to be terminated
        while self.__notification_service.is_alive():
            pass
        self.__notification_service.close()
