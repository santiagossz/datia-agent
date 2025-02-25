import streamlit as st
import asyncio
import uuid
import requests
from app.config import agent_cfg
import plotly.io as pio


async def main():
    st.set_page_config(
        page_title="Datia Agent",
        page_icon="🤖",
    )
    st.sidebar.write("""
        🎯 **DATIA**    
        *Automatiza el análisis de datos con IA*
        """)
    st.sidebar.text(" ")
    st.sidebar.selectbox(
        "Selecciona un modelo 🤖", [agent_cfg.OPENAI_MODEL, agent_cfg.OPENAI_MODEL_MINI]
    )

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []
        st.html(
            "<div style='font-size: 1.5rem; display: flex; height: 60vh; justify-content: center; align-items: center; text-align: center;flex-direction: column;'>"
            "<div>🚀</div>"
            "<div>Empieza a descubrir el potencial de tus datos</div>"
            "</div>",
        )

    params = {"session_id": st.session_state["session_id"]}
    st.session_state["messages"] = invoke_agent_api(params, "memory", "GET")
    messages = st.session_state["messages"]

    if "human_validation" not in st.session_state:
        st.session_state.human_validation = True

    if len(messages) > 0 and st.session_state.human_validation:
        for i, msg in enumerate(messages["user_input"]):
            st.chat_message("human").write(msg["content"])
            if len(messages["plot"]) > i and len(messages["new_plot"][i]) <= i:
                plot(messages["plot"][i])
            if len(messages["new_plot"]) > i:
                plot(messages["new_plot"][i])
            if len(messages["ai_response"]) > i:
                st.chat_message("ai").write(messages["ai_response"][i]["content"])

    if user_msg := st.chat_input("Escribe tu pregunta"):
        st.chat_message("human").write(user_msg)
        params["msg"] = user_msg
        res = invoke_agent_api(params, "test", "POST")
        if res.get("ai_response", None):
            st.chat_message("ai").write(res["ai_response"][-1]["content"])

        else:
            st.session_state.human_validation = False
            if res.get("validate_data", None):
                df = res["validate_data"]["data_head"]
                link = res["validate_data"]["link"]

                with st.form(key="validate_data_form"):
                    st.write(
                        "Por favor confirma si voy a utilizar la data correcta para mi análisis"
                    )
                    st.dataframe(df)
                    st.write(f"Source: {link}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.form_submit_button("✅ Si", on_click=human_validate)
                    with col2:
                        st.form_submit_button("❌ No", on_click=human_validate)


def invoke_agent_api(params, route="test", method="POST"):
    url = "http://localhost:8000"
    response = requests.request(method, f"{url}/{route}", params=params)
    return response.json()


def human_validate():
    params = {"session_id": st.session_state["session_id"]}
    res = invoke_agent_api(params, "validate_data", "POST")
    plot(res["validate_plot"]["plot"])
    if "user_text" not in st.session_state:
        st.session_state.user_text = ""

    st.text_area(
        "Hay algo que quieras cambiar en el gráfico?",
        key="user_text",
        on_change=human_validate_plot,
    )
    with st.form(key="validate_plot_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.form_submit_button(
                "✅ Enviar cambios",
                on_click=human_validate_plot,
            )
        with col2:
            st.form_submit_button("➡️ Dejar como está", on_click=human_validate_plot)


def human_validate_plot():
    params = {
        "session_id": st.session_state["session_id"],
        "human_input": st.session_state.user_text,
    }
    invoke_agent_api(params, "validate_plot", "POST")
    st.session_state.human_validation = True


def plot(res_plot):
    fig = pio.from_json(res_plot)
    st.chat_message("ai").plotly_chart(fig, key=str(uuid.uuid4()))


if __name__ == "__main__":
    asyncio.run(main())
