# TweetIndexer
This is an indexer meant to process .tsv tweet files (user, text, favourites, retweets, UNIX timestamp), and create a system of indexes to be later used for search purposes
It also contains a search utility for the created index, capable of looking up users and their tweets (full text search), is able to predict a user's sentiment for a word, output search to a file, or output the most frequently occuring words.

## Usage:
The program asks for a query, into which multiple things can be input separated by a space

- text:"text to search" -> output all matching tweets and their similarity score
- user:UserName -> outputs all tweets by the user
- freq(from,to) -> The frequency of top words, from the top X (top 3rd place) to top X place (up to 17th place)
- sentiment:UserName:word -> outputs the tweet plus the sentiment score from -1 to 1

Freq and sentiment can only be used alone, however text and user search can either be used independently or together. Due to the amount of output results it's a better idea to limit the amount displayed, or save the output to a file instead of the terminal:

-lX -> argument that limits output to top X best results.. for example: "user:Mihkail100 -l5" outputs only 5 tweets. With text, it outputs 5 best matches.
-o -> saves output to output.txt for viewing

-l and -o can be used together, but can only be used with text and user search.
