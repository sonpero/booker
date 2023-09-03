
# ----->    extract info from book file
import os
import requests
from datetime import datetime
# PyMuPDF
import fitz
from ebooklib import epub
from PIL import Image
# from .extract_cover import get_epub_cover, default_cover
# from booker.catalog.extract_cover import get_epub_cover, default_cover
from .extract_cover import get_epub_cover, default_cover

directory = '/volumes/homes/Alex/ebook/test'
files = os.listdir(directory)


class EbookInfoFetcher:
    def __init__(self, path_to_book):
        self.path_to_book = path_to_book
        self.relative_path_to_book = path_to_book.split('/')[-1]
        self.title = None
        self.author = None
        self.file_extension = None
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
        self.absolute_local_path_cover = None
        self.relative_local_path_cover = None
        self.run()

    def run(self):
        self.find_title_and_author_from_file()
        self.google_api_init()
        self.google_api_fetch_metadata()
        self.extract_cover()
        self.google_api_search_cover()
        self.set_default_cover()
        self.format_date()

    def find_title_and_author_from_file(self):
        self.file_extension = self.path_to_book.split('.')[-1]
        fetch_metadata_from_file = {'epub': self.epub_info,
                                    'pdf': self.pdf_info,
                                    'mobi': self.epub_info}

        fetch_metadata_from_file[self.file_extension]()

    def epub_info(self):
        book = epub.read_epub(self.path_to_book)
        try:
            self.title = book.get_metadata('DC', 'title')[0][0]
            self.author = book.get_metadata('DC', 'creator')[0][0]
        except IndexError:
            print('missing metadata')

    def pdf_info(self):
        book = fitz.open(self.path_to_book)
        metadata = book.metadata
        self.title = metadata.get("title", "unknown title")
        self.author = metadata.get("author", "unknown author")
        book.close()

    def google_api_init(self):
        url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:' \
              f'{self.title}+inauthor:{self.author}'
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
            self.title = self.title
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

    def extract_cover(self):
        if self.file_extension == 'epub':
            cover = get_epub_cover(self.path_to_book)
            image = Image.open(cover)
            standard_size = (250, 400)
            image = image.resize(standard_size)
            image = image.convert("RGB")
            cover_file_name = '_'.join(self.title.lower().split(' '))[:50]
            self.absolute_local_path_cover = \
                f'/volumes/homes/Alex/ebook/test/cover/{cover_file_name}.jpg'
            self.relative_local_path_cover = f'cover/{cover_file_name}.jpg'
            image.save(self.absolute_local_path_cover)
        else:
            pass

    def google_api_search_cover(self):
        try:
            if self.google_data['totalItems'] > 0 \
                    and self.absolute_local_path_cover is None:
                for item in self.google_data['items']:
                    book_info = item['volumeInfo']
                    self.image_url = book_info.get('imageLinks', {}).get('thumbnail')
                    if self.image_url:
                        break

                # todo: test if image_url not none
                # download cover thumbnail
                cover_file_name = '_'.join(self.title.lower().split(' '))[:50]
                response = requests.get(self.image_url)
                self.absolute_local_path_cover = \
                    f'/volumes/homes/Alex/ebook/test/cover/{cover_file_name}.jpg'
                self.relative_local_path_cover = f'cover/{cover_file_name}.jpg'
                with open(self.absolute_local_path_cover, 'wb') as f:
                    f.write(response.content)
                image = Image.open(self.absolute_local_path_cover)
                standard_size = (250, 400)
                image = image.resize(standard_size)
                image = image.convert("RGB")
                image.save(self.absolute_local_path_cover)
            else:
                pass
        except ValueError:
            pass

    def format_date(self):
        if self.published_date is not None:
            if str(len(self.published_date.split('-'))) == '1':
                date_obj = datetime.strptime(self.published_date, "%Y")
            elif str(len(self.published_date.split('-'))) == '2':
                date_obj = datetime.strptime(self.published_date, "%Y-%m")
            else:
                date_obj = datetime.strptime(self.published_date, "%Y-%m-%d")
            self.published_date = date_obj.strftime("%Y-%m-%d")
        else:
            pass

    def set_default_cover(self):
        if self.absolute_local_path_cover is None:
            image = default_cover(self.title)
            standard_size = (250, 400)
            image.resize(standard_size)
            cover_file_name = '_'.join(self.title.lower().split(' '))
            self.absolute_local_path_cover = \
                f'/volumes/homes/Alex/ebook/test/cover/{cover_file_name}.jpg'
            self.relative_local_path_cover = f'cover/{cover_file_name}.jpg'
            image.save(self.absolute_local_path_cover)



# ebook_info = EbookInfoFetcher('/volumes/homes/Alex/ebook/test/le_petit_prince.epub')
# ebook_info = EbookInfoFetcher('/volumes/homes/Alex/ebook/test/Microsoft_AZURE_DP-900_Data_Fundamentals_by_Abound_Academy.epub')
# ebook_info = EbookInfoFetcher('/volumes/homes/Alex/ebook/test/Docker Complete Guide To Docker For Beginners And Intermediates (Code tutorials Book 6) (Berg, Craig) (Z-Library).epub')
path = '/volumes/homes/Alex/ebook/test/le_petit_prince.epub'
# import ebooklib
# from ebooklib import epub
# book = epub.read_epub(path)
#
# for item in book.get_items():
#     if item.get_type() == ebooklib.ITEM_DOCUMENT:
#         print('==================================')
#         print('NAME : ', item.get_name())
#         print('----------------------------------')
#         print(item.get_content())
#         print('==================================')
#
# cover_image = book.get_item_with_id('cover')
# book.get_metadata('DC', 'title')
# book.get_metadata('DC', 'creator')
# book.get_metadata('DC', 'description')
# book.get_metadata('DC', 'date')
# book.get_metadata('DC', 'identifier')
# book.get_metadata('DC', 'coverage')
# book.get_metadata('DC', 'publisher')
