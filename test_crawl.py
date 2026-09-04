import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data

class TestCrawl(unittest.TestCase):
    def test_normalize_url_main(self) -> None:
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_http(self) -> None:
            input_url = "http://www.boot.dev/blog/path"
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected)
    
    def test_normalize_url_slash(self) -> None:
            input_url = "https://www.boot.dev/blog/path/"
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected)
    
    def test_normalize_url_invalidinput(self) -> None:
            self.assertEqual(normalize_url("Hello World"), "")
    
    def test_normalize_url_uppercase(self) -> None:
            input_url = "http://www.BOOT.dev/BLOG/path/"
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected)

class TestHeading(unittest.TestCase):
    
    def test_get_heading_from_html_basic(self) -> None:
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)
    
    def test_get_heading_from_html_empty(self) -> None:    
        input_body = "<html><body>Hello</body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
    
    def test_get_heading_from_html_h2(self) -> None: 
        input_body = "<html><body><h2>Test Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected) 

    def test_get_heading_from_html_with_whitespace(self) -> None:
        input_body = "<html><body><h1>      Title        </h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Title"
        self.assertEqual(actual, expected)

class TestParagraph(unittest.TestCase):
        
    def test_get_first_paragraph_from_html_main_priority(self) -> None:
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_basic(self) -> None:
        input_body = "<html><body><p>This is the first paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "This is the first paragraph."
        self.assertEqual(actual, expected)
            
    def test_get_first_paragraph_from_html_no_paragraph(self) -> None:
        input_body = "<html><body><h1>No paragraphs here</h1></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
        
    def test_get_first_paragraph_from_html_paragraph_fallback(self) -> None:
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <h1>no paragraph.</h1>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

class TestHtmlLinks(unittest.TestCase):
    
    def test_get_urls_from_html_absolute(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)
        
    def test_get_urls_from_html_relative(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/login"><span>Iniciar Sesión</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/login"]
        self.assertEqual(actual, expected)
        
    def test_get_urls_from_html_multiple_tags(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a><a href="https://blog.boot.dev"><span>Blog</span></a><a href="https://crawler-test.com/contact"><span>Contacto</span></a><a href="/login"><span>Iniciar Sesión</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com", "https://blog.boot.dev", "https://crawler-test.com/contact", "https://crawler-test.com/login"]
        self.assertEqual(actual, expected)
        
class TestHtmlImages(unittest.TestCase):
        
    def test_get_images_from_html_relative(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)    
    
    def test_get_images_from_html_absolute(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler-test.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)
        
    def test_get_images_from_html_multiple(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"><img src="https://crawler-test.com/banner.jpg" alt="Banner"><img src="http://other.com/footer.png" alt="Footer"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png", "https://crawler-test.com/banner.jpg", "http://other.com/footer.png"]
        self.assertEqual(actual, expected)
        
class TestPageDataExtract(unittest.TestCase):
    
    def test_extract_page_data_basic(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)
        
    def test_extract_page_data_no_heading(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)
        
    def test_extract_page_data_empty(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_main_section(self) -> None:
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <nav><p>Navigation paragraph</p></nav>
            <main>
                <h1>Main Title</h1>
                <p>Main paragraph content.</p>
            </main>
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        self.assertEqual(actual["heading"], "Main Title")
        self.assertEqual(actual["first_paragraph"], "Main paragraph content.")   

     
if __name__ == "__main__":
    unittest.main()