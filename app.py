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
    idx_choices = np.random.choice(len(df), p=df['Probability'], size=num_choices, replace=False)
    choice_probs = df['Probability'][idx_choices]
    choices = df[col0][idx_choices[np.argsort(choice_probs)]].values
    if nmax==1:
        return choices[0]
    else:
        return choices
           

def format_results(gender, ancestry, profession_list, alignment):
    gstr = gender.lower()
    astr = ancestry.lower()
    if len(profession_list)==1:
        pstr = profession_list[0].lower()
    else:
        pstr = profession_list[0].lower() + ' (former %s)'%profession_list[1].lower()
    asplit = tuple(alignment.split('-'))
    xstr = 'They exhibit %s, sometimes manifesting as %s'%asplit
    if gstr.startswith('a'):
        return 'An %s %s %s. %s.'%(gstr, astr, pstr, xstr)
    else:
        return 'A %s %s %s. %s.'%(gstr, astr, pstr, xstr)


st.title('Welcome to Jack\'s character generator')


df_prof = pd.read_csv('./Data/professions.csv')
df_ancestry = pd.read_csv('./Data/ancestries.csv')
df_gender = pd.read_csv('./Data/genders.csv')
df_align = pd.read_csv('./Data/alignments.csv')

wd = {'none': 0,
      'common': 20,
      'uncommon': 10,
      'rare': 3,
      'very rare': 1}
    
with st.sidebar:
    st.write('Adjust weightings for different rarities')
    w_common = st.slider('Common', 1, 100, 20)
    w_uncommon = st.slider('Uncommon', 1, w_common, 10)
    w_rare = st.slider('Rare', 1, w_uncommon, 3)
    w_vrare = st.slider('Very rare', 1, w_rare, 1)
    wd['common'] = w_common
    wd['uncommon'] = w_uncommon
    wd['rare'] = w_rare
    wd['very rare'] = w_vrare
    
for df in [df_ancestry, df_prof, df_gender, df_align]:
    convert_rarity_to_probability(df, wd)
    
    
num_char = st.slider('How many characters would you like to generate?', 1, 8, 3)
if st.button('Generate!'):
    for _ in range(num_char):
        gender = draw_sample(df_gender, nmax=1)
        ancestry = draw_sample(df_ancestry, nmax=1)
        if ancestry=='genasi':
            ancestry = 'genasi (%s)'%draw_sample(df_ancestry, nmax=1)
        profession_list = draw_sample(df_prof, nmax=2, bias=4)
        alignment = draw_sample(df_align, nmax=1)
        character = format_results(gender, ancestry, profession_list, alignment)
        st.write(character)