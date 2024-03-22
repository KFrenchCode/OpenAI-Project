from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.converters import AzureOCRDocumentConverter
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret

document_store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("converter", AzureOCRDocumentConverter(endpoint="azure_resource_url", api_key=Secret.from_token("565001e88e8d46cc9353039b6de7bbbe")))
pipeline.add_component("cleaner", DocumentCleaner())
pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
pipeline.add_component("writer", DocumentWriter(document_store=document_store))
pipeline.connect("converter", "cleaner")
pipeline.connect("cleaner", "splitter")
pipeline.connect("splitter", "writer")

pipeline.run({"converter": {"sources": ["Downloads/CENTCOM_Strategy_Documents2022-NATIONAL-DEFENSE-STRATEGY-NPR-MDR.PDF",
"Downloads/CENTCOM_Strategy_Documents/Biden-Harris-Administrations-National-Security-Strategy-10.2022.pdf", 
"Downloads/CENTCOM_Strategy_Documents/National_Intelligence_Strategy_2023.pdf",  
"Downloads/CENTCOM_Strategy_Documents/CENTCOM Posture statement.pdf",
"Downloads/CENTCOM_Strategy_Documents/DIA_Strategy_Oct_2022.pdf" ] }})




