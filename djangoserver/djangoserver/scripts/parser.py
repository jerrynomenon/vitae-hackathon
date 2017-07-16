import httplib2
import json
import math
import re
import urllib
import urllib.request


### CONSTANTS
CK_MULTIPLIER   = 10;
REP_MULTIPLIER  = 4;
LK_MULTIPLIER   = 2;

# Regex filters
subreddit_retriever = re.compile('\/r\/\\S+')
subreddit_retriever_alt = re.compile('\/r\/[a-zA-Z0-9]+')

def get_html(url):
    f = urllib.request.urlopen(url)
    return f.read().decode('utf-8')

def get_subreddits(html):
    return set(list(map(lambda x: x.lower()[3:], subreddit_retriever_alt.findall(html))))

html = get_html("https://www.quora.com/What-subreddits-should-a-software-engineer-follow")
sub_list = get_subreddits(html)

def get_json_response(url):
    resp, content = httplib2.Http().request(url)
    return json.loads(content)

#Reddit API methods
def rapi_comments(username, limit=25, after=""):
    return "https://www.reddit.com/user/" + username + "/comments.json?limit=" + str(limit) + "&before=" + after + "&after=null"

def rapi_submitted(username, limit=25, after=""):
    return "https://www.reddit.com/user/" + username + "/submitted.json?limit=" + str(limit) + "&before=" + after + "&after=null"

def rapi_about(username):
    return "https://www.reddit.com/user/" + username  + "/about.json"

def rapi_hotposts(subreddit):
    return "https://www.reddit.com/r/" + subreddit + "/hot.json"

def rapi_postcomments(post, depth=2):
    url = "https://www.reddit.com/r/" + post["data"]["subreddit"] + "/comments/" + post["data"]["id"] + ".json"
    url += "?depth=" + str(depth)
    return url

def rapi_sub_about(subreddit):
    return "https://www.reddit.com/r/" + subreddit + "/about.json"

### Convenience methods to use with Reddit API

def get_all_comments(username, limit=25, after=""):
    if(limit <= 100): 
        json = get_json_response(rapi_comments(username, limit, after))
        return json["data"]["children"]
    else:
        json = get_json_response(rapi_comments(username, 100, after))
        comments = json["data"]["children"]
        new_after = get_comment(comments, len(comments) - 1)["name"]
        return comments + get_all_comments(username, limit - 100, new_after)

def get_all_posts(username, limit=25, after=""):
    def recurse(limit, after, count):
        print(after)
        if(limit <= 100): 
            json = get_json_response(rapi_submitted(username, limit, after))
            return json["data"]["children"]
        else: 
            json = get_json_response(rapi_submitted(username, 100, after))
            submitted = json["data"]["children"]
            new_after = get_post(submitted, len(submitted) - 1)["name"]
            return submitted + recurse(limit - 100, new_after, count + 1)
    return recurse(limit, after, 1)

#def get_all_posts(username, limit=25):
#    json = get_json_response(rapi_submitted(username, limit))
#    return json["data"]["children"]

# Get overall link karma from user
def get_linkkarma(user_about):
    return user_about["data"]["link_karma"]

# Get overall comment karma from user
def get_commentkarma(user_about):
    return user_about["data"]["comment_karma"]

# Get comment from comment list
def get_comment(comments, index):
    return comments[index]["data"]

# Get a tuple representing (upvotes, downvotes) of a particular comment
def get_comment_updown(comment):
    return (comment["ups"], comment["downs"])

# Get post from list of posts
def get_post(submitted, index):
    return submitted[index]["data"]

# Get a tuple representing (upvotes, downvotes) of a particular post
def get_post_updown(post):
    return (post["ups"], post["downs"])

def get_hot_posts(subreddit):
    posts = get_json_response(rapi_hotposts(subreddit))
    return posts["data"]["children"]

def get_comments_from_post(post, depth=2):
    return get_json_response(rapi_postcomments(post, depth))

def get_subreddit_subscribers(subreddit):
    return get_json_response(rapi_sub_about(subreddit))["data"]["subscribers"]

### Vitae functions
## Item: Either a comment or a post

def vt_relevant_items(items, relevance_set):
    return list(filter(lambda x: x["data"]["subreddit"] in relevance_set, items))

#Get comments from item list
def vt_extract_comments(items):
    return list(filter(lambda x: x["data"]["name"][:2] == "t1", items))

#Get posts from item list
def vt_extract_posts(items):
    return list(filter(lambda x: x["data"]["name"][:2] == "t3", items))

#Get average link karma tuple from list of posts
def vt_avgkarma_post_link(posts):
    totalup = 0
    totaldown = 0
    length = len(posts)
    for post in posts:
        totalup += post["data"]["ups"]
        totaldown += post["data"]["downs"]
    return (totalup/length, totaldown/length)

def vt_avgreplies_post(posts):
    totalreplies = 0
    length = len(posts)
    for post in posts:
        totalreplies += post["data"]["num_comments"]
    return totalreplies/length

def vt_parse_items(items, sub_data, sub_set):
    points = {}
    firstname = items[0]["data"]["name"]
    for item in items:
        if(item["data"]["name"] == firstname): print ("Starting a cycle!")
        sub = item["data"]["subreddit"]
        if(sub + "_postavg" not in sub_data):
            sub_data[sub + "_postavg"] = vt_avgkarma_post_link(get_hot_posts(sub))
            sub_data[sub + "_replyavg"] = vt_avgreplies_post(get_hot_posts(sub))
        if(sub + "_subs" not in sub_data):
            sub_data[sub + "_subs"] = get_subreddit_subscribers(sub)

        if(item["data"]["name"][:2] == "t1"):
            if(sub + "_ck" not in points): points[sub + "_ck"] = 0
            if("posts" not in points): points["posts"] = 0
            if("gold" not in points): points["gold"] = 0
            points[sub + "_ck"] += float(item["data"]["ups"]) / math.sqrt(sub_data[sub + "_subs"])
            points["posts"] += 1
            points["gold"] += item["data"]["gilded"]
        elif(item["data"]["name"][:2] == "t3"):
            if(sub + "_lk" not in points): points[sub + "_lk"] = 0
            if(sub + "_rep" not in points): points[sub + "_rep"] = 0
            points[sub + "_lk"] += float(item["data"]["ups"]) / sub_data[sub + "_postavg"][0]
#            if(item["data"]["num_comments"] > 0): 
#                print (str(item["data"]["num_comments"]) + "/" +  str(sub_data[sub+"_replyavg"]) + " = " + str(float(item["data"]["num_comments"]) / sub_data[sub + "_replyavg"]))
            if(item["data"]["num_comments"] == 48): print("Got a 48")
            points[sub + "_rep"] += float(item["data"]["num_comments"]) / sub_data[sub + "_replyavg"]
#            if(item["data"]["subreddit"] == "archlinux"): 
#                print ("\tArch total rep: " + str(points["archlinux_rep"]))
    
    total_ck = 0
    total_lk = 0
    total_rep = 0
    for sub in sub_set:
        if(sub + "_ck" in points): total_ck += points[sub + "_ck"]
        if(sub + "_lk" in points): total_lk += points[sub + "_lk"]
        if(sub + "_rep" in points): total_rep += points[sub + "_rep"]
    
    points["total_ck"] = CK_MULTIPLIER * total_ck
    points["total_lk"] = LK_MULTIPLIER * total_lk
    points["total_rep"] = REP_MULTIPLIER * total_rep
    if("gold" not in points): points["gold"] = 0
    if("posts" not in points): points["posts"] = 0
    print(str(points))
    return points

def vt_get_score(points):
    return points["total_ck"] + points["total_lk"] + points["total_rep"] + points["gold"] + points["posts"];

#Get average comment karma tuple from comments in post, with given comment depth
def vt_avgkarma_post_comments(post, depth=2):
    def recurse(children, up, down):
        newup = up
        newdown = down
        for c in children:
            print("Recursing... " + c["data"]["id"])
            print("(%d,%d)" % (newup, newdown))
            if(c["kind"] == "more"): continue
            newup += c["data"]["ups"]
            newdown += c["data"]["downs"]
            if(c["data"]["ups"] < 0): print("ERROR\n=========\n" + str(c))
            print("\t(%d,%d)" % (c["data"]["ups"], c["data"]["downs"]))
            if(len(c["data"]["replies"]) == 0 or len(c["data"]["replies"]["data"]["children"]) == 0): continue
            else:
                [u,d] = recurse(c["data"]["replies"]["data"]["children"], newup, newdown)
                newup = u
                newdown = d

        return [newup, newdown]
    [u,d] =  recurse(post[1]["data"]["children"],0,0)
    return (u,d)

def main():
    html = get_html("https://www.quora.com/What-subreddits-should-a-software-engineer-follow")
    sub_list = get_subreddits(html)

    sub_list.add("archlinux")

    sub_data = {}

    comments = get_all_comments("wadawalnut", 100)
    posts = get_all_posts("wadawalnut", 100)

    items = vt_relevant_items(comments + posts, sub_list)
    vt_parse_items(items, sub_data, sub_list)

if __name__ == '__main__':
    main()
