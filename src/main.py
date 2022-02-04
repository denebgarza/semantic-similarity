import json

from opensearchpy import OpenSearch
from opensearchpy import helpers

import tensorflow as tf

def embed_text(text):
    vectors = model(text)
    return [vector.numpy().tolist() for vector in vectors]

def create_index():
    print("Creating OpenSearch index")

    client.indices.delete(INDEX_NAME, ignore=[404])
    with open(INDEX_FILE) as index_file:
        source = index_file.read().strip()
        client.indices.create(INDEX_NAME, body=source)

def index_data():
    # Generate the vectors
    with open(REVIEWS_FILE) as reviews_file:
        for line in reviews_file:
            reviews = json.loads(line)
            batch_request = []
            for i, review in enumerate(reviews):
                if i > 1000:
                    break
                print(f"Embedding {i}")
                vector = embed_text([review['t']])
                review['e'] = vector[0]
                batch_request.append({
                    "_index": INDEX_NAME,
                    "_id": i,
                    "_source": review
                })
                # client.index(index = INDEX_NAME, body = review, id = i, request_timeout=30)
                if i % BATCH_SIZE == 0:
                    helpers.bulk(client, batch_request)
                    batch_request = []

if __name__ == "__main__":
    REVIEWS_FILE = "data/reviews.json"
    INDEX_NAME = "reviews"
    INDEX_FILE = "data/index.json"
    BATCH_SIZE = 1000

    client = OpenSearch(
        hosts = [{'host': 'localhost', 'port': 9200}],
        http_compress = True,
        http_auth = ('admin', 'admin'),
        use_ssl = True,
        verify_certs = False
    )

    model = tf.saved_model.load('universal-sentence-encoder-large_5')
    create_index()
    index_data()

    while True:
        query_review = input("Enter review: ")
        vector = embed_text([query_review])[0]
        query = {
            "size": 10,
            "query": {
                "knn": {
                    "e": {
                        "vector": vector,
                        "k": 10
                    }
                }
            }
        }
        results = client.search(
            index = INDEX_NAME,
            body = query
        )
        sources = [result for result in results['hits']['hits']]
        for source in sources:
            print(f"{source['_id']}: {source['_source']['t']}\n")
