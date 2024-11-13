import os
import argparse
import shutil
from tqdm import tqdm
import pdfplumber  

def read_pdf(pdf_loc, page_infos: list = None):
    """
    Extracts text from a PDF file.

    Args:
        pdf_loc (str): The file path of the PDF to read.
        page_infos (list, optional): A list specifying the start and end pages to read.
            If None, reads the entire PDF. Defaults to None.

    Returns:
        str: The extracted text from the specified pages of the PDF.
    """
    pdf = pdfplumber.open(pdf_loc) 
    pages = pdf.pages[page_infos[0]:page_infos[1]] if page_infos else pdf.pages
    pdf_text = ''
    for _, page in enumerate(pages): 
        text = page.extract_text()  
        if text:
            pdf_text += text
    pdf.close() 
    return pdf_text  

def load_data(source_path, dest_path):
    """
    Copies files from a source directory to a destination directory, processing PDFs as text files.

    Args:
        source_path (str): The directory path to copy files from.
        dest_path (str): The directory path to copy files to.
            If 'faq', copies a JSON file instead of processing PDFs.

    Returns:
        None
    """
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    if dest_path == 'faq':
        source_path_json = os.path.join(source_path, 'pid_map_content.json')
        dest_path_json = "./faq/pid_map_content.json"
        shutil.copy(source_path_json, dest_path_json)
    else:
        masked_file_ls = os.listdir(source_path)
        for file in tqdm(masked_file_ls):
            pdf_file = read_pdf(os.path.join(source_path, file))
            with open(os.path.join(dest_path, file.replace('.pdf', '.txt')), 'w', encoding='utf-8') as f:
                f.write(pdf_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--source_path', type=str, required=True, help='讀取參考資料路徑') 

    args = parser.parse_args() 

    source_path_insurance = os.path.join(args.source_path, 'insurance')  
    corpus_dict_insurance = load_data(source_path_insurance, 'insurance')

    source_path_finance = os.path.join(args.source_path, 'finance')  
    corpus_dict_finance = load_data(source_path_finance, 'finance')

    source_path_faq = os.path.join(args.source_path, 'faq')  
    corpus_dict_faq = load_data(source_path_faq, 'faq')
