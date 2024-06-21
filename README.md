# html-wash
Does some HTML "washing" so that the HTML can then be sent to an LLM and use less tokens.

## What "Washing" Means
The process of "washing" HTML involves cleaning and optimizing HTML content to reduce token usage when sent to a language model. This includes:

- Removing HTML comments.
- Allowing only specific HTML tags and attributes.
- Replacing `<b>` tags with `<strong>`, and `<div>` tags with `<p>`.
- Adding missing `alt` attributes to `<img>` tags.
- Minifying the cleaned HTML to remove unnecessary spaces and reduce size.

## Pull and Run the Docker Image
To use the pre-built Docker image from Docker Hub, follow these instructions:

### Pull the Docker Image
Pull the latest Docker image from Docker Hub:
```
docker pull joesofteng/html-wash:latest
```

### Run the Docker Container
Run the Docker container with the correct settings:
```
docker run --name html-wash -d --restart unless-stopped -p 1010:3001 -e PORT=3001 joesofteng/html-wash:latest
```

## Test the Endpoint
Use cURL to test the deployed service and ensure comments are removed and HTML is minified:
```
curl -X POST http://127.0.0.1:1010/wash -d 'html=<figure><!-- This is a comment --><img src="image.jpg"><figcaption>An example image</figcaption></figure>'
```
