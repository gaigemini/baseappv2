# Gunakan Python 3.9 sebagai base image
FROM python:3.9-slim

# Install dependencies dasar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Buat direktori kerja
WORKDIR /app

# Install virtualenv di sistem
RUN pip install --no-cache-dir virtualenv

# Buat virtual environment di dalam direktori kerja
RUN virtualenv /app/venv

# Aktifkan virtual environment dan install library
RUN /app/venv/bin/pip install --no-cache-dir pandasai pandas==1.5.3 numpy==1.23

# Tambahkan virtual environment ke PATH
ENV PATH="/app/venv/bin:$PATH"

# Salin kode aplikasi ke dalam container
COPY . /app

# Perintah default untuk container
CMD ["python"]
