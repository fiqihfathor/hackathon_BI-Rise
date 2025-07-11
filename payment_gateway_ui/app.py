import streamlit as st
from single_payment import single_payment_page
from bulk_transaction_generator import bulk_transaction_page

pages = [
    single_payment_page,
    bulk_transaction_page
]

nav = st.navigation(pages)
nav.run()
