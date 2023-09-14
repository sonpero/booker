# ----->    extract info from book file
import os
import re
import requests
from datetime import datetime
from PIL import Image
from io import StringIO, BytesIO
from html.parser import HTMLParser
from typing import Type

# PyMuPDF
import fitz
from ebooklib import epub

from .configuration import storage_directory
from .extract_cover import get_epub_cover


# directory = conf.directory
files = os.listdir(storage_directory)


class MetadataExplorer:
    def __init__(self, path_to_book: str) -> None:
        """
        Initialize MetadataExplorer with the path to the ebook file.

        Args:
            path_to_book (str): The path to the ebook file.
        """
        self.path_to_book = path_to_book
        self.file_extension = None
        self.metadata = {}

    def run(self) -> dict[str, str]:
        """
        Run the metadata extraction process and return the extracted metadata.

        Returns:
            dict[str, str]: A dictionary containing extracted metadata.
        """
        self.init_metadata()
        self.find_file_extension()
        self.extract_metadata()
        return self.metadata

    def init_metadata(self) -> None:
        """
        Initialize the metadata dictionary with default values.
        """
        self.metadata['title'] = self.path_to_book \
            .split('/')[-1].split('.')[0]
        topics = ['creator', 'description', 'date', 'publisher']
        for topic in topics:
            self.metadata[topic] = None

    def extract_metadata(self) -> None:
        """
        Extract metadata from the ebook file based on its extension.
        """
        fetch_metadata_from_file = {'epub': self.epub_info,
                                    'pdf': self.pdf_info,
                                    'mobi': self.epub_info}

        try:
            fetch_metadata_from_file[self.file_extension]()
        except KeyError:
            print(f'file extension {self.file_extension} not managed')

    def epub_info(self) -> None:
        """
        Extract metadata from an EPUB file.
        """
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

    def pdf_info(self) -> None:
        """
        Extract metadata from a PDF file.
        """
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

    def find_file_extension(self) -> None:
        """
        Determine the file extension and store it in metadata.
        """
        self.file_extension = self.path_to_book.split('.')[-1]
        self.metadata['file_extension'] = self.file_extension
        self.metadata['path_to_book'] = self.path_to_book


class GoogleApiCaller:
    def __init__(self, book_reference: Type[MetadataExplorer]):
        """
        Initialize a GoogleApiCaller with book reference metadata.

        Args:
            book_reference (Type[MetadataExplorer]): An instance of
            MetadataExplorer containing book metadata.
        """
        self.title = book_reference['title']
        self.author = book_reference['creator']
        self.google_data = None
        self.image_url = None
        self.google_book_metadata = {}

    def run(self) -> dict[str, str]:
        """
        Run the Google Books API calls to fetch metadata and book cover URL.

        Returns:
            dict[str, str]: A dictionary containing Google Books API metadata
            and book cover URL.
        """
        self.api_init()
        self.fetch_metadata()
        self.search_cover()
        return self.google_book_metadata

    def api_init(self) -> None:
        """
        Initialize the Google API by sending a request to search for
        book information based on title and author.
        """
        url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:' \
              f'{self.title}+inauthor:{self.author}'
        response = requests.get(url)
        self.google_data = response.json()

    def fetch_metadata(self) -> None:
        """
        Extract relevant metadata from the Google Books API response.
        """
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

    def search_cover(self) -> None:
        """
        Search for the book cover URL in the Google Books API response.
        """
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


class EbookInfoFetcher:
    def __init__(self, metadata_from_file: Type[MetadataExplorer],
                 metadata_from_google: Type[GoogleApiCaller]) -> None:

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

    def run(self) -> None:
        self.extract_cover()
        self.format_date()

    def extract_cover(self) -> None:
        cover_image = self.extract_cover_from_file()
        if cover_image is None:
            cover_image = self.download_cover()

        if cover_image is None:
            self.set_default_cover()
        else:
            self.cover_image = cover_image
            self.write_cover_to_disk()

    def write_cover_to_disk(self) -> None:
        image = self.cover_image.resize(self.standard_size)
        image = image.convert("RGB")

        cover_file_name = '_'.join(self.title.lower().split(' '))[:50]
        self.absolute_local_path_cover = \
            f'{storage_directory}/cover/{cover_file_name}.jpg'
        self.relative_local_path_cover = f'cover/{cover_file_name}.jpg'

        image.save(self.absolute_local_path_cover)

    def extract_cover_from_file(self) -> Image:
        if self.file_extension == 'epub':
            cover = get_epub_cover(self.path_to_book)
            if cover is None:
                return None
            else:
                image = Image.open(cover)
                return image
        else:
            return None

    def download_cover(self) -> Image:
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

    def format_date(self) -> None:
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

    def set_default_cover(self) -> None:
        self.absolute_local_path_cover = \
            f'{storage_directory}/cover/default_cover.jpeg'
        self.relative_local_path_cover = f'cover/default_cover.jpeg'


class TextStripper(HTMLParser):
    def __init__(self):
        """
        Initialize a TextStripper instance, a subclass of HTMLParser.

        This class is used to extract plain text from HTML content.
        """
        super().__init__()
        self.reset()
        self.strict = False
        self.text = StringIO()

    def handle_data(self, d):
        """
         Handle HTML data by writing it to the internal text buffer.

         Args:
             d (str): The HTML data to be processed.
         """
        self.text.write(d)

    def get_data(self) -> str:
        """
        Get the extracted plain text.

        Returns:
            str: The plain text content extracted from the HTML.
        """
        return self.text.getvalue()


# ebook_info = MetadataExplorer(
#     '/volumes/homes/Alex/ebook/test/Piratage_Informatique.epub').run()
