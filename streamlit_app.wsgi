from streamlit import cli as _cli

def application(environ, start_response):
    # Set up arguments to pass to Streamlit
    args = ["streamlit", "run", "stockWeb.py"]
    
    # Call Streamlit CLI with the arguments
    _cli._main_run(args)

# Make sure to replace "stockWeb.py" with the actual filename of your Streamlit app
