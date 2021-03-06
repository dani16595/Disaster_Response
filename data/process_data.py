import sys
import pandas as pd
import sqlalchemy as db

def load_data(messages_filepath, categories_filepath):
    """Load two datasets csv and merge them

    Parameters:
    messages_filepath (string): path of message csv
    categories_filepath (string): path of categories csv

    Returns:
    dataframe:df

    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = messages.merge(categories, left_on='id', right_on='id')
    return df


def clean_data(df):
    """Clean data, create labels, clean columns names and drop duplicates

    Parameters:
    df (dataframe): dataframe which we can clean

    Returns:
    dataframe:df

    """
    categories = df["categories"].str.split(";",expand=True)
    row = categories.loc[0]
    category_colnames = row.apply(lambda x: x[:-2]).tolist()
    categories.columns = category_colnames
    # set each value to be the last character of the string
    for column in category_colnames:
        categories[column] = categories[column].astype(str).str.replace(column+"-","")
        #convert values 2 to 1
        categories.related[categories[column]=="2"]="1"
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    df=df.drop(["categories"],axis=1)
    df= pd.concat([df, categories],axis=1)
    # drop duplicates
    df.drop_duplicates(keep=False,inplace=True)
    return df


def save_data(df, database_filename):
    """Save dataframe into a database

    Parameters:
    df (dataframe): dataframe which we can save
    database_filename: path of database which we can save


    """
    engine = db.create_engine('sqlite:///'+database_filename)
    sql = db.text('DROP TABLE IF EXISTS disaster;')
    engine.execute(sql)
    df.to_sql("disaster", engine, index=False)


def main():
    if len(sys.argv) == 4:
        
        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()