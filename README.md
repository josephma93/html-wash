# html-wash
Does some HTML "washing" so that that HTML can then be sent to an LLM using less tokens.


## Rebuild and Deploy the Docker Image:
Rebuild the Docker image with the updated `app.py`:
```bash
docker build --platform linux/amd64 -t html-wash .
```

Tag the Docker image:
```bash
docker tag html-wash html-wash:latest
```

Save the Docker image to a file:
```bash
docker save -o html-wash.tar html-wash:latest
```

Copy the Docker image to the server:
```bash
scp html-wash.tar username@192.168.1.1:/home/username
```

SSH into the server:
```bash
ssh username@192.168.1.1
```

Load the Docker image on the server:
```bash
docker load -i /home/username/html-wash.tar
```

Stop and remove previous container if any:
```bash
docker stop html-wash && docker rm html-wash
```

Run the Docker container with the correct platform and name:
```bash
docker run --name html-wash -d --restart unless-stopped -p 1010:3001 -e PORT=3001 html-wash:latest
```

## Test the Endpoint:
Use cURL to test the deployed service and ensure comments are removed and HTML is minified:

```bash
curl -X POST http://127.0.0.1:1010/wash -d 'html=<figure><!-- This is a comment --><img src="image.jpg"><figcaption>An example image</figcaption></figure>'
```
