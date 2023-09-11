# ----->    extract info from book file
import os
import re
import requests
from datetime import datetime
# PyMuPDF
import fitz
from ebooklib import epub
from PIL import Image

from io import StringIO, BytesIO
from html.parser import HTMLParser

# from booker.catalog.extract_cover import get_epub_cover
from .extract_cover import get_epub_cover

directory = '/volumes/homes/Alex/ebook/test'
# directory = '/app/test'
files = os.listdir(directory)


class EbookInfoFetcher:
    def __init__(self, metadata_from_file, metadata_from_google):
        self.path_to_book = metadata_from_file['path_to_book']
        self.relative_path_to_book = self.path_to_book.split('/')[-1]
        self.title = metadata_from_file['title']
        self.file_extension = metadata_from_file['file_extension']


        if metadata_from_google['authors'] is None:
            self.author = metadata_from_file['creator']
        else:
            self.author = ', '.join(metadata_from_google['authors'])

        # select 1st non null
        self.publisher = metadata_from_file['publisher'] or \
                                metadata_from_google['publisher']

        self.published_date = metadata_from_file['date'] or \
                                metadata_from_google['publishedDate']

        self.description = metadata_from_file['description'] or \
                                metadata_from_google['description']

        self.subtitle = metadata_from_google['subtitle']
        self.categories = metadata_from_google['categories']
        self.page_count = metadata_from_google['pageCount']
        self.language = metadata_from_google['language']
        self.preview_link = metadata_from_google['previewLink']
        self.info_link = metadata_from_google['infoLink']
        self.image_url = metadata_from_google['image_url']

        self.absolute_local_path_cover = None
        self.relative_local_path_cover = None

        self.standard_size = (250, 400)
        self.cover_image = None

    def run(self):
        self.extract_cover()
        self.format_date()

    def extract_cover(self):
        cover_image = self.extract_cover_from_file()
        if cover_image is None:
            cover_image = self.download_cover()

        if cover_image is None:
            self.set_default_cover()
        else:
            self.cover_image = cover_image
            self.write_cover_to_disk()

    def write_cover_to_disk(self):
        image = self.cover_image.resize(self.standard_size)
        image = image.convert("RGB")

        cover_file_name = '_'.join(self.title.lower().split(' '))[:50]
        self.absolute_local_path_cover = \
            f'/volumes/homes/Alex/ebook/test/cover/{cover_file_name}.jpg'
        self.relative_local_path_cover = f'cover/{cover_file_name}.jpg'

        image.save(self.absolute_local_path_cover)

    def extract_cover_from_file(self):
        if self.file_extension == 'epub':
            cover = get_epub_cover(self.path_to_book)
            if cover is None:
                return None
            else:
                image = Image.open(cover)
                return image
        else:
            return None

    def download_cover(self):
        if self.image_url is None:
            return None
        else:
            # download cover thumbnail
            response = requests.get(self.image_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            else:
                return None

    def format_date(self):
        if (self.published_date is not None) \
                and (type(self.published_date) == str):
            if str(len(self.published_date.split('-'))) == '1':
                date_obj = datetime.strptime(self.published_date, "%Y")
            elif str(len(self.published_date.split('-'))) == '2':
                date_obj = datetime.strptime(self.published_date, "%Y-%m")
            elif str(len(self.published_date.split('-'))) > '2':
                date_obj = datetime.strptime(self.published_date.split('T')[0],
                                             "%Y-%m-%d")
            # test if date_obj is in format yyyy-mm-dd
            if re.match(r"\d{4}-\d{2}-\d{2}", date_obj.strftime("%Y-%m-%d")):
                self.published_date = date_obj.strftime("%Y-%m-%d")
            else:
                self.published_date = None
        else:
            pass

    def set_default_cover(self):
        self.absolute_local_path_cover = \
            f'/volumes/homes/Alex/ebook/test/cover/default_cover.jpeg'
        self.relative_local_path_cover = f'cover/default_cover.jpeg'


class MetadataExplorer:
    def __init__(self, path_to_book):
        self.path_to_book = path_to_book
        self.file_extension = None
        self.metadata = {}

    def run(self):
        self.init_metadata()
        self.find_file_extension()
        self.extract_metadata()
        return self.metadata

    def init_metadata(self):
        self.metadata['title'] = self.path_to_book \
            .split('/')[-1].split('.')[0]
        topics = ['creator', 'description', 'date', 'publisher']
        for topic in topics:
            self.metadata[topic] = None

    def extract_metadata(self):
        fetch_metadata_from_file = {'epub': self.epub_info,
                                    'pdf': self.pdf_info,
                                    'mobi': self.epub_info}

        try:
            fetch_metadata_from_file[self.file_extension]()
        except KeyError:
            print(f'file extension {self.file_extension} not managed')

    def epub_info(self):
        book = epub.read_epub(self.path_to_book)
        topics = ['title', 'creator', 'description', 'date', 'publisher']
        for topic in topics:
            try:
                string_without_html = TextStripper()
                string_without_html.feed(book.get_metadata('DC', topic)[0][0])
                self.metadata[topic] = string_without_html.get_data()
            except IndexError:
                self.metadata[topic] = None
                print(f'missing metadata: {topic}')

    def pdf_info(self):
        book = fitz.open(self.path_to_book)
        pdf_metadata = book.metadata
        self.metadata['title'] = pdf_metadata.get("title", "unknown title")
        self.metadata['creator'] = pdf_metadata.get("author", "unknown author")
        book.close()
        if self.metadata['title'] == '':
            self.metadata['title'] = self.path_to_book \
                .split('/')[-1].split('.')[0]
        else:
            pass

    def find_file_extension(self):
        self.file_extension = self.path_to_book.split('.')[-1]
        self.metadata['file_extension'] = self.file_extension
        self.metadata['path_to_book'] = self.path_to_book


class GoogleApiCaller:
    def __init__(self, book_reference):
        self.title = book_reference['title']
        self.author = book_reference['creator']
        self.google_data = None
        self.image_url = None
        self.google_book_metadata = {}

    def run(self):
        self.api_init()
        self.fetch_metadata()
        self.search_cover()
        return self.google_book_metadata

    def api_init(self):
        url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:' \
              f'{self.title}+inauthor:{self.author}'
        response = requests.get(url)
        self.google_data = response.json()

    def fetch_metadata(self):
        book_info_item = ['subtitle', 'authors', 'publisher',
                          'publishedDate',
                          'description', 'categories', 'pageCount',
                          'language',
                          'previewLink', 'infoLink']

        if self.google_data['totalItems'] > 0:
            book_info = self.google_data['items'][0]['volumeInfo']

            for item in book_info_item:
                try:
                    self.google_book_metadata[item] = book_info[item]
                except KeyError:
                    self.google_book_metadata[item] = None

        else:
            for item in book_info_item:
                self.google_book_metadata[item] = None
            print(f'nothing found for {self.title}')

    def search_cover(self):
        self.google_book_metadata['image_url'] = None
        try:
            if self.google_data['totalItems'] > 0:
                for item in self.google_data['items']:
                    book_info = item['volumeInfo']
                    self.image_url = book_info.get('imageLinks', {}) \
                        .get('thumbnail')
                    if self.image_url:
                        self.google_book_metadata['image_url'] = self.image_url
                        break
            else:
                pass
        except ValueError:
            pass


class TextStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


# ebook_info = MetadataExplorer(
#     '/volumes/homes/Alex/ebook/test/Piratage_Informatique.epub').run()
#
# ebook_api = GoogleApiCaller(ebook_info)
# ebook_api.run()
# ebook_api.author
# toto = ebook_api.google_book_metadata['authors']
# type(toto)