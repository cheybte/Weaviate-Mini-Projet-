import json
import weaviate
from weaviate.classes.config import Configure, Property, DataType

COLLECTION = "FAQ"

def main():
    # Connexion à Weaviate (port 8082 car tu as mappé 8082:8080)
    client = weaviate.connect_to_local(host="weaviate", port=8080, grpc_port=50051)

    try:
        # Recréer la collection proprement
        if client.collections.exists(COLLECTION):
            client.collections.delete(COLLECTION)

        col = client.collections.create(
            name=COLLECTION,
            vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
            properties=[
                Property(name="question", data_type=DataType.TEXT),
                Property(name="answer", data_type=DataType.TEXT),
                Property(name="tag", data_type=DataType.TEXT),
            ],
        )

        # Lire data.json
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Import batch
        with col.batch.dynamic() as batch:
            for obj in data:
                batch.add_object(properties=obj)

        # Tests : plusieurs requêtes (paraphrases)
        queries = [
            "comment je lance weaviate avec docker compose ?",
            "démarrer weaviate en conteneur",
            "installer et exécuter weaviate sur docker",
            "c’est quoi une base vectorielle ?",
            "comment retrouver une réponse par similarité de sens ?",
        ]

        for q in queries:
            res = col.query.near_text(
                query=q,
                limit=1,
                return_properties=["question", "answer", "tag"],
            )

            if not res.objects:
                print("\n=== Query ===")
                print("Q_user :", q)
                print("Aucun résultat.")
                continue

            best = res.objects[0]
            print("\n=== Query ===")
            print("Q_user :", q)
            print("Top1 Q :", best.properties["question"])
            print("Top1 A :", best.properties["answer"])
            print("Tag    :", best.properties["tag"])

    finally:
        client.close()

if __name__ == "__main__":
    main()