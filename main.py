import sys
from crawl import *

async def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <url>")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")
    
    try:
        
        crawl_content = await crawl_site_async(base_url=sys.argv[1])
        
        # if the crawl_content is a dictionary of pages with their details
        if isinstance(crawl_content,dict): 
            print(f'Number of pages: {len(crawl_content)}')
            for item in crawl_content.values():
                print(f"- {item['url']}: {len(item['outgoing_links'])} outgoing links")
                print(f"- Heading: {item['heading']}")
                print(f"- First Paragraph: {item['first_paragraph']}")
                print("")
        
    except Exception as e:
        print(f"Error fetching HTML content: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
