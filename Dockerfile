FROM pandoc/latex:3.9

# Install packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    ghostscript

# Create virtual environment for Flask application
RUN python3 -m venv /opt/flask_app

# Copy files and folders
COPY templates /app/templates
COPY csl /app/csl
COPY requirements.txt /app/requirements.txt
COPY md2files.py /app/md2files.py
COPY start_application.py /app/start_application.py
COPY filter /app/filter
COPY webinterface /app/webinterface
COPY images /app/images
COPY tex /app/tex

# Create article folder
RUN mkdir /app/article

# Activate virtual environment and install requirements
RUN /opt/flask_app/bin/pip install -r /app/requirements.txt

# Add virtual environment to PATH
ENV PATH="/opt/flask_app/bin:$PATH"

# Create directories for fonts
RUN mkdir -p /usr/share/fonts/libertinus \
    /usr/share/fonts/libertinus-math \
    /usr/share/fonts/opensans \
    /usr/share/fonts/noto-sans

# Copy fonts
COPY fonts/libertinus/. /usr/share/fonts/libertinus/
COPY fonts/libertinus-math/. /usr/share/fonts/libertinus-math/
COPY fonts/opensans/. /usr/share/fonts/opensans/
COPY fonts/noto-sans/. /usr/share/fonts/noto-sans/

# Update font cache
RUN fc-cache -f -v

# Install tlmgr and packages
RUN tlmgr update --self --all
RUN tlmgr install eso-pic quoting ragged2e lastpage wallpaper lineno footmisc
RUN tlmgr install academicons biblatex-apa babel microtype upquote footnotehyper
RUN tlmgr install xurl xkeyval bookmark hyphenat

# Install packages for new layout
RUN tlmgr install enumitem koma-script amsmath amscls amsfonts tools
RUN tlmgr install booktabs csquotes graphics hyperref xcolor etoolbox
RUN tlmgr --no-verify-downloads install l3kernel l3packages orcidlink noto
RUN tlmgr install libertinus libertinus-otf libertinus-fonts
RUN tlmgr install fontspec biblatex geometry lua-widow-control

# Rebuild TeX filename database after all installs
RUN mktexlsr

# Set the working directory
WORKDIR /app

# Set permissions
RUN chmod +x /app/md2files.py
RUN chmod +x /app/start_application.py

# Running container
ENTRYPOINT ["python3", "/app/start_application.py"]
