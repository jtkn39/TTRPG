import numpy as np
import pandas as pd
import streamlit as st


def convert_rarity_to_probability(df, weight_dict):
    probs = np.zeros(len(df))
    for i, rarity in enumerate(df['Rarity']):
        probs[i] = weight_dict[rarity]
    probs /= probs.sum()
    df['Probability'] = probs
    
    
def draw_sample(df, nmax=1, bias=8):
    col0 = df.columns[0]
    probs = np.ones(nmax) / (bias**np.arange(nmax))
    probs /= probs.sum()
    num_choices = 1+np.random.choice(nmax, p=probs)
    choices = np.random.choice(df[col0], p=df['Probability'], size=num_choices, replace=False)
    return choices


def format_results(gender, ancestry, profession):
    gstr = gender[0].title()
    if len(ancestry)==1:
        astr = ancestry[0].title()
    else:
        astr = 'half %s - half %s'%(ancestry[0].title(), ancestry[1].title())
    if len(profession)==1:
        pstr = profession[0].title()
    else:
        pstr = profession[0].title() + ' (former %s)'%profession[1].title()
    rstr = 'A %s %s %s'%(gstr, astr, pstr)
    return rstr


st.title('Welcome to the character generator')


df_prof = pd.read_csv('./Data/professions.csv')
df_ancestry = pd.read_csv('./Data/ancestries.csv')
df_gender = pd.read_csv('./Data/genders.csv')

wd = {'none': 0,
      'common': 20,
      'uncommon': 10,
      'rare': 3,
      'very rare': 1}

for df in [df_ancestry, df_prof, df_gender]:
    convert_rarity_to_probability(df, wd)
    
num_char = st.slider('How many characters would you like to generate?', 1, 20, 3)
if st.button('Generate!'):
    for _ in range(num_char):
        gender = draw_sample(df_gender, nmax=1)
        ancestry = draw_sample(df_ancestry, nmax=2, bias=8)
        profession = draw_sample(df_prof, nmax=2, bias=4)
        character = format_results(gender, ancestry, profession)
        st.write(character)