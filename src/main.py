import os
import re
import markdown

# Global variable to buffer posts to generate index.html
blogposts_data = [] 

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

# Blogpost data class
class PostData:
    # Create post data
    def __init__(self, path, post):
        path_start = path.find('/site/')
        self.path = path[path_start:]
        self.title = post.title
        self.date = post.date
        self.desc = post.description

# Adds the HTML source to a template
def add_to_template(source, post):
    template = """<!DOCTYPE html>
<html>
<head>
    <title> {} </title>
    <link rel="stylesheet" href="/style/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@700&family=Quicksand:wght@300&family=Roboto+Mono:wght@100&family=Roboto:ital,wght@0,300;1,300&display=swap" rel="stylesheet">
</head>
<body>
<div class="index-header">
    <span class="index-title"><a href="/index.html">Stelleron's Blog</a></span>
    <span class="index-box">
        <span>About</span>
        <span>Projects</span>
    </span>
    <hr/>
</div>

<div class="content">
{}
</div>

</body>
</html>"""

    return template.format(post.title, source)

# Used to create HTML files from a given markdown file
def create_html(md_path):
    # Load the markdown source
    file_source = open(os.path.join(SOURCE_PATH, md_path))

    # Before converting to HTML, convert it into a post
    content = file_source.read()
    post = Post(content)

    # Convert to HTML
    html_file_source = markdown.markdown(post.content)

    # Save it to a HTML file
    html_file_path = md_path.replace("md", "html")
    html_path = os.path.join(SITE_PATH, html_file_path)
    html_file = open(html_path, "w")
    html_file.write(add_to_template(html_file_source, post))

    # Add data to the blogpost
    blogposts_data.append(PostData(html_path, post))

    # Close files
    file_source.close()
    html_file.close()

# Used to generate an index.html
def generate_index():
    index_template = """<!DOCTYPE html>
<html>
<head>
    <title> My Blog </title>
    <link rel="stylesheet" href="/style/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Mono:wght@700&family=Quicksand:wght@300&family=Roboto+Mono:wght@100&family=Roboto:ital,wght@0,300;1,300&display=swap" rel="stylesheet">
</head>
<body>
<div class="index-header">
    <span class="index-title"><a href="/index.html" class="index-link">My Blog</a></span>
    <span class="index-box">
        <span><a class="index-link">About</a></span>
        <span><a class="index-link">Projects</a></span>
    </span>
    <hr/>
</div>
<div class="content">
{}
</div>

                  
</body>
</html>"""

    # Stores the HTML to be added to the index.html
    html_data = ""

    # Convert all of the stored blog data to HTML blocks 
    for blog_data in blogposts_data:
        html_buffer = """<a href=\"{0}\" class="index-post-title">{1}</a>
        <div class="index-post-date">{2}</div>
        <p class="index-post-desc">{3}</p>
        <hr/>"""
        html_buffer = html_buffer.format(blog_data.path, blog_data.title, blog_data.date, blog_data.desc)
        html_data += html_buffer

    # Format and write the index.html file
    index_source = index_template.format(html_data)
    index_file = open("index.html", "w")
    index_file.write(index_source)

# Call the main function
def main():
    print("Building site...")

    # Now create the site directory if it doesn't exist
    if (os.path.exists(SITE_PATH) == False):
        os.mkdir(SITE_PATH)

    # Now time to convert each post in the source directory into a HTML file and add it to the target directory
    source_files = os.listdir(SOURCE_PATH)
    print('Found {} file(s). Loading them all...\n'.format(len(source_files)))
    for path in source_files:
        create_html(path)
    
    # Generate an index.html
    generate_index()
    print("Finished building the site!")
    


if (__name__ == "__main__"):
    main()