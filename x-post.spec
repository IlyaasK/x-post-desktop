Name:           x-post
Version:        0.1.0
Release:        1%{?dist}
Summary:        A lightweight Linux desktop application for posting to X (Twitter)

License:        MIT
URL:            https://github.com/IlyaasK/x-post
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  gtk4-devel
BuildRequires:  gtk4-layer-shell-devel

Requires:       python3
Requires:       gtk4
Requires:       gtk4-layer-shell
Requires:       libadwaita
Requires:       python3-gobject

%description
A lightweight Linux desktop application for posting to X (Twitter) without distractions.
Uses GTK4 and Layer Shell protocol.

%prep
%setup -q

%install
mkdir -p %{buildroot}/opt/%{name}
cp -r ./* %{buildroot}/opt/%{name}/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<EOF
#!/bin/bash
cd /opt/%{name}
export GDK_BACKEND=wayland
export LD_PRELOAD=/usr/lib64/libgtk4-layer-shell.so.0

# Use the virtual environment python
if [ -f ./.venv/bin/python ]; then
    ./.venv/bin/python main.py
else
    echo "Error: Virtual environment not found in /opt/%{name}/.venv"
    exit 1
fi
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

%files
/opt/%{name}
%{_bindir}/%{name}

%changelog
* Sun Dec 01 2024 IlyaasK <your@email.com> - 0.1.0-1
- Initial package
