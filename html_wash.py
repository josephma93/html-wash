import logging
import os
from typing import Any, Dict, List, Tuple

import htmlmin
from bs4 import BeautifulSoup, Comment, Tag
from flask import Flask, request, Request
from markdownify import markdownify as md

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

presets: Dict[str, Dict[str, Any]] = {
    'pub-w': {
        'class_names': ('gen-field', 'pswp', 'underlay'),
        'partial_class_names': ('hidden',),
        'attributes': {'type': 'hidden'},
        'class_prefixes': ('dc-', 'du-'),
        'ids': ('tt4', 'tt35', 'questionContainer')
    }
}


def common_html_processing(soup: BeautifulSoup, config: Dict[str, Any]) -> None:
    class_names: Tuple[str, ...] = config.get('class_names', ())
    partial_class_names: Tuple[str, ...] = config.get('partial_class_names', ())
    attributes: Dict[str, str] = config.get('attributes', {})
    class_prefixes: Tuple[str, ...] = config.get('class_prefixes', ())
    ids: Tuple[str, ...] = config.get('ids', ())

    if class_prefixes:
        for element in soup.find_all(
                class_=lambda class_: class_ and any(cls.startswith(class_prefixes) for cls in class_.split())):
            if isinstance(element, Tag):
                element['class'] = [cls for cls in element['class'] if not cls.startswith(class_prefixes)]

    for element in soup.find_all(lambda tag: (
            (tag.has_attr('class') and (
                    any(cls in tag['class'] for cls in class_names) or
                    any(partial_cls in cls for cls in tag['class'] for partial_cls in partial_class_names)
            )) or
            any(tag.get(attr) == value for attr, value in attributes.items()) or
            (tag.has_attr('id') and tag['id'] in ids)
    )):
        element.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()


def remove_disallowed_tags(soup: BeautifulSoup, allowed_tags: Dict[str, List[str]]) -> None:
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            attrs = {key: value for key, value in tag.attrs.items() if key in allowed_tags[tag.name]}
            tag.attrs = attrs


def minify_html(soup: BeautifulSoup) -> str:
    cleaned_html = ''.join(str(tag) for tag in (soup.body.contents if soup.body else soup.contents))
    return htmlmin.minify(cleaned_html, remove_empty_space=True)


def clean_html(input_html: str, config: Dict[str, Any]) -> str:
    logger.info('Starting to clean HTML content.')
    soup = BeautifulSoup(input_html, 'html5lib')

    common_html_processing(soup, config)

    allowed_tags: Dict[str, List[str]] = {
        'html': [], 'title': [], 'body': [], 'head': [],
        'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': [],
        'hr': [], 'a': ['href'], 'i': [], 'img': ['src', 'width', 'height', 'alt'],
        'ol': [], 'ul': [], 'li': [], 'p': [], 'strong': [], 'table': [],
        'tbody': [], 'td': ['colspan', 'rowspan'], 'th': ['colspan', 'rowspan'],
        'tr': [], 'figure': [], 'figcaption': []
    }

    remove_disallowed_tags(soup, allowed_tags)

    minified_html = minify_html(soup)
    logger.info('Finished cleaning and minifying HTML content.')
    return minified_html


def filter_html_for_markdown(input_html: str, config: Dict[str, Any]) -> str:
    logger.info('Starting to filter HTML content for Markdown.')
    soup = BeautifulSoup(input_html, 'html5lib')

    common_html_processing(soup, config)

    allowed_tags: Dict[str, List[str]] = {
        'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': [],
        'p': [], 'a': ['href'], 'ul': [], 'ol': [], 'li': [], 'blockquote': [],
        'code': [], 'pre': [], 'img': ['src', 'alt'], 'strong': [], 'em': [],
        'table': [], 'thead': [], 'tbody': [], 'tr': [], 'th': [], 'td': [],
        'hr': [], 'br': []
    }

    remove_disallowed_tags(soup, allowed_tags)

    filtered_html = minify_html(soup)
    logger.info('Finished filtering HTML content for Markdown.')
    return filtered_html


def convert_html_to_markdown(input_html: str, config: Dict[str, Any]) -> str:
    logger.info('Starting to convert HTML to Markdown.')

    filtered_html = filter_html_for_markdown(input_html, config)
    markdown_content = md(str(filtered_html))

    logger.info('Finished converting HTML to Markdown.')
    return markdown_content


def retain_puppeteer_attributes(soup: BeautifulSoup) -> None:
    allowed_attributes = {'id', 'class', 'name', 'type', 'href', 'alt', 'placeholder'}
    for tag in soup.find_all(True):
        attrs = {key: value for key, value in tag.attrs.items() if key in allowed_attributes or key.startswith('data-')}
        tag.attrs = attrs


def clean_html_for_puppeteer(input_html: str, config: Dict[str, Any]) -> str:
    logger.info('Starting to clean HTML content for Puppeteer.')
    soup = BeautifulSoup(input_html, 'html5lib')

    common_html_processing(soup, config)
    retain_puppeteer_attributes(soup)

    minified_html = minify_html(soup)
    logger.info('Finished cleaning and minifying HTML content for Puppeteer.')
    return minified_html


def get_cleanup_config(req: Request) -> Dict[str, Any]:
    cleanup_preset = req.form.get('cleanup-preset')
    config: Dict[str, Any] = {
        'class_names': (),
        'partial_class_names': (),
        'attributes': {},
        'class_prefixes': (),
        'ids': ()
    }
    if cleanup_preset and cleanup_preset in presets:
        config.update(presets[cleanup_preset])

    class_names = req.form.getlist('class_names')
    if class_names:
        config['class_names'] = tuple(class_names)

    partial_class_names = req.form.getlist('partial_class_names')
    if partial_class_names:
        config['partial_class_names'] = tuple(partial_class_names)

    attributes = {key: req.form.get(key) for key in req.form.getlist('attributes')}
    if attributes:
        config['attributes'].update(attributes)

    class_prefixes = req.form.getlist('class_prefixes')
    if class_prefixes:
        config['class_prefixes'] = tuple(class_prefixes)

    ids = req.form.getlist('ids')
    if ids:
        config['ids'] = tuple(ids)

    return config


@app.route('/wash', methods=['POST'])
def clean_html_endpoint() -> tuple[str, int] | str:
    input_html = request.form.get('html')
    if not input_html:
        logger.error('Invalid input: No HTML content provided.')
        return 'Invalid input', 400
    config = get_cleanup_config(request)
    logger.info('Received HTML content for cleaning.')
    cleaned_html = clean_html(input_html, config)
    logger.info('Returning cleaned and minified HTML content.')
    return cleaned_html


@app.route('/filter-markdown', methods=['POST'])
def filter_html_for_markdown_endpoint() -> tuple[str, int] | str:
    input_html = request.form.get('html')
    if not input_html:
        logger.error('Invalid input: No HTML content provided.')
        return 'Invalid input', 400
    config = get_cleanup_config(request)
    logger.info('Received HTML content for filtering for Markdown.')
    filtered_html = filter_html_for_markdown(input_html, config)
    logger.info('Returning filtered HTML content for Markdown.')
    return filtered_html


@app.route('/markdownify', methods=['POST'])
def convert_html_to_markdown_endpoint() -> tuple[str, int] | str:
    input_html = request.form.get('html')
    if not input_html:
        logger.error('Invalid input: No HTML content provided.')
        return 'Invalid input', 400
    config = get_cleanup_config(request)
    logger.info('Received HTML content for filtering for Markdown.')
    markdown_content = convert_html_to_markdown(input_html, config)
    logger.info('Returning filtered HTML content and converted to Markdown.')
    return markdown_content


@app.route('/wash-pptr', methods=['POST'])
def clean_html_for_puppeteer_endpoint() -> tuple[str, int] | str:
    input_html = request.form.get('html')
    if not input_html:
        logger.error('Invalid input: No HTML content provided.')
        return 'Invalid input', 400
    config = get_cleanup_config(request)
    logger.info('Received HTML content for Puppeteer cleaning.')
    cleaned_html = clean_html_for_puppeteer(input_html, config)
    logger.info('Returning cleaned and minified HTML content for Puppeteer.')
    return cleaned_html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    logger.info(f'Starting Flask app on port {port}.')
    app.run(host='0.0.0.0', port=port)
