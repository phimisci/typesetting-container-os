FROM pandoc/latex:3.6.4.0-ubuntu

# Install packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

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

# Create article folder
RUN mkdir /app/article

# Create images folder
RUN mkdir /app/images

# Activate virtual environment and install requirements
RUN /opt/flask_app/bin/pip install -r /app/requirements.txt

# Add virtual environment to PATH
ENV PATH="/opt/flask_app/bin:$PATH"

# Create directories for fonts
RUN mkdir -p /usr/share/fonts/libertinus \
    /usr/share/fonts/libertinus-math \
    /usr/share/fonts/opensans

# Copy fonts
COPY fonts/libertinus/. /usr/share/fonts/libertinus/
COPY fonts/libertinus-math/. /usr/share/fonts/libertinus-math/
COPY fonts/opensans/. /usr/share/fonts/opensans/

# Update font cache
RUN fc-cache -f -v

# Install tlmgr and packages
RUN tlmgr update --self --all
RUN tlmgr install orcidlink fancyhdr

# Set the working directory
WORKDIR /app

# Set permissions
RUN chmod +x /app/md2files.py
RUN chmod +x /app/start_application.py

# Running container
ENTRYPOINT ["python3", "/app/start_application.py"]
