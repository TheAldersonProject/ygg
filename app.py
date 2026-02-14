"""Ygg GUI"""

import streamlit as st
from dotenv import load_dotenv

from ygg.app.helper import AppHelper

load_dotenv()

st.title("Ygg")
st.set_page_config(layout="wide", page_icon="🪾")

tab_ygg, tab_catalog = st.tabs(
    [
        "Ygg",
        "Catalog",
    ]
)

with tab_ygg:
    version = AppHelper.ygg_version()

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        st.subheader("Catalog Config")
        repository_config = AppHelper.ygg_config()
        st.dataframe(repository_config.model_dump())

    with col_2:
        st.subheader("Catalog Database Config")
        catalog_config = AppHelper.ygg_quack_config()
        st.dataframe(catalog_config.model_dump())

    with col_3:
        st.subheader("Catalog Object Storage Config")
        object_storage_config = AppHelper.ygg_s3_config()
        st.dataframe(object_storage_config.model_dump())

    with st.expander("Blueprints", expanded=True):
        st.subheader(f"Blueprints Version: {version}")

        with st.expander("ODCS", expanded=False, icon="🗺️"):
            st.code(AppHelper.blueprint_odcs(), language="json", line_numbers=True)

        with st.expander("Config", expanded=False, icon="📍"):
            st.code(AppHelper.blueprint_config(), language="yaml", line_numbers=True)

        with st.expander("Contract", expanded=False, icon="💠"):
            with st.expander("Spec", expanded=False, icon="📝"):
                st.code(AppHelper.contract_blueprint(), language="yaml", line_numbers=True)

        with st.expander("Servers", expanded=False, icon="💠"):
            with st.expander("Spec", expanded=False, icon="📝"):
                st.code(AppHelper.servers_blueprint(), language="yaml", line_numbers=True)

        with st.expander("Schema", expanded=False, icon="💠"):
            with st.expander("Spec", expanded=False, icon="📝"):
                st.code(AppHelper.schema_blueprint(), language="yaml", line_numbers=True)

        with st.expander("Schema Property", expanded=False, icon="💠"):
            with st.expander("Spec", expanded=False, icon="📝"):
                st.code(AppHelper.schema_property_blueprint(), language="yaml", line_numbers=True)

with tab_catalog:
    st.header("Catalog")
