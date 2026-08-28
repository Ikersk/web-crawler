import unittest
from crawl import normalize_url

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


if __name__ == "__main__":
    unittest.main()