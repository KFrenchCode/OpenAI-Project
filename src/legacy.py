import tkinter as tk
from typing import Self
import nltk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
from transformers import BartForConditionalGeneration, BartTokenizer
from nntplib import ArticleInfo
from tkinter import DISABLED
import os
import logging
import fitz #PymuPDF library
from PIL import Image



logging.basicConfig(level=logging.DEBUG)

nltk.download('punkt')



class SummarizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memo Tool")

        # Create and place widgets
        self.create_widgets()

        # Load pre-trained BART model and tokenizer
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

    def create_widgets(self):
        # Label and Entry for URL input
        url_label = tk.Label(self.root, text="Enter URL:")
        url_label.pack(pady=5, padx=10)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        # Button to initiate summarization
        summarize_button = tk.Button(self.root, text="Summarize", command=self.summarize_content)
        summarize_button.pack(pady=10)

        # Text widget to display the summary
        self.summary_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=15)
        self.summary_text.pack(pady=10, padx=10, ipadx=10, ipady=10, expand=True)


    def scrape_content(self, source):
        try:
            if source.startswith("http"):
                # If the source starts with "http", treat it as a URL
                response = requests.get(source)

                # Use a context manager for file handling
                with open("scraped_content.html", "w", encoding="utf-8") as file:
                    file.write(response.text)

                soup = BeautifulSoup(response.text, "html.parser")
                paragraphs = soup.find_all('p')
                content = ' '.join([para.text for para in paragraphs])
            elif source.endswith(".pdf"):
                # If the source ends with ".pdf", treat it as a PDF file
                with fitz.open(source) as pdf_document:
                    content = ''
                    for page_num in range(pdf_document.page_count):
                        page = pdf_document.load_page(page_num)
                        content += page.get_text()

            else:
                # Assume it's a local file path, read the content
                with open(source, "r", encoding="utf-8") as file:
                    content = file.read()

            return content
        except Exception as e:
            logging.exception("Error occurred while scraping: %s", str(e))
            return None

    def abstractive_summarize(self, content):
        inputs = self.tokenizer.encode("summarize: " + content, return_tensors="pt", max_length=1024, truncation=True)
        print("Inputs:", inputs)

        summary_ids = self.model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
        print("Summary IDs:", summary_ids)

        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def summarize_content(self):
        url = self.url_entry.get()
        content = self.scrape_content_from_url(url)

        if content and len(content) >= 1:
            # Generates abstractive summary using BART
            try:
                summary = self.abstractive_summarize(content)

                # Display the summary in the text widget
                self.summary_text.delete(1.0, tk.END)  # Clear previous content
                self.summary_text.insert(tk.END, summary)
            except Exception as e:
                self.summary_text.delete(1.0, tk.END)
                self.summary_text.insert(tk.END, f"Error summarizing content: {str(e)}")
                        # Display user-friendly error message in the GUI

        else:
                # Display user-friendly error message in the GUI
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, "Unable to summarize")

    def miu_function(self):
        # Retrieve content from multiple sample URLs (you can modify this list)
        urls = ['https://www.example1.com', 'https://www.example2.com', 'https://www.example3.com']

        combined_content = ''
        for url in urls:
            content = self.scrape_content_from_url(url)

            if content and len(content) >= 1:
                combined_content += content + '\n'

        if combined_content:
            try:
                # Generate abstractive summary using BART for the combined content
                summary = self.abstractive_summarize(combined_content)

                # Format and display the output in the console (you can modify this)
                formatted_output = f"Combined Content from All Sources:\n{combined_content}\n\nSummary:\n{summary}\n"
                print(formatted_output)

            except Exception as e:
                # Display an error message if abstractive summarization fails
                print(f"Error abstractive summarizing combined content: {str(e)}")

        else:
            # Display a message if content retrieval fails for all sources
            print("Unable to retrieve content from any source")

    def bluf_function(self):
        # Retrieve content from multiple sample URLs (you can modify this list)
        urls = ['https://www.example1.com', 'https://www.example2.com', 'https://www.example3.com']

        combined_content = ''
        for url in urls:
            content = self.scrape_content_from_url(url)

            if content and len(content) >= 1:
                combined_content += content + '\n'

        if combined_content:
            try:
                # Generate abstractive summary using BART for the combined content
                bluf_summary = self.abstractive_summarize(combined_content)

                # Display the BLUF summary in the console (you can modify this)
                print(f"Combined Content from All Sources:\n{combined_content}\n\nBLUF Summary:\n{bluf_summary}\n")

            except Exception as e:
                # Display an error message if abstractive summarization fails
                print(f"Error abstractive summarizing combined content: {str(e)}")

        else:
            # Display a message if content retrieval fails for all sources
            print("Unable to retrieve content from any source")

    def abstractive_summarize(self, content):
        # Load pre-trained BART model and tokenizer
        model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
        tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

        # Tokenize the content for summarization
        inputs = tokenizer.encode("summarize: " + content, return_tensors="pt", max_length=1024, truncation=True)

        # Generate the abstractive summary using the BART model
        summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)

        # Decode the summary IDs to get the final summary
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    # ... (the rest of your code remains unchanged)

    def rh_summarize(self, content):
        # Implement your RH summarization logic here
        # This could be a different summarization algorithm or format
        # Adjust this method according to your specific requirements
        rh_summary = f"RH Format: {content[:50]}..."  # Just an example, you need to customize this

        return rh_summary
    
    def rh_function(self):
    # Retrieve content from multiple sample URLs (you can modify this list)
        urls = ['https://www.example1.com', 'https://www.example2.com', 'https://www.example3.com']

combined_content = ''
def process_urls(self):
    for url in self.urls:
        content = self.scrape_content(url)[0]  # Only extract text content

    if content and len(content) >= 1:
        try:
            # Implement RH summarization logic here
            rh_summary = Self.rh_summarize(content)

            # Display the RH summary in the console (you can modify this)
            print(f"RH Summary for {url}:\n{rh_summary}\n")

        except Exception as e:
            # Display an error message if RH summarization fails
            print(f"Error RH summarizing content: {str(e)}")

    else:
        # Display a message if content retrieval fails for any source
        print(f"Unable to retrieve content from {url}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('300x100')

        # Create the 'MIU' button with a command to call the miu_function
        miu_button = tk.Button(self, text='MIU', command=self.miu_function)
        miu_button.pack(expand=True)

         # Create the 'RH' button with a command to call the rh_function
        rh_button = tk.Button(self, text='RH', command=self.rh_function)
        rh_button.pack(expand=True)

        # Create the 'BLUF' button with a command to call the bluf_function
        bluf_button = tk.Button(self, text='BLUF', command=self.bluf_function)
        bluf_button.pack(expand=True)

        style = tk.Style(self)
        style.configure('TButton', font=('Times New Roman', 16))
        style.map('TButton', foreground=[('pressed', 'blue'), ('active', 'red')])

        print(style.layout('TButton'))


if __name__ == "__main__":
    root = tk.Tk()
    app = SummarizerApp(root)
    root.mainloop()

