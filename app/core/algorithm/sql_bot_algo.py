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




def __query_ai_n_get_related_schema(prompt,related_schema, language,model="gpt-4o", max_tokens=500):
   system_message = """
            You are a helpful assistant for a {industry}. The database schema details are stored in Chroma DB. Given the user input: {context}, 

            Given is Schema Description stored in chroma db with their id {schema}. Kindly filter related schema 

            **Respond ONLY with a JSON array format with same schema description format provided **.
            .
        """
        # Query the model
   response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message.format(context=prompt,industry=industry,schema=related_schema)}
                # {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
   print(response.choices[0].message.content)
   return response.choices[0].message.content;


def __query_with_custom_data_only_nostream(prompt, language,model="gpt-4o", max_tokens=500):
   system_message = """
           You are a helpful assistant for a {industry}. The database schema details are stored in Chroma DB. Given the user input: {context}, first rephrase it while preserving all details. 

            Then, segregate it into minimal, well-defined contexts for SQL query generation, ensuring no information is lost. If multiple IDs are mentioned for a **common entity type** (e.g., Production Bags, Sales Orders), group them into a **single context** instead of separating them.  

            Each context should be distinct and structured for separate SQL queries.  

            **Respond ONLY with a JSON array format with only object node name context ** and nothing else with the structured context array so i can direcrtly loop over it.
            .
        """
        # Query the model
   response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message.format(context=prompt,industry=industry)}
                # {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
   print(response.choices[0].message.content)
   return response.choices[0].message.content;


def __query_chroma_n_get_title(collection_name,context):
    returned_collection_results = vector_db.query_chroma_n_club_document_title(collection_name,context);
    documents_with_ids = []
    for item in returned_collection_results:
        print(item)
        start_marker = "START_MARKER"
        end_marker = "END_MARKER"
        pattern = r'{}(.*?){}'.format(re.escape(start_marker), re.escape(end_marker))
        # Search for the note text following 'SQL_schema_note'
        match = re.search(pattern, str(item["document"]), re.DOTALL)
        # Print the extracted note (if found)
        if match:
            print("Extracted Note:", match.group(1))
            document_data = {
            "id": item["id"],  # Safely extract the id (None if not found)
            "schema_description": match.group(1)  # Document text/content
            }
            documents_with_ids.append(document_data)
    print(documents_with_ids)            
    return documents_with_ids;
            

def __get_related_schema(schema_description,model="gpt-4o", max_tokens=500):
    system_message = """
           You are a helpful assistant for a {industry}. 
            .
        """
        # Query the model
    response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message.format(context=prompt,industry=industry)}
                # {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
    print(response.choices[0].message.content)
    return response.choices[0].message.content;
   # print(item["context"])


def __get_chroma_actual_scehma(collection_name,returned_related_schema):
    id_list = [item["id"] for item in returned_related_schema]
    related_schema =  vector_db.query_chroma(collection_name,id_list)
    return related_schema
       
 
def __generate_db_query(context, prompt, language,model="gpt-4o", max_tokens=500):
   system_message = """You are a helpful assistant that specializes in MSSQL 2019 query generation of an Accounting Database based on schema that is provided
        If the schema is insufficient, you may ask for more details, but **DO NOT** provide explanations, descriptions, or introductory text.
        .Use the following schema to generate:\n\n{context} .
        Generate SQL step by step procedure , i will fire response directly in MS SQL . Do not provide me any query explanation or description.I will just copy paste it in my SSMS
        """
        # Query the model
   response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message.format(context=context,language=language)},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
   return response.choices[0].message.content;    


def __recheck_sql_query(prompt,query,error,context,model="gpt-4o", max_tokens=500):
   system_message = """
        
        """
        # Query the model
   response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message.format(context=context)},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
   return response.choices[0].message.content;    

def query_with_custom_data_only(prompt, language,model="gpt-4o", max_tokens=500):
   json_payload = {}
   json_payload["user_code"] = "1"
   json_payload["chat_history_code"] = "1"
   json_payload["question_asked"] =prompt
   
   

   # yield "data: Checking Context ...</br> \n\n"
   multiple_context = __query_with_custom_data_only_nostream(prompt,language=language)
   # yield "data: Cleaning Context in readable format...</br> \n\n"
   cleaned_string = multiple_context.replace("json", "").replace("`", "")
   json_payload["related_context_retrieved"] = cleaned_string
   data = json.loads(cleaned_string)

   for item in data:
      # yield "data: Finding related schema.. </br> \n\n"
      schema_description = __query_chroma_n_get_title("mt_collection",context=item["context"])
      # yield "data: Get Actual Schema ...</br> \n\n"
      returned_related_schema = __query_ai_n_get_related_schema(item["context"],str(schema_description),language=language)
      # yield "data: Cleaning Schema ...</br> \n\n"
      returned_related_schema = returned_related_schema.replace("json", "").replace("`", "")
      returned_related_schema = json.loads(returned_related_schema)
      sql_schema = __get_chroma_actual_scehma("mt_collection",returned_related_schema)
      context = "\n".join(sql_schema)
      # yield "data: Generating Query...</br> \n\n"
      query = __generate_db_query(context,prompt=prompt,language=language)
      # yield "data: Executing Query...</br> \n\n"
      context =  sql_db.execute_query(query)
      # yield "data: Generating Answers...</br> </br>  \n\n"
      print(query,"query")
      json_payload["sql_query"] = query
      system_message = """You are a helpful assistant that specializes in Accounting Application for Jewellery Industry for context that is provided
        Answer the query using only the context provided below in a friendly and concise bulleted manner.
        You can rephrase the answer using proper explanation and Grammer.Also you can provide some analytics based on context.
        If there isn't enough information below, say Sorry, I can only answer questions based on my custom knowledge base.
        .Use the following context:\n\n{context} .
        Format responses in HTML with appropriate tags like <ul>, <li>, <strong>,<br>, <div>.
        You can use Angular Material classes also.Font should be small.
        Respond in {language} language only
        """
        
      sql_db.insert_chat_log(json_payload);
        # Query the model
      response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message.format(context=context,language=language)},
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
          yield 'data: ' + content.replace("`", "").replace('html',"")  + "\n\n"# Yield the valid content
   return "";
        


async def __sql_bot_algo_main(prompt,language):


    multiple_context = __query_with_custom_data_only_nostream(prompt,language=language)
    cleaned_string = multiple_context.replace("json", "").replace("`", "")
    data = json.loads(cleaned_string)
    # Loop through the context
    for item in data:
      schema_description = __query_chroma_n_get_title("mt_collection",context=item["context"])
      returned_related_schema = __query_ai_n_get_related_schema(item["context"],str(schema_description),language=language)
      returned_related_schema = returned_related_schema.replace("json", "").replace("`", "")
      returned_related_schema = json.loads(returned_related_schema)
      sql_schema = __get_chroma_actual_scehma("mt_collection",returned_related_schema)
      context = "\n".join(sql_schema)
      query = __generate_db_query(context,prompt=prompt,language=language)
      formatted_results_sql =  sql_db.execute_query(query)
      print(query,"query")
      return formatted_results_sql
      
    return "";
   