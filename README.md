# x-post

A lightweight Linux desktop application for posting to X (Twitter) without distractions. Built with Python and PyQt6.

## Features

- **Distraction-Free**: Post without viewing your timeline.
- **Media Support**: Attach images/videos or paste images directly from your clipboard (`Ctrl+V`).
- **Drag & Drop**: Drag files into the window to attach them.
- **Keyboard Shortcuts**:
    - `Ctrl+Enter`: Post tweet.
    - `Esc`: Close window.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/IlyaasK/x-post.git
    cd x-post
    ```

2.  **Install dependencies**:
    This project uses `uv` for dependency management.
    ```bash
    uv sync
    ```
    **System Dependencies**: You must have `gtk4` and `gtk4-layer-shell` installed on your system.
    - Arch: `sudo pacman -S gtk4 gtk4-layer-shell libadwaita`
    - Fedora: `sudo dnf install gtk4 gtk4-layer-shell libadwaita`
    - Ubuntu/Debian: `sudo apt install libgtk-4-dev libgtk4-layer-shell-dev`

## Configuration

1.  **API Keys**: You need a valid X Developer Account with Write permissions.
    *   Go to the [X Developer Portal](https://developer.twitter.com/en/portal/dashboard).
    *   Create a **Project** and an **App**.
    *   In your App settings, go to **User authentication settings** and click **Edit**.
        *   **App permissions**: Select **Read and Write**.
        *   **Type of App**: Select **Web App, Automated App or Bot**.
        *   **App info**: Set **Callback URI** and **Website URL** to `http://localhost` (required fields, but not used by this app).
        *   Save settings.
    *   Go to the **Keys and Tokens** tab.
    *   Regenerate **Consumer Keys** (API Key & Secret) and **Authentication Tokens** (Access Token & Secret) to ensure they have the updated permissions.
2.  **Environment Variables**:
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your keys:
    ```ini
    CONSUMER_KEY=your_consumer_key
    CONSUMER_SECRET=your_consumer_secret
    ACCESS_TOKEN=your_access_token
    ACCESS_TOKEN_SECRET=your_access_token_secret
    ```

## Usage

Run the application using the launch script (Recommended):
```bash
./launch.sh
```
*The launch script automatically sets `GDK_BACKEND=wayland` and handles `LD_PRELOAD` fixes required for `gtk4-layer-shell`.*

Or manually:
```bash
GDK_BACKEND=wayland LD_PRELOAD=/usr/lib64/libgtk4-layer-shell.so.0 uv run main.py
```

## Hyprland Integration

To bind the app to a shortcut (e.g., `Super+X`) in Hyprland, add this to your `hyprland.conf`:

```conf
bind = $mainMod, X, exec, /path/to/x-post/launch.sh
```

**Note**: Since this app uses the Wayland Layer Shell protocol, no window rules are needed to force it to float. It will automatically behave like a launcher/overlay.
