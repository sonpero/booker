import pytest
import os
from PIL import Image

import booker.catalog.configuration as conf
from booker.catalog.ebook_info import EbookInfoFetcher

directory = conf.directory
path_to_test_book = f'{directory}/le_petit_prince.epub'
# Define sample metadata for testing
sample_metadata_from_file = {
    'path_to_book': path_to_test_book,
    'title': 'Sample Book Title',
    'file_extension': 'epub',
    'creator': 'Sample Author',
    'publisher': 'Sample Publisher',
    'date': '2022-01-01',
    'description': 'Sample Book Description',
}

sample_metadata_from_google = {
    'authors': ['Sample Author'],
    'subtitle': 'Sample Subtitle',
    'categories': ['Fiction', 'Fantasy'],
    'pageCount': 300,
    'language': 'English',
    'previewLink': 'https://preview-link.com',
    'infoLink': 'https://info-link.com',
    'image_url': 'https://image-url.com/cover.jpg',
}


@pytest.fixture
def ebook_info_fetcher_instance():
    # Create an instance of EbookInfoFetcher for testing
    return EbookInfoFetcher(sample_metadata_from_file,
                            sample_metadata_from_google)


def test_extract_cover(ebook_info_fetcher_instance):
    # Test the extract_cover method
    ebook_info_fetcher_instance.extract_cover()
    assert isinstance(ebook_info_fetcher_instance.cover_image,
                      type(Image.new('RGB', (1, 1))))


def test_write_cover_to_disk(ebook_info_fetcher_instance):
    # Test the write_cover_to_disk method
    ebook_info_fetcher_instance.extract_cover()
    ebook_info_fetcher_instance.write_cover_to_disk()
    assert os.path.exists(ebook_info_fetcher_instance.absolute_local_path_cover)


def test_format_date(ebook_info_fetcher_instance):
    # Test the format_date method
    ebook_info_fetcher_instance.format_date()
    assert ebook_info_fetcher_instance.published_date == '2022-01-01'


def test_set_default_cover(ebook_info_fetcher_instance):
    # Test the set_default_cover method
    ebook_info_fetcher_instance.set_default_cover()
    assert os.path.exists(ebook_info_fetcher_instance.absolute_local_path_cover)
