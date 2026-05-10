mkdir -p ~/.streamlit/

echo "1
[server]\n\|
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" › ~/.streamlit/config.toml