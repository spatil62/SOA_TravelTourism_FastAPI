from django.shortcuts import render
import requests

def get_media(request):
    token = 'IGQWRPbk8xcEJUVVlnS2dpb0RBdGlCRDV0UjBYbkdacVJXLWRlUWhxYWxIWUxFZAHNreHJMeVQ4dUlxaW9JOE53Ry1MLWhHbG1yLXFWNU80UnRHdWJVZAG5nMlJ1dnFXVTdmNWVvWGNEVURFZA2sySUNvWmVEQ1dxTFUZD'
    url = 'https://graph.instagram.com/me/media?fields=id,caption&access_token='+token
    
    response = requests.get(url,)
    data = response.json()
    all_media = data['data']
    output = []

    target = 6
    collected_media = 0

    for media in all_media:
        media_id = media["id"]
        media_uri = 'https://graph.instagram.com/'+media_id+'?fields=id,media_type,media_url,username,timestamp&access_token='+token
        response = requests.get(media_uri,)
        media_data = response.json()

        if media_data["media_type"] != "IMAGE":
            continue
        
        collected_media +=1 

        if collected_media > 6:
            print(f"Fetched {target} images.")
            break

        media["url"] = media_data["media_url"]
        media["type"] = media_data["media_type"]
        media["username"] = media_data["username"]
        media["timestamp"] = media_data["timestamp"]
        output.append(media)

    
    return render (request, 'instagram.html', { "all_media": output} )