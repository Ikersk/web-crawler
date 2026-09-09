import asyncio
from types import TracebackType
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup
from typing import TypedDict
import requests
class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

class AsyncCrawler:
    def __init__(self,base_url: str, max_concurrency: int, max_pages: int) -> None:
        self.base_url = base_url
        self.base_domain = urllib.parse.urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session: aiohttp.ClientSession | None = None
        self.max_pages = max_pages  
        self.should_stop: bool = False
        self.all_tasks: set[asyncio.Task] = set()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self,exc_type: type[BaseException] | None,exc_val: BaseException | None,exc_tb: TracebackType | None,) -> None:
        if self.session is not None:
            await self.session.close() 
    
    # This method checks if a page can be added to the crawl data. It ensures that the crawler does not exceed the maximum page limit and that the page has not already been visited. If the maximum page limit is reached, it sets a flag to stop further crawling and cancels any ongoing tasks.
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            
            if self.should_stop:
                return False
            
            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print(f"Reached maximum page limit of {self.max_pages}. Stopping further crawling.")
                for task in self.all_tasks:
                    if not task.done():
                        task.cancel()  
                return False
        
            if normalized_url in self.page_data:
                return False
            
            return True
    
    # This method fetches the HTML content of a given URL using an asynchronous HTTP GET request. It checks for HTTP errors and ensures that the content type is "text/html". If successful, it returns the HTML content as a string; otherwise, it handles exceptions and returns None.
    async def get_html(self,url):
        if self.session is None:
            return None
        try:
            async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
                
                if response.status > 399: 
                    raise Exception(f"HTTP error {response.status} for URL: {url}")
                
                if "text/html" not in response.headers.get("Content-Type", ""): # check if the content type is a valid HTML page
                    raise Exception(f"Content-Type is not text/html for URL: {url}")
                
                return await response.text() 
               
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    # This method is the core of the asynchronous crawling process. It takes a URL, checks if it should be crawled based on domain and visit history, fetches its HTML content, extracts relevant data, and identifies outgoing links. It then recursively creates tasks to crawl each of those outgoing links, while respecting concurrency limits and handling task management.    
    async def crawl_page(self,current_url:str):
        if self.should_stop: # check if the crawling process should be stopped due to reaching the maximum page limit
            print("Crawling stopped.")
            return self.page_data
         
        current_splitted = urllib.parse.urlsplit(current_url)
        normalized_current_url = normalize_url(current_url)
         
        if self.base_domain != current_splitted.netloc:
            return self.page_data
        
        if await self.add_page_visit(normalized_current_url) == False:
            return self.page_data
        
        async with self.semaphore:
            print(f"Crawling {normalized_current_url}")
            current_html = await self.get_html(current_url)
            
            if isinstance(current_html,str):
                async with self.lock:
                    self.page_data[normalized_current_url] = extract_page_data(current_html,current_url)
                next_url_list = get_urls_from_html(current_html,self.base_url)
            else:
                return self.page_data  
        
        tasks: list[asyncio.Task[None]] = [] # list to hold the tasks for crawling the outgoing links
        
        for next_url in next_url_list: # iterate through the list of outgoing links and create a new task for each link to crawl it asynchronously
            task = asyncio.create_task(self.crawl_page(next_url))
            tasks.append(task)
            self.all_tasks.add(task) # add the task to the set of all tasks to keep track of them for potential cancellation if the maximum page limit is reached

        if tasks: # if there are tasks to crawl the outgoing links, gather them and wait for their completion. The `return_exceptions=True` argument allows the gathering to continue even if some tasks raise exceptions, ensuring that the crawling process is robust and can handle errors gracefully.
            try:
                await asyncio.gather(*tasks, return_exceptions=True) # gather the tasks and wait for their completion
            finally:
                for task in tasks:
                    self.all_tasks.discard(task) # remove the completed tasks from the set of all tasks to keep the tracking accurate and prevent memory leaks. This ensures that only active tasks are kept in the set, allowing for proper management of the crawling process.
                            
    # This method initiates the crawling process starting from the base URL. It calls the `crawl_page` method and returns the collected page data once the crawling is complete.
    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data
    
   
# This function serves as a wrapper to initiate the asynchronous crawling process. It creates an instance of the `AsyncCrawler` class with the specified base URL, maximum concurrency, and maximum pages. It then uses an asynchronous context manager to ensure proper resource management and calls the `crawl` method to start the crawling process. Finally, it returns the collected page data as a dictionary.    
async def crawl_site_async(base_url: str, max_concurrency: int, max_pages: int) -> dict:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()
 
# This function normalizes a given URL by splitting it into its components, ensuring that it has a valid network location (netloc), and returning a lowercase string representation of the netloc combined with the path, with any trailing slashes removed. If the URL is invalid or an error occurs during processing, it returns an empty string.
def normalize_url(input_url: str) -> str: 
    try:
        splitted = urllib.parse.urlsplit(input_url)
        if not splitted.netloc:
            return ''
        
        final_path = f"{splitted.netloc}{splitted.path.rstrip("/")}"
        return final_path.lower()
    
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        return ''

# get the first heading from the html, if no heading return empty string
def get_heading_from_html(html: str) -> str:
    
    try:
        soup = BeautifulSoup(html,'html.parser')
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        return ''
    
    # If there is a <h1> tag, return its text. If not, check for a <h2> tag and return its text. If neither is found, return an empty string.
    if soup.find('h1')!= None:
        return soup.find('h1').get_text(strip=True)
    elif soup.find('h2')!= None:
        return soup.find('h2').get_text(strip=True)
    else:
        return ''
# get the first paragraph from the html, if no paragraph return empty string    
def get_first_paragraph_from_html(html: str) -> str:
    
    try:
        soup = BeautifulSoup(html,'html.parser')
        main_soup = soup.find('main')
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        return ''
    
    # If there is a <main> tag, prioritize the first paragraph within it. Otherwise, return the first paragraph found in the entire HTML document. If no paragraphs are found, return an empty string.
    main_soup = soup.find('main')
    if main_soup != None:
        if main_soup.find('p') != None:
            return main_soup.find('p').get_text(strip=True)
        
    if soup.find('p')!= None:
        return soup.find('p').get_text(strip=True)
    else:
        return ''
    
# This function extracts all URLs from the provided HTML content. It uses BeautifulSoup to parse the HTML and find all anchor (<a>) tags. For each anchor tag, it retrieves the href attribute, constructs an absolute URL using the base URL, and appends it to a list. If any errors occur during parsing or URL construction, they are handled gracefully, and an empty list is returned in case of failure.
def get_urls_from_html(html: str, base_url: str) -> list[str]:
    
    try:
        soup = BeautifulSoup(html,'html.parser')
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        return []
    
    url_list = []
    all_tags = soup.find_all('a') # list with all the <a> tags in the form of tag objects so that we can access their attributes and text content
    
    try: 
        for tag in all_tags:
            url_from_tag = tag.get('href')
            absolute_url = urllib.parse.urljoin(base_url,url_from_tag)
            url_list.append(absolute_url)
        
    except Exception as e:
        print(f"{str(e)}: {url_from_tag} is not a valid URL")

    return url_list

# This function extracts all image URLs from the provided HTML content. It uses BeautifulSoup to parse the HTML and find all image (<img>) tags. For each image tag, it retrieves the src attribute, constructs an absolute URL using the base URL, and appends it to a list. If any errors occur during parsing or URL construction, they are handled gracefully, and an empty list is returned in case of failure.
def get_images_from_html(html: str, base_url: str) -> list[str]:
    
    try:
        soup = BeautifulSoup(html,'html.parser')
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        return []
    
    images_url_list = []
    all_tags = soup.find_all('img') # list with all the <img> tags in the form of tag objects so that we can access their attributes and text content
    
    try:
        for tag in all_tags:
            image_url = tag.get('src')
            absolute_url = urllib.parse.urljoin(base_url,image_url)
            images_url_list.append(absolute_url)       
    except Exception as e:
        print(f"{str(e)}: {image_url} is not a valid image URL")
        
    return images_url_list

# This function extracts the main data from a given HTML page and returns it as a `PageData` dictionary. It retrieves the page's URL, heading, first paragraph, outgoing links, and image URLs using the previously defined helper functions.
def extract_page_data(html: str, page_url: str) -> PageData:
    data: PageData = {'url': page_url,
                    'heading': get_heading_from_html(html),
                    'first_paragraph': get_first_paragraph_from_html(html),
                    'outgoing_links': get_urls_from_html(html, page_url),
                    'image_urls': get_images_from_html(html, page_url)
                    }
    
    return data  