#!/usr/bin/env python
# coding: utf-8

# # Read in the data

# In[1]:


import pandas as pd
import numpy
import re

data_files = [
    "ap_2010.csv",
    "class_size.csv",
    "demographics.csv",
    "graduation.csv",
    "hs_directory.csv",
    "sat_results.csv"
]

data = {}

for f in data_files:
    d = pd.read_csv("schools/{0}".format(f))
    data[f.replace(".csv", "")] = d


# # Read in the surveys

# In[2]:


all_survey = pd.read_csv("schools/survey_all.txt", delimiter="\t", encoding='windows-1252')
d75_survey = pd.read_csv("schools/survey_d75.txt", delimiter="\t", encoding='windows-1252')
survey = pd.concat([all_survey, d75_survey], axis=0)

survey["DBN"] = survey["dbn"]

survey_fields = [
    "DBN", 
    "rr_s", 
    "rr_t", 
    "rr_p", 
    "N_s", 
    "N_t", 
    "N_p", 
    "saf_p_11", 
    "com_p_11", 
    "eng_p_11", 
    "aca_p_11", 
    "saf_t_11", 
    "com_t_11", 
    "eng_t_11", 
    "aca_t_11", 
    "saf_s_11", 
    "com_s_11", 
    "eng_s_11", 
    "aca_s_11", 
    "saf_tot_11", 
    "com_tot_11", 
    "eng_tot_11", 
    "aca_tot_11",
]
survey = survey.loc[:,survey_fields]
data["survey"] = survey


# # Add DBN columns

# In[3]:


data["hs_directory"]["DBN"] = data["hs_directory"]["dbn"]

def pad_csd(num):
    string_representation = str(num)
    if len(string_representation) > 1:
        return string_representation
    else:
        return "0" + string_representation
    
data["class_size"]["padded_csd"] = data["class_size"]["CSD"].apply(pad_csd)
data["class_size"]["DBN"] = data["class_size"]["padded_csd"] + data["class_size"]["SCHOOL CODE"]


# # Convert columns to numeric

# In[4]:


cols = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
for c in cols:
    data["sat_results"][c] = pd.to_numeric(data["sat_results"][c], errors="coerce")

data['sat_results']['sat_score'] = data['sat_results'][cols[0]] + data['sat_results'][cols[1]] + data['sat_results'][cols[2]]

def find_lat(loc):
    coords = re.findall("\(.+, .+\)", loc)
    lat = coords[0].split(",")[0].replace("(", "")
    return lat

def find_lon(loc):
    coords = re.findall("\(.+, .+\)", loc)
    lon = coords[0].split(",")[1].replace(")", "").strip()
    return lon

data["hs_directory"]["lat"] = data["hs_directory"]["Location 1"].apply(find_lat)
data["hs_directory"]["lon"] = data["hs_directory"]["Location 1"].apply(find_lon)

data["hs_directory"]["lat"] = pd.to_numeric(data["hs_directory"]["lat"], errors="coerce")
data["hs_directory"]["lon"] = pd.to_numeric(data["hs_directory"]["lon"], errors="coerce")


# # Condense datasets

# In[5]:


class_size = data["class_size"]
class_size = class_size[class_size["GRADE "] == "09-12"]
class_size = class_size[class_size["PROGRAM TYPE"] == "GEN ED"]

class_size = class_size.groupby("DBN").agg(numpy.mean)
class_size.reset_index(inplace=True)
data["class_size"] = class_size

data["demographics"] = data["demographics"][data["demographics"]["schoolyear"] == 20112012]

data["graduation"] = data["graduation"][data["graduation"]["Cohort"] == "2006"]
data["graduation"] = data["graduation"][data["graduation"]["Demographic"] == "Total Cohort"]


# # Convert AP scores to numeric

# In[6]:


cols = ['AP Test Takers ', 'Total Exams Taken', 'Number of Exams with scores 3 4 or 5']

for col in cols:
    data["ap_2010"][col] = pd.to_numeric(data["ap_2010"][col], errors="coerce")


# # Combine the datasets

# In[7]:


combined = data["sat_results"]

combined = combined.merge(data["ap_2010"], on="DBN", how="left")
combined = combined.merge(data["graduation"], on="DBN", how="left")

to_merge = ["class_size", "demographics", "survey", "hs_directory"]

for m in to_merge:
    combined = combined.merge(data[m], on="DBN", how="inner")

combined = combined.copy().fillna(combined.mean())
combined = combined.fillna(0)


# # Add a school district column for mapping

# In[8]:


def get_first_two_chars(dbn):
    return dbn[0:2]

combined["school_dist"] = combined["DBN"].apply(get_first_two_chars)


# # Find correlations

# In[9]:


correlations = combined.corr()
correlations = correlations["sat_score"]



# # Plotting survey correlations

# In[10]:


# Remove DBN since it's a unique identifier, not a useful numerical value for correlation.
survey_fields.remove("DBN")


# In[11]:


import matplotlib.pyplot as plt 


# In[15]:


print(survey_fields)


# In[ ]:


#combined[]


# In[12]:

# for a in survey_fields:
#     plt.scatter(y=combined['sat_score'],x=combined[a])
#     plt.title(a)
#     plt.show()

# In[ ]:

# High student response rate for schools with good scores
# teacher is across the board
# parents across the board even more whether school does good or bad they voice their opinions

#  aca. expectations from teachers a bit indicative

# saf. from students rather indicative, and aca. expectations


# In[ ]:
#correlations on safety scores from students & teachers
# combined.plot.scatter(x='saf_s_11',y='sat_score')
# plt.show()

# combined.plot.scatter(x='saf_t_11',y='sat_score')
# plt.show()

# In[ ]:

import re
safety = []
for a in combined.columns:
    b = re.search(r'saf',a)
    if b:
        b
        a

        safety.append(a)

    else :
        pass

# In[ ]:
# safety scores by borough
boro_pv = combined.pivot_table(index='boro')
print(boro_pv[safety].sort_values('saf_s_11'))
print(boro_pv['sat_score'].sort_values())
#inconclusive

# In[ ]:
# plotting out the correlations between demographics and sat

cols_demo= []
for a in combined.columns :
    if re.search(r'per\b',a):
        cols_demo.append(a)
    else :
        pass
cols_demo.append('sat_score')

print(combined[cols_demo].corr())
# for a in cols_demo :
#     combined.plot.scatter(x=a,y='sat_score')


# With a low percentage of asians there is a heavy cluster of low sat
    #scores, might want to check out some schools under 1300
# regarding females and males if anythig males do worse
# the white plot is similar to the asians,under 1300 too
# higher hispanic per have strong negative correlation
# black per similar to the hispanics

# In[ ]:
# checking out some schools with his_per > 95%
combined[combined['hispanic_per'] > 95.0]
his_sch = combined[combined['hispanic_per'] > 95.0][['SCHOOL NAME','sat_score','ell_percent','frl_percent','boro']].sort_values('sat_score')
# seem to be in Manhattan and the Bronx

# In[ ]:
lh_hs = combined[(combined['hispanic_per'] < 10.0) & (combined['sat_score'] > 1800)]
lh_hs[['boro','eng_s_11','aca_s_11','sat_score']].sort_values(['aca_s_11','eng_s_11'])
# regarding boro these seem to be more scattered

# In[ ]:
# high female per & high sat score
hf_hs = combined[(combined['female_per'] > 60.0) & (combined['sat_score'] > 1700)]
hf_hs[['SCHOOL NAME','female_per','sat_score']]
# low absent rate, high number of extracurricular activites,more sports
    # many asians/whites, admissions screened

# In[ ]:
# will check out how ap test takers would influence sat_score
    # this variable will be used by percentage to reduce and correlation
        #correlation carry over form total_enrollment

combined['ap_per'] = combined['AP Test Takers '] / combined['total_enrollment']
# print(combined['ap_per'])
#will plot a scatter plot
combined.plot.scatter('ap_per', 'sat_score')
#there is a cluster towards bottom left which is composed of low sat score
    # low ap percents


# en continuación podría continuar el analisís por asignando una puntuacion
    # a cada escuela que se crea a traves sus características inherentes
    #estas características coincidirían con las indican que un escuela
    #es buena y tal vez se puede introducir otras que resten de esta
    # puntuacion
# despues se haría un pivot table para averugar cuales son los boros
    # con las mejores escuelas y a la vez agregar otra table
    # con informacion sobre cual boro es mas económico entre otras cosas
#
