#import the library
from google_play_scraper import app, Sort, reviews
import pandas as pd
import numpy as np

#scrape application metadata
app_id = "coffee.fore2.fore"  # ID aplikasi Fore Coffee
try:
    app_data = app(app_id)
except Exception as e:
    print("Error fetching app data:", e)
    app_data = None

#scrape reviews from users
try:
    user_reviews, _ = reviews(
        app_id,
        lang='id', #Bahasa Indonesia
        country='id', #Negara Indonesia
        sort=Sort.NEWEST, #newest reviews
        count=100 #take 100 reviews
    )
except Exception as e:
    print("Error fetching reviews:", e)
    user_reviews = []

#store application metadata
if app_data:
    app_info = {
        "Title": app_data.get("title", "N/A"),
        "Developer": app_data.get("developer", "N/A"),
        "Rating": app_data.get("score", "N/A"),
        "Reviews Count": app_data.get("reviews", "N/A"),
        "Description": app_data.get("description", "N/A"),
    }
    app_df = pd.DataFrame([app_info])
    app_df.to_csv("app_metadata.csv", index=False)
    print("Metadata aplikasi berhasil disimpan!")
else:
    print("Metadata aplikasi tidak tersedia.")

#store reviews from users
if user_reviews:
    reviews_data = [
        {"Rating": review["score"],
         "Content": review["content"],
         "App Version": review["appVersion"]
        }
        for review in user_reviews
    ]
    reviews_df = pd.DataFrame(reviews_data)
    reviews_df.to_csv("app_reviews.csv", index=False)
    print("Ulasan pengguna berhasil disimpan!")
else:
    print("Tidak ada ulasan pengguna yg tersedia")

#cleaning data
#read data from files
app_df = pd.read_csv("app_metadata.csv")
reviews_df = pd.read_csv("app_reviews.csv")

#normalisasi rating ulasan ke float
reviews_df["Rating"] = reviews_df["Rating"].astype(float)

#potong deskripsi jika terlalu panjang
app_df["Short Description"] = app_df["Description"].apply(lambda x:x[:100] + '   ' if len(x) > 100 else x)

#membersihkan teks dari emoji, tanda baca, dan lainnya
import re
import emoji

def clean_text(text):
    text = text.lower() #ubah tulisan menjadi huruf kecil
    text = emoji.replace_emoji(text, replace='') #hapus emoji
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text) #hapus tanda baca dan karakter khusus
    text = re.sub(r'\st', ' ', text) #hapus spasi ganda
    return text 

#aplikasikan fungsi ke kolom ulasan
app_df["Description"] = app_df["Description"].apply(clean_text)
reviews_df["Content"] = reviews_df["Content"].apply(clean_text)
print(reviews_df.columns)
print(app_df.columns)


#tampilkan data aplikasi dan contoh ulasan
print("Metadata Aplikasi:")
print(app_df.head())
print("\nUlasan pengguna:")
print(reviews_df.head())

#import library
from textblob import TextBlob

#analisis statistik rating
print(f"Rating Aplikasi:{app_df['Rating']}")
print(f"Jumlah Ulasan: {len(reviews_df)}")
print(f"Rating Rata-Rata: {reviews_df['Rating'].mean():.2f}")

#analisis sentimen pd ulasan pengguna
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

#tambahkan kolom sentimen ke dataframe ulasan
reviews_df["Sentiment"] = reviews_df["Content"].apply(analyze_sentiment)

#hitung rata-rata sentimen
average_sentiment = reviews_df["Sentiment"].mean()
print(f"Rata-rata Sentimen: {average_sentiment:.2f}")

#filter ulasan negatif
negative_reviews = reviews_df[reviews_df["Sentiment"] < 0]

#tampilkan ulasan negatif
print("Ulasan Pengguna dengan Sentimen Negatif: ")
print(f"Jumlah Ulasan Negatif:{len(negative_reviews)}")
print(negative_reviews.head())

#filter ulasan positif
positive_reviews = reviews_df[reviews_df["Sentiment"] > 0]

#tampilkan ulasan positif
print("Ulasan Pengguna dengan Sentimen Positif: ")
print(f"Jumlah Ulasan Positif:{len(positive_reviews)}")
print(positive_reviews.head())

#filter ulasan neutral
neutral_reviews = reviews_df[reviews_df["Sentiment"] == 0]
print(f"Jumlah Ulasan Neutral:{len(neutral_reviews)}")
print(neutral_reviews.head())

#visualisasi 
import matplotlib.pyplot as plt
import seaborn as sns

#visualisasi distribusi rating ulasan pengguna
plt.figure(figsize=(8,5))
sns.histplot(reviews_df["Rating"], bins=10, kde=True)
plt.title("Distribusi Rating Ulasan Pengguna")
plt.xlabel("Rating")
plt.ylabel("Frekuensi")
plt.show()

#visualisasi distribusi sentimen ulasan pengguna
plt.figure(figsize=(8, 5))
sns.histplot(reviews_df["Sentiment"], bins=10, kde=True)
plt.title("Distribusi Sentimen Ulasan Pengguna")
plt.xlabel("Sentimen (Negatif ke Positif)")
plt.ylabel("Frekuensi")
plt.axvline(average_sentiment, color='red', linestyle='dashed', linewidth=2, label=f"Rata-Rata: {average_sentiment:.2f}")
plt.legend()
plt.show()