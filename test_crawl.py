import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html

class TestCrawl(unittest.TestCase):
    def test_normalize_url_main(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_http(self):
            input_url = "http://www.boot.dev/blog/path"
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected)
    
    def test_normalize_url_slash(self):
            input_url = "https://www.boot.dev/blog/path/"
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected)
    
    def test_normalize_url_invalidinput(self):
            self.assertIsNone(normalize_url("Hello World"))
    
    def test_normalize_url_uppercase(self):
            input_url = "http://www.BOOT.dev/BLOG/path/"
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected)

class TestHeading(unittest.TestCase):
    
    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)
    
    def test_get_heading_from_html_empty(self):    
        input_body = "<html><body>Hello</body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
    
    def test_get_heading_from_html_h2(self): 
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
        
    def test_get_first_paragraph_from_html_main_priority(self):
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
        
    def test_get_first_paragraph_from_html_paragraph_fallback(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <h1>no paragraph.</h1>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)



if __name__ == "__main__":
    unittest.main()