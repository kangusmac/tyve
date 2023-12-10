import streamlit as st
import pandas as pd
import mymapslinks as mml
from pathlib import Path
from enum import Enum

class Mypage(Enum):
    TABLE = 0
    INFO = 1


@classmethod
def formatted_options(cls):
    return [x.name for x in cls]

# --------------------------------------------- Config ---------------------------------------------

csv_folder = Path.cwd() / 'clean'
csv_files = [file for file in csv_folder.glob('*.csv')]
csv_dict =  {file.stem: file for file in csv_files}

csv_info = Path.cwd() / 'data'
csv_info_files = [file for file in csv_info.glob('*.csv')]
csv_info_dict =  {file.stem: file for file in csv_info_files}

# --------------------------------------------- Config ---------------------------------------------
menu_key = 'menu'
page = 'page'
session_state = st.session_state
sidebar = st.sidebar

def update_session_state(key, value):
    session_state[key] = value

def update_menu_key():
    session_state[menu_key] = session_state['dag_uge']


def init_session_state():
    if page not in session_state:
        update_session_state(menu_key, list(csv_dict.keys())[0])
        update_session_state(page, Mypage.TABLE.value)

def load_data():
    st.write('### Tømninger:')
    st.write(f'## {format_menu_key()}')
    file = csv_dict[session_state[menu_key]]
    df = pd.read_csv(file)
    return df


def load_info():
    st.write('### Info:')
    st.write(f'## {format_menu_key()}')
    file = csv_info_dict[session_state[menu_key]]

    df = pd.read_csv(file)
    antal = df['antal'].sum()
    st.write(f'Antal: {antal}')
    
    st.text('Fordelt på følgende størrelser(antal i liter):')
    antal_type = df.groupby(['type'])[["antal"]].sum(numeric_only=True).reset_index()
    antal_type = antal_type.set_index('type')
    st.write(antal_type.T)
    st.divider()

    st.write('Sække til ombytning:')
    antal_sække = df[df['sæk']].groupby(['gade', 'nr','postnr', 'beholder', 'fremsætter'])['antal'].sum(numeric_only=True).reset_index()
    st.write(f' Antal: {df["sæk"].sum()}')
    if st.checkbox('Vis Adresser', key='1', value=True):
            
        st.dataframe(antal_sække, use_container_width=True, hide_index=True)
        st.divider()

    st.write('Fremsætninger:')
    antal_fremsætninger = df[df['fremsætter']].groupby(['gade', 'nr','postnr', 'beholder'])['antal'].sum(numeric_only=True).reset_index()
    st.write(f' Antal: {df["fremsætter"].sum()}')
    if st.checkbox('Vis Adresser', key='2', value=False):
        st.dataframe(antal_fremsætninger, use_container_width=True, hide_index=True)
        

def format_menu_key():
    return ' '.join(session_state[menu_key].split("_")).title()

def setup_sidebar():
    sidebar.title('Menu')
    menu = sidebar.selectbox(
        "Vælg Dag og Uge",
        key= 'dag_uge',
        options=csv_dict,
        on_change=update_menu_key)
    
    with sidebar.expander('Info', expanded=False):
        st.button('Vis Info', key='info', on_click=update_session_state, args=(page, Mypage.INFO.value))
        st.button('Vis Tømninger', key='table', on_click=update_session_state, args=(page, Mypage.TABLE.value))
        se_kort()
def se_kort():
    link = mml.get_link(session_state[menu_key])
    st.markdown(f'- Se kort over [placering]({link})')


if __name__ == "__main__":

        init_session_state()
        setup_sidebar()

        if session_state[page] == Mypage.TABLE.value:
            st.dataframe(load_data(), use_container_width=True, hide_index=True)
        elif session_state[page] == Mypage.INFO.value:
            #st.dataframe(load_info(), use_container_width=True, hide_index=True)
            load_info()
        else:
            st.write('No Matching Page')


        
                    