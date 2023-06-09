from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json 
import numpy as np
from fastapi import FastAPI, Request, Form
import random
import time
time.clock = time.time
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
import openai
import os 


temp='%s%k%-%N%V%b%i%n%T%V%Y%L%a%W%N%T%M%9%I%o%u%x%z%T%3%B%l%b%k%F%J%y%h%0%n%P%X%A%s%J%h%7%8%t%W%h%a%2%f%d%z'
api_key=""
for i in range(1,len(temp),2):
    api_key+=temp[i]
os.environ["OPENAI_API_KEY"] = api_key

openai.api_key = api_key
COMPLETIONS_MODEL = "text-davinci-002"

app = FastAPI()
templates = Jinja2Templates(directory="")
class static:
   user_data=None
   email=None
   step='step1'
   history=[]
   vocabs=[]
   messages=[]
   template2="""
   \n
   history:
   {chat_history}
    user: {question}
    A2Zbot:generate a very short response.
   """
   template="""
    You are A2ZBot  (Artificial Intelligence Bot) to make english warmup conversation based on user interests.
    You are a smart bot to know user information:user name is {},english level is {},interests and goals are  {}.
    You must to Check evrey user reponse and correct user response based on only grammar and spelling.
    Do not generate user response.
    you are a smart bot to Use many Emojis for each response.
    you must response to user shortly.
    do not return a long response. 
    firstly please resonse to user in smart way then tell user about A2ZBot then ask user "how he is doing?" in the same response.
    You must to learn user only one thing in response.
    You must to tell user if his response incorrect based on grammar and spelling.
    do not use media suggestions.
    do not suggest to user any online resources to learn english.
    You must to tell user joke or advice related to user interests if user is not ready or if user in bad mood.
    you are a smart bot to ask user about A2Zbot feedback at the end of conversation.
    don't ask questions back! 
    don't generate chat_history.
    you must to suggest topics related to user interests and goals.
    allow to user to leave if he want and say goodbye and please do not ask him about next session.
    tell user about A2ZBot if he ask some thing like "who are you?","what can you do?","what is your goals?".
    """
   memory=ConversationBufferMemory(memory_key="chat_history")
def warmup(msg):
    prompt_template = PromptTemplate(input_variables=["chat_history","question"], template=static.template+static.template2)
    llm_chain = LLMChain(
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9,
        max_tokens=100, n=1),
        prompt=prompt_template,
        verbose=False,
        memory=static.memory,
   
        )
    result=llm_chain.run(question=msg)
    time.sleep(0.5)
    return result.replace('A2ZBot:','',-1).replace('AI:','',-1).replace('A2Zbot:','',-1)
   
def vocabularies(number,domain):
    text='more than {} "{}" vocabularies without duplicating,please return as following:word,word,'.format(number,domain)
    messages=[]
    system_role={"role": "system", "content": """You are smart bot to return specific vocabularies,please do not say anything to user,assistant reply must be like this :word,word,.."""}
    user_role={"role": "user", "content": "more than 3 Travel vocabularies without duplicating"}

    assistant_role={"role": "assistant", "content": "Adventure,Boarding pass,Explorer,Journey"}

    messages.append(system_role)
    messages.append(user_role)
    messages.append(assistant_role)
    if text:
        messages.append({"role": "user", "content": text})
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages,temperature=0.9
        )
        reply = chat.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return reply

def A2ZBot(prompt):
  bot_response=openai.Completion.create(
        prompt=prompt,
        temperature=0.9,
        max_tokens=700,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model=COMPLETIONS_MODEL
    )["choices"][0]["text"].strip(" \n")
  return bot_response
def check(bot_response,user_response,problem):
  #prompt=""""please return "yes" if user response '{}' that is related to bot response: '{}',user response should be '{}' """.format(user_response.strip(),bot_response.strip(),problem)
  prompt="""check if "{}" in following conversation ? return 'yes' if it is true else return 'no' " .\n Bot: {} \nUser: {}""".format(problem,bot_response.strip(),user_response.strip())
  temp=A2ZBot(prompt)
  if "no".lower() in temp.lower():
    prompt="""give user example  response for this 'Bot:{}'  """.format(bot_response)
    result=A2ZBot(prompt)
    return result
  else:
    return False
def conversation(user_response):
  if user_response.strip()=='':
    return "You did not send anything!!!!"
  if user_response.strip()=='START_STUDY_PLAN':
    return "Your study plan is not avilable for this version!!"
    
  if user_response.strip()=='RESET':
    static.messages=[]
    return "History of Conversation has been deleted"
  if static.step=='step1':
        static.step='step2'
        bot_response= "What is your name?"
        static.history.append(bot_response)
        return bot_response
  if static.step=='step2':
    bot_response=check(static.history[-1],user_response,'user says his name no matter if he write his name in small letters')
    if bot_response:
      return 'This is an example for good response:\n'+bot_response
    else:
      static.history.append(user_response)
      static.step='step3'
      bot_response= "Nice to meet you.\nHow old are you?"
      static.history.append(bot_response)
      return bot_response
  if static.step=='step3':
    bot_response=check(static.history[-1],user_response,'User must to write his age ')
    if bot_response:
      
      return 'This is an example for good response:\n'+bot_response
    else:
      static.history.append(user_response)
      static.step='step4'
      bot_response="""What is your current english level:
       <ul>
       <li>* A1</li>
       <li>* A2</li>
       <li>* B1</li>
       <li>* B2</li>
       <li>* C1</li>
       <li>* C2</li>
       </ul>
       """
      static.history.append(bot_response)
      return bot_response
  if static.step=='step4':
    bot_response=check(static.history[-1],user_response,'User must to write his English Level from Bot options ')
    if bot_response:
      
      return 'This is an example for good response:\n'+bot_response
    else:
      static.history.append(user_response)
      static.step='step5'
      bot_response="""What is your target english level:
       <ul>
       <li>* A1</li>
       <li>* A2</li>
       <li>* B1</li>
       <li>* B2</li>
       <li>* C1</li>
       <li>* C2</li>
       </ul>
      """
      static.history.append(bot_response)
      return bot_response
  if static.step=='step5':
    bot_response=check(static.history[-1],user_response,'User must to write his English Level from Bot options ')
    if bot_response:
      
      return 'This is an example for good response:\n'+bot_response
    else:
      static.history.append(user_response)
      static.step='step6'
      bot_response="""Please choose one or two paths from the following pathes: 
      <ul>
       <li>* Travel</li>
       <li>* Business</li>
       <li>* Fun/communication</li>
       <li>* Education</li>
       <li>* Default,General English</li> 
       </ul>
      """
      static.history.append(bot_response)
      return bot_response
  
  if static.step=='step6':
    bot_response=check(static.history[-1],user_response,'User write his English Path from Bot options')
    if bot_response:
      
      return 'This is an example for good response:\n'+bot_response
    else:
      static.history.append(user_response)
      static.step='step7'
      bot_response="""what are your interests?
      <ul>
         <li> 1. Sport </li> 
        <li>2. Art </li> 
         <li> 3. History </li> 
         <li> 4. Technology </li> 
         <li> 5. Gaming </li> 
         <li> 6. Movies </li> 
         <li> 7. Culture </li> 
         <li> 8. Management </li> 
         <li> 9. Science </li> 
         <li> 10. Adventure </li> 
         <li> 11. Space </li> 
         <li> 12. Cooking </li> 
         <li> 13. Reading </li> 
         <li> 14. Lifestyle </li>
         <li> ... </li> 
       </ul>
      """
      static.history.append(bot_response)
      return bot_response
  if static.step=='step7':
    bot_response=check(static.history[-1],user_response,'User write his interests')
    if bot_response:
      return 'This is an example for good response:\n'+bot_response
    else:
      static.history.append(user_response)
      static.step='step8'
      code_=A2ZBot('Write python code to create dict called "user_details" with following keys "name,age,current_english_level,path,target_english_level,path,interests" and store user data from following history:\n {}'.format(static.history))
      exec('static.'+code_)
      return """Let's start our journey in English.<br><span style="color:green">Type <b>OK</b> to continue..</span>"""
  if static.step=='step8':
    
    temp1=A2ZBot("""return more than 100 {} vocabularies  for {} english level as following:
                word,word,word
                """.format(static.user_details['path'],static.user_details['current_english_level']))
    temp1=vocabularies(100,static.user_details['path'])
    temp2=vocabularies(50,static.user_details['interests'])
    static.vocabs=temp1.split(',')+temp2.split(',')
    with open("user_data.json", "r") as read_file:
      data = json.load(read_file)
    data[static.email]["user_details"]=static.user_details
    data[static.email]["vocabs"]=static.vocabs
    with open("user_data.json", "w") as write_file:
      json.dump(data, write_file)
    static.step='step9'
    return """Thanks for your time, your information has been successfully collected and you can start your journey with A2ZBot.<br><span style="color:green">Type <b>Hello</b> to start warmup conversation</span>"""
  
  if static.step=='step9' and user_response.strip()!='RESET' and user_response.strip()!='START_STUDY_PLAN' :
    with open("user_data.json", "r") as read_file:
      data = json.load(read_file)
    static.user_data=data[static.email]
    static.template=static.template.format(static.user_data['user_details']['name'],static.user_data['user_details']['current_english_level'],static.user_data['user_details']['interests']+' '+static.user_data['user_details']['path'])
    try:
      return warmup(user_response)
    except:
      return """I'm Sory!!, warmup Conversation size exceeds available limits,let's move to your study plan.or type 'RESET' to restart"""  
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/SignUp")
def form_post(request: Request, username: str = Form(...),email: str = Form(...),password: str = Form(...)):
    with open("user_data.json", "r") as read_file:
      data = json.load(read_file)
    data[email]={'username':username,'password':password}
    with open("user_data.json", "w") as write_file:
      json.dump(data, write_file)
    return templates.TemplateResponse("login.html", {"request": request})
@app.post("/Login")
def form_post(request: Request,email: str = Form(...),password: str = Form(...)):
    with open("user_data.json", "r") as read_file:
      data = json.load(read_file)
    try:
       
      static.email=email
      static.user_data=data[email]
      if static.user_data['password']==password:
        if 'user_details' in data[email].keys():
          static.step='step9'

        return templates.TemplateResponse("index.html", {"request": request})
      else:
        return templates.TemplateResponse("login.html", {"request": request})
    except:
      pass
@app.get("/getChatBotResponse")
def get_bot_response(msg: str):
      return str(conversation(msg))
    


if __name__ == "__main__":
    uvicorn.run("chat:app")