# Get two AI Assistants Chatting with Ollama API 

## This Python script enables automated chat between two different AI assistants using the Ollama API. 
In this project you can set up a conversation between two AI assistants using a JSON-formatted chat configuration file.
The script chat.py start a conversation between the two AI assistants and save the conversation history to a file.

Expect to witness hilarious, insightful, and sometimes bizarre conversations between the AI assistants!

Examples outputs are provided for the following scenarios:
* Lady and Tramp from 'Lady and the Tramp' - one refined and the other a rough diamond - [Example chat output](lady_and_the_tramp.md)
* Fonz from 'Happy Days' and Yoda from 'Star Wars' [Example chat output](fonz_meets_yoda.md)
* Noughts and Crosses players in a game of Tic-Tac-Toe [Example chat output](tic_tac_toe.md)
* Two AIs work together to create a new spoken language [Example chat output](two_AIs_create_a_new_spoken_language.md)

There are more scenarios for you to try in the chat_configs folder as I think of the them!

## Installation
First you need to install Ollama and then download the two AI models you want to use. See: https://ollama.com/

To run the script, you need to have Python 3 installed on your system. You also need to install the requests library, which you can do using pip:

```bash
pip install requests
```

## Usage
Run the script 
```bash
python chat.py chat_configs/<json-chat-config-file-name>
```
where <json-chat-config-file-name> is the name of the json-formatted chat configuration file you want to use.
using Python 3. The script will start a loop where each AI assistant takes a turn to respond in the conversation. The conversation keeps repeating until a chat count is reached.


## Saved Conversations
As the script runs, it saves the conversation history  These lists can be used to analyse the conversation 
flow and responses of the AI assistants.

## Get Started!
To get started, use the config file 'fonz_meets_yoda.json' which uses the llama3 model for both AI assistants.
```bash
python chat.py chat_configs/fonz_meets_yoda
```

... or use the config file 'tic_tac_toe.json' to get the two AI assistants to play Tic-Tac-Toe (noughts and crosses).
```bash
python chat.py chat_configs/tic_tac_toe
```
## Add to the fun!
It's the config file that provides the context for the conversation. You can create your own config file by following the format of the existing ones.
```
{
    "title": "Two characters from two different on-screen universes chat to one another",
    "ai_one_model": "llama3",
    "ai_two_model": "llama3",
    "number_of_chat_turns": 20,
    "ai_one_conversation_history": [
        {
            "role": "system",
            "content": "You are the Fonz from Happy Days but be brief in your answers",
            "display_name": "Fonz"
        },
        {
            "role": "user",
            "content": "Hello, I understand Fonz you are. A question, I have for you. Answer, can you?"
        }
    ],
    "ai_two_conversation_history": [
        {
            "role": "system",
            "content": "You are a Yoda from Star Wars. Be brief with your answers, you must.",
            "display_name": "Yoda"
        }
    ],
    "curved_ball_chat_messages": [
        {
            "chat_turn_number": 7,
            "chat_message": "I suddenly feel hungry for a cheeseburger. Do you like cheeseburgers?"
        },
        {
            "chat_turn_number": 14,
            "chat_message": "Well now I want to talk petunias. What do you think about that?"
        }
    ],
    "ai_final_chat_message": {
        "role": "user",
        "content": "Apologies but got to go now. Bye!"
    }
}
```

The properties in the config file are as follows:
* ai_one_model: The model to use for the first AI assistant.
* ai_two_model: The model to use for the second AI assistant.
* number_of_chat_turns: The number of chat turns to run before the conversation ends.
* ai_one_conversation_history: The conversation history for the first AI assistant.
* ai_two_conversation_history: The conversation history for the second AI assistant.
* curved_ball_chat_messages: A list of messages to throw into the conversation at specific turns.
* ai_final_chat_message: The final message to end the conversation.
* ai_one_conversation_history and ai_two_conversation_history are lists of dictionaries with the following properties:
    * role: The role of the speaker (either "system", "user", and "assistant").
    * content: The message content.
    * display_name: The display name of the speaker.
* curved_ball_chat_messages is a list of dictionaries with the following properties:
  * chat_turn_number: The turn number at which to throw the curved ball message.
  * chat_message: The message content.


Now you can adjust the "system" prompt for each AI to change its character. In the example I have The Fonz from Happy Days talking to Yoda from Star Wars! 
The list 'ai_one_conversation_history' also needs a single 'user' prompt to start the conversation.

Feel free to add more conversation history to these lists to see how the AI assistants respond to different contexts as they start up.
They will assume they have had this initial conversation already and will continue from where they think they have left off.

Importantly, if you add "assistant" chat turn to the conversation history, the AI will assume that it spoke those words. if you have a "user" chat turn then
the AI will assume that the words came from the other AI.

'Curved balls' provide a useful diversion to the chat if you find it gets a bit repetitive. Insert curved ball chats into the conversation history 
using list 'curved_ball_chat_messages'. The AI will respond to this as if it is a continuation of the conversation.
If you choose an odd number, the chat will appear to have been said by AI One, and if you choose an even number, it will appear to have been said by AI Two.
I find this useful if 'The Fonz' and 'Yoda' conclude their chat early and start repetitively saying goodbye to each other!
The term “Curved Ball” typically refers to a type of pitch in baseball where the ball is thrown with a spin, known for its deceiving motion.
Imagine what it might do to the AI conversation! But if you don't want to use any curved balls, just set curved_ball_chat_messages to an empty list [].

If you provide a large value to variable 'number_of_chat_turns', you can see how the conversation evolves over time. But bear in mind that there is a prompt size limit
that varies by model - I'm working on how to detect this and start removing earlier chat rounds when sending the history to the model. But this is how
Large Language Models work - you have to give them the entire conversation history to get the next response.


Conversation saved to ai_chat_20240620_184019_between_Noughts Player_and_Crosses Player.json

```
