def extract(mpyqArc_instance):
    """Extract all the files inside the MPQ archive in memory."""
    if self.files:
        return dict((f, mpyqArc_instance.read_file(f)) for f in mpyqArc_instance.files)
    else:
        raise RuntimeError("Can't extract whole archive without listfile.")

def extract_to_disk(mpyqArc_instance):
    """Extract all files and write them to disk."""
    archive_name, extension = os.path.splitext(os.path.basename(mpyqArc_instance.file.name))
    
    if not os.path.isdir(os.path.join(os.getcwd(), archive_name)):
        os.mkdir(archive_name)
    os.chdir(archive_name)
    
    for filename, data in mpyqArc_instance.extract().items():
        f = open(filename, 'wb')
        f.write(data or "")
        f.close()

def extract_files(mpyqArc_instance, *filenames):
    """Extract given files from the archive to disk."""
    for filename in filenames:
        data = mpyqArc_instance.read_file(filename)
        f = open(filename, 'wb')
        f.write(data or "")
        f.close()
        
import os

print os.path.join("abc", "bcd")