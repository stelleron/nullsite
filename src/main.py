from operator import index, truediv
import os
import re
import markdown
import toml
import datetime

# Global variable to buffer posts to generate index.html
blogposts_data = [] 

# Global variable to the name of the blog
blog_name = 0

# Global variable for the blog's footer
footer = "<br>"

# Global variable for storing the path of About and Projects folder
about_path = ""
projects_path = ""

# Relevant paths
SOURCE_DIR = "posts"
SITE_DIR = "site"    
ROOT_DIR = os.getcwd()
SOURCE_PATH = os.path.join(ROOT_DIR, SOURCE_DIR)
SITE_PATH = os.path.join(ROOT_DIR, SITE_DIR) 

GITHUB_LINK = """<a href="{}"><img src="/images/base/github-mark.svg" class="icon" width="32" height="32"></a>"""
LINKEDIN_LINK = """<a href="{}"><img src="/images/base/linkedin-mark.svg" class="icon" width="32" height="32"></a>"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title> {} </title>
    <link rel="stylesheet" href="/style/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Ubuntu+Mono&display=swap" rel="stylesheet">  
</head>
<body>
<div class="index-header">
    <span class="index-title"><a href="/index.html" class="index-link">{}</a></span>
    <span class="index-box">
        <span><a href = \"{}\" class="index-link">About</a></span>
        <span><a href = \"{}\" class="index-link">Projects</a></span>
    </span>
    <hr/>
</div>
<div class="content">
{}
<hr>
</div>

<div class="index-footer">
{}
</div>
                  
</body>
</html>"""

# Special page class
class SpecialPage:
    # Creates a special page
    def __init__(self, source):
        # Extract frontmatter from the source
        source_copy = source
        stripped_source = source.replace("\n", "")
        frontmatter = re.search('===(.*)===', stripped_source)

        # Then get the title, date and description
        frontdata = frontmatter.group(1)
        title_loc = frontdata.find('title')
        self.title = (frontdata[title_loc + len("title:") + 1:])

        # Then get the content of the markdown file ignoring the frontmatter
        endptr = source_copy.replace("===", "xxx", 1).find("===")
        self.content = source_copy[endptr + len("==="):]

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
         # Also store the date of the object in datetime format(for sorting)
        self.sort_date = datetime.datetime.strptime(self.date,"%d-%m-%Y").date()

    def __gt__(self, other):
        if (self.sort_date > other.sort_date):
            return True
        else:
            return False

# Adds the HTML source to a template
def add_to_template(source, post):
    global footer
    return HTML_TEMPLATE.format(post.title, blog_name, about_path, projects_path, source, footer)

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
    # Sort the blogposts
    blogposts_data.sort(reverse=True)

    # Stores the HTML to be added to the index.html
    html_data = ""

    x = 0
    # Convert all of the stored blog data to HTML blocks 
    for blog_data in blogposts_data:
        html_buffer = """<a href=\"{0}\" class="index-post-title">{1}</a>
        <div class="index-post-date">{2}</div>
        <p class="index-post-desc">{3}</p>
        """
        html_buffer = html_buffer.format(blog_data.path, blog_data.title, blog_data.date, blog_data.desc)
        # If not the last blog post, also add a horizontal line
        if (x < len(blogposts_data) - 1):
            html_buffer += "<hr>"

        html_data += html_buffer
        x += 1

    # Format and write the index.html file
    index_source = HTML_TEMPLATE.format(blog_name, blog_name, about_path, projects_path, html_data, footer)
    index_file = open("index.html", "w")
    index_file.write(index_source)

# Generate footer
def generate_footer(config):
    global footer
    # If there are links in the config.toml footer section , create a new footer with them
    footer_config = config["footer"]
    if len(footer_config) > 0:
        footer = ""
        print("Adding footer...")

        # Look for a GitHub link
        if ("github" in footer_config):
            print("Found GitHub link!")
            # Add the GitHub icon to the footer and the link
            github_logo = GITHUB_LINK
            github_logo = github_logo.format(footer_config["github"])
            footer += github_logo
        
        # Look for a LinkedIn link
        if ("linkedin" in footer_config):
            print("Found LinkedIn link")
            # Add the LinkedIn icon to the footer and the link
            linkedin_logo = LINKEDIN_LINK
            linkedin_logo = linkedin_logo.format(footer_config["linkedin"])
            footer += linkedin_logo

        print("\n")
    return footer

# Generate special pages
def generate_special_pages(config):
    global about_path
    global projects_path

    about_dest_loc = ""
    projects_dest_loc = ""
    about_page = ""
    projects_page = ""
    about_page_source = ""
    projects_page_source = ""

    # First generate the About and Projects page and save their links
    if ("about" in config):
        # Load the source and destination paths

        source_loc = config["about"]
        dest_loc = source_loc.replace("md", "html")
        dest_loc = os.path.basename(dest_loc)
        dest_loc = os.path.join(SITE_PATH, dest_loc)
        source_loc = os.path.join(ROOT_DIR, source_loc)

        # Now load the souce 
        file_source = open(source_loc)
        about_page = SpecialPage(file_source.read())

        # And convert it to HTML
        about_page_source = markdown.markdown(about_page.content)

        # Finally add the link 
        path_start = dest_loc.find('/site/')
        about_path = dest_loc[path_start:]
        about_dest_loc = dest_loc

    # Then generate the projects page
    if ("projects" in config):
        # Load the source and destination paths

        source_loc = config["projects"]
        dest_loc = source_loc.replace("md", "html")
        dest_loc = os.path.basename(dest_loc)
        dest_loc = os.path.join(SITE_PATH, dest_loc)
        source_loc = os.path.join(ROOT_DIR, source_loc)

        # Now load the souce 
        file_source = open(source_loc)
        projects_page = SpecialPage(file_source.read())

        # And convert it to HTML
        projects_page_source = markdown.markdown(projects_page.content)

        # Finally add the link 
        path_start = dest_loc.find('/site/')
        projects_path = dest_loc[path_start:]
        projects_dest_loc = dest_loc

    # Convert the two pages here once links have been generatedh)
    about_file = open(about_dest_loc, "w")
    about_file.write(add_to_template(about_page_source, about_page))

    projects_file = open(projects_dest_loc, "w")
    projects_file.write(add_to_template(projects_page_source, projects_page))

# Main function
def main():
    global blog_name
    global footer

    print("Building site...")

    # First parse the config.toml in the base directory
    config = toml.load("config.toml")
    blog_name = "{}\'s Blog".format(config["name"])
    
    # Also generate a footer
    footer = generate_footer(config)

    # Now create the site directory if it doesn't exist
    if (os.path.exists(SITE_PATH) == False):
        os.mkdir(SITE_PATH)

    # Now time to convert each post in the source directory into a HTML file and add it to the target directory
    source_files = os.listdir(SOURCE_PATH)

    for path in source_files:
        if (os.path.isdir(os.path.join(SOURCE_PATH, path))):
            # Remove any folders
            source_files.remove(path)

    print("First generating any special pages...")
    generate_special_pages(config)

    print('Found {} file(s). Loading them all...\n'.format(len(source_files)))
    for path in source_files:
        create_html(path)
    
    # Generate an index.html
    generate_index()
    print("Finished building the site!")
    


if (__name__ == "__main__"):
    main()