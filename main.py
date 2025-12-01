import os
import sys
import gi

# Force Wayland backend for Layer Shell
os.environ["GDK_BACKEND"] = "wayland"

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from gui import PostWindow

class XPostApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.ilyaas.xpost",
                         flags=0)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PostWindow(self)
        win.present()

def main():
    app = XPostApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
