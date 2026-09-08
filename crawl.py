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
    def __init__(self,base_url) -> None:
        self.base_url = base_url
        self.base_domain = urllib.parse.urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session: aiohttp.ClientSession | None = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self,exc_type: type[BaseException] | None,exc_val: BaseException | None,exc_tb: TracebackType | None,) -> None:
        if self.session is not None:
            await self.session.close() 
    
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if normalized_url in self.page_data:
                return False
            return True
    
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
    
        
    async def crawl_page(self,current_url:str):
         
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
              
        tasks = []
        for url in next_url_list:
            tasks.append(asyncio.create_task(self.crawl_page(url)))
        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data
    
async def crawl_site_async(base_url: str) -> dict:
    async with AsyncCrawler(base_url) as crawler:
        return await crawler.crawl()
 
        

def normalize_url(input_url: str) -> str: # normalize the url to a standard format, if the url is invalid return None
    try:
        splitted = urllib.parse.urlsplit(input_url)
        if not splitted.netloc:
            return ''
        
        final_path = f"{splitted.netloc}{splitted.path.rstrip("/")}"
        return final_path.lower()
    
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        return ''
    
def get_heading_from_html(html: str) -> str: # get the first heading from the html, if no heading return empty string
    
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
    
def get_first_paragraph_from_html(html: str) -> str: # get the first paragraph from the html, if no paragraph return empty string
    
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

def extract_page_data(html: str, page_url: str) -> PageData:
    data: PageData = {'url': page_url,
                    'heading': get_heading_from_html(html),
                    'first_paragraph': get_first_paragraph_from_html(html),
                    'outgoing_links': get_urls_from_html(html, page_url),
                    'image_urls': get_images_from_html(html, page_url)
                    }
    
    return data

def safe_get_html(url: str) -> str | None:
    try:
        return get_html(url)
    except Exception as e:
        print(f"{e}")
        return None
    
def crawl_page(base_url: str, current_url:str | None =None, page_data: dict | None =None):
    
    if page_data == None:
        page_data = {}
        
    if current_url == None:
        current_url = base_url
            
    base_splitted = urllib.parse.urlsplit(base_url)
    current_splitted = urllib.parse.urlsplit(current_url)
    normalized_current_url = normalize_url(current_url)
    
        
    if base_splitted.hostname != current_splitted.hostname:
        return page_data
    
    if normalized_current_url in page_data:
        return page_data
    
    print(f"Crawling {normalized_current_url}")
    current_html = safe_get_html(current_url)
    
    # If the HTML content is successfully fetched (i.e., it's a string), extract the page data and store it in the `page_data` dictionary. 
    # Then, retrieve the list of outgoing URLs from the current page and recursively crawl each of those URLs. 
    # Finally, return the updated `page_data` dictionary. If the HTML content could not be fetched (i.e., it's not a string), simply return the current `page_data` without making any changes.
    if isinstance(current_html,str):
        page_data[normalized_current_url] = extract_page_data(current_html,normalized_current_url)
        next_url_list = get_urls_from_html(current_html,base_url)
        
        for url in next_url_list:
            crawl_page(base_url,url,page_data)
        return page_data
    else:
        return page_data
    
    
    