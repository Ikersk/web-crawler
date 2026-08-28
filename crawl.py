import urllib.parse

def normalize_url(input_url: str) -> str | None:
    try:
        splitted = urllib.parse.urlsplit(input_url)
        if not splitted.netloc:
            return None
        
        final_path = f"{splitted.netloc}{splitted.path.rstrip("/")}"
        return final_path.lower()
    
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__} - {e}")