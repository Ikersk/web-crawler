import os
import sys
from crawl import *
from json_report import write_json_report

async def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <url> <max_concurrency> <max_pages>")
        sys.exit(1)
    else:
        print(f"starting to crawl {sys.argv[1]} with max_concurrency={sys.argv[2]} and max_pages={sys.argv[3]}")
        print("Press Enter to continue...")
        input()
    
    try:
        crawl_content: dict = await crawl_site_async(base_url=sys.argv[1], max_concurrency=int(sys.argv[2]), max_pages=int(sys.argv[3]))
        # if the crawl_content is a dictionary of pages with their details
        if isinstance(crawl_content,dict):
            write_json_report(crawl_content)
            print(f"Report generated successfully. found {len(crawl_content)} pages")
            sys.exit(0)
        
    except Exception as e:
        print(f"Error fetching HTML content: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
