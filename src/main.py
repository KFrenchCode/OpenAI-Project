import tkinter as tk
from tkinter import filedialog
from transformers import pipeline, Pipeline, PreTrainedTokenizerFast
import requests
from bs4 import BeautifulSoup
import fitz
from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
from docx import Document

load_dotenv()

class ReportGeneratorApp:
    # ReportGenerator Initializer
    # takes a TKinter root objects and then creates widgets, initializes model
    def __init__(self, root):
        # Initialize variables
        self.root: tk.Tk = root
        self.source_list: list[dict[str, str]] = []
        self.source_widgets: list[tk.Widget] = []
        self.title: str = "Report Generator v0.1"

        # Initialize source type variable
        self.source_type_var = tk.StringVar()

        # Initialize widgets
        self.root.title(self.title)
        self.create_initial_widgets()

        self.current_source_location: str = ""

        # # Initialize Model LEGACY, SWITCHED TO OPENAI
        # self.summarizer: Pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Initialize OpenAI
        self.client = OpenAI(
            api_key=os.getenv("VSFS_KEY"),
        )

        # Initialize encoder
        self.encoder = tiktoken.get_encoding("cl100k_base")


        # Initialize Summaries
        self.summaries: list[dict[str, str]] = []

        self.export_document = Document()
        

    def create_initial_widgets(self):
        # Create title
        title_label = tk.Label(self.root, text=self.title, font=("Arial", 25))
        title_label.grid(column=0, row=0)

        # New Source Label
        self.source_list_label = tk.Label(self.root, text="Add Source", font=("Arial", 18))
        self.source_list_label.grid(column=0, row=1)

        # Create first source frame
        new_source_frame = tk.Frame(self.root)
        new_source_frame.grid(column=0, row=2)

        # Title of Source Label
        new_source_title_label = tk.Label(new_source_frame, text="Title of Source:", font=("Arial", 12), width=50)
        new_source_title_label.grid(column=0, row=0, pady=5)

        # Title of Source Entry
        self.new_source_title_entry = tk.Entry(new_source_frame)
        self.new_source_title_entry.grid(column=1, row=0, pady=5)

        # Country of Source Label
        new_source_country_label = tk.Label(new_source_frame, text="Country of Source:", font=("Arial", 12), width=50)
        new_source_country_label.grid(column=0, row=1, pady=5)

        # Country of Source Entry
        self.new_source_country_entry = tk.Entry(new_source_frame)
        self.new_source_country_entry.grid(column=1, row=1, pady=5)

        # Source Type Label
        source_type_label = tk.Label(new_source_frame, text="Source Type:", font=("Arial", 12))
        source_type_label.grid(column=0, row=2, pady=5)

        # Radio button for URL
        self.source_type_url = tk.Radiobutton(new_source_frame, text="URL", variable=self.source_type_var, value="url", command=self.toggle_source_input)
        self.source_type_url.grid(column=1, row=2, pady=5)

        # Radio button for File
        self.source_type_file = tk.Radiobutton(new_source_frame, text="File", variable=self.source_type_var, value="file", command=self.toggle_source_input)
        self.source_type_file.grid(column=1, row=3, pady=5)

        # Initially, set the source type to URL
        self.source_type_var.set("url")

        # URL of Source Label
        new_source_url_label = tk.Label(new_source_frame, text="Source Location:", font=("Arial", 12))
        new_source_url_label.grid(column=0, row=4, pady=5)

        # # URL of Source Entry
        self.new_source_url_entry = tk.Entry(new_source_frame)
        self.new_source_url_entry.grid(column=1, row=4, pady=5)

        # # File Upload Button
        self.file_upload_button = tk.Button(new_source_frame, text="Upload File", command=self.upload_file)
        # self.file_upload_button.grid(column=0, row=4, pady=5)


        # Submit Button
        new_source_submit = tk.Button(new_source_frame, text="Add Source", command=self.add_new_source_command)
        new_source_submit.grid(column=0, row=5, pady=5)


        #Source List Label
        self.source_list_label = tk.Label(self.root, text="Source List", font=("Arial", 18), width=50)
        self.source_list_label.grid(column=1, row=1)

        # Source List Frame
        self.source_list_frame = tk.Frame(self.root)
        self.source_list_frame.grid(column=1, row=2, sticky="nsew")

        # Summarize Button
        summarize_button = tk.Button(self.root, text="Summarize Sources", command=self.summarize)
        summarize_button.grid(column=0, row=3)

        # Save Summaries Frame 
        self.save_source_summaries_frame = tk.Frame(self.root)
        self.save_source_summaries_frame.grid(column=0, row=4)

        # New Source Label
        self.save_source_summaries_label = tk.Label(self.save_source_summaries_frame, text="Save Source", font=("Arial", 18))
        self.save_source_summaries_label.grid(column=0, row=0)

        self.save_source_summaries_button = tk.Button(self.save_source_summaries_frame, text="Save to .docx", command=self.save_summaries_to_docx)
        self.save_source_summaries_button.grid(column=0, row=1, pady=5)


    def toggle_source_input(self):
        source_type = self.source_type_var.get()

        # Hide all widgets initially
        self.new_source_url_entry.grid_forget()
        self.file_upload_button.grid_forget()

        # Show the relevant widget based on the source type
        if source_type == "url":
            self.new_source_url_entry.grid(column=1, row=4, pady=5, padx=5)
        elif source_type == "file":
            self.file_upload_button.grid(column=1, row=4, pady=5, padx=5)

    def create_file_upload_button(self):
        # Create a file upload button
        self.file_upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.file_upload_button.grid(row=4, pady=5, padx=5)

    def upload_file(self):
        # Open a file dialog to select a file
        self.current_source_location = filedialog.askopenfilename(filetypes=[("PDFs", ".pdf")])

    def reset_source_inputs(self) -> None:
        self.new_source_title_entry.delete(0, 'end')
        self.new_source_url_entry.delete(0, 'end')

    def delete_source_command(self, index: int) -> None:
        # Delete the source at the specified index
        del self.source_list[index]
        
        # Update the GUI to reflect the changes
        self.update_source_list_gui()

    def update_source_list_gui(self) -> None:
        # Clear all widgets in source_list_frame
        for widget in self.source_list_frame.winfo_children():
            widget.destroy()

        # Re-populate source_list_frame with updated source_list
        for i, source in enumerate(self.source_list):
            source_title = source["source_title"]
            
            # Source List Item Title
            source_list_title = tk.Label(self.source_list_frame, text=source_title, font=("Arial", 12))
            source_list_title.grid(column=0, row=i, sticky="w")

            # Delete Button
            delete_button = tk.Button(self.source_list_frame, text="Delete", command=lambda i=i: self.delete_source_command(i))
            delete_button.grid(column=1, row=i, padx=5, sticky="e")

    def add_new_source_command(self) -> None:
        title = self.new_source_title_entry.get()

        if self.source_type_var.get() == "url":
            self.current_source_location = self.new_source_url_entry.get()
        else: 
            self.current_source_location = self.current_source_location

        self.source_list.append({
            "source_title": title,
            "source_classification": "UNCLASSIFIED",
            "source_country": self.new_source_country_entry.get(),
            "source_type": self.source_type_var.get(),
            "source_location": self.current_source_location
        })

        self.update_source_list_gui()
        self.reset_source_inputs()

    def get_text_from_url(self, url):
        try:
            # Fetch the HTML content of the webpage
            response = requests.get(url)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all the text from the HTML
                all_text = soup.get_text(separator='\n', strip=True).replace("\n", " ").replace("\t", " ")
                
                return all_text
            else:
                # If the request was not successful, print an error message
                
                raise Exception(f"Error: Unable to fetch content from {url}. Status code: {response.status_code}")
                                      
        except Exception as e:
            print(f"Error: Unable to extract text from {url}. {str(e)}")
            raise e
            
    
    def get_text_from_pdf(self, filename):
        try:
            # Open the PDF file
            pdf_document = fitz.open(filename)
            
            # Initialize an empty string to store the extracted text
            all_text = ""
            
            # Iterate through each page of the PDF
            for page_number in range(pdf_document.page_count):
                # Get the text of the page
                page = pdf_document[page_number]
                text = page.get_text("text").replace("\n", " ").replace("\t", " ")
                
                # Append the text to the result string
                all_text += text + '\n'
            
            # Close the PDF document
            pdf_document.close()
            
            return all_text.strip()  # Remove leading and trailing whitespaces
        except Exception as e:
            print(f"Error: Unable to extract text from {filename}. {str(e)}")
            raise e

    def summarize(self):
        for source in self.source_list:
            source_type = source["source_type"]
            text = ""

            if source_type == "url":
                try:
                    text = self.get_text_from_url(source["source_location"])
                except Exception as e:
                    print(e)
                    continue
            else:
                try:
                    text = self.get_text_from_pdf(source["source_location"])

                except Exception as e:
                    print(e)
                    continue

            # Split the text into chunks based on the maximum token length
            max_token_length = 12000

            encoding = self.encoder.encode(text)

            chunks = [encoding[i:i + max_token_length] for i in range(0, len(encoding), max_token_length)]

            # Initialize summary bits
            summary_bits = []

            # Summarize each chunk and print the results
            for i, chunk in enumerate(chunks):
                print(f"Currently processing chunk {i+1}/{len(chunks)}...")
                
                text_chunk = self.encoder.decode(chunk)
                summary_object = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are going to act as a summarizer for the following text, giving 2-3 sentences of summarization:"
                        },
                        {
                            "role": "user",
                            "content": text_chunk
                        }
                    ],
                    model="gpt-3.5-turbo-16k"
                )

                summary_bits.append(summary_object.choices[0].message.content.replace("\n", " "))

            all_summaries_together_text = " ".join(summary_bits)

            total_summary_object = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are going to act as a summarizer for the following text, giving 5-6 sentences of summarization:"
                        },
                        {
                            "role": "user",
                            "content": all_summaries_together_text
                        }
                    ],
                    model="gpt-3.5-turbo-16k"
                )
            
            # print(total_summary_object.choices[0].message.content)

            summary_dict_object = {
                "source_title": source["source_title"],
                "source_classification": source["source_classification"],
                "source_country": source["source_country"],
                "source_type": source["source_type"],
                "source_summary": total_summary_object.choices[0].message.content
            }

            self.summaries.append(summary_dict_object)

            print(f"Done Summarizing Source: {source['source_title']}")

        print("Done summarizing all sources")


    def save_summaries_to_docx(self):
        print("save summaries to word file")
        self.export_document.add_heading("[MIU or Reporting Highlights]", level=0)
        
        for summary in self.summaries:
            classification = self.export_document.add_paragraph()
            classification.add_run(summary["source_classification"]).bold = True
            country = self.export_document.add_paragraph()
            country.add_run(summary["source_country"]).bold = True
            title = self.export_document.add_paragraph()
            title.add_run(summary["source_title"]).bold = True

            self.export_document.add_paragraph()

            add_bluf = self.export_document.add_paragraph()
            add_bluf.add_run("[ADD BLUF]").bold = True

            self.export_document.add_paragraph()
            summary_label 
            self.export_document.add_paragraph("Summary: "+summary["source_summary"])


        self.export_document.save("ReportTemplate.docx")


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()