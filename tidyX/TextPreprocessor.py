import re
from unidecode import unidecode
import numpy as np
import regex
import emoji
from pandas import DataFrame
from typing import Union
import spacy
from spacy.lang.es import Spanish
import pandas as pd
from thefuzz import fuzz
from collections import Counter
from typing import List, Tuple
# pip install python-Levenshtein

class TextPreprocessor:
    def __init__(self):
        pass

    @staticmethod
    def remove_repetitions(string: str, exceptions = ["r", "l", "n", "c", "a", "e", "o"]) -> str:
        """
        Removes consecutive repeated characters in a given string, with some optional exceptions.

        For example, the string 'coooroosooo' would be transformed to 'coroso'.

        Args:
            string (str): The text to be processed.
            exceptions (list, optional): A list of characters that can be repeated once consecutively 
                                        without being removed. Defaults to ['r', 'l', 'n', 'c', 'a', 'e', 'o'].

        Returns:
            str: The processed text with consecutive repetitions removed, except for characters in the exceptions list.
        """

        if not exceptions: # (exceptions == None):
            # Remove all consecutive repetitions
            string = re.sub(r'(.)\1+', r'\1', string)
        else:
            # Allow one repetition for characters in exceptions list
            exceptions_pattern = "|".join(re.escape(char) for char in exceptions)
            string = re.sub(r'({})\1+'.format(exceptions_pattern), r'\1\1', string)
            
            # Remove all other consecutive repetitions
            string = re.sub(r'([^{}])\1+'.format(re.escape(exceptions_pattern)), r'\1', string)

        return string

    @staticmethod
    def remove_last_repetition(string: str) -> str:
        """
        Removes the repetition of the last character in each word of a given string.
        
        In Spanish, no word ends with a repeated character. However, in social media,
        it is common to emphasize words by repeating the last character. This function
        cleans the text to remove such repetitions. 
        
        For example, the input "Holaaaa amigooo" would be transformed to "Hola amigo".
        
        Args:
            string (str): The text to be processed.
            
        Returns:
            str: The processed text with the last character of each word de-duplicated.
        """
        
        return re.sub(r'(\w)\1+\b', r'\1', string) 

    @staticmethod
    def remove_urls(string: str) -> str:
        """
        Removes all URLs that start with "http" from a given string.
        
        This function scans the entire string and removes any sequence of characters that
        starts with "http" and continues until a space or end of line is encountered.
        
        Args:
            string (str): The text to be processed.
            
        Returns:
            str: The processed text with URLs removed.
        """
        
        return re.sub(r"http\S+", '', string) # re.sub(r"http[^ ]+", '', string)

    @staticmethod
    def remove_RT(string: str) -> str:
        """
        Removes the "RT" prefix from tweets.
        
        This function removes the "RT" prefix that usually appears at the beginning of retweets.
        It accounts for the possibility of varying white-space after "RT".
        
        Args:
            string (str): The tweet text to be processed.
            
        Returns:
            str: The processed tweet text with the "RT" prefix removed if it appears at the beginning.
        """
        
        return re.sub(r"^RT\s+", '', string) # re.sub("^RT ", '', string)

    @staticmethod
    def remove_accents(string: str, delete_emojis = True) -> str:
        """
        Removes accents and optionally emojis from a string.

        This function removes accent marks from characters in a given string. If specified, it can also remove emojis.

        Args:
            string (str): The input string potentially containing accented characters and/or emojis.
            delete_emojis (bool, optional): If True, removes emojis from the string. Default is True.

        Returns:
            str: The string with accented characters and optionally emojis removed.
        """
        
        if delete_emojis:
            return unidecode(string)
        else:
            string = re.sub(u"[àáâãäå]", 'a', string)
            string = re.sub(u"[èéêë]", 'e', string)
            string = re.sub(u"[ìíîï]", 'i', string)
            string = re.sub(u"[òóôõö]", 'o', string)
            string = re.sub(u"[ùúûü]", 'u', string)
            # Uncomment the next line if you also want to replace "ñ" with "n"
            # string = re.sub(u"[ñ]", 'n', string)
            
        return string

    @staticmethod
    def remove_hashtags(string: str) -> str:
        """
        Removes hashtags from a given string.
        
        This function scans the string and removes any text that starts with a '#' 
        and is followed by alphanumeric characters.
        
        Args:
            string (str): The text that may contain hashtags.
            
        Returns:
            str: The processed text with hashtags removed.
        """
        
        return re.sub(r'#\w+', '', string)

    @staticmethod
    def remove_mentions(string: str, extract = True):
        """
        Removes mentions (e.g., @username) from a given tweet string.

        This function scans the string and removes any text that starts with '@' 
        followed by the username. Optionally, it can also return a list of unique mentions.

        Args:
            string (str): The tweet text that may contain mentions.
            extract (bool, optional): If True, returns a list of unique mentions. Defaults to True.

        Returns:
            str: The processed tweet text with mentions removed.
            list: If `extract` is True, returns a list of unique mentioned accounts in the tweet.
        """
        
        mentions = []
        # Extract mentions if needed
        if extract:
            mentions = list(set(re.findall(r"@\w+", string))) # np.unique(re.findall(pattern = "@[^ ]+", string = string))
        
        # Remove mentions
        string = re.sub(r"@\w+", "", string) # re.sub("@[^ ]+", "", string)
        
        return string, mentions

    @staticmethod
    def remove_special_characters(string: str) -> str:
        """
        Removes all characters from a string except for lowercase letters and spaces.
        
        This function scans the string and removes any character that is not a lowercase letter or a space.
        As a result, punctuation marks, exclamation marks, special characters, numbers, and uppercase letters are eliminated.
        
        Args:
            string (str): The text that may contain special characters.
            
        Returns:
            str: The processed text with special characters removed.
        """
        
        return regex.sub('[^a-z\p{So} ]+', '', string)

    @staticmethod
    def remove_extra_spaces(string: str) -> str:
        """
        Removes extra spaces within and surrounding a given string.
        
        This function trims leading and trailing spaces and replaces any occurrence of consecutive spaces between words with a single space.
        
        Args:
            string (str): The text that may contain extra spaces.
            
        Returns:
            str: The processed text with extra spaces removed.
        """
        
        string = re.sub(" +", " ", string)
        return string.strip()

    @staticmethod
    def space_between_emojis(string: str) -> str:
        """
        Inserts spaces around emojis within a string.
        
        This function adds a space before and after each emoji character in the given string to ensure that emojis are separated from other text or emojis. Extra spaces are then removed.

        Args:
            string (str): The text that may contain emojis.

        Returns:
            str: The processed text with spaces inserted around each emoji.
        """
        
        return TextPreprocessor.remove_extra_spaces(''.join((' ' + c + ' ') if c in emoji.UNICODE_EMOJI['en'] else c for c in string))

    @staticmethod
    def preprocess(string: str, delete_emojis = True, extract = True, 
                exceptions = ["r", "l", "n", "c", "a", "e", "o"]):
        """
        Preprocesses tweets by applying a series of cleaning functions. The function performs the following steps:

        1. Removes the 'RT' prefix from retweeted tweets. (remove_RT)
        2. Converts the entire string to lowercase. (.lower)
        3. Removes all accents and optionally emojis. (remove_accents)
        4. Extracts and/or removes all mentions (e.g., @elonmusk). (remove_mentions)
        5. Removes URLs. (remove_urls)
        6. Removes hashtags. (remove_hashtags)
        7. Removes special characters such as !, ?, -, ;, etc. (remove_special_characters)
        8. Removes extra spaces between words. (remove_extra_spaces)
        9. Removes consecutive repeated characters, with exceptions defined in the `exceptions` parameter. (remove_repetitions and remove_last_repetition)
        
        Args:
            string (str): The raw tweet text.
            delete_emojis (bool): Whether to remove emojis from the string. Default is True.
            extract (bool): If True, returns a list of all accounts mentioned in the tweet. Default is True.
            exceptions (list): List of characters allowed to be repeated. Default is ['r', 'l', 'n', 'c', 'a', 'e', 'o'].

        Returns:
            str: The cleaned tweet text.
            mentions (list): If `extract` is True, a list of mentioned accounts is returned.
        """

        # Remove RT at the beginning of the tweets
        string = TextPreprocessor.remove_RT(string)
        # Lowercase all characters
        string = string.lower()
        # Remove accents:
        string = TextPreprocessor.remove_accents(string, delete_emojis = delete_emojis)
        # Extract and remove all mentions
        string, mentions = TextPreprocessor.remove_mentions(string, extract = extract)
        # Remove links
        string = TextPreprocessor.remove_urls(string)
        # Remove hashtags
        string = TextPreprocessor.remove_hashtags(string)
        # Remove special characters:
        string = TextPreprocessor.remove_special_characters(string)
        # Allow only one space between words
        string = TextPreprocessor.remove_extra_spaces(string)
        # Remove repetited characters
        string = TextPreprocessor.remove_repetitions(string, exceptions = exceptions)
        # Remove repetitions in the last charcater
        string = TextPreprocessor.remove_last_repetition(string)

        if extract:
            return string, mentions
        else:
            return string

    @staticmethod
    def remove_words(string: str, bag_of_words) -> str:
        """Removes all occurrences of words listed in bag_of_words from the string.
        
        This function is particularly useful for removing stopwords. Exercise caution 
        with the words listed in bag_of_words: this function performs an exact match, 
        meaning it won't remove variations of the words not appearing in the bag_of_words.

        Args:
            string (str): The input string containing unwanted words.
            bag_of_words (list): List of words to be removed from the string.

        Returns:
            str: The string with unwanted words removed.
        """
        
        # Create a regex pattern to match any word from bag_of_words surrounded by word boundaries
        pattern = r'\b(?:{})\b'.format('|'.join(re.escape(word) for word in bag_of_words)) # r'\b(?:{})\b'.format('|'.join(bag_of_words))
        
        # Note that I've used re.escape to ensure that any special characters in your bag of words are treated as 
        # literals. This is useful in cases where the bag of words contains characters that could be misinterpreted 
        # as regular expression metacharacters (like ., ?, *, etc.).

        # Remove words from the string that match the pattern
        string = re.sub(pattern, '', string)
        
        # Remove extra spaces
        string = TextPreprocessor.remove_extra_spaces(string)

        return string

    @staticmethod
    def unnest_tokens(df: DataFrame, input_column: str, create_id: bool = True) -> DataFrame:
        """Flattens a DataFrame by tokenizing a specified column.

        This function takes a pandas DataFrame and a column name to tokenize. 
        Each token becomes a row in the resulting DataFrame. Tokens are separated by spaces.

        Args:
            df (DataFrame): The input DataFrame to be flattened.
            input_column (str): The name of the column to tokenize.
            create_id (bool, optional): If True, adds an "id" column based on the DataFrame's index. Defaults to True.

        Returns:
            DataFrame: A DataFrame where each row corresponds to a token.
        """
        
        # Reset the index and create an "id" column if create_id is True
        if create_id:
            df = df.reset_index().rename(columns={"index": "id"})
        
        # Tokenize the specified column
        df[input_column] = df[input_column].str.split(" ")
        
        # Explode the DataFrame to create one row per token
        df = df.explode(input_column)
        
        return df

    @staticmethod
    def spanish_lemmatizer(token: str, model: Spanish) -> str:
        """Lemmatizes a given token using Spacy's Spanish language model.
        
        Note: Before using this function, a Spacy model for Spanish should be downloaded.
        Use `python -m spacy download name_of_model` to download a model. Available models:
        "es_core_news_sm", "es_core_news_md", "es_core_news_lg", "es_dep_news_trf".
        For more information, visit https://spacy.io/models/es

        Args:
            token (str): The token to be lemmatized.
            model (spacy.lang.es.Spanish): A Spacy language model object.

        Returns:
            str: The lemmatized version of the token, with accents removed.
        """
        
        if not token:
            return token
        
        try:
            lemma = model(token)[0].lemma_
            lemma = TextPreprocessor.remove_accents(lemma)
            return lemma
        except Exception as e:
            print(f"An error occurred: {e}")
            return token
    
    @staticmethod
    def create_bol(lemmas: np.ndarray, verbose: bool = True) -> pd.DataFrame:
        """Group lemmas based on Levenshtein distance to handle misspelled words in social media data.
        
        Args:
            lemmas (np.ndarray): An array containing lemmas to be grouped.
            verbose (bool, optional): If True, prints the progress at each 5% increment. Defaults to True.
            
        Returns:
            pd.DataFrame: A DataFrame with four columns ["bow_id", "bow_name", "lemma", "threshold"].
                        Each row represents a lemma and the bag of lemmas it belongs to.
        """
        
        # Create an empty dataframe to store the bags of words (lemmas)
        bow_df = pd.DataFrame()
        # How many lemmas do we have?
        num_lemmas = len(lemmas)
        # Iterator
        iterator = 0
        # Step to show the progress every 5%
        step = int(num_lemmas * 0.05)

        # lemmas is an array that will reduce its size because when an element of lemmas is assigned to a bag of
        # words, it will be dropped from the array. When all the lemmas have been assigned to a bag of words,
        # lemmas array will be empty.
        while len(lemmas) > 0:
            try:
                # Pick a lemma: lemma i
                current_lemma = lemmas[0]
                # Let calculate the distance between the lemma i and the other lemmas
                distances = np.array([fuzz.ratio(current_lemma, lemma) for lemma in lemmas])
                # fuzz.ratio is very sensible to small words so is important to control for this
                threshold = 88 if len(current_lemma) < 3 else 87 if len(current_lemma) <= 4 else 86 if len(current_lemma) == 5 else 85
                
                # Find the position inside the array of the lemmas that have threshold% coincidence with lemma i
                similar_lemmas_idx = np.where(distances > threshold)[0]
                # Create bag_i
                similar_lemmas = lemmas[similar_lemmas_idx]

                # Compile the information in a dataframe
                bag_data = pd.DataFrame({
                    "bow_id": iterator + 1,
                    "bow_name": similar_lemmas[0],
                    "lemma": similar_lemmas,
                    "similarity": distances[similar_lemmas_idx],
                    "threshold": threshold
                })

                # Delete the words that were already assigned to a bag of words.
                # The reason is because the lemma i is near to the lemma j, the opposite is also true.
                # And if exists another word k that is near to j, we also expect that the word k also be near to the word i
                lemmas = np.delete(lemmas, similar_lemmas_idx)
                # Put the results in the important DataFrame
                bow_df = pd.concat([bow_df, bag_data])
            
                # Progress indicator
                if verbose and iterator % step == 0:
                        progress = np.round(100 - (len(lemmas) / num_lemmas * 100), 2)
                        print(f"{progress}% completed.")
                        
                iterator += 1
            except Exception as e:
                print(f"An error occurred: {e}")
                break
        
        return bow_df.reset_index(drop = True)

