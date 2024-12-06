# Function to generate answers using GPT-4
def answer_question_with_gpt4(email_text, question, client):    
    # Construct a prompt combining the question and email content
    prompt_text = f"{question}: {email_text}"
    messages = [
        # System instruction to define the assistant's role
        {"role": "assistant", "content": "You are an assistant who answers questions based on the email content provided."},
        # User's input question and email context
        {"role": "user", "content": prompt_text}
    ]
    # Call the OpenAI API to generate a response
    response = client.chat.completions.create(
        model="gpt-4",  # Specify the model to use
        messages=messages,  # Provide the prompt messages
        temperature=0.2,  # Low temperature for deterministic answers
        max_tokens=200,  # Limit the length of the response
        frequency_penalty=0.0  # No penalty for frequent terms
    )
    # Extract the response text from the API response
    response_text = response.choices[0].message.content
    # Retrieve the number of tokens used in the interaction
    tokens_used = response.usage.total_tokens
    
    # Return the generated response and token usage as a dictionary
    return {"response": response_text, "tokens_used": tokens_used}

