import openai
from flask import app
import json

from src.constants import CHAT_CACHE
from src.core.cache_manager import get_cache
from src.logging.logging_helper import log_info
delimiter = "####"

base_context2 = [{'role': 'system', 'content': """
You are a chat assistant which will help customer to buy cloths and apparels on an ecommerce website. \
You first greet the customer, and will ask what would they like to search for. \
User is expected to input his search query in raw text. \
Format your response as a JSON object with keys "tags", "filters" and "responseForUser". \
You will extract the values for "tags" and "filters" from the user input, set value to empty string if user input is unrelated to cloths and apparels. \
Supported filters are Size, Color, Brand, Price, Material, User Rating and Discount. \
The value for "responseForUser" will be "Please wait till we fetch products based on your filters" only if user input is relevant, \
otherwise the value for "responseForUser" should be your normal reply asking how can you help the user. \
"""}]

# Good and Decent.
base_context_3 = [{'role': 'system', 'content': f"""
You will be provided with a customer query. \
The customer service query will be delimited with {delimiter} characters.
Output a python object which has following format: 
    'tags': <a list of tags associated with apparels and clothing extracted from customer service query> 
AND 
    'filters': <a list of filter object associated with apparels and clothing extracted from customer service query> 
AND 
    'responseForUser': <a response you want to give for customer query.> 

Customer query must contain apparels and clothing related questions.
Allowed filters are Size, Color, Brand, Price, Material, User Rating and Discount. 
If no tags and filters found, output empty list for tags and filters \
and ask user to make an appropriate query related to  clothing and apparels.
Once tags and filters are finalised by user, please response user with message like \
'Please wait while we fetch products for you based on filters and tags.'
"""}]

# Worked
base_context_4 = [{'role': 'system', 'content': f"""
You will be provided with a customer query. \
The customer service query will be delimited with {delimiter} characters.
Output a python object which has three fields in following format: 
    'tags': <a list of tags associated with apparels and clothing extracted from customer service query> 
AND 
    'filters': <a list of filter object just associated with apparels and clothing extracted from customer service query. \
    e.g. "filters"=[{{"size":"XL"}}, {{"color":"blue"}}, {{"brand": "Nike"}}] > 
AND 
    'responseForUser': <a response you want to give for customer query> 
.
Customer query must contain apparels and clothing related questions.
Allowed filters are Size, Color, Brand, Price, Material, User Rating and Discount. 
If customer query doesn't contains some filters from the allowed list mentioned above, \
ask the customer if they want to apply the remaining filters one by one.
If no tags and filters found, output empty list for tags and filters \
and ask customer to make an appropriate query related to clothing and apparels.
Only output the python object, with nothing else.
"""}]

# Allowed filters are:
# Size
# Color
# Brand
# Price
# Material
# User Rating
# Discount

# Kind of worked.
base_context_5 = [{'role': 'system', 'content': f"""
You will be provided with a customer query. \
The customer service query will be delimited with {delimiter} characters.
Output a python object which has three fields in following format: 
    'tags': <a list of tags associated with apparels and clothing extracted from customer service query> 
AND 
    'filters': <a list of filter object just associated with apparels and clothing extracted from customer service query. \
    the filter object has key 'type' and value will be a list. \
    e.g. "filters"=[{{"size":["XL","L"]}}, {{"color":["blue","green"]}}, {{"brand": ["Nike"]}}, {{"price":"1000-5000"}}]> \
    Allowed filters types are size, color, brand, price, material, user_rating and discount. 
AND 
    'responseForUser': <a response you want to give for customer query> 
.
Customer query must contain apparels and clothing related questions.
If customer query doesn't contains all the filters from the allowed filters list mentioned above, \
ask the customer if they want to apply the remaining filters one by one.
If no tags and filters found, output empty list for tags and filters \
and ask customer to make an appropriate query related to clothing and apparels.
Only output the python object, with nothing else.
"""}]

# best so far.
base_context6 = [{'role': 'system', 'content': f"""
Follow these steps to answer the customer queries in form of python object who details are given below.
The customer service query will be delimited with {delimiter} characters.

Step 1:{delimiter} First decide if user is querying about a products from category cloths or apparels.

Step 2:{delimiter} If user is querying about products from category cloths or apparels, \
extract the various filter types from customer query. e.g. "size", "color", "brand", "price" etc. \
Allowed filters types are size, color, brand, price, material, user_rating and discount. \
Otherwise, your response to customer query would be asking them to query products related to cloths and apparels only in friendly tone.

Step3:{delimiter} If the extracted filter types does not cover all allowed filter type list given above, \
your response to customer query would be asking them if they want to apply other remaining filter types as well in friendly tone. \
Otherwise your response to customer query would be asking them to wait while the system fetch the \
desired products according to the filters provided by them.

Step 4:{delimiter} If user is querying about products from category cloths or apparels, \
extract the list of tags from the customer query. Otherwise give the empty list.

Output a python object which has three fields in following format: 
    'tags': <a list of tags associated with apparels and clothing extracted from customer service query in Step 4> 
AND 
    'filters': <a list of filter object just associated with apparels and clothing extracted from customer service query in Step 2. \
    the filter object has filter type as key and the filter values will be a list. \
    e.g. "filters"=[{{"size":["XL","L"]}}, {{"color":["blue","green"]}}, {{"brand": ["Nike"]}}, {{"price":"1000-5000"}}]> \
AND 
    'responseForUser': <your response to the customer query based on steps above> 
.
Only output the python object, with nothing else.
"""}]

category = "cloths and apparels for children"
base_context7 = [{'role': 'system', 'content': f"""
Follow these steps to answer the customer queries in form of python object who details are given below.
The customer service query will be delimited with {delimiter} characters.

Step 1:{delimiter} First decide if user is querying about a products from category "{category}". Convert the customer query into short query related to a product for search engine.

Step 2:{delimiter} If user is querying about products from category "{category}", \
extract the various filter types from customer query. e.g. "size", "color", "price" and "discount" \
Allowed filters types are size, color, price and discount. \
Otherwise, your response to customer query would be asking them to query products related to {category} only in friendly tone.

Step3:{delimiter} If the extracted filter types does not cover all allowed filter type list given above, \
your response to customer query would be asking them if they want to apply other remaining filter types as well in friendly tone. \
Otherwise your response to customer query would be asking them to wait while the system fetch the \
desired products according to the filters provided by them.

Step 4:{delimiter} If user is querying about products from category "{category}", \
extract the list of tags from the customer query. Otherwise give the empty list.

Output a python object which has three fields in following format: 
    "query": <Short search query related to product extracted in Step 1. Exclude the filter related details extracted in Step 2. Leave it empty if it is not related to {category}>
AND
    "tags": <a list of tags associated with {category} extracted from customer service query in Step 4> 
AND 
    "filters": <a list of filter object just associated with {category} extracted from customer service query in Step 2. \
    the filter object has filter type as key and the filter values will be a list. \
    e.g. "filters"=[{{"size":["XL","L"]}}, {{"color":["blue","green"]}}, {{"price":"1000-5000"}}]> \
AND 
    "responseForUser": <your response to the customer query based on steps above> 
.
Only output the python object, with nothing else.
"""}]

base_context = [{'role': 'system', 'content': f"""
Follow these steps to answer the customer queries in form of python object who details are given below.
The customer service query will be delimited with {delimiter} characters.

Step 1:{delimiter} First decide if user is querying about a products from category "{category}". Convert the customer query into keywords string for searching.

Step 2:{delimiter} If user is querying about products from category "{category}", \
extract the various filter types from customer query. e.g. "size", "color", "price" and "discount" \
Allowed filters types are size, color, price and discount. \
Otherwise, your response to customer query would be asking them to query products related to {category} only in friendly tone.

Step3:{delimiter} If the extracted filter types does not cover all allowed filter type list given above, \
your response to customer query would be asking them if they want to apply other remaining filter types as well in friendly tone. \
Otherwise your response to customer query would be asking them to wait while the system fetch the \
desired products according to the filters provided by them.

Step 4:{delimiter} If user is querying about products from category "{category}", \
extract the list of tags from the customer query. Otherwise give the empty list.

Output a python object which has three fields in following format: 
    "keywords": <keywords string extracted in Step 1 for searching. Return empty string if it is not related to {category}>
AND
    "tags": <a list of tags associated with {category} extracted from customer service query in Step 4> 
AND 
    "filters": <a list of filter object just associated with {category} extracted from customer service query in Step 2. \
    the filter object has filter type as key and the filter values will be a list. \
    e.g. "filters"=[{{"size":["XL","L"]}}, {{"color":["blue","green"]}}, {{"price":"1000-5000"}}]> \
AND 
    "responseForUser": <your response to the customer query based on steps above> 
.
Only output the python object, with nothing else.
"""}]

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
    )
    #     print(str(response.choices[0].message))
    return response.choices[0].message["content"]


def get_chat_message_reply(chat_id, prompt):
    chat_cache = get_cache(CHAT_CACHE)
    context = chat_cache.get(chat_id)
    context = base_context if context is None else context
    context.append({'role': 'user', 'content': f"{delimiter}{prompt}{delimiter}"})

    full_response = get_completion_from_messages(context)
    context.append({'role': 'assistant', 'content': f"{full_response}"})

    chat_cache.set(chat_id, context)

    log_info(str(full_response))
    # json_response = json.loads(full_response)
    # response = json_response["responseForUser"]
    return full_response


