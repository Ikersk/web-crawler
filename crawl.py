import urllib.parse
from bs4 import BeautifulSoup

def normalize_url(input_url: str) -> str | None: # normalize the url to a standard format, if the url is invalid return None
    try:
        splitted = urllib.parse.urlsplit(input_url)
        if not splitted.netloc:
            return None
        
        final_path = f"{splitted.netloc}{splitted.path.rstrip("/")}"
        return final_path.lower()
    
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")
        
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