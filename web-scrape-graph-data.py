#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import requests


# In[ ]:


URL = "https://www.worldometers.info/coronavirus/country/uk/"


# In[ ]:


parsed_html = requests.get(URL)
soup = BeautifulSoup(parsed_html.content, "html.parser")


# In[ ]:


scripts = soup.find_all('script')
script = scripts[21].text


# In[ ]:


import json
dates = script.split("categories: [",1)[1].split("]",1)[0]
dates = "["+dates+"]"
dates = json.loads(dates)


# In[ ]:


data = script.split("data: [",1)[1].split("]",1)[0]
data = "["+data+"]"
data = json.loads(data)


# In[ ]:


import matplotlib.pyplot as plt
plt.bar(dates[1:],data[1:])


# In[ ]:




