# Note that this code was generated by ChatGPT and from online sources.
# This is not intended to modify any of the webtool data, it only checks if all the links in the tool are working properly.
# This is only to assist in debugging the tool.

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from urllib.parse import urljoin
import threading
import sys
import os

# Set up the Selenium WebDriver (using Safari here)
driver = webdriver.Safari()

# Open the webpage
url = "http://127.0.0.1:5000/"  # Replace with your target URL
driver.get(url)

# Find all links on the page
links = driver.find_elements(By.TAG_NAME, "a")

# Create a set to store all the links
all_links = set()

# Extract href attributes (links)
for link in links:
	href = link.get_attribute("href")
	if href:
		all_links.add(href)

# Set to track already checked links
already_checked = set()

# To store invalid links and their statuses
invalid_links = []

# Check each link's validity asynchronously
def check_link_validity(link):
	if str(link)[-1] != '#' and str(link)[-1]!=']':
		try:
			response = requests.get(link, timeout=100)
			if response.status_code == 200:
				print(f"Valid link: {link}")
			else:
				print(f"Invalid link (Status code {response.status_code}): {link}")
				invalid_links.append({'url': link, 'status': f"Status code {response.status_code}"})
		except requests.exceptions.RequestException as e:
			print(f"Error with link: {link} ({e})")
			invalid_links.append({'url': link, 'status': f"Error: {e}"})
		finally:
			already_checked.add(link)

# Function to process all links in parallel
def process_links_in_parallel():
	threads = []
	for link in all_links:
		if link not in already_checked:
			if url in link:
				thread = threading.Thread(target=check_link_validity, args=(link,))
				threads.append(thread)
				thread.start()
			else:
				print(f"{link} is external, not checking")

	# Wait for all threads to finish
	for thread in threads:
		thread.join()

# Process main page links
process_links_in_parallel()

# After checking the main links, check for sub-links
# Gather all sub-links without visiting individual pages
sub_links = set()
for link in all_links:
	print(f'Checking subpages for {link}')
	
	try:
		response = requests.get(link, timeout=100)
		if response.status_code == 200:
			# Add sub-links from the page to check
			driver.get(link)
			sub_elements = driver.find_elements(By.TAG_NAME, "a")
			for sub_link in sub_elements:
				sub_href = sub_link.get_attribute("href")
				if sub_href and sub_href not in already_checked:
					sub_links.add(sub_href)
	except requests.exceptions.RequestException as e:
		print(f"Error with link: {link} ({e})")

# Now check all sub-links asynchronously
all_links.update(sub_links)
process_links_in_parallel()

# Generate the HTML report for invalid links
def generate_html_report(invalid_links):
	# HTML structure
	html_content = """
	<html>
	<head>
		<title>Broken Link Report</title>
		<style>
			body {
				font-family: Arial, sans-serif;
				margin: 20px;
			}
			table {
				width: 100%;
				border-collapse: collapse;
				margin-top: 20px;
			}
			th, td {
				border: 1px solid #ddd;
				padding: 8px;
				text-align: left;
			}
			th {
				background-color: #f2f2f2;
			}
		</style>
	</head>
	<body>
		<h1>Broken Link Report</h1>
		<p>The following links were found to be broken:</p>
		<table>
			<tr>
				<th>Link URL</th>
				<th>Status</th>
			</tr>
	"""

	# Add rows for each invalid link
	for link in invalid_links:
		html_content += f"""
		<tr>
			<td><a href="{link['url']}" target="_blank">{link['url']}</a></td>
			<td>{link['status']}</td>
		</tr>
		"""

	html_content += """
		</table>
	</body>
	</html>
	"""

	# Save the report to a file
	output_file = "broken_link_report.html"
	with open(output_file, "w") as file:
		file.write(html_content)
	
	print(f"Report generated: {output_file}")

# Generate the HTML report for broken links
generate_html_report(invalid_links)

# Close the WebDriver
driver.quit()
