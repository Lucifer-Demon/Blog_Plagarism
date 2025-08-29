import plagiarismchecker.algorithm.ConsineSim as cosine_calc_module
from apiclient.discovery import build
import time
import os
print(f"DEBUG: Running webSearch.py from: {os.path.abspath(__file__)}")
print(f"DEBUG: In webSearch.py - cosine_calc_module object: {cosine_calc_module}")
print(f"DEBUG: In webSearch.py - type of cosine_calc_module object: {type(cosine_calc_module)}")
# print(f"DEBUG: In webSearch.py - cosine_calc_module.cosineSim object: {cosine_calc_module.cosineSim}") #backup
# print(f"DEBUG: In webSearch.py - type of cosine_calc_module.cosineSim object: {type(cosine_calc_module.cosineSim)}") #backup


# Current VALID API key
searchEngine_API = 'AIzaSyCAeR7_6TTKzoJmSwmOuHZvKcVg_lhqvCc' 
searchEngine_Id = '758ad3e78879f0e08'

def searchWeb(text, output, c):
    max_retries = 3
    initial_delay = 1 # seconds

    for attempt in range(max_retries):
        try:
            resource = build("customsearch", 'v1',
                             developerKey=searchEngine_API).cse()
            result = resource.list(q=text, cx=searchEngine_Id).execute()
            searchInfo = result['searchInformation']

            if(int(searchInfo['totalResults']) > 0):
                maxSim = 0
                itemLink = ''
                # This will store the highest similarity item's details for the current search
                best_item_details = {} 
                numList = len(result['items']) 
                if numList >= 5: # Limit to top 5 results for processing
                    numList = 5
                for i in range(0, numList):
                    item = result['items'][i]
                    content = item['snippet']
                    
                    # --- CALL THE FUNCTION USING THE MODULE ALIAS ---
                    simValue = cosine_calc_module.cosineSim(text, content)
                    if simValue > maxSim:
                        maxSim = simValue
                        itemLink = item['link']
                        # Store specific details you need for the template from the 'item'
                        best_item_details = {
                            'title': item.get('title', 'No Title'),
                            'snippet': item.get('snippet', 'No Snippet'),
                            'displayLink': item.get('displayLink', itemLink)
                        }
                    
                    # If this specific link was already in 'output' from previous searches,
                    # ensure we use its original link, and potentially update its details
                    if item['link'] in output:
                        itemLink = item['link']
                        break # Found a match, prioritize it for updating

                if itemLink: # Only update if a valid itemLink was found
                    if itemLink in output:
                        print('if', maxSim)
                        output[itemLink]['count'] = output[itemLink].get('count', 0) + 1 # Increment count
                        # Update similarity based on average if this link was already present
                        c[itemLink] = ((c[itemLink] * (output[itemLink]['count']-1) + maxSim)/(output[itemLink]['count']))
                    else:
                        print('else', maxSim)
                        print(text)
                        print(itemLink)
                        # Store the details along with an initial count for a new link
                        output[itemLink] = {
                            'count': 1,
                            'title': best_item_details.get('title'),
                            'snippet': best_item_details.get('snippet'),
                            'displayLink': best_item_details.get('displayLink'),
                            # Add other fields from 'item' if needed
                        }
                        c[itemLink] = maxSim
            return output, c, 0 # Success, return 0 for error code

        except Exception as e:
            print(text)
            print(f"Attempt {attempt + 1} failed: {e}")
            # Check for rate limit errors to retry
            if ("per-second limit" in str(e) or "daily limit" in str(e)) and attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                # If it's not a rate limit error, or max retries reached, return permanent failure
                print('error')
                c['error'] = f"Web search failed: {str(e)}" # Pass specific error to 'c'
                return output, c, 1 # Permanent failure, return 1

    # If all retries fail, set a final error message
    c['error'] = "Web search failed after multiple retries due to rate limit or other error."
    return output, c, 1