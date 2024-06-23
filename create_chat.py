# chatmaker.py is a python script that generates a chatbot from
# asking interactive questioons. The result is a .json file that
# contains the conversation configuration.

import json
import requests


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


if __name__ == '__main__':
    try:
        print("Creating chat configuration...")

        chat_dict = {}

        chat_dict['title'] = input('What is the title of the chat? > ')

        # get the list of models from the server
        model_name_List = _get_List_of_downloaded_models()
        if model_name_List:
            print("\nList of models available:")
            for i, model_name in enumerate(model_name_List):
                print("  {}. {}".format(i + 1, model_name))
            print("\n")
        else:
            print("No models available. Please download a model first.")
            print("Exiting chat creation.")
            exit()

        # user to enter model's numeric number from the menu
        print("Please select the model for AI One and AI Two from the list above.")
        print("Enter the number corresponding to the model you want to use.")
        print("Press enter to use the default model (LLama3).")
        model_number = input("\nModel Number:")
        if model_number:
            model_number = int(model_number)
            if model_number < 1 or model_number > len(model_name_List):
                print("Invalid model number. Exiting chat creation.")
                exit()
            chat_dict['ai_one_model'] = model_name_List[model_number - 1]
            chat_dict['ai_two_model'] = model_name_List[model_number - 1]
        else:
            if not chat_dict['ai_one_model']:
                chat_dict['ai_one_model'] = 'llama3'
            if not chat_dict['ai_two_model']:
                chat_dict['ai_two_model'] = 'llama3'

        print('You chose model {} for both AI One and AI Two.'.format(chat_dict['ai_one_model']))

        chat_dict['number_of_chat_turns'] = input('\nHow many chat turns are there (press enter for 20 turns)? > ')
        if not chat_dict['number_of_chat_turns']:
            chat_dict['number_of_chat_turns'] = 20
        else:
            chat_dict['number_of_chat_turns'] = int(chat_dict['number_of_chat_turns'])

        ai_one_system_role = {
            "role": "system",
            "display_name": input('\nWhat is the name of your character played by AI One? > '),
        }
        ai_one_system_role['content'] = input(
            'Describe the character of {} (e.g. You are an expert in ... / You are a character from ... ) > '.format(
                ai_one_system_role['display_name']))
        ai_one_system_role['content'] = 'Your name is {}. {}.'.format(ai_one_system_role['display_name'],
                                                                      ai_one_system_role['content'])
        chat_dict['ai_one_conversation_history'] = [ai_one_system_role]
        if input(
                'Do you want this character to be brief in their responses? (y if brief / n or press enter for model default) > ').lower() == 'y':
            ai_one_system_role['content'] += '. Be brief in your responses.'

        ai_two_system_role = {
            "role": "system",
            "display_name": input('\nWhat is the name of your character played by AI Two? > '),
        }
        ai_two_system_role['content'] = input(
            'Describe the character of {} (e.g. You want to know about ... / You are afraid of ...  ) > '.format(
                ai_two_system_role['display_name']))
        ai_two_system_role['content'] = 'Your name is {}. {}.'.format(ai_two_system_role['display_name'],
                                                                      ai_two_system_role['content'])
        chat_dict['ai_two_conversation_history'] = [ai_two_system_role]
        if input(
                'Do you want this character to be brief in their responses? (y if brief / n or press enter for model default) > ').lower() == 'y':
            ai_two_system_role['content'] += '. Be brief in your responses.'

        chat_dict['ai_one_conversation_history'].append({
            "role": "user",
            "content": input(
                '\nWhat is the first thing that {} will say to {} to get the conversation going? > '.format(
                    ai_two_system_role['display_name'], ai_one_system_role['display_name']))
        })

        chat_dict['curved_ball_chat_messages'] = []
        while input("\nDo you want to add {} curved ball chat message? (y/n) > ".format(
                'another' if len(chat_dict['curved_ball_chat_messages']) > 0 else 'a')).lower() == 'y':
            chat_dict['curved_ball_chat_messages'].append({
                "chat_turn_number": int(input(
                    'At what turn number shall we throw the curved ball (odd number to be spoken by {}, even from {})? > '.format(
                        ai_one_system_role['display_name'], ai_two_system_role['display_name']))),
                "chat_message": input('What is the chat message of the curved ball chat message? > '),
            })

        chat_dict['ai_final_chat_message'] = {}
        chat_dict['ai_final_chat_message']["1"] = {
            "role": "user",
            "content": input('\nWhat is the final "goodbye" chat message that will be spoken by {}? > '.format(
                ai_one_system_role['display_name']))
        }
        chat_dict['ai_final_chat_message']["2"] = {
            "role": "user",
            "content": input('\nWhat is the final "goodbye" chat message that will be spoken by {}? > '.format(
                ai_two_system_role['display_name']))
        }

        temperature = input(
            '\nHow would you like the AI model to behave?\nChoose a number between 0 to 9 where\n  0 (coherent and rational)\n  5 (balanced and reasonable)\n  9 (creative and diverse)\n  (press enter for 5)? > ')
        if not temperature:
            chat_dict['temperature'] = 0.5
        else:
            chat_dict['temperature'] = float(int(temperature) / 10)

        # remove any empty curved ball chat messages
        chat_dict['curved_ball_chat_messages'] = [msg for msg in chat_dict['curved_ball_chat_messages'] if
                                                  (msg['chat_message'] and int(msg['chat_turn_number']) > 0)]

        # print the chat configuration in a human-friendly format:
        print("\nChat Configuration:")
        print("Title: {}".format(chat_dict['title']))
        print("\nAI One Model: {}".format(chat_dict['ai_one_model']))
        print("AI Two Model: {}".format(chat_dict['ai_two_model']))
        print("\nNumber of Chat Turns: {}".format(chat_dict['number_of_chat_turns']))
        print("\nTemperature Factor: {}".format(chat_dict['temperature'] * 10))
        print("\nAI One:")
        print("  Display Name: {}".format(chat_dict['ai_one_conversation_history'][0]['display_name']))
        print("  Character: {}".format(chat_dict['ai_one_conversation_history'][0]['content']))
        print("\nAI Two:")
        print("  Character: {}".format(chat_dict['ai_two_conversation_history'][0]['content']))
        print("  Display Name: {}".format(chat_dict['ai_two_conversation_history'][0]['display_name']))
        print("  First Message from {}: {}".format(chat_dict['ai_two_conversation_history'][0]['display_name'],
                                                   chat_dict['ai_one_conversation_history'][1]['content']))
        print("\nCurved Ball Chat Messages:")
        for msg in chat_dict['curved_ball_chat_messages']:
            print("  Turn Number: {}".format(msg['chat_turn_number']))
            print("  Message spoken by {}: {}".format(
                chat_dict['ai_two_conversation_history'][0]['display_name'] if msg['chat_turn_number'] % 2 == 0 else
                chat_dict['ai_one_conversation_history'][0]['display_name'],
                msg['chat_message']
            ))
        print("\nFinal Goodbye Message from {}: {}:".format(chat_dict['ai_one_conversation_history'][0]['display_name'],
                                                            chat_dict['ai_final_chat_message']["1"]['content']))
        print("\nFinal Goodbye Message from {}: {}:".format(chat_dict['ai_two_conversation_history'][0]['display_name'],
                                                            chat_dict['ai_final_chat_message']["2"]['content']))

        # save the chat dictionary to a json file
        if input("\nDo you want to save the chat configuration? (y/n) > ").lower() == 'y':
            file_name = 'chat_configs/{}'.format(
                input("Enter the file name to save the chat configuration: ") + ".json")
            if not file_name.endswith('.json.json'):
                file_name = file_name.replace('.json.json', '.json')
            with open(file_name, "w") as f:
                json.dump(chat_dict, f, indent=4)

            print("Chat configuration saved to{}".format(file_name))
            print(
                "You can edit the file directly to change the chat configuration and add more curved ball chat messages!")
            # TODO: Add an option to run the chat! The commented-out lines are not working properly yet.
            # if input('Would you like run the chat now? (y/n) > ').lower() == 'y':
            #    import chat
            #    chat.run_chat_interaction(chat_dict)
        else:
            print("Chat configuration not saved.")

    except KeyboardInterrupt as ki:
        print("You interrupted the chat creation! Chat configuration not saved.")

    except Exception as e:
        print("An error occurred during chat creation! Chat configuration not saved.")
        print(e.with_traceback(None))
