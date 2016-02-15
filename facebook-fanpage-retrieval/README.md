## Facebook FanPage Data Retrieval

**Author: [Douglas Cirqueira](https://br.linkedin.com/in/douglascirqueira)**

**This code retrieves data from a Facebook FanPage. This data includes posts and comments of those posts.**

**Configuration**
In order to run the code, first set the configs in the `config.xml` file, which has the following settings:

- fanpage: the Facebook FanPage to work on.
- accessToken: a valid Facebook API access token, which can be obtained [here](https://developers.facebook.com/tools/explorer/)
- posts quantity: the maximum number of posts to be retrieved.
- since: Since when posts should be retrieved.
- until: Until when posts should be retrieved.
- comments quantity: the maximum number of comments to be retrieved from posts.


**Data**
The data retrieved from a Facebook FanPage will be saved in the following pattern:

- data
  - fanpage name
  	- posts (directory with a csv file containing all posts)
  	- comments (directory with csv files (named as `date__postId`) containing comments from all retrieved posts and one csv file containing all comments retrieved)


**Running Code**
For running the code, just run the file `retrieve_fanpage.py`
