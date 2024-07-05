# html-wash

Does some HTML "washing" so that the HTML can then be sent to an LLM and use fewer tokens.

## What "Washing" Means

The process of "washing" HTML involves cleaning and optimizing HTML content to reduce token usage when sent to a
language model. This includes (but not limited to):

- Removing HTML comments.
- Allowing only specific HTML tags and attributes.
- Minifying the cleaned HTML to remove unnecessary spaces and reduce size.

## Features

- **HTML Cleaning:** Removes comments and disallowed tags, retains specific tags and attributes.
- **Markdown Filtering:** Filters HTML content and retains only the tags and attributes usable for Markdown.
- **Markdown Conversion:** Uses the filtered HTML from the Markdown Filtering process and converts it to Markdown using
  the `markdownify` library with default configurations.
- **Puppeteer Cleaning:** Retains only specific attributes useful for Puppeteer.

## Configuration

All endpoints accept the following optional configuration parameters:

- `class_names`: List of class names to remove. Removes any element with a class that matches exactly any of the
  provided class names.
- `partial_class_names`: List of partial class names to remove. Removes any element with a class that contains any of
  the provided partial class names.
- `attributes`: List of attributes to remove. Removes any element with the specified attributes and values.
- `class_prefixes`: List of class prefixes to remove. Removes classes from elements that start with any of the provided
  prefixes, but the element itself is not removed.
- `ids`: List of IDs to remove. Removes any element with an ID that matches exactly any of the provided IDs.
- `cleanup-preset`: Preset configuration for cleanup.

### Preset: `pub-w`

- `class_names`: `gen-field`, `pswp`, `underlay`
- `partial_class_names`: `hidden`
- `attributes`: `type="hidden"`
- `class_prefixes`: `dc-`, `du-`
- `ids`: `tt4`, `tt35`, `questionContainer`

To use a preset, specify `cleanup-preset` with the preset name (e.g., `pub-w`) in your request. Note that if you use
additional configuration parameters along with a preset, the additional parameters will overwrite the corresponding
preset values. This allows you to leverage the benefits of the preset while customizing or adjusting the parameters as
needed.

### Example Configuration Parameters

Here are some example parameters to help you understand how to send these configurations via cURL:

#### Example 1: Removing Specific Classes and IDs

```bash
curl -X POST http://127.0.0.1:1010/wash -d 'html=<div class="remove-me keep-me also-remove" id="delete-this keep-this">Content</div>' -d 'class_names=remove-me' -d 'class_names=also-remove' -d 'ids=delete-this'
```

**After:**

```html
<div class="keep-me" id="keep-this">Content</div>
```

#### Example 2: Removing Elements with Partial Class Names and Specific Attributes

```bash
curl -X POST http://127.0.0.1:1010/wash -d 'html=<div class="hidden-item keep-item partially-hidden">Content</div><input type="hidden"><input type="temp"><input type="text">' -d 'partial_class_names=hidden' -d 'partial_class_names=partially' -d 'attributes=type=hidden' -d 'attributes=type=temp'
```

**After:**

```html
<div class="keep-item">Content</div>
<input type="text">
```

#### Example 3: Removing Classes with Specific Prefixes

```bash
curl -X POST http://127.0.0.1:1010/wash -d 'html=<div class="dc-item du-item other-item keep-item">Content</div>' -d 'class_prefixes=dc-' -d 'class_prefixes=du-'
```

**After:**

```html
<div class="other-item keep-item">Content</div>
```

#### Example 4: Using a Preset with Additional Customization

```bash
curl -X POST http://127.0.0.1:1010/wash -d 'html=<div class="gen-field custom-class another-custom keep-field">Content</div>' -d 'cleanup-preset=pub-w' -d 'class_names=custom-class' -d 'class_names=another-custom'
```

**After:**

```html
<div class="keep-field">Content</div>
```

### Note

When using multiple configuration parameters, each parameter should be sent separately with the `-d` flag in cURL. The
parameters will be applied in the order they are received, with any additional parameters overwriting the corresponding
values in the preset if a preset is used.

## Pull and Run the Docker Image

To use the pre-built Docker image from Docker Hub, follow these instructions:

### Pull the Docker Image

Pull the latest Docker image from Docker Hub:

```bash
docker pull joesofteng/html-wash:latest
```

### Run the Docker Container

Run the Docker container with the correct settings:

```bash
docker run --name html-wash -d --restart unless-stopped -p 1010:3001 -e PORT=3001 joesofteng/html-wash:latest
```

## Endpoints

### Clean HTML

Cleans and minifies the provided HTML content.

```plaintext
POST /wash
Form Data:
- html: The HTML content to be cleaned.
- Optional configuration parameters: class_names, partial_class_names, attributes, class_prefixes, ids, cleanup-preset
```

Example cURL command:

```bash
curl -X POST http://127.0.0.1:1010/wash -d 'html=<figure><!-- This is a comment --><img src="image.jpg"><figcaption>An example image</figcaption></figure>'
```

### Filter HTML for Markdown

Filters HTML content and prepares it for Markdown conversion.

```plaintext
POST /filter-markdown
Form Data:
- html: The HTML content to be filtered for Markdown.
- Optional configuration parameters: class_names, partial_class_names, attributes, class_prefixes, ids, cleanup-preset
```

Example cURL command:

```bash
curl -X POST http://127.0.0.1:1010/filter-markdown -d 'html=<figure><img src="image.jpg"><figcaption>An example image</figcaption></figure>'
```

### Convert HTML to Markdown

Converts the provided HTML content to Markdown.

```plaintext
POST /markdownify
Form Data:
- html: The HTML content to be converted to Markdown.
- Optional configuration parameters: class_names, partial_class_names, attributes, class_prefixes, ids, cleanup-preset
```

This uses the logic of filtering HTML for Markdown first and then converts the filtered HTML to Markdown using
the `markdownify` library with default configurations.

Example cURL command:

```bash
curl -X POST http://127.0.0.1:1010/markdownify -d 'html=<h1>Title</h1><p>Some content.</p>'
```

### Clean HTML for Puppeteer

Cleans HTML content while retaining attributes useful for Puppeteer.

```plaintext
POST /wash-pptr
Form Data:
- html: The HTML content to be cleaned for Puppeteer.
- Optional configuration parameters: class_names, partial_class_names, attributes, class_prefixes, ids, cleanup-preset
```

Example cURL command:

```bash
curl -X POST http://127.0.0.1:1010/wash-pptr -d 'html=<div id="content">Content to be cleaned</div>'
```
