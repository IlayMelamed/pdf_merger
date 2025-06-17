#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Merger Module - Handles merging of PDF documents.
"""

import io
from pypdf import PdfReader, PdfWriter
from tkinter import messagebox


class PdfMerger:
    """
    PdfMerger class for merging PDF documents.

    Provides functionality to:
    - Store the main PDF in memory
    - Merge a second PDF after a specific page
    - Export the merged PDF to a file
    """

    def __init__(self):
        """Initialize the PDF merger."""
        self.main_pdf_bytes = None
        self.insert_pdf_path = None
        self.modified = False

    def set_main_pdf(self, file_path=None, pdf_bytes=None):
        """
        Set the main PDF document from a file path or bytes.

        Args:
            file_path (str, optional): Path to the main PDF file.
            pdf_bytes (bytes, optional): Main PDF content as bytes.

        Returns:
            bool: True if PDF was set successfully, False otherwise.
        """
        try:
            if file_path:
                with open(file_path, 'rb') as f:
                    self.main_pdf_bytes = f.read()
            elif pdf_bytes:
                self.main_pdf_bytes = pdf_bytes
            else:
                messagebox.showerror("Error", "No PDF source provided.")
                return False

            # Reset modification state
            self.modified = False
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to set main PDF: {str(e)}")
            return False

    def set_insert_pdf(self, file_path):
        """
        Set the PDF to insert.

        Args:
            file_path (str): Path to the PDF file to insert.

        Returns:
            bool: True if PDF was set successfully, False otherwise.
        """
        try:
            # Validate that the file can be opened as PDF
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                if len(reader.pages) == 0:
                    messagebox.showerror("Error", "The selected PDF file contains no pages.")
                    return False

            self.insert_pdf_path = file_path
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to set insert PDF: {str(e)}")
            return False

    def merge_after_page(self, page_idx):
        """
        Merge the insert PDF after the specified page of the main PDF.

        Args:
            page_idx (int): Index of the page after which to insert (0-based).

        Returns:
            bytes: The merged PDF content as bytes, or None if merge failed.
        """
        if not self.main_pdf_bytes:
            messagebox.showerror("Error", "No main PDF loaded.")
            return None

        if not self.insert_pdf_path:
            messagebox.showerror("Error", "No insert PDF selected.")
            return None

        try:
            # Create readers for both PDFs
            main_stream = io.BytesIO(self.main_pdf_bytes)
            reader_main = PdfReader(main_stream)

            # Print debugging info
            print(f"Main PDF has {len(reader_main.pages)} pages")
            print(f"Inserting after page {page_idx}")

            # Check if the page_idx is valid
            if page_idx >= len(reader_main.pages):
                messagebox.showerror("Error", f"Invalid page index: {page_idx}. The document only has {len(reader_main.pages)} pages.")
                return None

            # Keep the insert file open until we're done with it
            with open(self.insert_pdf_path, 'rb') as insert_file:
                reader_insert = PdfReader(insert_file)
                print(f"Insert PDF has {len(reader_insert.pages)} pages")

                # Create a writer for the output
                writer = PdfWriter()

                # Add pages from main PDF up to and including the current page
                for i in range(page_idx + 1):
                    writer.add_page(reader_main.pages[i])

                # Add all pages from the insert PDF
                for page in reader_insert.pages:
                    writer.add_page(page)

                # Add remaining pages from the main PDF
                for i in range(page_idx + 1, len(reader_main.pages)):
                    writer.add_page(reader_main.pages[i])

                # Write to bytes
                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_stream.seek(0)

                # Update main PDF bytes
                self.main_pdf_bytes = output_stream.getvalue()

            # Close the main stream
            main_stream.close()

            # Set modified flag
            self.modified = True

            return self.main_pdf_bytes

        except Exception as e:
            import traceback
            print("Error during merge:")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to merge PDFs: {str(e)}")
            return None

    def save_to_file(self, file_path):
        """
        Save the merged PDF to a file.

        Args:
            file_path (str): Path where to save the merged PDF.

        Returns:
            bool: True if PDF was saved successfully, False otherwise.
        """
        if not self.main_pdf_bytes:
            messagebox.showerror("Error", "No PDF content to save.")
            return False

        try:
            with open(file_path, 'wb') as f:
                f.write(self.main_pdf_bytes)

            # Reset modification state after saving
            self.modified = False
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
            return False

    def is_modified(self):
        """
        Check if the PDF has been modified.

        Returns:
            bool: True if PDF has been modified, False otherwise.
        """
        return self.modified

    def has_main_pdf(self):
        """
        Check if a main PDF is loaded.

        Returns:
            bool: True if a main PDF is loaded, False otherwise.
        """
        return self.main_pdf_bytes is not None

    def has_insert_pdf(self):
        """
        Check if an insert PDF is selected.

        Returns:
            bool: True if an insert PDF is selected, False otherwise.
        """
        return self.insert_pdf_path is not None
