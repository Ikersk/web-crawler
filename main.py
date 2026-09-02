import sys
import requests

def get_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")
    
    if response.status_code > 399: 
        raise Exception(f"HTTP error {response.status_code} for URL: {url}")
    
    if "text/html" not in response.headers.get("Content-Type", ""): # check if the content type is a valid HTML page
        raise Exception(f"Content-Type is not text/html for URL: {url}")
    
    return response.text # return the HTML content of the page
    
def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <url>")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")
    
    try:
        html_content = get_html(sys.argv[1])
        print(f"HTML content fetched successfully for URL: {sys.argv[1]}")
        print(html_content)
        
    except Exception as e:
        print(f"Error fetching HTML content: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
