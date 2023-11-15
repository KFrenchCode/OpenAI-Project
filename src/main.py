from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext
import os
import requests
from bs4 import BeautifulSoup
import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize
import gensim
from gensim.summarization import summarize



def main():
    a = 1
    b = 2
    print(a+b)




class SummarizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Content Summarizer")

        # Create and place widgets
        self.create_widgets()

    def create_widgets(self):
        # Label and Entry for URL input
        url_label = tk.Label(self.root, text="Enter URL:")
        url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        # Button to initiate summarization
        summarize_button = tk.Button(self.root, text="Summarize", command=self.summarize_content)
        summarize_button.pack(pady=10)

        # Text widget to display the summary
        self.summary_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=15)
        self.summary_text.pack(pady=10)

    def scrape_content_from_url(self, url):
        # Your existing code for scraping content from a URL
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all('p')
            content = ' '.join([para.text for para in paragraphs])
            return content
        except Exception as e:
            print("Error occurred while scraping:", str(e))
            return None

    def summarize_content(self):
        # Get URL from entry widget
        url = self.url_entry.get()

        # Scrape content from the URL
        content = self.scrape_content_from_url(url)

        if content:
            # Generate summary using gensim's TextRank algorithm
            summary = self.extractive_summarize(content)

            # Display the summary in the text widget
            self.summary_text.delete(1.0, tk.END)  # Clear previous content
            self.summary_text.insert(tk.END, summary)

    def extractive_summarize(self, content):
        summary = summarize(content, ratio=0.2)  # Adjust the ratio as needed
        return summary

if __name__ == "__main__":
    root = tk.Tk()
    app = SummarizerApp(root)
    root.mainloop()

    def basic_summarize(self, content):
        # Your existing code for basic summarization
        sent_detector = nltk.data.load("tokenizers/punkt/english.pickle")
        sentences = sent_detector.tokenize(content.strip())
        
        # Print the sentences for debugging
        print("Sentences:", sentences)
        
        summary = ' '.join(sentences[:2])  # Adjust this to fit your needs
        return summary


if __name__ == "__main__": 
   
    # Initialize the Tkinter app
    root = tk.Tk()

    app = SummarizerApp(root)
    root.mainloop()
