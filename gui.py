import sys
import os
import gi
import tempfile
from PIL import ImageGrab

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')

from gi.repository import Gtk, Gdk, GObject, Gtk4LayerShell, GLib

from x_client import XClient

class PostWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        
        self.client = None
        try:
            self.client = XClient()
        except Exception as e:
            print(f"Failed to initialize X Client: {e}")
            # We might want to show an error dialog here, but for now let's proceed
            # The user will see errors if they try to post

        self.media_paths = []
        self.temp_files = []

        self.init_layer_shell()
        self.init_ui()
        self.apply_css()

    def init_layer_shell(self):
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        
        # Anchor to top
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.LEFT, False)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, False)
        
        # Margins
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.TOP, 100)
        
        # Keyboard interactivity
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.EXCLUSIVE)

    def init_ui(self):
        self.set_default_size(600, 200)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.set_child(main_box)

        # Text Input
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.set_size_request(-1, 100)
        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.connect("changed", self.update_char_count)
        
        # Placeholder text (Gtk4 TextView doesn't have native placeholder, so we simulate or just leave empty)
        # For simplicity, we'll leave it empty for now or add a label above
        
        # Scrolled Window for text view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.text_view)
        scrolled_window.set_vexpand(True)
        main_box.append(scrolled_window)

        # Media Preview
        self.media_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.media_box.set_visible(False)
        main_box.append(self.media_box)

        # Controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.append(controls_box)

        self.attach_btn = Gtk.Button(label="Attach")
        self.attach_btn.connect("clicked", self.attach_media)
        controls_box.append(self.attach_btn)

        self.char_count_label = Gtk.Label(label="0/280")
        controls_box.append(self.char_count_label)

        # Spacer
        spacer = Gtk.Label()
        spacer.set_hexpand(True)
        controls_box.append(spacer)

        self.post_btn = Gtk.Button(label="Post")
        self.post_btn.add_css_class("suggested-action")
        self.post_btn.connect("clicked", self.post_tweet)
        controls_box.append(self.post_btn)

        # Key controller for shortcuts
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

    def apply_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        window {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border-radius: 12px;
        }
        textview {
            background-color: #313244;
            color: #cdd6f4;
            border-radius: 8px;
        }
        text {
            background-color: #313244;
            color: #cdd6f4;
        }
        button {
            background-color: #89b4fa;
            color: #1e1e2e;
            border-radius: 6px;
            font-weight: bold;
            padding: 5px 10px;
        }
        button:hover {
            background-color: #b4befe;
        }
        button:disabled {
            background-color: #45475a;
            color: #6c7086;
        }
        label {
            color: #a6adc8;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_key_pressed(self, controller, keyval, keycode, state):
        # Ctrl+Enter to post
        if (state & Gdk.ModifierType.CONTROL_MASK) and keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            self.post_tweet(None)
            return True
        
        # Esc to close
        if keyval == Gdk.KEY_Escape:
            self.close()
            return True
            
        # Ctrl+V for image paste
        if (state & Gdk.ModifierType.CONTROL_MASK) and keyval == Gdk.KEY_v:
            # We need to check clipboard for image
            # Gtk4 clipboard handling for images is async and a bit complex
            # We'll use Pillow's grabclipboard as a fallback/simplification like before
            self.paste_image_from_clipboard()
            # We don't return True here because we want default text paste to work too if it's text
            
        return False

    def paste_image_from_clipboard(self):
        try:
            img = ImageGrab.grabclipboard()
            if img:
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                img.save(temp_file.name)
                temp_file.close()
                self.add_media(temp_file.name)
                self.temp_files.append(temp_file.name)
        except Exception as e:
            print(f"Paste error: {e}")

    def attach_media(self, button):
        # File chooser dialog
        # In GTK4, FileChooserDialog is deprecated in favor of FileDialog, but for simplicity/compatibility:
        dialog = Gtk.FileChooserDialog(
            title="Select Media",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.ACCEPT
        )
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images & Videos")
        filter_img.add_pattern("*.png")
        filter_img.add_pattern("*.jpg")
        filter_img.add_pattern("*.jpeg")
        filter_img.add_pattern("*.gif")
        filter_img.add_pattern("*.mp4")
        dialog.add_filter(filter_img)
        
        dialog.set_select_multiple(True)
        
        dialog.connect("response", self.on_file_dialog_response)
        dialog.show()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            files = dialog.get_files()
            for f in files:
                path = f.get_path()
                if path:
                    self.add_media(path)
        dialog.destroy()

    def add_media(self, path):
        if len(self.media_paths) >= 4:
            # Show error
            return

        self.media_paths.append(path)
        self.update_media_preview()

    def update_media_preview(self):
        # Clear existing
        child = self.media_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.media_box.remove(child)
            child = next_child

        if not self.media_paths:
            self.media_box.set_visible(False)
            return

        self.media_box.set_visible(True)
        
        for path in self.media_paths:
            try:
                # Load image for preview
                # For video, we might need a generic icon or thumbnailer, but let's try loading as image first
                # or just use a label if it fails
                texture = Gdk.Texture.new_from_filename(path)
                picture = Gtk.Picture.new_for_paintable(texture)
                picture.set_content_fit(Gtk.ContentFit.COVER)
                picture.set_size_request(80, 80)
                self.media_box.append(picture)
            except:
                label = Gtk.Label(label=os.path.basename(path))
                self.media_box.append(label)

    def update_char_count(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        count = len(text)
        self.char_count_label.set_text(f"{count}/280")
        
        if count > 280:
            self.char_count_label.add_css_class("error") # We'd need to define this class
            self.post_btn.set_sensitive(False)
        else:
            self.char_count_label.remove_css_class("error")
            self.post_btn.set_sensitive(True)

    def post_tweet(self, button):
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        
        if not text and not self.media_paths:
            return

        if self.post_btn:
            self.post_btn.set_label("Posting...")
            self.post_btn.set_sensitive(False)
        
        # Process events to show update
        while GLib.MainContext.default().iteration(False):
            pass

        try:
            if self.client:
                self.client.post_tweet(text, self.media_paths)
            self.close()
        except Exception as e:
            print(f"Error posting: {e}")
            if self.post_btn:
                self.post_btn.set_label("Post")
                self.post_btn.set_sensitive(True)

    def close_request(self):
        # Cleanup
        for f in self.temp_files:
            try:
                os.remove(f)
            except:
                pass
        return super().close_request()
