# SI 201 HW4 (Library Checkout System)
# Your name:James Mancilla
# Your student id:
# Your email:jameman@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = []

    # open the file html_path in read mode and assigns it to file
    #html content then reads the entire contents of the html file into a string varibale
    with open(html_path, 'r') as file:
        html_content = file.read()
#create a soup onject to parse the html contwnt
    soup = BeautifulSoup(html_content, 'html.parser')

    # we are now looping through all div tages that have the class we are lookign for
    #we then use finall to reurn a loist of all matching elements
    #each matching element is called a card to resprest one listing card
    for card in soup.find_all('div', class_='t1jojoys dir dir-ltr'):  # class from search results
        a_tag = card.find('a', href=True)
        #a tage checks if an anchro tag was found in which it gets the value of the href attricute 
        #we then check if the URL contains /rooms/ and estract listing ids 
        if a_tag:
            link = a_tag['href']
            if "/rooms/" in link:
                # get the listing id from the URL we using [1] to take the second part and .split(?) to splt at ? to remove query parameters [0] then gets the first
                listing_id = link.split("/rooms/")[1].split("?")[0]
                # get the title from the card inse the anchrotag
                title = a_tag.get_text().strip()
                if title != "":
                    listings.append((title, listing_id))

    return listings


    
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    #create the filename  and open it in read mode and then read the entre HTML content into a string 
    filename = f"html_files/listing_{listing_id}.html"
    with open(filename, 'r') as file:
        html = file.read()
    #we then create our beautiful soup object to parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    # we rhewn set the degault policy number to pendingwhich will be updated if found
    policy = "Pending"  # default
    host_section = soup.find('div', class_='f19phm7j dir dir-ltr')  # container for host info
    if host_section:
        lis = host_section.find_all('li') #wwe first check if the host sectionw as found then we final all li which stands for list items within the host section
        for li in lis: #once we habe them all our goal is then to looop through each item and get the content of the list item and remove whitespace If found, sets policy to that text and breaks out of the loop (stops searching)
            text = li.get_text().strip()
            if "STR" in text or text.lower() == "exempt":
                policy = text
                break

    # host typle then sets the default to regular and id the host section exitss and contains the word superhost in the text we change it
    host_type = "regular"
    if host_section and "Superhost" in host_section.get_text():
        host_type = "Superhost"

    # we then go through and find h2 heading tag within the host section to get a name
    host_name_tag = host_section.find('h2')
    host_name = host_name_tag.get_text().strip() if host_name_tag else "Unknown"

    # we then find all h2 rags with the class below and get the subtitle text or empty string if not found
    subtitle_tag = soup.find('h2', class_='i1j2t6l2')  # the listing subtitle
    subtitle = subtitle_tag.get_text().strip() if subtitle_tag else ""
    if "Private" in subtitle:
        room_type = "Private Room" #we then try and determine the room type
    elif "Shared" in subtitle:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

    #Sets default location rating to 0.0 Finds the first <span> with class below then check if the rating tage was found and convert it to a float and make sure that worked
    loc_rating = 0.0
    rating_tag = soup.find('span', class_='r1dxllyb dir dir-ltr')
    if rating_tag:
        try:
            loc_rating = float(rating_tag.get_text().strip())
        except:
            loc_rating = 0.0

    # final nested dict with all information
    return {
        listing_id: {
            "policy_number": policy,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": loc_rating
        }
    }
    


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    database = []

    # get all the titles and ids from the search results
    listings = load_listing_results(html_path)

    # loop through each listing
    for title, listing_id in listings:
        # get the details dictionary for this listing
        details = get_listing_details(listing_id)[listing_id]  # nested dict

        # create a tuple with all the info in order
        listing_tuple = (
            title,
            listing_id,
            details["policy_number"],
            details["host_type"],
            details["host_name"],
            details["room_type"],
            details["location_rating"]
        )

        # add it to the database
        database.append(listing_tuple)

    return database
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    # we now sort the last element in each tuple in descending order
    sorted_data = sorted(data, key=lambda x: x[-1], reverse=True)

    # we then open the file in write mode 
    with open(filename, 'w', newline='') as csvfile:
        #we then create a CSV writer object which takes the file object and rreturns a writer that can write CSV rows
        writer = csv.writer(csvfile)
        
        # write headers
        writer.writerow(["Listing Title", "Listing ID", "Policy Number",
                         "Host Type", "Host Name", "Room Type", "Location Rating"])

        # write each row
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)