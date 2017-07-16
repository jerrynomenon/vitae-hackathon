import requests
import json

oauth_token = 'token b83d1811bd8774ef0af33f7672fabcfe3c37ab0c'


def getinfo():
    url = 'https://api.github.com/graphql'
    headers = {
        'Authorization': oauth_token
    }
    query = '''
    query {
        viewer {
            repositories(first:100){
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    name
                    languages(first:100)
                    {
                        nodes{
                        name
                        }
                    }
                }
            }
        }
    }
    '''
    r = requests.post(url, headers=headers, json={"query": query})
    print(r)
    print(r.text)


getinfo()
