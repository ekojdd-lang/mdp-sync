from models.article import Article

# Article test
test_article = {
    "gencod": "9782253159064",
    "titre": "Test",
    "prix": 10.00,
}

article = Article(test_article)
data = article.to_dict()

print(f"Nombre de champs: {len(data)}")
print(f"Champs: {list(data.keys())}")