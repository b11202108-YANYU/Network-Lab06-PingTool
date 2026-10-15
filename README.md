# Python Ping Tool

A lightweight command-line and web Ping tool that sends ICMP echo requests
through the system `ping` utility. The system `ping` command must be installed.

## Setup

Create and activate the virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install the Flask web dependency:

```sh
python -m pip install -r requirements.txt
```

## Usage

```sh
python ping_tool.py example.com
python ping_tool.py -c 2 -W 3 127.0.0.1
```

By default, the tool sends 4 requests and waits up to 1 second for each
response. Output and the exit status come from the system `ping` command.
The web interface accepts IPv4 or IPv6 addresses and limits each test to 20
requests.

## Web interface

Start the web server:

```sh
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser on the same
machine. The server listens on `0.0.0.0:5000`.

## Tests

```sh
python -m unittest -v
```
