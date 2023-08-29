
# ----->    extract info from book file
import os

# PyMuPDF
import fitz
import requests

from ebooklib import epub

directory = '/volumes/homes/Alex/ebook/test'
files = os.listdir(directory)


class EbookInfoFetcher:
    def __init__(self, path_to_book):
        self.path_to_book = path_to_book
        self.title = None
        self.author = None
        self.google_data = None
        self.subtitle = None
        self.publisher = None
        self.published_date = None
        self.description = None
        self.categories = None
        self.page_count = None
        self.language = None
        self.preview_link = None
        self.info_link = None
        self.image_url = None
        self.run()

    def run(self):
        self.find_title_and_author_from_file()
        self.google_api_init()
        self.google_api_fetch_metadata()
        self.google_api_search_cover()

    def find_title_and_author_from_file(self):
        file_extension = self.path_to_book[-3:]
        fetch_metadata_from_file = {'pub': self.epub_info,
                                    'pdf': self.pdf_info}
        fetch_metadata_from_file[file_extension]()

    def epub_info(self):
        book = epub.read_epub(self.path_to_book)
        self.title = book.get_metadata('DC', 'title')[0][0]
        self.author = book.get_metadata('DC', 'creator')[0][0]

    def pdf_info(self):
        book = fitz.open(self.path_to_book)
        metadata = book.metadata
        self.title = metadata.get("title", "unknown title")
        self.author = metadata.get("author", "unknown author")
        book.close()

    def google_api_init(self):
        url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:' \
              f'{self.title}inauthor:{self.author}'

        response = requests.get(url)
        self.google_data = response.json()

    def google_api_fetch_metadata(self):
        if self.google_data['totalItems'] > 0:
            book_info = self.google_data['items'][0]['volumeInfo']
            google_title = book_info['title']
            book_info_item = ['subtitle', 'authors', 'publisher',
                              'publishedDate',
                              'description', 'categories', 'pageCount',
                              'language',
                              'previewLink', 'infoLink']

            for item in book_info_item:
                try:
                    globals()[f'google_{item}'] = book_info[item]
                except KeyError:
                    globals()[f'google_{item}'] = None

            # select 1st non null
            self.author = ', '.join(google_authors or self.author)
            self.title = google_title or self.title
            self.subtitle = google_subtitle
            self.publisher = google_publisher
            self.published_date = google_publishedDate
            self.description = google_description
            self.categories = google_categories
            self.page_count = google_pageCount
            self.language = google_language
            self.preview_link = google_previewLink
            self.info_link = google_infoLink

        else:
            print(f'nothing found for {self.title}')

    def google_api_search_cover(self):
        if self.google_data['totalItems'] > 0:
            for item in self.google_data['items']:
                book_info = item['volumeInfo']
                self.image_url = book_info.get('imageLinks', {}).get('thumbnail')
                if self.image_url:
                    break

            # todo: test if image_url not none
            # download cover thumbnail
            cover_file_name = '_'.join(self.title.lower().split(' '))
            response = requests.get(self.image_url)
            with open(cover_file_name + ".jpg", "wb") as f:
                f.write(response.content)
        else:
            pass


ebook_info = EbookInfoFetcher('/volumes/homes/Alex/ebook/test/le_petit_prince.epub')
ebook_info.title