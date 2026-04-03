#SI 201 HW4 (Library Checkout System)
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
    with open(html_path, 'r', encoding='utf-8-sig') as file:
        html_content = file.read()
#create a soup onject to parse the html contwnt
    soup = BeautifulSoup(html_content, 'html.parser')

    # we are now looping through all div tages that have the class we are lookign for
    #we then use finall to reurn a loist of all matching elements
    #each matching element is called a card to resprest one listing card
    pattern = r'/(\d+)\?'
    divs = soup.find_all('div', itemprop ="itemListElement")
    for item in divs:
        mtag = item.find("meta", itemprop = 'url')
        if mtag is None:
            continue
        full_url = mtag.get('content', '')
        id_matches = re.findall(pattern, full_url)
        if not id_matches:
            continue
        listing_id = id_matches[0]
        title_id = 'title_'+listing_id
        title_div = soup.find('div', id=title_id)
        listing_title=title_div.get_text(strip = True)
        listings.append((listing_title,listing_id))
    return listings



   
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================

def get_listing_details(listing_id) -> dict:
    """
    Parses the individual listing HTML file and extracts:
    policy_number, host_type, host_name, room_type, location_rating.

    Returns:
        dict: {listing_id: {key: value, ...}}
    """
     # Construct the file path
    filename = f"html_files/listing_{listing_id}.html"
    
    # Read HTML file
    with open(filename, 'r', encoding='utf-8-sig') as file:
        html = file.read()
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    policy = "Pending"  # Default if not found
    host_section = soup.find('li', class_='f19phm7j dir dir-ltr')  # Host info container
    
    if host_section:
        span = host_section.find("span", class_="ll4r2nl dir dir-ltr")  # The span containing policy/license info
        if span:
            text = span.get_text().strip().replace("\ufeff", "")  # Clean whitespace/unicode
            # Categorize into Pending, Exempt, or license number
            if "exempt" in text:
                policy = "Exempt"
            elif "pending" in text:
                policy = "Pending"
            elif "STR" in text:
                policy = text


    # class_ to use is = _1mhorg9
    # soup.find("span", class_="_1mhorg9")
    host_type = "regular"  # default
    if soup.find("span", class_="_1mhorg9"):
        host_type = "Superhost"
    
    #class to use it _tqmy57
    host_name = "Unknown"  # default

    host_tags = soup.find('div' , class_ = 'tehcqxo dir dir-ltr') 
    name_div = host_tags.find('h2') if host_tags else None

    if name_div:
        host_name = name_div.get_text().strip().replace("Hosted by ", "")
    
    subtitle_tag = soup.find('h2', class_='i1j2t6l2')  # Listing subtitle
    subtitle = subtitle_tag.get_text().strip() if subtitle_tag else ""
    
    if "Private" in subtitle:
        room_type = "Private Room"
    elif "Shared" in subtitle:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"

   #class to use is _4oybiu
    loc_rating = 0.0  # default

    spans = soup.find_all('span', class_='_4oybiu')

    try:

        locationspan = spans[3]
        text = locationspan.get_text().strip()

        value = float(text)

        loc_rating = value
    except:
        loc_rating =0
            
    
      

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

    listings = load_listing_results(html_path)

    for title, listing_id in listings:
        details_dict = get_listing_details(listing_id)[listing_id]

        listing_tuple = (
            title,
            listing_id,
            details_dict["policy_number"],
            details_dict["host_type"],
            details_dict["host_name"],
            details_dict["room_type"],
            details_dict["location_rating"]
        )
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
    # Sort by Location Rating (descending)
    sorted_data = sorted(data, key=lambda x: x[-1], reverse=True)

    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
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
    ratings_dict = {}  #intialize our dictionary so we cna store rating for each room type
    for listing in data: #we loop through our data
        room_type = listing[5]    #now we are setting room_type to the vaule in lsitings 6th position  
        rating = listing[6]       #same concept as room_type    
        if rating > 0.0:        #we are now checkingif the rating is greater than 0 so that we arent including listings that dont have ratings which would mess with our avg      
            if room_type not in ratings_dict: #here we check if the room type hasnt been seen before which is our classic dictionary technique
                ratings_dict[room_type] = []
            ratings_dict[room_type].append(rating)
    # all the above is how weve been doing this beklow we then loop through and calculate avg by summing ratings and dividing by the count rounding to the first decimal place
    avg_ratings = {}
    for room_type, ratings in ratings_dict.items():
        if len(ratings) == 0:
            break
        avg_ratings[room_type] = round(sum(ratings) / len(ratings), 1)


    return avg_ratings
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
    invalid_listings = []
    # we create two regex patterns to check our data
    pattern1 = re.compile(r"20\d{2}-00\d{4}STR")  # 20##-00####STR
    pattern2 = re.compile(r"STR-000\d{4}")        # STR-000####
#we list through each listing tuple in our data and extract the listing id and the policy number
    for listing in data:
        listing_id = listing[1]
        policy = listing[2]    
        # Ignore "Pending" and "Exempt" by skipping over to the next one
        if policy in ["Pending", "Exempt"]:
            continue
        # Check if policy matches either valid format
        if not (pattern1.fullmatch(policy) or pattern2.fullmatch(policy)):
            if listing_id =="":
                break

            
    invalid_listings.append(listing_id)


    return invalid_listings
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
    # Base URL for Google Scholar search
    url = "https://scholar.google.com/scholar"

    # Parameters for the search query
    params = {
        "q": query
    }

    # Send the request
    response = requests.get(url, params=params)

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    titles = []

    # Each result title is inside an <h3 class="gs_rt">
    results = soup.find_all("h3", class_="gs_rt")

    for result in results:
        title = result.get_text(strip=True)
        titles.append(title)

    return titles
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
        
        self.assertEqual(len(self.listings), 18, "There should be exactly 18 listings extracted.")

    # Check that the FIRST (title, id) tuple is correct
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"),
                        "The first listing should be ('Loft in Mission District', '1944564').")


    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]


        
       
        details_list = []

    # Call get_listing_details() on each listing id and collect the results
        for listing_id in html_list:
            details = get_listing_details(listing_id)
            details_list.append(details[listing_id])

            # Spot-check 1: Listing 467507 has the correct policy number
        self.assertEqual(details_list[0]["policy_number"], "STR-0005349",
                        "Listing 467507 should have policy number 'STR-0005349'.")
        self.assertEqual(details_list[0]['policy_number'], 'STR-0005349', 'Liting 0005349 is STR-0005349')
        print('dandjwkl')
        # Spot-check 2: Listing 1944564 has host type 'Superhost' and room type 'Entire Room'
        index_1944564 = html_list.index("1944564")
        self.assertEqual(details_list[index_1944564]["host_type"], "Superhost",
                        "Listing 1944564 should have host type 'Superhost'.")
        self.assertEqual(details_list[index_1944564]["room_type"], "Entire Room",
                        "Listing 1944564 should have room type 'Entire Room'.")

        # Spot-check 3: Listing 1944564 has location rating 4.9
        self.assertEqual(details_list[index_1944564]["location_rating"], 4.9,
                        "Listing 1944564 should have location rating 4.9.")
        print('hi')
        print(details_list[0])
        print('Hello')     

    def test_create_listing_database(self):
        


        
        for listing in self.detailed_data:
            self.assertEqual(len(listing), 7, f"Each listing tuple should have 7 elements, found {len(listing)}.")
        last_listing = self.detailed_data[-1]
        expected_last = ("Guest suite in Mission District", "467507", "STR-0005349",
                     "Superhost", "Jennifer", "Entire Room", 4.8)
        self.assertEqual(last_listing, expected_last, "The last listing tuple does not match the expected values.")

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # 1. Write the CSV
        output_csv(self.detailed_data, out_path)

        # 2. Read it back
        with open(out_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # 3. Check the first data row (after headers)
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253",
                                "Superhost", "Ingrid", "Entire Room", "5.0"])

        # 4. Remove the file to clean up
        os.remove(out_path)


    def test_avg_location_rating_by_room_type(self):
    # Call the function with the detailed data
        avg_ratings = avg_location_rating_by_room_type(self.detailed_data)
        
        # Check that the average for "Private Room" is 4.9
        self.assertIn("Private Room", avg_ratings, "Private Room should be a key in the average ratings dictionary.")
        self.assertAlmostEqual(avg_ratings["Private Room"], 4.9, places=1,
                            msg=f"Expected average for Private Room to be 4.9, got {avg_ratings['Private Room']}")


    def test_validate_policy_numbers(self):
        
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"],
                     "The invalid policy listings should exactly match ['16204265'].")




def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")




if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)
