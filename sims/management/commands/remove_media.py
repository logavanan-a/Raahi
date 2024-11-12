from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Send Remainder mail after 7 days'

    def handle(self, *args, **options):

        directory_path = str(settings.MEDIA_ROOT) + '/pdf_file/'

        # List all files in the directory
        files = os.listdir(directory_path)

        # Loop through the files and remove each one
        for file in files:
            file_path = os.path.join(directory_path, file)
            os.remove(file_path)

        all_files = os.listdir(settings.MEDIA_ROOT)

        # Filter files with .pdf extension
        pdf_files = [file for file in all_files if file.lower().endswith(".pdf")]

        # Print the list of .pdf files
        for pdf_file in pdf_files:
            os.remove(str(settings.MEDIA_ROOT)+'/'+pdf_file)

         # Filter files with .png extension
        pdf_files = [file for file in all_files if file.lower().endswith(".png")]

        # Print the list of .png files
        for pdf_file in pdf_files:
            os.remove(str(settings.MEDIA_ROOT)+'/'+pdf_file)
