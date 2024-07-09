import requests
from bs4 import BeautifulSoup


def google_search(query):
    try:
        # Perform Google search
        url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Check if request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for search result links
            search_results = soup.find_all('div', class_='tF2Cxc')

            if search_results:
                # Extract titles and URLs from search results
                results = []
                for result in search_results:
                    link = result.find('a')
                    title = link.text if link else 'No title'
                    url = link['href'] if link else 'No URL'
                    results.append({'title': title, 'url': url})

                # Prepare response
                response_text = ''
                for idx, result in enumerate(results[:3], start=1):
                    response_text += f"Result {idx}: {result['title']}\n"
                    response_text += f"URL: {result['url']}\n\n"

                return response_text.strip()
            else:
                return "No relevant results found."
        else:
            return f"Failed to perform Google search. Status code: {response.status_code}"
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "Error occurred during search."
