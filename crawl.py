import urllib.parse
from bs4 import BeautifulSoup
from typing import TypedDict
class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]
    

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
    