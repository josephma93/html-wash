import os
import logging
from flask import Flask, request
from bs4 import BeautifulSoup, Comment
import htmlmin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def clean_html(input_html):
    logger.info('Starting to clean HTML content.')

    # Parse the HTML snippet using BeautifulSoup with the html5lib parser
    soup = BeautifulSoup(input_html, 'html5lib')

    # Remove comments
    comments_removed = 0
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
        comments_removed += 1
    logger.info(f'Removed {comments_removed} comments from HTML.')

    # List of allowed tags and their allowed attributes
    allowed_tags = {
        'html': [],
        'title': [],
        'body': [],
        'head': [],
        'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': [],
        'hr': [],
        'a': ['href'],
        'i': [],
        'img': ['src', 'width', 'height', 'alt'],
        'ol': [],
        'ul': [],
        'li': [],
        'p': [],
        'strong': [],
        'table': [],
        'tbody': [],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan'],
        'tr': [],
        'figure': [],
        'figcaption': []
    }

    # Remove disallowed tags and attributes
    tags_unwrapped = 0
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()  # Remove the tag but keep its contents
            tags_unwrapped += 1
        else:
            attrs = {key: value for key, value in tag.attrs.items() if key in allowed_tags[tag.name]}
            tag.attrs = attrs
    logger.info(f'Unwrapped {tags_unwrapped} disallowed tags from HTML.')

    # Replace specific tags
    b_tags_replaced = 0
    for b_tag in soup.find_all('b'):
        b_tag.name = 'strong'
        b_tags_replaced += 1
    logger.info(f'Replaced {b_tags_replaced} <b> tags with <strong> tags.')

    div_tags_replaced = 0
    for div_tag in soup.find_all('div'):
        div_tag.name = 'p'
        div_tags_replaced += 1
    logger.info(f'Replaced {div_tags_replaced} <div> tags with <p> tags.')

    # Add missing alt attributes to img tags
    img_tags_updated = 0
    for img_tag in soup.find_all('img'):
        if 'alt' not in img_tag.attrs:
            img_tag['alt'] = ''
            img_tags_updated += 1
    logger.info(f'Added missing alt attributes to {img_tags_updated} <img> tags.')

    # Get the cleaned HTML snippet
    cleaned_html = ''.join(str(tag) for tag in soup.body.contents)

    # Minify the cleaned HTML
    minified_html = htmlmin.minify(cleaned_html, remove_empty_space=True)
    logger.info('Finished cleaning and minifying HTML content.')
    return minified_html


@app.route('/wash', methods=['POST'])
def clean_html_endpoint():
    input_html = request.form.get('html')
    if not input_html:
        logger.error('Invalid input: No HTML content provided.')
        return 'Invalid input', 400

    logger.info('Received HTML content for cleaning.')
    cleaned_html = clean_html(input_html)
    logger.info('Returning cleaned and minified HTML content.')
    return cleaned_html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    logger.info(f'Starting Flask app on port {port}.')
    app.run(host='0.0.0.0', port=port)
