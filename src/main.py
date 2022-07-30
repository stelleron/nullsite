import os
import re
import markdown

# Relevant paths
SOURCE_DIR = "posts"
SITE_DIR = "site"    
ROOT_DIR= os.getcwd()
SOURCE_PATH = os.path.join(ROOT_DIR, SOURCE_DIR)
SITE_PATH = os.path.join(ROOT_DIR, SITE_DIR) 

# Post class 
class Post:
    # Create a post
    def __init__(self, source):
        # Extract frontmatter from the source
        source_copy = source
        stripped_source = source.replace("\n", "")
        frontmatter = re.search('===(.*)===', stripped_source)
        
        # Then get the title, date and description
        frontdata = frontmatter.group(1)

        title_loc = frontdata.find('title')
        date_loc = frontdata.find('date')
        description_loc = frontdata.find('description')

        self.title = (frontdata[title_loc + len("title:") + 1 : date_loc])
        self.date = (frontdata[date_loc + len("date:") + 1 : description_loc])
        self.description = (frontdata[description_loc + len("description:"):])
        
        # Then get the content of the markdown file ignoring the frontmatter
        endptr = source_copy.replace("===", "xxx", 1).find("===")
        self.content = source_copy[endptr + len("==="):]

# Adds the HTML source to a template
def add_to_template(source):
    template = """<!DOCTYPE html>
<html>
<head>
    <title> My family is a potato </title>
</head>
<body>

{}
                  
</body>
</html>"""
    return template.format(source)

# Used to create HTML files from a given markdown file
def create_html(md_path):
    # Load the markdown source
    file_source = open(os.path.join(SOURCE_PATH, md_path))

    # Before converting to HTML, convert it into a post
    content = file_source.read()
    post = Post(content)

    # Convert to HTML
    html_file_source = markdown.markdown(post.content)

    # Finally save it to a HTML file
    html_file_path = md_path.replace("md", "html")
    html_path = os.path.join(SITE_PATH, html_file_path)
    html_file = open(html_path, "w")
    html_file.write(add_to_template(html_file_source))

# Call the main function
def main():
    print("Building site...")

    # Now create the site directory if it doesn't exist
    if (os.path.exists(SITE_PATH) == False):
        os.mkdir(SITE_PATH)

    # Now time to convert each post in the source directory into a HTML file and add it to the target directory
    source_files = os.listdir(SOURCE_PATH)
    print('Found {} file(s). Loading them all...'.format(len(source_files)))
    for path in source_files:
        create_html(path)
    


if (__name__ == "__main__"):
    main()