FROM debian AS fet-builder

WORKDIR /fet

COPY ./fet-7.5.5/ .

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libice6 \
    libxtst6 \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxau6 \
    libxdmcp6 \
    qtbase5-dev \
    gcc g++ \
    qt5-qmake \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN qmake fet.pro && make -j 24 && strip fet-cl

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libice6 \
    libxtst6 \
    libnss3 \
    libx11-6 \
    libxcb1 \
    libxau6 \
    libxdmcp6 \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=fet-builder /fet/fet-cl /usr/local/bin/fet-cl

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN rm -rf /app/fet-7.5.5

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app


USER appuser

EXPOSE 8200

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port" , "8200"]