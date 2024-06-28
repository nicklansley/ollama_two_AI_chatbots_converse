import datetime

import requests
import json
import sys

# ensure encoding is utf-8
sys.stdout.reconfigure(encoding='utf-8')

# this list will store the formatted conversation
formatted_conversation_list = []


def _record_conversation(chat_message, suppress_print=False):
    formatted_conversation_list.append(chat_message)
    if not suppress_print:
        print(chat_message)


def _get_List_of_downloaded_models():
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get('http://localhost:11434/api/tags', headers=headers)
        if response.status_code == 200:
            models = response.json()
            # check if models is a dictionary
            if isinstance(models, dict):
                model_name_List = []
                for model in models['models']:
                    model_name_List.append(model['name'])
                return model_name_List
            else:
                print('Failed to get list of models.')
                print('Response:', response.text)
                return []
        else:
            print('Failed to get list of models.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('Failed to get list of models.')
        print('Error:', e)
        return []


def _is_model_available(model_name):
    models = _get_List_of_downloaded_models()
    if model_name in models:
        return True
    return False


def _chat_to_ai(conversation_history, ai_number, temperature=0.5):
    response_chat = {
        "role": "assistant",
        "content": "",
        "options": {
            "temperature": temperature,
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
        response = requests.post('http://localhost:11434/api/chat', data=json.dumps(ollama_payload), headers=headers,
                                 stream=True)
        if response.status_code == 200:

            # Handle the stream of responses
            formatted_chat_text = ''
            for line in response.iter_lines():
                # Filter out keep-alive new lines
                if line:
                    decoded_line = line.decode('utf-8')
                    chat_response = json.loads(decoded_line)
                    chat_message = chat_response['message']['content']
                    response_chat['content'] += chat_message

                    print(chat_message, end='', flush=True)
                    formatted_chat_text += chat_message

                    # Check if the conversation is done
                    if chat_response.get('done', False):
                        # printing is suppressed because the code above has already streamed the chat to the screen
                        _record_conversation('{}\n\n'.format(formatted_chat_text.strip()), suppress_print=True)
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


def _ai_summarise_chat(conversation, temperature=0.5):
    conversation_role = [
        {
            "role": "system",
            "content": "You are an expert at taking chat transcripts and summarizing them concisely.",
            "options": {
                "temperature": temperature,
            }
        },
        {
            "role": "user",
            "content": "Please summarize this conversation: {}".format(conversation),
            "options": {
                "temperature": temperature,
            }
        }
    ]

    headers = {
        'Content-Type': 'application/json'
    }

    # Send the chat request with history
    ollama_payload = {
        "model": ai_chat_config['ai_two_model'],
        "messages": conversation_role
    }

    try:
        response = requests.post('http://localhost:11434/api/chat', data=json.dumps(ollama_payload), headers=headers,
                                 stream=True)
        if response.status_code == 200:

            # Handle the stream of responses
            formatted_chat_text = ''
            for line in response.iter_lines():
                # Filter out keep-alive new lines
                if line:
                    decoded_line = line.decode('utf-8')
                    chat_response = json.loads(decoded_line)
                    chat_message = chat_response['message']['content']

                    print(chat_message, end='', flush=True)
                    formatted_chat_text += chat_message

                    # Check if the conversation is done
                    if chat_response.get('done', False):
                        # printing is suppressed because the code above has already streamed the chat to the screen
                        _record_conversation('\n\nSummary of conversation\n-----------------------\n\n{}\n\n'.format(formatted_chat_text.strip()), suppress_print=True)
                        break
        else:
            print('Failed to send chat request.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)

    except requests.exceptions.RequestException as e:
        print('Failed to send chat request.')
        print('Error:', e)


# Call this function to save conversation history
def _save_conversation_json(path, conversation, display_save_message=False):
    if display_save_message:
        print('Conversation saved to {}'.format(path))
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=4)


def _summarise_conversation(formatted_conversation_list):
    # This function takes the formatted conversation list and returns a summary of the conversation
    conversation = ''
    for line in formatted_conversation_list:
        conversation += line + '\n'

    _ai_summarise_chat(conversation)


def _save_formatted_conversation(path):
    print('Formatted Conversation saved to {}'.format(path))
    with open(path, 'w') as f:
        for line in formatted_conversation_list:
            f.write(line + '\n')
        f.write('\n\n** The End **')


def _chat_run(conversation_history, ai_number, ai_display_name, ai_other_number, counter, ai_chat):
    print('\n\n')
    _record_conversation('({} of {}) {}:'.format(counter + 1, ai_chat['number_of_chat_turns'], ai_display_name))
    ai_response = _chat_to_ai(conversation_history[ai_number], ai_number, ai_chat['temperature'])
    ai_message = ai_response
    conversation_history[ai_number].append(ai_message)
    ai_other_message = ai_message.copy()
    ai_other_message['role'] = 'user'
    conversation_history[ai_other_number].append(ai_other_message)

    for curved_ball in ai_chat['curved_ball_chat_messages']:
        if counter == int(curved_ball['chat_turn_number']) - 1:
            print('\n\n')
            _record_conversation('\n\n(Curved Ball) {}:\n{}\n'.format(ai_display_name, curved_ball['chat_message']))
            # Insert the curved ball chat message into the conversation history by adding it
            # to the end of the last chat message in each AI conversation history list:
            formatted_curved_ball_message = '\n{}'.format(curved_ball['chat_message'])
            conversation_history[ai_number][-1]['content'] += formatted_curved_ball_message
            conversation_history[ai_other_number][-1]['content'] += formatted_curved_ball_message
            break

    _save_conversation_json('ai_{}_conversation_history.json'.format(ai_number), conversation_history[ai_number])


def run_chat_interaction(ai_chat):
    save_file_name = 'chat_history/our_chat.json'  # default file name
    try:
        # Check if the models are available
        if not _is_model_available(ai_chat['ai_one_model']):
            print(
                'AI One model "{}" is not available. Please download the model first or alter the config file to use one of these models:'.format(
                    ai_chat['ai_one_model']))
            for model in _get_List_of_downloaded_models():
                print('   ' + model)
            return
        if not _is_model_available(ai_chat['ai_two_model']):
            print(
                'AI Two model "{}" is not available. Please download the model first or alter the config file to use one of these models:'.format(
                    ai_chat['ai_two_model']))
            for model in _get_List_of_downloaded_models():
                print('   ' + model)
            return

        # create_a_conversation_history_file
        save_file_name = 'chat_history/ai_chat_{}_between_{}_and_{}.json'.format(
            datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
            ai_chat['ai_one_conversation_history'][0][
                'display_name'],
            ai_chat['ai_two_conversation_history'][0][
                'display_name'])
        # Print the AI display names by using a list, so we can easily switch between the two AIs using 1 or 2
        # for AI One or AI Two
        ai_display_name = [None, ai_chat['ai_one_conversation_history'][0]['display_name'],
                           ai_chat['ai_two_conversation_history'][0]['display_name']]

        _record_conversation(
            "Starting chat between {} and {} in '{}'...\n".format(ai_display_name[1], ai_display_name[2],
                                                                  ai_chat['title']))
        _record_conversation(
            'AI One ({}) style is: {}'.format(ai_display_name[1], ai_chat['ai_one_conversation_history'][0]['content']))
        _record_conversation(
            'AI Two ({}) style is: {}'.format(ai_display_name[2], ai_chat['ai_two_conversation_history'][0]['content']))
        _record_conversation('-----')
        _record_conversation(
            '{} started the conversation: {}'.format(ai_chat['ai_two_conversation_history'][0]['display_name'],
                                                     ai_chat['ai_one_conversation_history'][1]['content']))
        _record_conversation('-----')

        print('(First chat output may be delayed while AI model is loaded...)')

        # by storing the conversation history in a list, we can easily switch between the two AIs: 1 or 2 for AI One or AI Two
        conversation_history = [None, ai_chat['ai_one_conversation_history'], ai_chat['ai_two_conversation_history']]
        chatting_to_ai_one = True
        chat_counter = 0

        while chat_counter < int(ai_chat['number_of_chat_turns']):
            ai_number = 1 if chatting_to_ai_one else 2
            ai_other_number = 2 if chatting_to_ai_one else 1

            # Time to say goodbye
            if chat_counter >= int(ai_chat['number_of_chat_turns']) - 2:
                conversation_history[ai_number].append(ai_chat['ai_final_chat_message'][str(ai_other_number)])
                _record_conversation('\n\n(Saying goodbye) {}:\n{}\n'.format(ai_display_name[ai_other_number],
                                                                             ai_chat['ai_final_chat_message'][
                                                                                 str(ai_other_number)]['content']))

            # Perform a chat
            _chat_run(conversation_history, ai_number, ai_display_name[ai_number], ai_other_number, chat_counter,
                      ai_chat)

            # Swap AIs
            chatting_to_ai_one = not chatting_to_ai_one
            chat_counter += 1


        print('\n\b\b---------\nSummarising conversation...')
        _summarise_conversation(formatted_conversation_list)

    except KeyboardInterrupt:
        print('Chat ended.')
        # create a file name that includes date and time:

        print('Conversation history saved {}.json.'.format(save_file_name))

    finally:
        print('\n\n')
        _save_conversation_json(save_file_name, ai_chat, display_save_message=True)
        _save_formatted_conversation(save_file_name.replace('.json', '_formatted.txt'))


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
