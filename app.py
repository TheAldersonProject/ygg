"""Skadi App."""

import streamlit as st

from ygg.skadi.helper import (
    extract_fundamentals_info_from_sf_web_page,
    extract_sf_web_page,
    get_url_as_markdown,
    inflate_contract_fundamentals,
)
from ygg.utils.files_utils import get_yaml_from_json_content

st.set_page_config(layout="wide")
st.title("Skadi")


if not st.session_state.get("scraped_md", None):
    st.session_state["scraped_md"] = None
    scraped_md = None

if not st.session_state.get("md_sample", None):
    st.session_state["md_sample"] = None
    md_sample = None

if not st.session_state.get("md_sample_summary", None):
    st.session_state["md_sample_summary"] = None
    md_sample_summary = None

with st.container():
    with st.container():
        col_l, col_r = st.columns(2)

        with col_l:
            # if st.session_state.get("textract_response", None):
            contract_fundamentals, schema_ = st.tabs(["Contract", "Schema"])
            with contract_fundamentals:
                contract_url = st.text_area(
                    "URL",
                    value="https://docs.snowflake.com/en/guides-overview-cost",
                )
                if st.button("Extract Contract Info", key="extract_contract_info"):
                    scraped_contract_md = get_url_as_markdown(contract_url)
                    st.session_state["scraped_contract_md"] = scraped_contract_md
                    contract_scrape_response = extract_fundamentals_info_from_sf_web_page(
                        st.session_state.get("scraped_contract_md", "")
                    )
                    st.session_state["contract_textract_response"] = contract_scrape_response
                    # st.session_state["md_sample_summary"] = md_sample_summary
                    # st.session_state["md_sample"] = md_sample
                    # st.session_state["contract_schema_cols"] = contract_schema_cols

                if st.session_state.get("scraped_contract_md", None):
                    with st.expander("Scraped Markdown", expanded=False):
                        st.markdown(st.session_state.get("scraped_contract_md", ""))

                if st.session_state.get("contract_textract_response", None):
                    with st.expander("Structured Output", expanded=False):
                        contract_textract_response = st.session_state.get("contract_textract_response", None)
                        if contract_textract_response:
                            contract_textract_response = contract_textract_response.model_dump_json()
                            st.json(contract_textract_response)

                with st.form("skadi_contract_template"):
                    st.subheader("Contract Fundamentals")

                    contract_textract_response = st.session_state.get("contract_textract_response", None)

                    cl1, cl2 = st.columns(2)
                    with cl1:
                        frm_api_version = st.selectbox("Api Version", options=["v3.1.0"], key="frm_apiVersion")
                    with cl2:
                        frm_kind = st.selectbox("Kind", options=["DataContract"], key="frm_kind")

                    frm_tenant = st.text_input("Tenant", value="", key="frm_tenant")
                    frm_domain = st.text_input("Domain", value="", key="frm_domain")
                    frm_name = st.text_input("Name", value="", key="frm_name")

                    cls, clt = st.columns(2)
                    with cls:
                        frm_status = st.selectbox("Status", options=["draft", "active", "deprecated"], key="frm_status")
                    with clt:
                        frm_tags = st.multiselect(
                            "Tags", options=[], default=[], key="frm_tags", accept_new_options=True
                        )

                    frm_data_product = st.text_input("Data Product", value="", key="frm_data_product")

                    if contract_textract_response:
                        with st.container():
                            with st.expander("Authoritative Definitions", expanded=False):
                                frm_url = st.text_input("URL", value=contract_url, key="frm_auth_def_url")
                                frm_type_ = st.text_input(
                                    "Type", value=contract_textract_response.type_of_document, key="frm_auth_def_type"
                                )
                                frm_description = st.text_area(
                                    "Description",
                                    value=contract_textract_response.document_description,
                                    key="frm_auth_def_description",
                                )

                        with st.container():
                            with st.expander("Add Description", expanded=False):
                                frm_purpose = st.text_area("Purpose", value="", key="frm_purpose")
                                frm_limitations = st.text_area("Limitations", value="", key="frm_limitations")
                                frm_usage = st.text_area("Usage", value="", key="frm_usage")

                    if st.form_submit_button("Add Contract Fundamentals", key="add_contract_fundamentals_form"):
                        frm_id = f"dc-{frm_tenant}-{frm_domain}-{frm_name}"
                        form_map: dict = {
                            "id": frm_id,
                            "apiVersion": frm_api_version,
                            "kind": frm_kind,
                            "tenant": frm_tenant,
                            "domain": frm_domain,
                            "name": frm_name,
                            "status": frm_status,
                            "tags": contract_textract_response.tags,
                            "dataProduct": frm_data_product,
                            "authoritativeDefinitions": [
                                {
                                    "url": contract_url,
                                    "type": contract_textract_response.type_of_document,
                                    "description": contract_textract_response.document_description,
                                    "id": "" if not contract_url else f"{frm_id}-authoritative-definition",
                                }
                            ],
                            "description": {
                                "purpose": contract_textract_response.purpose,
                                "limitations": contract_textract_response.limitations,
                                "usage": contract_textract_response.usage,
                                "id": "" if not contract_textract_response.usage else f"{frm_id}-description",
                            },
                        }
                        skadi_body = inflate_contract_fundamentals(form_map)
                        st.session_state["skadi_contract_body"] = skadi_body

            with schema_:
                st.subheader("Schema")
                url = st.text_area(
                    "URL",
                    value="https://docs.snowflake.com/en/sql-reference/organization-usage/rate_sheet_daily",
                )
                if st.button("Extract Schema"):
                    scraped_md = get_url_as_markdown(url)
                    st.session_state["scraped_md"] = scraped_md
                    response, contract_schema, md_sample, md_sample_summary, contract_schema_cols = extract_sf_web_page(
                        st.session_state.get("scraped_md", "")
                    )
                    st.session_state["textract_response"] = response
                    st.session_state["md_sample_summary"] = md_sample_summary
                    st.session_state["md_sample"] = md_sample
                    st.session_state["contract_schema_cols"] = contract_schema_cols

                with st.container():
                    if st.session_state.get("textract_response", None):
                        textract_, markdown_, sf_scrape_ = st.tabs(["Textract", "Markdown", "Sample Data"])
                        with textract_:
                            st.subheader("Textract")
                            response_scp = st.session_state.get("textract_response", None)

                            if response_scp:
                                with st.expander("Textract", expanded=False):
                                    st.json(response_scp.model_dump())
                                    st.json(contract_schema)

                        with markdown_:
                            st.subheader("Scraped Markdown")
                            with st.expander("Markdown", expanded=False):
                                md = st.session_state.get("scraped_md", "")
                                st.markdown(md)

                        with sf_scrape_:
                            st.subheader("Data Sample")
                            if st.session_state.get("md_sample_summary", None):
                                with st.expander("Data Sample Summary", expanded=False):
                                    md_sample_summary = st.session_state.get("md_sample_summary", None)
                                    st.code(md_sample_summary, height="stretch")

                                with st.expander("Data Sample", expanded=False):
                                    md_sample = st.session_state.get("md_sample", None)
                                    st.code(md_sample, height=250)

                            if st.session_state.get("contract_schema_cols", None):
                                with st.expander("Data Sample Summary", expanded=False):
                                    contract_schema_cols = st.session_state.get("contract_schema_cols", None)
                                    cl = []
                                    for c in contract_schema_cols:
                                        cl.append(c.model_dump())
                                    st.json(cl)

        with col_r:
            yaml_fundamentals, yaml_schemas = st.tabs(["Contract Yaml", "Schemas"])

            with yaml_fundamentals:
                st.subheader("Contract Fundamentals")
                if st.session_state.get("skadi_contract_body", None):
                    bd = st.session_state.get("skadi_contract_body").model_dump_json()
                    sb = get_yaml_from_json_content(bd)
                    st.code(sb, language="yaml")

            with yaml_schemas:
                st.subheader("Contract Schemas")
                if st.session_state.get("skadi_contract_body", None):
                    bd = st.session_state.get("skadi_contract_body").model_dump_json()
                    sb = get_yaml_from_json_content(bd)
                    st.code(sb)
