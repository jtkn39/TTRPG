import numpy as np
import os
import pandas as pd
import streamlit as st

# TODO - born locally or in a distant land?

st.set_page_config(initial_sidebar_state='collapsed')


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
    idx_choices = np.random.choice(len(df), p=df['Probability'],
                                   size=num_choices, replace=False)
    choice_probs = df['Probability'][idx_choices].values
    choices = df[col0][idx_choices].values
    choices = choices[np.argsort(choice_probs)]
    if len(choices)==1:
        return choices[0]
    else:
        return list(choices)
    

def create_character(df_list, optional_weights):
    character_dict = {}
    for df in df_list:
        attribute = df.columns[0]
        if attribute=='Profession':
            sample = draw_sample(df, nmax=2, bias=4)
            if type(sample)==list:
                sample = '%s (formerly %s)'%(sample[0], sample[1])
        elif attribute in optional_weights.keys():
            prob = optional_weights[attribute]
            if np.random.random_sample()<prob:
                sample = draw_sample(df)
            else:
                sample = None
        else:
            sample = draw_sample(df)
            if attribute=='Ancestry' and sample=='genasi':
                sample = 'genasi (%s)'%draw_sample(df, nmax=1)
        character_dict[attribute] = sample
    return character_dict

                
def generate_character_description(character_dict):
    age = character_dict['Age']
    gender = character_dict['Gender']
    ancestry = character_dict['Ancestry']
    profession = character_dict['Profession']
    alignment = character_dict['Alignment']
    drawback = character_dict['Drawback']
    disorder = character_dict['Disorder']
    companion = character_dict['Companion']
    retainer = character_dict['Retainer']
    output = 'They are a %s %s %s %s.  \n' %(age, gender, ancestry, profession)
    if age.startswith('a') or age.startswith('e'):
        output = output.replace(' a ', ' an ')
    virtue, vice = alignment.split('-')
    output += 'They try to embody %s, but can lapse into %s.  \n'%(virtue, vice)
    for extra in [drawback, disorder]:
        if extra is not None:
            output += 'They %s. '%extra
    for extra in [companion, retainer]:
        if extra is not None:
            output += 'They have a %s companion.'%extra.lower()
            break
    return output.strip()

def add_character_to_roster(character_dict):
    df_character = pd.DataFrame(character_dict, index=[0])
    st.session_state.character_list.append(character_dict)
    st.session_state.df = pd.concat([st.session_state.df, df_character], ignore_index=True)
    

def delete_roster():
    columns = ['Name', 'Age', 'Gender', 'Ancestry',
               'Profession', 'Alignment', 'Drawback',
               'Disorder', 'Companion', 'Retainer']
    st.session_state.character_list = []
    st.session_state.df = pd.DataFrame(columns=columns)

    
    
st.title('Welcome to Jack\'s character generator')

df_weirdness = pd.read_csv('weirdness_weights.csv')
rarities = df_weirdness[df_weirdness.columns[0]]
weirdness_prompt = 'Select the level of weirdness for your characters'
weirdness = st.radio(weirdness_prompt, df_weirdness.columns[1:], horizontal=True, index=1)
weights = df_weirdness[weirdness]
weight_dict = dict(zip(rarities, weights))

d0 = './Data'
flist_csv = [os.path.join(d0, f) for f in os.listdir(d0) if f.endswith('.csv')]
df_list = []
for f_csv in flist_csv:
    df = pd.read_csv(f_csv)
    convert_rarity_to_probability(df, weight_dict)
    df_list.append(df)
    
with st.sidebar:
    st.write('Adjust weightings for different rarities')
    p_db = st.slider('Probability of generating a drawback', 0.0, 1.0, 1.0)
    p_dis = st.slider('Probability of generating a disorder', 0.0, 1.0, 0.3)
    p_comp = st.slider('Probability of generating a companion', 0.0, 1.0, 0.1)
    p_ret = st.slider('Probability of generating a retainer', 0.0, 1.0, 0.0)
    option_weights = {'Drawback': p_db,
                      'Disorder': p_dis,
                      'Companion': p_comp,
                      'Retainer': p_ret}

    
num_prompt = 'How many characters would you like to generate?'

columns = ['Name', 'Age', 'Gender', 'Ancestry',
           'Profession', 'Alignment', 'Drawback',
           'Disorder', 'Companion', 'Retainer']
if 'character_list' not in st.session_state:
    st.session_state.character_list = []
    st.session_state.df = pd.DataFrame(columns=columns)
    


with st.form('Generate characters'):
        
    character_dict = create_character(df_list, option_weights)
    description = generate_character_description(character_dict)
    st.write(description)
    add_character = st.checkbox('Add character to roster')
    submitted = st.form_submit_button('Next!')
    if submitted:
        if add_character:
            add_character_to_roster(character_dict)


with st.expander('Show roster'):
    csv = convert_df(st.session_state.df)
    dl_prompt = 'Press to download characters in csv format'
    st.download_button(dl_prompt, csv, 'my_random_characters.csv', 'text/csv')
    for character_dict in st.session_state.character_list:
        description = generate_character_description(character_dict)
        st.write(description)
    st.button('Delete roster?', on_click=delete_roster)
    
    
    