# Web Crawler

An asynchronous Python web crawler that explores pages within a starting domain and writes the collected data to a JSON report. For each page, it records the URL, the first heading, the first paragraph, outgoing links, and image URLs.

## Features

- Asynchronous crawling with configurable concurrency.
- Crawling limited to the starting domain.
- Configurable maximum number of pages.
- Extraction of headings, paragraphs, links, and image URLs.
- JSON output written to `report.json`.

## Requirements

- Python 3.13 or newer
- Internet access for the target website

## Installation

Clone the repository and move into the project directory:

```bash
git clone https://github.com/Ikersk/web-crawler.git
cd web-crawler
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

## Usage

Run the crawler with a starting URL, the maximum number of concurrent requests, and the maximum number of pages to crawl:

```bash
python main.py <url> <max_concurrency> <max_pages>
```

For example:

```bash
python main.py https://example.com 5 50
```

The program displays the crawl configuration and waits for you to press **Enter** before starting. When crawling finishes, the report is saved as `report.json` in the project directory.

### Command-line arguments

| Argument | Description |
| --- | --- |
| `url` | The starting URL. Pages outside this URL's domain are ignored. |
| `max_concurrency` | Maximum number of pages fetched at the same time. |
| `max_pages` | Maximum number of pages included in the crawl. |

## Report format

`report.json` contains an array of page objects. Each object includes:

```json
{
	"url": "https://example.com/",
	"heading": "Example Domain",
	"first_paragraph": "This domain is for use in illustrative examples...",
	"outgoing_links": ["https://example.com/about"],
	"image_urls": ["https://example.com/logo.png"]
}
```

Fields are returned as empty strings or empty arrays when the corresponding content is not found.

## Running the tests

Run the test suite with:

```bash
python -m unittest discover
```

## Future improvements

### Scheduled crawling and email reports

Make the crawler run on a schedule and deploy it to a server. A scheduled job could execute the crawler every hour, day, or week, then email the generated JSON report as an attachment or include a summary of the crawl results in the message. Possible scheduling options include cron, a systemd timer, or a cloud scheduler.

### Graph visualization of page links

Use a graph or data-visualization library to create an image showing the relationships between crawled pages. Each page would be represented as a node, and each outgoing link as an edge. This would make it easier to identify the site's structure, highly connected pages, and isolated sections. Libraries such as NetworkX with Matplotlib, or a browser-based visualization library, could be evaluated for this feature.

## License

No license has been added yet.
