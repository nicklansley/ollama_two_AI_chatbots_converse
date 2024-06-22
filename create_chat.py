# chatmaker.py is a python script that generates a chatbot from
# asking interactive questioons. The result is a .json file that
# contains the conversation configuration.

import json

if __name__ == '__main__':
    try:
        print("Creating chat configuration...")

        chat_dict = {
            "title": input('What is the title of the chat? > '),
            "ai_one_model": input('What is the model for AI one (just press enter for LLama3 default) ? > '),
            "ai_two_model": input('What is the model for AI two (just press enter for LLama3 default) ? > '),
            "number_of_chat_turns": int(input('How many chat turns are there? > ')),
            "ai_one_conversation_history": [
                {
                    "role": "system",
                    "content": input('Describe the character of AI One (e.g. You are an expert at ... ) > '),
                    "display_name": input('What is the display name of your AI One character? > ')
                },
                {
                    "role": "user",
                    "content": input(
                        'What is the first thing that AI Two will say to AI One to get the conversation going? > ')
                }
            ],
            "ai_two_conversation_history": [
                {
                    "role": "system",
                    "content": input('Describe the character of AI Two (e.g. You want to know about ... ) > '),
                    "display_name": input('What is the display name of your AI Two character? > ')
                }
            ],
            "curved_ball_chat_messages": [
                {
                    "chat_turn_number": input(
                        'What is the chat turn number of the first curved ball chat message (0 for no curved ball) ? > '),
                    "chat_message": input(
                        'What is the chat message of the first curved ball chat message (keep empty for no curved ball) ? > ')
                },
                {
                    "chat_turn_number": input(
                        'What is the chat turn number of the second curved ball chat message (0 for no curved ball) ? > '),
                    "chat_message": input(
                        'What is the chat message of the second curved ball chat message (keep empty for no curved ball) ? > ')
                }
            ],
            "ai_final_chat_message": {
                "role": "user",
                "content": input('What is the final "goodbye" chat message? > ')
            }
        }

        # make 'llama3' the default model if no model name is entered by the user
        if not chat_dict['ai_one_model']:
            chat_dict['ai_one_model'] = 'llama3'
        if not chat_dict['ai_two_model']:
            chat_dict['ai_two_model'] = 'llama3'

        # ask if the user would like to add any further curved ball chat messages - loop until the user is done and add to the chat dictionary
        while input("Do you want to add another curved ball chat message? (y/n) > ").lower() == 'y':
            chat_dict['curved_ball_chat_messages'].append({
                "chat_turn_number": input('What is the chat turn number of the curved ball chat message? > '),
                "chat_message": input('What is the chat message of the curved ball chat message? > ')
            })

        # remove any empty curved ball chat messages
        chat_dict['curved_ball_chat_messages'] = [msg for msg in chat_dict['curved_ball_chat_messages'] if
                                                  (msg['chat_message'] and int(msg['chat_turn_number']) > 0)]

        # print the chat configuration in a human-friendly format:
        print("\nChat Configuration:")
        print("Title: {}".format(chat_dict['title']))
        print("AI One Model: {}".format(chat_dict['ai_one_model']))
        print("AI Two Model: {}".format(chat_dict['ai_two_model']))
        print("Number of Chat Turns: {}".format(chat_dict['number_of_chat_turns']))
        print("AI One:")
        print("  Character: {}".format(chat_dict['ai_one_conversation_history'][0]['content']))
        print("  Display Name: {}".format(chat_dict['ai_one_conversation_history'][0]['display_name']))
        print("  First Message from AI Two: {}".format(chat_dict['ai_one_conversation_history'][1]['content']))
        print("AI Two:")
        print("  Character: {}".format(chat_dict['ai_two_conversation_history'][0]['content']))
        print("  Display Name: {}".format(chat_dict['ai_two_conversation_history'][0]['display_name']))
        print("Curved Ball Chat Messages:")
        for msg in chat_dict['curved_ball_chat_messages']:
            print("  Turn Number: {}".format(msg['chat_turn_number']))
            print("  Message: {}".format(msg['chat_message']))
        print("Final Chat Message:")
        print("  {}".format(chat_dict['ai_final_chat_message']['content']))

        # save the chat dictionary to a json file
        if input("Do you want to save the chat configuration? (y/n) > ").lower() == 'y':
            file_name = 'chat_configs/{}'.format(
                input("Enter the file name to save the chat configuration: ") + ".json")
            if not file_name.endswith('.json.json'):
                file_name = file_name.replace('.json.json', '.json')
            with open(file_name, "w") as f:
                json.dump(chat_dict, f, indent=4)

            print("Chat configuration saved to{}".format(file_name))
        else:
            print("Chat configuration not saved.")

    except KeyboardInterrupt as ki:
        print("You interrupted the chat creation! Chat configuration not saved.")

    except Exception as e:
        print("An error occurred during chat creation! Chat configuration not saved.")
        print(e)
