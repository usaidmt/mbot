import os
import openai
from dotenv import load_dotenv
import json
from ...db import sql_db
from ...db import vector_db
import re
import time


load_dotenv()


openai.api_key  = os.getenv("API_KEY"); 
industry  = os.getenv("INDUSTRY"); 




def generate_response(context, prompt, language,model="gpt-4o", max_tokens=500):

   system_message = """You are a helpful assistant that specializes in IT Infrastructure Industry and COMnet Solutions Pvt Ltd Company data and context that is provided
        Answer the query using only the context provided below in a friendly and concise bulleted manner.
        You can rephrase the answer using proper explanation and Grammer.
        
        If a prompt is detected as irrelevant to the current context what we provided, but if you find any single words related to prompt. you should answer based on that found words\n\n

        If there isn't enough information below, say Sorry, I can only answer questions based on my custom knowledge base.

        Use the following context:\n\n{context}.
        Format responses in HTML with appropriate tags like <ul>, <li>, <strong>,<br>, <div> .
        Respond in {language} language only
        """;
   system_message = system_message.format(context=context, language=language);
   
   # system_message = os.getenv("SYSTEM_MESSAGE").format(context=context, language=language);
   # system_message = "You are a helpful assistant  data and context that is provided. Answer the query using only the context provided below in a friendly and concise bulleted manner. You can rephrase the answer using proper explanation and Grammer. If there isn't enough information below, say Sorry, I can only answer questions based on my custom knowledge base. Use the following context 3. BILL OF QUANTITIES (BOQ) Item No: 1 | Description: Frature Pandya | Unit:  | Quantity: 1,200 | Unit Rate (USD): 18.00 | Total Amount (USD): 21,600.00 Item No:  | Description: Total Contract Price | Unit:  | Quantity:  | Unit Rate (USD):  | Total Amount (USD): 964,600.00 4. PROJECT DURATION Commencement Date: May 01, 2025 Completion Date: October 30, 2025 Total Duration: 6 months 5. PAYMENT TERMS"

        # Query the model
   response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=True
        ) 
     
   for chunk in response:
      content = chunk.choices[0].delta.content  # Extract content
      if content is not None:  # Validate it's not None
        time.sleep(0.05)
        yield 'data: ' + content  + "\n\n"# Yield the valid content
      
   # return response
    # else:
    #     # If no match is found, return a fallback message
    #     return "I'm sorry, I can only answer questions based on my custom knowledge base." 
