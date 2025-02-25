# datia-agent

Data Analyst Agent

## How To


1. Create *google sheet* and *supabase* connections using n8n worflows from [n8n-workflows](./n8n-workflows)
2. Add environment variables into `.env` file. Use [.env.example](.env.example) as reference
3. Create python virtual environment
    
    * install [UV](https://github.com/astral-sh/uv) (python package manager)
        ```
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

    * create `.venv` virtual environment
        ```
        uv sync
        ```
3. Deploy API using [FastAPI](https://fastapi.tiangolo.com/)

    ```
    cd app
    uv run main.py
    ```

3. Deploy [Streamlit](https://streamlit.io) frontend chat for testing 

    ```
    cd streamlit
    uv run streamlit run chat.py 
    ```

4. Test

    Go to http://localhost:8501/ and ask questions to DatIA AI. Examples: 

    * cuantas ventas realicé cada semana por hombre y mujer para el productos de Beauty?
    * cuanto tengo de inventario por cada categoría de producto? cual es la categoría con mayor inventario?
