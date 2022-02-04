1. Download the [universal-sentence-encoder-large-5](https://tfhub.dev/google/universal-sentence-encoder-large/5) model and place the directory in the project's root.

2. Run OpenSearch locally: `docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" opensearchproject/opensearch:latest`

3. From the project's root folder, run `python src/main.py` (must be Python 3). The indexing of reviews will begin automatically. After the indexing is done, you'll be able to input text to get back reviews which are semantically similar to the text.
