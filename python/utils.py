# Built-in imports
import requests
import json
import os
import base64
from dotenv import load_dotenv


load_dotenv()

def getResponse(userQuery: str, characterID: str, sessionID: str, voiceResponse: str):
    '''
    This function makes an API call to the convai servers to get back
    a response from the bot to the given user query.
    Returns:
        text: <response from the bot>
        sessionID: <marks the chat-session the conversation belongs to>  [Refer docs for more details]
        charID: <character id sent in the request body>
        audio: null / "<base64 encoded audio>"
        samplerate: null / "<sample rate of the audio in Hz>"
    '''
    CHARACTER_GET_RESPONSE_URL = os.getenv("CHARACTER_GET_RESPONSE_URL")

    payload={
        'userText': userQuery,
        'charID': characterID,
        'sessionID': sessionID,
        'voiceResponse': voiceResponse
    }

    headers = {
    "CONVAI-API-KEY": os.getenv("CONVAI_API_KEY"),
    }

    response = requests.request("POST", CHARACTER_GET_RESPONSE_URL, headers=headers, data=payload)

    if response.status_code == 200:   # this indicates that the request has been processed succesfully
        data = response.json()  # Read the JSON data from the response

        # Display the reponse of the character to the user
        # character_response = data["text"]
        # print(CHARACTER_NAME+": "+character_response)

        '''
        Remember Points 2 & 3, where we dicussed a lot on "session" and "sessionID", here we are going to
        handle that.
        Since, we have sent "-1" as sessionID for the very first conversation, the system understanda that
        this is the start of a new conversation session. It returns a unique ID to mark this start. We
        have to reuse that to continue conversations by maintaining context of the session.
        If we send an old sessionID, the systems understands that the user is trying to maintain context
        from a particular conversation session and thus returns the same sessionID back as validation.
        
        sessionID = data["sessionID"]
        '''

        '''
        Handling the audio data.
        As you can see, we have passed "True" for "voiceResponse" attribute. Thus we will get back some data
        in the "audio" attribute of the response. The data is encoded in base64 format.
        So the natural course of action should be to decode the data. Then we write that data into an audio file
        to be played later.
        
        if voiceResponse:   # We move on with the next steps only if we are expecting some audio data
            decode_string = base64.b64decode(data["audio"])

            with open('audioResponse.wav','wb') as f:
                f.write(decode_string)
        '''

        return data

    else:   # The status_code for the response is something other than 200.
        print("The conversation request has failed")
        
        data = response.json()  # Read the JSON data from the response
        print("ERROR: ", data["ERROR"])