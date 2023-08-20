import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(initial_sidebar_state='collapsed')


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')



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
           

def format_results(age, gender, ancestry, profession_list, alignment,
                   drawback, has_drawback, disorder, has_disorder,
                   companion, has_companion, retainer, has_retainer):
    agestr = age.lower()
    gstr = gender.lower()
    astr = ancestry.lower()
    if len(profession_list)==1:
        pstr = profession_list[0].lower()
    else:
        pstr = profession_list[0].lower() + ' (former %s)'%profession_list[1].lower()
    asplit = tuple(alignment.split('-'))
    xstr = 'They exhibit %s, sometimes manifesting as %s.'%asplit
    if has_drawback:
        xstr += ' They %s.'%drawback
    if has_disorder:
        xstr += ' They %s.'%disorder
    if has_companion:
        xstr +=' They have a %s companion.'%companion.lower()
    if has_retainer:
        xstr +=' They have a %s retainer.'%retainer.lower()
    if agestr.startswith('a') or agestr.startswith('e'):
        return 'An %s %s %s %s. %s'%(agestr, gstr, astr, pstr, xstr)
    else:
        return 'A %s %s %s %s. %s'%(agestr, gstr, astr, pstr, xstr)



st.title('Welcome to Jack\'s character generator')


df_prof = pd.read_csv('./Data/professions.csv')
df_ancestry = pd.read_csv('./Data/ancestries.csv')
df_gender = pd.read_csv('./Data/genders.csv')
df_align = pd.read_csv('./Data/alignments.csv')
df_db = pd.read_csv('./Data/drawbacks.csv')
df_dis = pd.read_csv('./Data/disorders.csv')
df_age = pd.read_csv('./Data/ages.csv')
df_companions = pd.read_csv('./Data/companions.csv')
df_retainers = pd.read_csv('./Data/retainers.csv')

wd = {'none': 0,
      'common': 12,
      'uncommon': 4,
      'rare': 2,
      'very rare': 1}
    
with st.sidebar:
    st.write('Adjust weightings for different rarities')
    w_common = st.slider('Common', 1, 100, wd['common'])
    w_uncommon = st.slider('Uncommon', 1, w_common, wd['uncommon'])
    w_rare = st.slider('Rare', 1, w_uncommon, wd['rare'])
    w_vrare = st.slider('Very rare', 1, w_rare, wd['very rare'])
    wd['common'] = w_common
    wd['uncommon'] = w_uncommon
    wd['rare'] = w_rare
    wd['very rare'] = w_vrare
    p_db = st.slider('Probability of having a drawback', 0.0, 1.0, 0.5)
    p_dis = st.slider('Probability of having a disorder', 0.0, 1.0, 0.15)
    p_comp = st.slider('Probability of having a companion', 0.0, 1.0, 0.2)
    p_ret = st.slider('Probability of having a retainer', 0.0, 1.0, 0.1)
    
for df in [df_ancestry, df_prof, df_gender, df_align, df_db, 
           df_dis, df_age, df_companions, df_retainers]:
    convert_rarity_to_probability(df, wd)
    
    
num_char = st.slider('How many characters would you like to generate?', 1, 20, 1)
columns = ['Name', 'Age', 'Gender', 'Ancestry', 'Profession', 'Former Profession',
           'Alignment', 'Drawback', 'Disorder', 'Companion', 'Retainer']
df_out = pd.DataFrame(columns=columns, index=range(num_char))
if st.button('Generate!'):
    for i in range(num_char):
        age = draw_sample(df_age, nmax=1)
        gender = draw_sample(df_gender, nmax=1)
        ancestry = draw_sample(df_ancestry, nmax=1)
        if ancestry=='genasi':
            ancestry = 'genasi (%s)'%draw_sample(df_ancestry, nmax=1)
        profession_list = draw_sample(df_prof, nmax=2, bias=4)
        alignment = draw_sample(df_align, nmax=1)
        drawback = draw_sample(df_db, nmax=1)
        disorder = draw_sample(df_dis, nmax=1)
        companion = draw_sample(df_companions, nmax=1)
        retainer = draw_sample(df_retainers, nmax=1)
        samp1, samp2, samp3, samp4 = np.random.rand(4)
        description = format_results(age, gender, ancestry, profession_list, alignment,
                                     drawback, p_db>samp1, disorder, p_dis>samp2,
                                     companion, p_comp>samp3, retainer, p_ret>samp4)
        st.write(description)
        df_out['Age'][i] = age
        df_out['Gender'][i] = gender
        df_out['Ancestry'][i] = ancestry
        df_out['Profession'][i] = profession_list[0]
        if len(profession_list)>1:
            df_out['Former Profession'][i] = profession_list[1]
        df_out['Alignment'][i] = alignment
        if p_db>samp1:
            df_out['Drawback'][i] = drawback
        if p_dis>samp2:
            df_out['Disorder'][i] = disorder
        if p_comp>samp3:
            df_out['Companion'][i] = companion
        if p_ret>samp4:
            df_out['Retainer'][i] = retainer
            
    csv = convert_df(df_out)

    st.download_button(
       "Press to Download",
       csv,
       "my_random_characters.csv",
       "text/csv",
       key='download-csv'
    )
        