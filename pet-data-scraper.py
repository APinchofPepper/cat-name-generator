import requests
from bs4 import BeautifulSoup
import os
import time
import re
import shutil

# List of base URLs for each city
base_urls = {
    'New York': 'https://www.adoptapet.com/pet-search?speciesId=2&radius=50&postalCode=10029&city=New+York&state=NY&sortOption=Nearest&transport=false&page=',
    'Los Angeles': 'https://www.adoptapet.com/pet-search?speciesId=2&radius=50&postalCode=90001&city=Los+Angeles&state=CA&sortOption=Nearest&transport=false&page=',
    'Chicago': 'https://www.adoptapet.com/pet-search?speciesId=2&radius=50&postalCode=60654&city=Chicago&state=IL&sortOption=Nearest&transport=false&page=',
    'Houston': 'https://www.adoptapet.com/pet-search?speciesId=2&radius=50&postalCode=77001&city=Houston&state=TX&sortOption=Nearest&transport=false&page=',
    'Phoenix': 'https://www.adoptapet.com/pet-search?speciesId=2&radius=50&postalCode=85001&city=Phoenix&state=AZ&sortOption=Nearest&transport=false&page='
}

# Directory to save dataset
os.makedirs('dataset', exist_ok=True)

# Set headers to include a User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def sanitize_filename(name):
    """Sanitize the filename by replacing or removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def is_valid_name(name):
    """Check if the name is valid based on the specified criteria."""
    # Check if the name contains any numbers, unwanted words, or non-letter characters
    invalid_patterns = [
        r'\d',                # Numbers
        r'[^\w\s-]',          # Non-letter characters (excluding hyphen and space)
        r'\b(foster|adopt|and|FOSTER|ADOPT|AND|FOSTERANDADOPT|FOSTERADOPT|FOSTER-ADOPT|fosterandadopt|FosterandAdopt|foster-adopt|Foster-Adopt)\b',  # Unwanted words
    ]
    for pattern in invalid_patterns:
        if re.search(pattern, name.lower()):
            return False
    return True

def scrape_page(url, city_name, seen_names):
    # Send a GET request to the website with headers
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all cat listings (limit to 41 as max per page)
        cat_listings = soup.find_all('div', class_='pet-card')[:41]

        # If there are no cat listings, stop scraping
        if not cat_listings:
            print(f'No more listings found on {url}. Ending scraping for {city_name}.')
            return False

        valid_data_found = False  # Flag to check if valid data is found

        # Loop through each listing and extract relevant data
        for idx, cat in enumerate(cat_listings):
            # Extract the cat's name
            name_tag = cat.find('p', class_='font-bold truncate truncate-12 text-h3 tablet:text-h3-secondary leading-h4 name tablet:truncate-24')
            name = name_tag.text.strip() if name_tag else f"Unknown_{idx}"
            
            # Validate the name
            if not is_valid_name(name) or name in seen_names:
                print(f'Skipping invalid or duplicate name: {name}')
                continue

            sanitized_name = sanitize_filename(name)
            seen_names.add(name)  # Mark this name as seen

            # Extract the cat's gender (if available)
            gender_age_tag = cat.find('div', class_='sex-age')
            gender_age_text = gender_age_tag.text.strip() if gender_age_tag else "Unknown"
            gender = gender_age_text.split(',')[0].strip() if ',' in gender_age_text else "Unknown"

            # Extract the image URL from the <img> tag within <div class="z-10 pet-photo-inner">
            image_div = cat.find('div', class_='z-10 pet-photo-inner')
            if image_div:
                image_tag = image_div.find('img')
                image_url = image_tag['src'] if image_tag else None
            else:
                image_url = None

            if image_url and name != "Unknown" and gender != "Unknown":
                valid_data_found = True  # Valid data is found

                cat_dir = os.path.join('dataset', city_name, sanitized_name)
                os.makedirs(cat_dir, exist_ok=True)

                # Save the cat's information in a text file with UTF-8 encoding
                with open(os.path.join(cat_dir, 'info.txt'), 'w', encoding='utf-8') as f:
                    f.write(f"Name: {name}\nGender: {gender}")

                # Download the image
                img_response = requests.get(image_url, headers=headers)
                if img_response.status_code == 200:
                    img_filename = os.path.join(cat_dir, 'image.jpg')
                    with open(img_filename, 'wb') as img_file:
                        img_file.write(img_response.content)
                    print(f'Saved data for {name} in {city_name}')
                else:
                    print(f'Failed to download image for {name}. Deleting incomplete data in {city_name}.')
                    shutil.rmtree(cat_dir)
            else:
                print(f'Data for {name} is incomplete (Name: {name}, Gender: {gender}, Image URL: {image_url}). Deleting data in {city_name}.')
                if name != "Unknown" and gender != "Unknown" and image_url:
                    cat_dir = os.path.join('dataset', city_name, sanitized_name)
                    if os.path.exists(cat_dir):
                        shutil.rmtree(cat_dir)

        # If no valid data was found on this page, stop scraping this city
        if not valid_data_found:
            print(f"No valid data found on page {url}. Stopping scraping for {city_name}.")
            return False

        return True
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code} for {city_name}')
        return False

# Scrape each city
for city_name, base_url in base_urls.items():
    print(f"Starting scraping for {city_name}")
    page_number = 1  # Start scraping at page 1 for each city
    seen_names = set()  # Initialize a set to track seen names

    while True:
        current_url = f"{base_url}{page_number}"
        print(f"Scraping page: {page_number} for {city_name}")
        
        # Scrape the current page
        if not scrape_page(current_url, city_name, seen_names):
            break  # Stop if no more valid listings are found

        # Move to the next page
        page_number += 1
        
        # Throttle the requests to avoid overwhelming the server
        time.sleep(2)

    # After finishing with the current city, move on to the next city in the loop
