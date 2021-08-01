import os
import hashlib
import pandas as pd


def get_path(path:str):
    pdf_filepaths = []
    for root, directories, files in os.walk(path, topdown=False):
        for name in files:
            if name[-4:] == '.pdf':
                pdf_filepaths.append(os.path.join(root, name))

    return pdf_filepaths

# ## Check data for duplicate entries
# We can identify duplicate pdfs by computing the checksum of each file and then counting the unique values. So let us define the checksum function `get_checksum()`:

# https://stackoverflow.com/questions/16874598/how-do-i-calculate-the-md5-checksum-of-a-file-in-python#16876405



def extract_filename(filepath: str) -> str:
    filename = os.path.basename(filepath).split('.')
    return filename[0]


def get_checksum(filepath: str) -> str:
    # Open,close, read file and calculate MD5 on its contents
    with open(filepath, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        return hashlib.md5(data).hexdigest()


#
def export_filelist(list_filepath):

    """
    Create a pandas dataframe from the list of filepath's and
    also add a checksum column that is computed using our `get_checksum()` function.

    Finally we Export the DataFrame with the unique Files
    """

    df = pd.DataFrame(list_filepath, columns = ['path'])
    df['Name'] = df['path'].apply(extract_filename)
    df['checksum'] = df['path'].apply(get_checksum)

    # In the final step, we can analyse the results of this activity. It seems that our available data is in reality only half as large as it initially appears.
    print('Total number of pdfs: {}'.format(df['checksum'].count()))
    print('Total number of unique pdfs: {}'.format(len(df['checksum'].unique())))

    # Now we create a df of unique pdfs by removing duplicate checksums

    df_unique = df.drop_duplicates(subset=['checksum'])
    df_unique.to_csv('./retrieval/Data/ImportFileList.csv')

if __name__ == "__main__":


    path = './CAPTUM'
    filelist = get_path(path=path)
    if len(filelist)>0:
        export_filelist(list_filepath=filelist)
        print('Export was successfull!')

    else: print('Filelist was empty. No Export!')

