# google-starter

# Autocomplete Project

## How to Run

### Initial Run (Build Cache)

If this is your first time running the project, execute the following command in your terminal to build the cache file `cache.pkl`:

```bash
python main.py
```

### Running the Web Interface
To start the graphical web interface using Flask:
```bash
python app.py
```
* The web app will be available at http://localhost:5000.
* It uses the cached database for quick autocomplete queries.

### Example Usage
#### Terminal Interface
```bash
python main.py
```

Then type queries to get autocomplete suggestions. Example:

```bash
Type your query and press Enter.
Type 'exit' to quit.
query: hello worl
 1.  20  Example 478. A hello world task  [File: userguide.txt, Line: 36908]
 2.  20  Example 479. A customizable hello world task  [File: userguide.txt, Line: 36940]
 3.  20             client(ip, port, "Hello World 1")  [File: socketserver.txt, Line: 599]
 4.  20             client(ip, port, "Hello World 2")  [File: socketserver.txt, Line: 600]
 5.  20             client(ip, port, "Hello World 3")  [File: socketserver.txt, Line: 601]
```