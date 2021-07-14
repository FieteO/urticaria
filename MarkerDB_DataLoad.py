import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def parse_html(url: str):

    """
    This function sends an request to the MarkerDB_Download-Site and
    returns the html code
    """

    try:
        text = requests.get(url, headers=headers).text
        soup = BeautifulSoup(text, "html.parser")
        return soup

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_links(url: str):

    """
    This function fetches the Downloadlink for the Marker-TSV-Files
    and the Marker-Type mentioned in the Header.

    The return of the Function is a Dict with key=Marker-Type and value=Downloadlink
    """

    soup = parse_html(url=f'{url}/downloads')

    header = [td.text for tbody in soup('tbody')
              for td in tbody('td')
              if len(td.text)> 10]

    links = [f"{url}{a['href']}" for a in soup('a')
            if 'TSV' in a.text
            ]

    return dict(zip(header, links))

# Set an empty DataFrame
def load_marker_date():

    """
    This function iterates through the dict containing the Links for the
    Marker-Data
    """

    df_Marker = pd.DataFrame(columns = ['Marker Name', 'Marker Type'])

    for key , value in get_links(url=url).items():
        df = pd.read_csv(value, sep='\t', usecols=[1], header=None)
        df.columns = ['Marker Name']
        df['Marker Type'] = key
        df_Marker = df_Marker.merge(df, how='outer')

    df_Marker.drop_duplicates(inplace=True, ignore_index=True)

    return df_Marker



def save_DataFrame(data: pd.DataFrame):

    """
    Saves the merged Dataframe into csv.
    """

    target_path = os.path.join(os.getcwd(), 'retrieval/Data')
    filename = 'MarkerDB.csv'
    print(data.head(10))
    try:
        data.to_csv(f'{target_path}/{filename}', sep=';', index=True)
        print(f'DataFrame successfully saved into {target_path}')
    except:
        print('Somthing went wrong during the saving process. Check the code again.')


if __name__ == "__main__":

    url = "https://markerdb.ca"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'}

    data = load_marker_date()
    save_DataFrame(data=data)
