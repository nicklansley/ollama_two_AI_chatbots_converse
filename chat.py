import datetime

import requests
import json
import sys

# Replace 'your_api_key' with your actual API key for Ollama API
api_url = 'http://localhost:11434/api/chat'

# ensure encoding is utf-8
sys.stdout.reconfigure(encoding='utf-8')


def _chat_to_ai(conversation_history, ai_number):
    response_chat = {
        "role": "assistant",
        "content": "",
        "options": {
            "temperature": 2,
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the chat request with history
    ollama_payload = {
        "model": ai_chat_config['ai_one_model'] if ai_number == 1 else ai_chat_config['ai_two_model'],
        "messages": conversation_history
    }

    try:
        response = requests.post(api_url, data=json.dumps(ollama_payload), headers=headers, stream=True)
        if response.status_code == 200:

            # Handle the stream of responses
            for line in response.iter_lines():
                # Filter out keep-alive new lines
                if line:
                    decoded_line = line.decode('utf-8')
                    chat_response = json.loads(decoded_line)
                    chat_message = chat_response['message']['content']
                    response_chat['content'] += chat_message

                    print(chat_message, end='', flush=True)

                    # Check if the conversation is done
                    if chat_response.get('done', False):
                        print('\n\n')
                        break
        else:
            print('Failed to send chat request.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('Failed to send chat request.')
        print('Error:', e)
        response_chat['content'] = 'Failed to send chat request.'

    return response_chat


# Call this function to save conversation history
def _save_conversation(path, conversation, display_save_message=False):
    if display_save_message:
        print('Conversation saved to {}'.format(path))
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=4)


def _chat_run(conversation_history, ai_number, ai_display_name, ai_other_number, counter, ai_chat):
    print('({} of {}) {}:'.format(counter + 1, ai_chat['number_of_chat_turns'], ai_display_name))
    ai_response = _chat_to_ai(conversation_history[ai_number], ai_number)
    ai_message = ai_response
    conversation_history[ai_number].append(ai_message)
    ai_other_message = ai_message.copy()
    ai_other_message['role'] = 'user'
    conversation_history[ai_other_number].append(ai_other_message)
    for curved_ball in ai_chat['curved_ball_chat_messages']:
        if counter == int(curved_ball['chat_turn_number']) - 1:
            print('(Curved Ball) {}:\n{}\n'.format(ai_display_name, curved_ball['chat_message']))
            curved_ball_chat_insertion = {
                "role": "user",
                "content": curved_ball['chat_message']
            }
            conversation_history[ai_other_number].append(curved_ball_chat_insertion)
            ai_message = curved_ball_chat_insertion.copy()
            ai_message['role'] = 'assistant'
            conversation_history[ai_number].append(ai_message)
    _save_conversation('ai_{}_conversation_history.json'.format(ai_number), conversation_history[ai_number])


def run_chat_interaction(ai_chat):
    save_file_name = 'chat_history/our_chat.json'  # default file name
    try:
        # create_a_conversation_history_file
        save_file_name = 'chat_history/ai_chat_{}_between_{}_and_{}.json'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
                                                                    ai_chat['ai_one_conversation_history'][0][
                                                                        'display_name'],
                                                                    ai_chat['ai_two_conversation_history'][0][
                                                                        'display_name'])
        # Print the AI display names by using a list, so we can easily switch between the two AIs using 1 or 2
        # for AI One or AI Two
        ai_display_name = [None, ai_chat['ai_one_conversation_history'][0]['display_name'],
                           ai_chat['ai_two_conversation_history'][0]['display_name']]

        print("Starting chat between {} and {} in {}...\n".format(ai_display_name[1], ai_display_name[2],
                                                                  ai_chat['title']))
        print(
            'AI One ({}) style is: {}'.format(ai_display_name[1], ai_chat['ai_one_conversation_history'][0]['content']))
        print(
            'AI Two ({}) style is: {}'.format(ai_display_name[2], ai_chat['ai_two_conversation_history'][0]['content']))
        print('-----')
        print('{} started the conversation: {}'.format(ai_chat['ai_two_conversation_history'][0]['display_name'],
                                                       ai_chat['ai_one_conversation_history'][1]['content']))
        print('-----')

        # by storing the conversation history in a list, we can easily switch between the two AIs - 1  or 2 for AI One or AI Two
        conversation_history = [None, ai_chat['ai_one_conversation_history'], ai_chat['ai_two_conversation_history']]
        chatting_to_ai_one = True
        chat_counter = 0

        while chat_counter < int(ai_chat['number_of_chat_turns']):
            ai_number = 1 if chatting_to_ai_one else 2
            ai_other_number = 2 if chatting_to_ai_one else 1

            # Time to say goodbye
            if chat_counter >= int(ai_chat['number_of_chat_turns']) - 2:
                conversation_history[ai_number].append(ai_chat['ai_final_chat_message'][str(ai_other_number)])
                print('(Saying goodbye) {}:\n{}\n'.format(ai_display_name[ai_other_number],
                                                          ai_chat['ai_final_chat_message'][str(ai_other_number)]['content']))

            # Perform a chat
            _chat_run(conversation_history, ai_number, ai_display_name[ai_number], ai_other_number, chat_counter,
                      ai_chat)

            # Swap AIs
            chatting_to_ai_one = not chatting_to_ai_one
            chat_counter += 1

    except KeyboardInterrupt:
        print('Chat ended.')
        # create a file name that includes date and time:

        print('Conversation history saved {}.json.'.format(save_file_name))

    finally:
        _save_conversation(save_file_name, ai_chat, display_save_message=True)


if __name__ == '__main__':
    # define a command line parameter to specify the AI chat file
    if len(sys.argv) > 1:
        ai_chat_file = sys.argv[1] + '' if sys.argv[1].endswith('.json') else sys.argv[1] + '.json'
    else:
        print('Please specify the AI chat file as a command line parameter.')
        sys.exit(1)

    # load the ai_chat.json file to configure the chat
    with open(ai_chat_file) as f:
        ai_chat_config = json.load(f)
    run_chat_interaction(ai_chat_config)
