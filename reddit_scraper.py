import praw
import csv
import validators
import argparse
import prawcore 
import matplotlib.pyplot as plt 
# Reddit API authentication
reddit_API = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    username="YOUR_REDDIT_USERNAME",
    password="YOUR_REDDIT_PASSWORD",
    user_agent="linux:APIBASEDSCRAPER:1.0 (by u/YOUR_REDDIT_USERNAME)"
)

def url_validation(url):
    try:
        validation = validators.url(url)
        return bool(validation)
    
    except Exception:
        return False 

def scraping_contents(subreddit, limit_of_comments=15):
    """
    Streams comments from a subreddit until the limit is reached.
    """
    formatted_lines = []

    try:
        stream_generation = reddit_API.subreddit(subreddit)

        comment_streams = stream_generation.stream.comments(skip_existing=True)

    except (prawcore.exceptions.RequestException, 
            prawcore.exceptions.ResponseException, 
            prawcore.exceptions.PrawcoreException) as f:
        
        print(f"Errors raised: {f}")

    count = 0
    for comment in comment_streams:
        if count >= limit_of_comments:
            break 

        individual_comment = (
            f"REDDITOR: {comment.author}\n"
            f"POST TITLE: {comment.submission.title}\n"
            f"COMMENT: {comment.body}\n"
            "------"
        )

        formatted_lines.append(individual_comment)
        count += 1 

    return formatted_lines

def fetching_comments_by_type(comment_type, permalink,
                              comment_limit, keyword=None, 
                              output_file=""):
    """
    Fetches comments from a specific post by type (top, new, hot, old, controversial).
    """
    formatted_output = []

    if url_validation(permalink):
        permalink_split = permalink.split("/")[6]
    else:
        return "Invalid link"

    # Extract ID from permalink
    try:
        submission = reddit_API.submission(permalink_split)

    except prawcore.exceptions.ResponseException:
        return "Response exception raised"
    
    except AttributeError:
        return "Attribute error occured."
    
    
    # Set comment sort type
    if comment_type in ["top", "hot", "new", "old", "controversial"]:
        submission.comment_sort = comment_type
    else:
    # Set comment type default as top
        submission.comment_sort = "top"

    submission.comments.replace_more(limit=0)

    count = 0
    try:
        for comment in submission.comments.list():
                # Skip AutoModerator
            if comment.author and comment.author.name.lower() == "automoderator":
                continue  

            elif keyword is not None and keyword.lower() not in comment.body.lower():
                continue 

            if count >= comment_limit:
                break 

            ind_comment = (
                f"REDDITOR: {comment.author}\n"
                f"POST TITLE: {comment.submission.title}\n"
                f"COMMENT: {comment.body}\n"
                "------\n"
            )
            formatted_output.append(ind_comment)
            count += 1 

        if output_file and output_file.endswith(".csv"):

            with open(output_file, mode="w") as file:
                writer = csv.writer(file)
                writer.writerow(formatted_output)
        else:
            return "File Should have a csv extension"
        

    except (prawcore.exceptions.ResponseException, 
            prawcore.exceptions.RequestException, 
            FileNotFoundError, PermissionError, IsADirectoryError) as e:
        print(f"Error while fetching comments {e}")
        return [] 

    return formatted_output

def scraping_post_submissions(subreddit, post_type, 
                              limit=10, min_score=None,
                              keyword=None, graph=None):
    
    titles = []
    scores = []

    scraped_post = [] 
    try:    
        subreddit_obj = reddit_API.subreddit(subreddit)

        type_mapping = {
            "hot": subreddit_obj.hot,
            "controversial": subreddit_obj.controversial, 
            "new": subreddit_obj.new,
            "top": subreddit_obj.top,
        }

        if post_type in type_mapping:

            posts = type_mapping.get(post_type, subreddit_obj.top)(limit=limit) 

        else:
            return "Invalid post type"

        for post in posts:
            if min_score is not None and post.score <= min_score:
                continue 
            elif keyword and keyword.lower() not in post.title.lower():
                continue 
            elif post.author and post.author.name.lower() == "automoderator":
                continue 
                 
            post_specifics = (
                f"----------\n"
                f"POST TITLE: {post.title}\n"
                f"----------\n"
                f"POST SCORE: {post.score}\n"
                f"----------\n"
                f"URL: {post.url}\n"
                f"___________________________________________________________\n"
            )
            scraped_post.append(post_specifics)
            titles.append(post.title[:50])
            scores.append(post.score)

        if graph:
            plt.figure(figsize=(20,9))
            plt.barh(titles, scores)
            plt.xlabel('Score')
            plt.ylabel('Title')
            plt.title(f"Top {len(scores)} from r/{subreddit} ({post_type})")
            plt.tight_layout()
            plt.savefig("Results.png")
            plt.show()

            

    except (prawcore.exceptions.ResponseException, prawcore.exceptions.RequestException) as f:
        print(f"Response exception raised {f}")
        return []
    return scraped_post 


if __name__ == "__main__":

    try:
        parser = argparse.ArgumentParser(description="A Reddit scraping tool.")
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
    except (argparse.ArgumentError, argparse.ArgumentError):
        print("Argument error raised.")
        

    
    posts_parser = subparsers.add_parser('posts', help='Scrape post submissions from a subreddit.')
    posts_parser.add_argument('--subreddit', required=True, help='The name of the subreddit to scrape from.')
    posts_parser.add_argument('--type', default='top', help='The type of posts to scrape [hot, controversial, new, top]. Default is "top".')
    posts_parser.add_argument('--limit', type=int, default=10, help='The number of posts to scrape. Default is 10.')
    posts_parser.add_argument('--min_score', type=int, help='The minimum score a post must have to be included.')
    posts_parser.add_argument('--keyword', help='A keyword to filter posts by, based on the title.')
    posts_parser.add_argument('--graph', action="store_true", help="A graph for scores and titles will be presented to the user and given as Results.png")

    
    comments_parser = subparsers.add_parser('comments', help='Fetch comments from a specific post.')
    comments_parser.add_argument('--permalink', required=True, help='The full permalink URL of the Reddit post.')
    comments_parser.add_argument('--type', default='top', help='The type of comments to fetch (top, new, hot, old, controversial). Default is "top".')
    comments_parser.add_argument('--limit', type=int, default=15, help='The number of comments to fetch. Default is 15.')
    comments_parser.add_argument('--keyword', help='A keyword to filter comments by, based on their body content.')
    comments_parser.add_argument('--output_file', help='The name of the CSV file to save the comments to. Must end with .csv')

    args = parser.parse_args()

    if args.command == 'posts':
        scraped_posts = scraping_post_submissions(
            
            subreddit=args.subreddit,
            post_type=args.type,
            limit=args.limit,
            min_score=args.min_score,
            keyword=args.keyword,
            graph=args.graph,
        )
        for post in scraped_posts:
            print(post)

    elif args.command == 'comments':
        comments = fetching_comments_by_type(
            comment_type=args.type,
            permalink=args.permalink,
            comment_limit=args.limit,
            keyword=args.keyword,
            output_file=args.output_file
        )
        if isinstance(comments, str):
            print(f"Error: {comments}")
        else:
            for comment in comments:
                print(comment)
    else:
        parser.print_help()

# Example command: python3 reddit_scraper.py posts --subreddit AskReddit --type top --limit 15