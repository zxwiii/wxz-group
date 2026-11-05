import os
import shutil
import json

# Create directories
os.makedirs("src/layouts", exist_ok=True)
os.makedirs("src/pages/news", exist_ok=True)
os.makedirs("src/content/news", exist_ok=True)
os.makedirs("src/data", exist_ok=True)
os.makedirs("public/admin", exist_ok=True)
os.makedirs("public/images/uploads", exist_ok=True)

# 1. Copy data
if os.path.exists("extracted_data/content/all_members.json"):
    shutil.copy("extracted_data/content/all_members.json", "src/data/members.json")

# Copy 64 Markdown news articles to src/content/news/
news_source_dir = "extracted_data/content/news"
if os.path.exists(news_source_dir):
    for f in os.listdir(news_source_dir):
        if f.endswith(".md"):
            shutil.copy(os.path.join(news_source_dir, f), os.path.join("src/content/news", f))

print(f"Copied news to src/content/news/ ({len(os.listdir('src/content/news'))} articles).")
