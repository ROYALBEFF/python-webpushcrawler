import dbus
import dbus.service
from dbus.bus import BusConnection


class NotificationHandler(dbus.service.Object):

    # define static notification service, interface and object path
    service = "org.freedesktop.Notifications"
    interface = "org.freedesktop.Notifications"
    object_path = "/org/freedesktop/Notifications"

    def __init__(self, bus_address):
        """
        Register the org.freedesktop.Notifications service and an object implementing the corresponding interface
        on the given bus. Make sure that the org.freedesktop.Notifications service doesn't exist on the bus yet.

        :param bus_address:
            Address of the desired bus. D-BUS addresses are of the form 'unix:*=*'
        """
        # maximum notification ID is the biggest number that can be represented by 32 bits (uint32)
        self.__max_id = 4294967295
        # start notification IDs at 1 since 0 is not allowed
        self.__id_count = 1

        # get bus name of service on the defined bus connection and create service object
        self.__bus_name = dbus.service.BusName(self.service, bus=BusConnection(bus_address))
        self.__service_object = dbus.service.Object.__init__(self, self.__bus_name, self.object_path)

    @dbus.service.method(dbus_interface=interface, in_signature="susssasa{sv}i", out_signature="u")
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        """
        This function is called when an application calls the Notify member of the org.freedesktop.Notifications
        interface. After finishing this function call a notification ID will be send in response and the notification
        will be send over the D-BUS.

        For more information check out the D-BUS protocol:
        http://www.galago-project.org/specs/notification/0.9/x408.html

        :param app_name:
            String. Name of the application calling the Notify member.
        :param replaces_id:
            Integer.
            Case replaces_id = 0: Assign the next ID (id_count) to this notification.
            Case replaces_id /= 0: Assign the given ID to this notification.
        :param app_icon:
            String. Path to application icon.
        :param summary:
            String. Summary describing the notification text.
        :param body:
            String. Notification text.
        :param actions:
            List. Defining all possible actions that can be invoked.
        :param hints:
            Dictionary. Addition information such as image data.
        :param expire_timeout:
            Integer. Notification expiration time.
        :return:
            Integer. Notification ID.
        """
        # notification id takes the value of the replacement id if its not 0
        notification_id = replaces_id
        if notification_id == 0:
            notification_id = self.__id_count
            self.__id_count += 1
            # if the notification ID exceeds the maximum value, reset it to 1
            if notification_id >= self.__max_id:
                self.__id_count = 1

        # invoke default action such that the browser opens the corresponding URL
        self.ActionInvoked(notification_id, "default")
        # close notification (3 = notification was closed by CloseNotification member)
        self.CloseNotification(notification_id)
        self.NotificationClosed(notification_id, 3)

        return notification_id

    @dbus.service.method(dbus_interface=interface, in_signature="u", out_signature="")
    def CloseNotification(self, notification_id):
        """
        This function is called when an application calls the CloseNotification member of the
        org.freedesktop.Notifications interface. After finishing this function call the notification will be closed.

        For more information check out the D-BUS protocol:
        http://www.galago-project.org/specs/notification/0.9/x408.html

        :param notification_id:
            Integer. Notification ID.
        """
        pass

    @dbus.service.method(dbus_interface=interface, in_signature="", out_signature="as")
    def GetCapabilities(self):
        """
        This function is called when an application calls the GetCapabilities member of the
        org.freedesktop.Notifications interface. After finishing this function call a list of capabilities will be send
        in response over the D-BUS.

        For more information check out the D-BUS protocol:
        http://www.galago-project.org/specs/notification/0.9/x408.html

        :return:
            List of object capabilities.
        """
        return ['actions', 'body', 'body-markup', 'icon-static', 'persistence', 'sound']

    @dbus.service.method(dbus_interface=interface, in_signature="", out_signature="ssss")
    def GetServerInformation(self):
        """
        This function is called when an application calls the GetServerInformation member of the
        org.freedesktop.Notifications interface. After finishing this function call the name, vendor and version
        of this script will be send in response over the D-BUS.

        For more information check out the D-BUS protocol:
        http://www.galago-project.org/specs/notification/0.9/x408.html

        :return:
            Name, vendor, version as strings.
        """
        return "webcrawler", "webcrawler", "0.1", "0"

    @dbus.service.signal(dbus_interface=interface, signature="us")
    def ActionInvoked(self, notification_id, action):
        """
        This function is called when an ActionInvoked signal (org.freedesktop.Notifications interface) should be emitted.
        After finishing this function call the ActionInvoked signal will be broadcasted over the D-BUS.

        For more information check out the D-BUS protocol:
        http://www.galago-project.org/specs/notification/0.9/x408.html

        :param notification_id:
            Integer. Notification ID.
        :param action:
            String. Action that will be invoked. Possible actions are defined when calling Notify.
        """
        pass

    @dbus.service.signal(dbus_interface=interface, signature="uu")
    def NotificationClosed(self, notification_id, reason):
        """
        This function is called when an NotificationClosed signal (org.freedesktop.Notifications interface) should be
        emitted. After finishing this function call the NotificationClosed signal will be broadcasted over the D-BUS.

        For more information check out the D-BUS protocol:
        http://www.galago-project.org/specs/notification/0.9/x408.html

        :param notification_id:
            Integer. Notification ID.
        :param reason:
            Integer. Number (1-4) defining the reason why the notification was closed.
        """
        pass
